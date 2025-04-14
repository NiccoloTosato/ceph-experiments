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

#!/bin/bash -e

scale_blkio () {
echo "Scalink blkio $1"
  ssh root@$1 sh /root/blkio/blkio.sh $2

}

for host in xx.xx.xx.xx yy.yy.yy.yy ; do
  scale_blkio $host $1
done



