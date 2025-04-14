#!/bin/bash

# SPDX-FileCopyrightText: 2025 Isac Pasianotto <isac.pasianotto@phd.units.it>
# SPDX-FileCopyrightText: 2025 Niccolo Tosato <niccolo.tosato@phd.units.it>
# SPDX-FileCopyrightText: 2025 Ruggero Lot <ruggero.lot@areasciencepark.it>
#
# SPDX-License-Identifier: GPL-3.0-or-later

# Ensure the speed argument is provided
if [ -z "$1" ]; then
    echo "Usage: $0 <speed>"
    echo "Example: $0 1mb"
    exit 1
fi

SPEED=$1

# Fetch the list of container IDs matching "osd"
container_ids=$(podman ps | grep osd | awk '{print $1}')

# Check if there are any containers to update
if [ -z "$container_ids" ]; then
    echo "No containers matching 'osd' found."
    exit 0
fi

device_ids=$(lsblk | grep disk | grep 20T | awk '{print $1}')
limit=""

# Loop through each device ID
for device in $device_ids; do
    # Append to the result string
    limit+="--device-write-bps /dev/${device}:${SPEED}mb --device-read-bps /dev/${device}:${SPEED}mb "
done
#limit+="--device-write-bps:/dev/nvme0n1:100mb --device-read-bps:/dev/nvme0n1:100mb "
# Loop through each container ID and apply the update
for container_id in $container_ids; do
    echo "Updating container $container_id with device write limit of $SPEED..."
    podman update $container_id  ${limit}
    # Check if the update was successful
    if [ $? -eq 0 ]; then
        echo "Successfully updated container $container_id."
    else
        echo "Failed to update container $container_id. Please check the logs for details."
    fi
done

echo "Update process completed."
