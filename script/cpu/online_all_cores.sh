#!/bin/bash -e

# SPDX-FileCopyrightText: 2025 Isac Pasianotto <isac.pasianotto@phd.units.it>
# SPDX-FileCopyrightText: 2025 Niccolo Tosato <niccolo.tosato@phd.units.it>
# SPDX-FileCopyrightText: 2025 Ruggero Lot <ruggero.lot@areasciencepark.it>
#
# SPDX-License-Identifier: GPL-3.0-or-later

echo "Host: $(hostname)"
echo "Starting to online all CPU cores, current cores online $(nproc)"

# Counter to track how many CPUs were onlined
ONLINED=0
ONLINE=$(nproc)
# Iterate through all available CPU cores
for cpu in /sys/devices/system/cpu/cpu[0-9]*/online; do
    cpu_id=$(basename "$(dirname "$cpu")")
    current_state=$(cat "$cpu")
    if [ "$current_state" -eq 0 ]; then
        echo 1 > "$cpu" 2>/dev/null
        new_state=$(cat "$cpu")
        if [ "$new_state" -eq 1 ]; then
            ONLINED=$((ONLINED + 1))
        else
            echo "Failed to online $cpu_id. Skipping."
	exit 3
        fi
    fi
done

echo "Finished processing. Total online cores: $ONLINE + $ONLINED"

if [ "$(nproc)" != "32" ]; then
echo "Failed onlining"
else
echo "Successfull onlining"
fi
