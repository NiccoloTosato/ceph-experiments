#!/bin/bash

# SPDX-FileCopyrightText: 2025 Isac Pasianotto <isac.pasianotto@phd.units.it>
# SPDX-FileCopyrightText: 2025 Niccolo Tosato <niccolo.tosato@phd.units.it>
# SPDX-FileCopyrightText: 2025 Ruggero Lot <ruggero.lot@areasciencepark.it>
#
# SPDX-License-Identifier: GPL-3.0-or-later

# Ensure the user provides the number of cores to offline
if [ -z "$1" ]; then
    echo "Usage: $0 <number_of_cores_to_offline>"
    exit 1
fi

NUM_TO_OFFLINE=$1
OFFLINED=0
# Get the total number of CPUs
TOTAL_CPUS=31

# Iterate over all CPUs from 0 to TOTAL_CPUS-1
for ((cpu=31; cpu>0; cpu--)); do
    if [ "$OFFLINED" -ge "$NUM_TO_OFFLINE" ]; then
        break
    fi
    # Check if the CPU can be offlined
    CPU_PATH="/sys/devices/system/cpu/cpu$cpu/online"
    if [ -f "$CPU_PATH" ]; then
        current_state=$(cat "$CPU_PATH")
        if [ "$current_state" -eq 1 ]; then
            echo 0 > "$CPU_PATH" 2>/dev/null
            new_state=$(cat "$CPU_PATH")
            if [ "$new_state" -eq 0 ]; then
                OFFLINED=$((OFFLINED + 1))
            else
                echo "Failed to offline cpu$cpu. Skipping."
		exit 3
            fi
        else
            OFFLINED=$((OFFLINED + 1))
        fi
    else
        echo "cpu$cpu does not support online/offline. Skipping."
    fi
done

echo "Finished processing. Total cores offlined: $OFFLINED."

# If not enough cores were offlined, notify the user
if [ "$OFFLINED" -lt "$NUM_TO_OFFLINE" ]; then
    echo "Warning: Could only offline $OFFLINED out of $NUM_TO_OFFLINE requested cores."
fi
