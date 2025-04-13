#!/bin/bash

# SPDX-FileCopyrightText: 2025 Isac Pasianotto <isac.pasianotto@phd.units.it>
# SPDX-FileCopyrightText: 2025 Niccolo Tosato <niccolo.tosato@phd.units.it>
# SPDX-FileCopyrightText: 2025 Ruggero Lot <ruggero.lot@areasciencepark.it>
#
# SPDX-License-Identifier: GPL-3.0-or-later

if [ -z "$1" ]; then
  echo "Usage: $0 <filesystem_type>"
  echo "Example: $0 xfs"
  exit 1
fi

filesystem_type=$1

io_engines=("libaio" "posixaio" "uring" "sync") 
repeat_count=5

mkdir -p results

# Loop through each I/O engine
for engine in "${io_engines[@]}"; do
  # Repeat each command five times
  for i in $(seq 1 $repeat_count); do
    # Run fio with appropriate file, output format, and unique output filename
    fio --output="results/${filesystem_type}-${engine}_${i}.json" --output-format=json+ "${filesystem_type}-${engine}.fio"
  done
done
