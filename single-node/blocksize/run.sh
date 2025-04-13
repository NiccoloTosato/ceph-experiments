#!/bin/bash

# SPDX-FileCopyrightText: 2025 Isac Pasianotto <isac.pasianotto@phd.units.it>
# SPDX-FileCopyrightText: 2025 Niccolo Tosato <niccolo.tosato@phd.units.it>
# SPDX-FileCopyrightText: 2025 Ruggero Lot <ruggero.lot@areasciencepark.it>
#
# SPDX-License-Identifier: GPL-3.0-or-later

for i in {1..5}
do
  echo "Run #$i:"
  fio --output-format=json+ --output=results/bs-experiment_${i}.json bs-experiment.fio
done
