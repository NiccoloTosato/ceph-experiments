#!/bin/bash

# Define arrays for cores, modes, replicas, and run IDs
memory="128"
cores=(32 24 16 8)
modes=("read" "write" "randread" "randwrite")
replicas=(1 2 3)
run_ids=$(seq 1 7)
date
# Iterate over all combinations
for core in "${cores[@]}"; do
  ./cpu/offline_core.sh $((32-${core}))
  for run_id in $run_ids; do
    for mode in "${modes[@]}"; do
        for replica in "${replicas[@]}"; do
                # Construct the FIO job file path and results output path
                job_file="job/${mode}/${mode}_replica${replica}"
                output_file="results/${mode}_replica_${replica}_core_${core}_memory_${memory}_run_${run_id}.json"
                # Run the FIO command
                echo "Running FIO for core=$core, mode=$mode, replica=$replica, run_id=$run_id..."
	        fio "$job_file" --output "$output_file" --client=hostfile --output-format=json
		echo -n "Read= "
                cat $output_file | jq '.client_stats[6].read.bw_bytes / 1024 / 1024'
                echo -n "Write= "
                cat $output_file | jq '.client_stats[6].write.bw_bytes / 1024 / 1024'
                # Check if the command was successful
                if [ $? -ne 0 ]; then
                    echo "Error: FIO failed for $job_file (core=$core, mode=$mode, replica=$replica, run_id=$run_id)"
                fi
            done
        done
    done
done
date
echo "All FIO tests completed."
