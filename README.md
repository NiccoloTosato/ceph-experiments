# Ceph experiments

Benchmarking Ceph across hardware setups for cost-performance optimization.

## What's in ? 

- `extra`: notes about switch configurations, nodes provisioning and FIO debugging session and ceph deploy.
- `multi-node`: result obtained using 8-node cluster, `json` with results and `fio` job file are provided. One folder is present for each experiment.
- `script`: this folder contain the script used to modify the number of cores, amount of ram and device performance. 
- `single-node`: results used to assess the single node performance, before ceph deploy
