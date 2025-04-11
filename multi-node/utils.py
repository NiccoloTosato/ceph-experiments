import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

def open_result(fstype):
    #init an empty dataframe
    df = pd.DataFrame()
    
    for engine in ["libaio","uring","posixaio","sync"]:
        for run_id in range(1,7):
            with open(f'{fstype}/{fstype}-{engine}_{run_id}.json', 'r') as file:
                job = json.load(file)
                #add run id 
                job['run_id']=run_id
                job['fstype']=fstype
                df_tmp=json_to_dataframe(job)
                df= pd.concat([df, df_tmp], ignore_index=True)
    df = df.astype({'numjobs':'int'})
    return df

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


def plot_read_write_cs3(df):
    # Set a cleaner style and color palette
    sns.set_theme(style="whitegrid")#, palette="tab10")
    sns.set_palette("crest")  # Try "mako", "crest", "flare", or "rocket"
    # Create the plot with refined settings
    custom_palette = ['#FFB000', '#DC267F', '#FE6100', '#785EF0', ]
    data_tmp=df.copy()
    data_tmp["ram"]=data_tmp["ram"]/16
    data_tmp["core"]=data_tmp["core"]/16
    
    ax = sns.relplot(
        data=data_tmp[((data_tmp["mode"]=="read") | (data_tmp["mode"]=="write"))& (data_tmp["replica"]!=1)],
        x="ram",
        y="bw",
        col="replica",
        row="mode",
        hue="core",
        style="core",
        kind="line",
        height=4,  # Adjust height for better proportions
        aspect=1.4,  # Wider aspect ratio for readability
        markers=True,  # Show markers at each data point
        dashes=False,  # Use solid lines for clarity
         palette=custom_palette,
    )
    
    # Set axis labels with better descriptions
    #ax.set_axis_labels("Amount of RAM [GB]", "Bandwidth [GB/s]")
    #ax.set_axis_labels("Number of cores", "Bandwidth [GB/s]")
    ax.set_axis_labels("RAM per OSD [GB]", "Bandwidth [GB/s]",fontsize=17)
    
    # Add a title for the legend and improve placement
    ax._legend.set_title("Core per OSD")
    ax._legend.set_bbox_to_anchor((1.09, 0.5))  # Position legend outside the plot
    
    
    title_custom=["Read - Replica x2","Read - Replica x3","Write - Replica x2","Write - Replica x3" ]
    # Set individual titles for each subplot
    for i, a in enumerate(ax.axes.flat):
        # You can customize the titles as needed
        title = f"{title_custom[i]}"  # This will dynamically use the existing title
        a.set_title(title, fontsize=18)  # Set custom title for each subplot
        
    for a in ax.axes.flat:
        a.set_xticks(np.array([32, 64, 128, 192])/16)
        a.set_xticklabels(np.array([32, 64, 128, 192],dtype=np.int32)//16,fontsize=17)
        a.tick_params(axis='y', labelsize=17)
        a.set_ylim((2,12))
    
    
    for ax_sub in ax.axes.flat:
        for line in ax_sub.lines:
            line.set_markersize(8)  # Increase marker size (adjust value as needed)
    
    
    ax.tight_layout()
    plt.setp(ax._legend.get_texts(), fontsize=17)  # Adjust the text size
    plt.setp(ax._legend.get_title(), fontsize=17)  # Adjust the title size
    
    # Improve the x-axis labels on each subplot
    #for idx,a in enumerate(ax.axes.flat):
    #    if idx in [0,1,2]:
    #        a.set_ylim([3,17])
    #    a.set_xticks(df["ram"].unique())
    #    a.set_xticklabels(df["ram"].unique(), fontsize=18, rotation=0)
    
    # Adjust spacing between plots for clarity
    ax.tight_layout()
    for ax_sub in ax.axes.flat:
        for line in ax_sub.lines:
            line.set_markersize(8)  # Increase marker size (adjust value as needed)
    
    
    
    plt.savefig("sequential.svg",format="svg", bbox_inches='tight')
    plt.show()



def plot_rand_read_write_cs3(df):
    # Set a cleaner style and color palette
    sns.set_theme(style="whitegrid")#, palette="tab10")
    sns.set_palette("crest")  # Try "mako", "crest", "flare", or "rocket"
    # Create the plot with refined settings
    data_tmp=df[((df["mode"]=="randread") | (df["mode"]=="randwrite"))& (df["replica"]!=1) ].copy()
    data_tmp["bw"]=data_tmp["bw"]*(10**9)/(4*1024)
    data_tmp["ram"]=data_tmp["ram"]/16
    data_tmp["core"]=data_tmp["core"]/16
    
    data_tmp["mode"] = pd.Categorical(data_tmp["mode"], categories=["randread","randwrite"], ordered=True)
    ax = sns.relplot(
        data=data_tmp[(data_tmp["mode"] == "randwrite") | (data_tmp["mode"] == "randread")],
        x="ram",
        y="bw",
        col="replica",
        row="mode",
        hue="core",
        kind="line",
        style="core",
        height=4,  # Adjust height for better proportions
        aspect=1.4,  # Wider aspect ratio for readability
        markers=True,  # Show markers at each data point
        dashes=False,  # Use solid lines for clarity
        palette=['#FFB000', '#DC267F', '#FE6100', '#785EF0', ]
    )
    
    # Set axis labels with better descriptions
    ax.set_axis_labels("RAM per OSD [GB]", "Bandwidth [GB/s]",fontsize=17)
    
    # Add a title for the legend and improve placement
    ax._legend.set_title("Core per OSD")
    ax._legend.set_bbox_to_anchor((1.10, 0.5))  # Position legend outside the plot
    
    for ax_sub in ax.axes.flat:
        for line in ax_sub.lines:
            line.set_markersize(8)  # Increase marker size (adjust value as needed)
    
    title_custom=["Read - Replica x1","Read - Replica x2","Read - Replica x3","Write - Replica x1","Write - Replica x2","Write - Replica x3" ]
    title_custom=["Read - Replica x2","Read - Replica x3","Write - Replica x2","Write - Replica x3" ]
    
    # Set individual titles for each subplot
    for i, a in enumerate(ax.axes.flat):
        # You can customize the titles as needed
        title = f"{title_custom[i]}"  # This will dynamically use the existing title
        a.set_title(title, fontsize=16)  # Set custom title for each subplot
        
    import matplotlib.ticker as ticker 
    import numpy as np
    def scientific_notation(x, pos):
        if x == 0:
            return "0"
        exponent = int(np.floor(np.log10(abs(x))))
        coeff = x / 10**exponent
        if exponent == 0:
            return f'{x:.0f}'
        elif exponent == 1:
            return r"${:.1f} \cdot 10^1$".format(x)
        else:
            return r"${:.1f} \cdot 10^{{{}}}$".format(coeff, exponent)
    
    for a in ax.axes.flat:
        a.set_xticks(np.array([32, 64, 128, 192])/16)
        a.set_xticklabels(np.array([32, 64, 128, 192],dtype=np.int32)//16,fontsize=17)
        a.tick_params(axis='y', labelsize=17)
            # Set y-axis to scientific notation
        #a.yaxis.set_major_formatter(ticker.FuncFormatter(scientific_notation))
    
        #a.set_ylim((2,12))
    #######################################################################
    def scientific_notation(x, pos):
        return f"${x:.1e}$"  # Format as LaTeX scientific notation
    from matplotlib.ticker import ScalarFormatter
    for ax_sub in ax.axes.flat:
        plt.ticklabel_format(axis='y', style='sci', scilimits=(0,0),useMathText=True)  # Y-axis scientific notation
        #ax_sub.yaxis.set_major_formatter(ticker.FuncFormatter(scientific_notation))
    #######################################################################
    ax.tight_layout()
    plt.setp(ax._legend.get_texts(), fontsize=17)  # Adjust the text size
    plt.setp(ax._legend.get_title(), fontsize=17)  # Adjust the title size
    
    
    plt.savefig("random.svg",format="svg", bbox_inches='tight')
    
    plt.show()
    
def plot_read_write_cs3(df):
    # Set a cleaner style and color palette
    sns.set_theme(style="whitegrid")#, palette="tab10")
    #sns.set_palette("crest")  # Try "mako", "crest", "flare", or "rocket"
    # Create the plot with refined settings
    
    data_tmp=df[((df["mode"]=="randread") | (df["mode"]=="randwrite"))& (df["replica"]!=1)  ].copy()
    data_tmp["bw"]=data_tmp["bw"]*(10**9)/(4*1024)
    data_tmp["mode"] = pd.Categorical(data_tmp["mode"], categories=["randread","randwrite"], ordered=True)
    
    ax = sns.relplot(
            data=data_tmp[(data_tmp["mode"]=="randread") | (data_tmp["mode"]=="randwrite") ], 
        x="device_speed",
         y="bw",
        col="replica",
        row="mode",
        hue="core",
        kind="line",
        height=4,  # Adjust height for better proportions
        aspect=1.6,  # Wider aspeopenflightmapsct ratio for readability
        markers=False,  # Show markers at each data point
        dashes=True,  # Use solid lines for clarity
        palette="Set1"
    )
    
    
    
    ax.set(xlabel='HDD speed [MiB/s]', ylabel="Bandwidth [GB/s]")
    
    for a in ax.axes.flat:
        a.set_xticks(ticks=df["device_speed"].unique()) # set new labels
        a.set_xticklabels(fontsize=8, rotation=0, labels=df["device_speed"].unique())
        ############################################
    # Set axis labels with better descriptions
    ax.set_axis_labels("HDD speed [MiB/s]", "IOPS",fontsize=16)
    
    #ax.set_axis_labels("Number of cores", "Bandwidth [GB/s]")
    
    # Add a title for the legend and improve placement
    #ax._legend.set_title("Number of cores")
    #ax._legend.set_bbox_to_anchor((1.09, 0.5))  # Position legend outside the plot
    
    
    title_custom=["Read - Replica x1","Read - Replica x2","Read - Replica x3","Write - Replica x1","Write - Replica x2","Write - Replica x3" ]
    title_custom=["Read - Replica x2","Read - Replica x3","Write - Replica x2","Write - Replica x3" ]
    
    # Set individual titles for each subplot
    for i, a in enumerate(ax.axes.flat):
        # You can customize the titles as needed
        title = f"{title_custom[i]}"  # This will dynamically use the existing title
        a.set_title(title, fontsize=17)  # Set custom title for each subplot
        
    
    for a in ax.axes.flat:
        a.set_xticks(ticks=df["device_speed"].unique()) # set new labels
        a.set_xticklabels(fontsize=16, rotation=0, labels=df["device_speed"].unique())
        a.tick_params(axis='y', labelsize=16)
    
        a.set_xlim((99,276))
        a.set_ylim((4000,12000))
    
    #######################################################################
    def scientific_notation(x, pos):
        return f"${x:.1e}$"  # Format as LaTeX scientific notation
    from matplotlib.ticker import ScalarFormatter
    for ax_sub in ax.axes.flat:
        plt.ticklabel_format(axis='y', style='sci', scilimits=(0,0),useMathText=True)  # Y-axis scientific notation
        #ax_sub.yaxis.set_major_formatter(ticker.FuncFormatter(scientific_notation))
    #######################################################################
    
    ax.tight_layout()
    #plt.setp(ax._legend.get_texts(), fontsize=16)  # Adjust the text size
    #plt.setp(ax._legend.get_title(), fontsize=16)  # Adjust the title size
    ax._legend.remove()
    
    plt.savefig("random-hdd.svg", format='svg', bbox_inches='tight')
    plt.show()

def plot_rand_read_write_cs3(df):
    # Set a cleaner style and color palette
    sns.set_theme(style="whitegrid")#, palette="tab10")
    #sns.set_palette("crest")  # Try "mako", "crest", "flare", or "rocket"
    # Create the plot with refined settings
    
    data_tmp=df[((df["mode"]=="read") | (df["mode"]=="write"))& (df["replica"]!=1)  ].copy()
    #data_tmp["bw"]=data_tmp["bw"]*(10**9)/(4*1024)
    data_tmp["mode"] = pd.Categorical(data_tmp["mode"], categories=["read","write"], ordered=True)
    
    ax = sns.relplot(
            data=data_tmp[(data_tmp["mode"]=="read") | (data_tmp["mode"]=="write") ], 
        x="device_speed",
         y="bw",
        col="replica",
        row="mode",
        hue="core",
        kind="line",
        height=4,  # Adjust height for better proportions
        aspect=1.6,  # Wider aspect ratio for readability
        markers=False,  # Show markers at each data point
        dashes=True,  # Use solid lines for clarity
        palette="Set1"
    )
    
    
    
    
    for a in ax.axes.flat:
        a.set_xticks(ticks=df["device_speed"].unique()) # set new labels
        a.set_xticklabels(fontsize=8, rotation=0, labels=df["device_speed"].unique())
        ############################################
    # Set axis labels with better descriptions
    ax.set_axis_labels("HDD speed [MiB/s]", "Bandwidth [GB/s]",fontsize=16)
    
    #ax.set_axis_labels("Number of cores", "Bandwidth [GB/s]")
    
    # Add a title for the legend and improve placement
    #ax._legend.set_title("Number of cores")
    #ax._legend.set_bbox_to_anchor((1.09, 0.5))  # Position legend outside the plot
    
    
    title_custom=["Read - Replica x1","Read - Replica x2","Read - Replica x3","Write - Replica x1","Write - Replica x2","Write - Replica x3" ]
    title_custom=["Read - Replica x2","Read - Replica x3","Write - Replica x2","Write - Replica x3" ]
    
    # Set individual titles for each subplot
    for i, a in enumerate(ax.axes.flat):
        # You can customize the titles as needed
        title = f"{title_custom[i]}"  # This will dynamically use the existing title
        a.set_title(title, fontsize=17)  # Set custom title for each subplot
        
    
    for a in ax.axes.flat:
        a.set_xticks(ticks=df["device_speed"].unique()) # set new labels
        a.set_xticklabels(fontsize=16, rotation=0, labels=df["device_speed"].unique())
        a.tick_params(axis='y', labelsize=16)
        a.set_xlim((99,276))
        a.set_ylim((1,5))
    
    
    ax.tight_layout()
    #plt.setp(ax._legend.get_texts(), fontsize=16)  # Adjust the text size
    #plt.setp(ax._legend.get_title(), fontsize=16)  # Adjust the title size
    ax._legend.remove()
    
    plt.savefig("sequential-hdd.svg", format='svg', bbox_inches='tight')
    plt.show()
