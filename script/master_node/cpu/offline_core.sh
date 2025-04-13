#!/bin/bash -e

# SPDX-FileCopyrightText: 2025 Isac Pasianotto <isac.pasianotto@phd.units.it>
# SPDX-FileCopyrightText: 2025 Isac Pasianotto isac.pasianotto@phd.units.it
# SPDX-FileCopyrightText: 2025 Niccolo Tosato <niccolo.tosato@phd.units.it>
# SPDX-FileCopyrightText: 2025 Niccolo Tosato niccolo.tosato@phd.units.it
# SPDX-FileCopyrightText: 2025 Ruggero Lot <ruggero.lot@areasciencepark.it>
# SPDX-FileCopyrightText: 2025 opyright=Ruggero Lot ruggero.lot@areasciencepark.it
#
# SPDX-License-Identifier: GPL-3.0-or-later

scale_core () {
echo "Offlining $2 cores on host $1"
  ssh root@$1 sh /root/cpu/online_all_cores.sh
  ssh root@$1 sh /root/cpu/offline_core.sh $2
  proc=$(ssh root@$1 nproc)
if [ $2 != $((32 - proc)) ]; then
echo "Failed on scaling !!!!!"
exit 3
fi

}
for host in xx.xx.xx.xx yy.yy.yy.yy ; do
  scale_core $host $1
done
