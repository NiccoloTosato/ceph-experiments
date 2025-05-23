#!/bin/bash

# SPDX-FileCopyrightText: 2025 Isac Pasianotto <isac.pasianotto@phd.units.it>
# SPDX-FileCopyrightText: 2025 Niccolo Tosato <niccolo.tosato@phd.units.it>
# SPDX-FileCopyrightText: 2025 Ruggero Lot <ruggero.lot@areasciencepark.it>
#
# SPDX-License-Identifier: GPL-3.0-or-later

repeat_count=15
device_count=12

mkdir -p results

# Loop through each I/O engine
for device in $(seq 1 $device_count); do
  for repeat in $(seq 1 $repeat_count); do
    # Run fio with appropriate file, output format, and unique output filename
    fio --output="results/write_disk_${device}_${repeat}.json" --output-format=json+ "disk_${device}_write.fio"
    fio --output="results/read_disk_${device}_${repeat}.json" --output-format=json+ "disk_${device}_read.fio"
  done
done
