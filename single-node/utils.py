# SPDX-FileCopyrightText: 2025 2025 Isac Pasianotto <isac.pasianotto@phd.units.it>
# SPDX-FileCopyrightText: 2025 2025 Niccolo Tosato <niccolo.tosato@phd.units.it>
# SPDX-FileCopyrightText: 2025 2025 Ruggero Lot <ruggero.lot@areasciencepark.it>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def json_to_dataframe(job):
    """
    Given a parsed json, return a dataframe.
    """
    df = pd.DataFrame()
    global_options=job["global options"]
    for j in job['jobs']:
        options=dict()
        options=options | global_options
        options['jobname']=j['jobname']
        try:
            options['fstype']=job['fstype']
        except KeyError as err:
            options['fstype']='unknown'
        try:
            options['run_id']=job['run_id']
        except KeyError as err:
            options['run_id']=-1
        try:
            options['sys_cpu']=j['sys_cpu']*int(j['job options']['numjobs'])
            options['usr_cpu']=j['usr_cpu']*int(j['job options']['numjobs'])
        except:
            options['device_count']=job['device_count']
        try:
            options = options | j['job options']  
        except:
            print(f"Error in job {j['jobname']}")
            continue
        options["bandwidth"]=0
        for key,value in j['read'].items():
            if not isinstance(value,dict):
                if key == "bw_bytes":
                    value=value/1024/1024
                    options["bandwidth"]+=value
                options[f'read_{key}']=value
        for key,value in j['write'].items():
            if not isinstance(value,dict):
                if key == "bw_bytes":
                    value=value/1024/1024
                    options["bandwidth"]+=value
                options[f'write_{key}']=value
        
        experiment=pd.DataFrame(options, index=[0])
        #print(experiment['jobname'])
        df= pd.concat([df, experiment], ignore_index=True)
    return df


def open_result(fstype):
    #init an empty dataframe
    df = pd.DataFrame()
    
    for engine in ["libaio","uring","posixaio","sync"]:
        for run_id in range(1,6):
            with open(f'{fstype}/results/{fstype}-{engine}_{run_id}.json', 'r') as file:
                job = json.load(file)
                #add run id 
                job['run_id']=run_id
                job['fstype']=fstype
                df_tmp=json_to_dataframe(job)
                df= pd.concat([df, df_tmp], ignore_index=True)
    df = df.astype({'numjobs':'int'})
    return df

def plot_results(fstype,results):
    filtered=results[results['fstype']==fstype]
    ax  = sns.relplot(
        data=filtered, x="numjobs", y="bandwidth", col="ioengine",row="rw",
        hue="bs", kind="line"#, style="event", kind="line",
    )
    ax.set(xlabel='Number of process', ylabel='BW [MiB/s]')
    ax.legend.set_title("Block size [Bytes]")
    for a in ax.axes.flat:
        a.set_xticks(ticks=filtered["numjobs"].unique()) # set new labels
        a.set_xticklabels(fontsize=8, rotation=0, labels=filtered["numjobs"].unique())
        min_y,max_y=a.get_yticks()[[0,-1]]
        min_y=0
        if max_y-min_y < 1000:
            new_ticks=list(range(int(min_y),int(max_y)+25,25))
            a.set_yticks(ticks=new_ticks)
            a.set_yticklabels(fontsize=8, rotation=0, labels=new_ticks)
        ax.set(ylim=(0, 300))


def print_table_max_mean_min(results,fstype):
    results=results[results["numjobs"]==1]
    for test in ["read","write"]:
        print(f"Result on {fstype},test {test}")
        print(f" Max {results[(results["fstype"]==fstype) & (results["rw"]==test)]["bandwidth"].max()} MiB/s")
    for test in ["randread","randwrite"]:
        print(f"Result on {fstype},test {test}")
        print(f" Max {results[(results["fstype"]==fstype) & (results["rw"]==test) & (results["bs"]=="4k")]["bandwidth"].max()/4096*1024*1024} IOPS")