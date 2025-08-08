#!/bin/bash

# Define arrays for cores, modes, replicas, and run IDs
memory="192"
core="32"
speeds=("100" "125" "150" "175" "200" "225" "250" "275" )
modes=("read" "write" "randread" "randwrite")
replicas=(1 2 3)
run_ids=$(seq 1 7)
date
# Iterate over all combinations
for speed in "${speeds[@]}"; do
  ./blkio/blkio.sh ${speed}
  for run_id in $run_ids; do
    for mode in "${modes[@]}"; do
        for replica in "${replicas[@]}"; do
                # Construct the FIO job file path and results output path
                job_file="job/${mode}/${mode}_replica${replica}"
                output_file="results_device/${mode}_replica_${replica}_core_${core}_memory_${memory}_speed_${speed}_run_${run_id}.json"
                # Run the FIO command
                echo "Running FIO for core=$core, mode=$mode, replica=$replica, run_id=$run_id..."
	        fio "$job_file" --output "$output_file" --client=hostfile --output-format=json
		echo -n "Read= "
                cat $output_file | jq '.client_stats[5].read.bw_bytes / 1024 / 1024'
                echo -n "Write= "
                cat $output_file | jq '.client_stats[5].write.bw_bytes / 1024 / 1024'
                # Check if the command was successful
                if [ $? -ne 0 ]; then
                    echo "Error: FIO failed for $job_file (core=$core, mode=$mode, replica=$replica, run_id=$run_id)"
                fi
            done
        done
    done
done
done
date
echo "All FIO tests completed."
