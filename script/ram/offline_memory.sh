#!/bin/bash

# SPDX-FileCopyrightText: 2025 Isac Pasianotto <isac.pasianotto@phd.units.it>
# SPDX-FileCopyrightText: 2025 Niccolo Tosato <niccolo.tosato@phd.units.it>
# SPDX-FileCopyrightText: 2025 Ruggero Lot <ruggero.lot@areasciencepark.it>
#
# SPDX-License-Identifier: GPL-3.0-or-later

# Iterate through all memory blocks
for memblock in /sys/devices/system/memory/memory*/state; do
    block_name=$(basename "$(dirname "$memblock")")
    current_state=$(cat "$memblock")
    
    echo "Processing $block_name (current state: $current_state)..."

    if [ "$current_state" == "online" ]; then
        # Attempt to offline the memory block
        echo "Trying to offline $block_name..."
        echo offline > "$memblock" 2>/dev/null

        # Check if the operation was successful
        new_state=$(cat "$memblock")
        if [ "$new_state" == "offline" ]; then
            echo "$block_name successfully offlined."
        else
            echo "Failed to offline $block_name. Skipping."
        fi
    else
        echo "$block_name is already offline. Skipping."
    fi
done

echo "Finished processing all memory blocks."
