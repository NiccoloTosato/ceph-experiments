#!/bin/bash

# SPDX-FileCopyrightText: 2025 Isac Pasianotto <isac.pasianotto@phd.units.it>
# SPDX-FileCopyrightText: 2025 Niccolo Tosato <niccolo.tosato@phd.units.it>
# SPDX-FileCopyrightText: 2025 Ruggero Lot <ruggero.lot@areasciencepark.it>
#
# SPDX-License-Identifier: GPL-3.0-or-later

# Check if the script is run as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root"
    exit 1
fi

echo "Starting to online all memory blocks..."

# Iterate through all memory blocks
for memblock in /sys/devices/system/memory/memory*/state; do
    block_name=$(basename "$(dirname "$memblock")")
    current_state=$(cat "$memblock")
    
    echo "Processing $block_name (current state: $current_state)..."

    if [ "$current_state" == "offline" ]; then
        # Attempt to online the memory block
        echo "Trying to online $block_name..."
        echo online > "$memblock" 2>/dev/null

        # Check if the operation was successful
        new_state=$(cat "$memblock")
        if [ "$new_state" == "online" ]; then
            echo "$block_name successfully onlined."
        else
            echo "Failed to online $block_name. Skipping."
        fi
    else
        echo "$block_name is already online. Skipping."
    fi
done

echo "Finished processing all memory blocks."
