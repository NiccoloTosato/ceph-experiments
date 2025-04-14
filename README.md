<!--
SPDX-FileCopyrightText: 2025 2025 Isac Pasianotto <isac.pasianotto@phd.units.it>
SPDX-FileCopyrightText: 2025 2025 Niccolo Tosato <niccolo.tosato@phd.units.it>
SPDX-FileCopyrightText: 2025 2025 Ruggero Lot <ruggero.lot@areasciencepark.it>

SPDX-License-Identifier: CC-BY-4.0
-->

# Ceph experiments

Benchmarking Ceph across hardware setups for cost-performance optimization.

## What's in ? 

- `extra`: notes about switch configurations, nodes provisioning and FIO debugging session and ceph deploy.
- `multi-node`: result obtained using 8-node cluster, `json` with results and `fio` job file are provided. One folder is present for each experiment.
- `script`: this folder contain the script used to modify the number of cores, amount of ram and device performance. 
- `single-node`: results used to assess the single node performance, before ceph deploy
