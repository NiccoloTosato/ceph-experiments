<!--
SPDX-FileCopyrightText: 2025 2025 Isac Pasianotto <isac.pasianotto@phd.units.it>
SPDX-FileCopyrightText: 2025 2025 Niccolo Tosato <niccolo.tosato@phd.units.it>
SPDX-FileCopyrightText: 2025 2025 Ruggero Lot <ruggero.lot@areasciencepark.it>

SPDX-License-Identifier: CC-BY-4.0
-->

# ceph deploy logbook

## bootstrap

- `dnf install -y ceph-base ceph-common ceph-volume podman`
- `systemctl enable --now podman`
- `systemctl enable --now chronyd`
- `dnf install cephadm -y`
- `nmcli connection add type infiniband ifname ibp139s0 ipv4.addresses xx.xx.xx.xx/24 ipv4.method manual`
- `hostnamectl set-hostname ceph13`
- `lvextend -l +100%FREE fedora_ceph13`
- `xfs_growfs /dev/mapper/fedora_ceph13-root`
- `cephadm bootstrap --mon-ip xx.xx.xx.xx`
- `ceph config set mgr mgr/dashboard/server_addr xx.xx.xx.xx`
- `ceph dashboard set-grafana-api-url https://xx.xx.xx.xx:3000`
-  copy `/etc/ceph/ceph.pub` to all ceph nodes
-  `ceph-volume lvm zap /dev/sd* --destroy` to clear devices

Expand the cluster
```
ceph orch host add ceph0[1-8]
ceph orch host add genoa00[1-2]
```

Edit the config adding:
```
$ ceph orch ls  --export > conf.yaml


---
service_type: osd
service_id: cost_capacity
service_name: osd.cost_capacity
placement:
  host_pattern: ceph1*
spec:
  data_devices:
    rotational: 1
  filter_logic: AND
  objectstore: bluestore
---
service_type: osd
service_id: iops_optimized
service_name: osd.iops
placement:
  host_pattern: ceph1*
spec:
  data_devices:
    rotational: 0
  filter_logic: AND
  objectstore: bluestore
---
service_type: mds
service_id: benchmark
service_name: mds.benchmark
placement:
  count: 2
  host_pattern: 'genoa00*'
```
Final setup:
```
daemon          osd             redeploy        sd              status
[root@ceph13 ceph]# ceph orch ls
NAME                PORTS        RUNNING  REFRESHED  AGE  PLACEMENT
alertmanager        ?:9093,9094      1/1  72s ago    3m   count:1
ceph-exporter                        6/6  8m ago     3m   *
crash                                6/6  8m ago     3m   *
grafana             ?:3000           1/1  72s ago    3m   count:1
mds.benchmark                        2/2  98s ago    3m   count:2;genoa00*
mgr                                  2/2  7m ago     3m   count:2
mon                                  5/5  8m ago     3m   count:5
node-exporter       ?:9100           6/6  8m ago     3m   *
osd.cost_capacity                     48  8m ago     3m   ceph1*
osd.iops_optimized                     8  8m ago     3m   ceph1*
prometheus          ?:9095           1/1  72s ago    3m   count:1
```

## Create fs
```
$ ceph fs volume create benchmark
```

Create rule:

```
ceph osd crush rule create-replicated replicated_rule_ssd_host default host ssd
ceph osd crush rule create-replicated replicated_rule_hdd_host default host hdd
```

Create pool:

```
ceph osd pool create benchmark.data.replica1 replicated_rule_hdd_host
ceph osd pool create benchmark.data.replica2 replicated_rule_hdd_host
ceph osd pool create benchmark.data.replica3 replicated_rule_hdd_host
```

Set pool size:
```
ceph config set global  mon_allow_pool_size_one true
ceph osd pool set benchmark.data.replica1 size 1 --yes-i-really-mean-it
ceph osd pool set benchmark.data.replica2 size 2
ceph osd pool set benchmark.data.replica3 size 3
```
Disable autoscale, change pg
```
ceph osd pool set benchmark.data.replica1 pg_autoscale_mode off
ceph osd pool set benchmark.data.replica2 pg_autoscale_mode off
ceph osd pool set benchmark.data.replica3 pg_autoscale_mode off
ceph osd pool set cephfs.benchmark.data pg_autoscale_mode off
```

```
ceph config set global mon_max_pg_per_osd 350
ceph osd pool set benchmark.data.replica1 pg_num 2048
ceph osd pool set benchmark.data.replica2 pg_num 2048
ceph osd pool set benchmark.data.replica3 pg_num 2048
ceph osd pool set cephfs.benchmark.data pg_num 32
```

Add datapool to benchmark fs
```
ceph fs add_data_pool benchmark benchmark.data.replica1
ceph fs add_data_pool benchmark benchmark.data.replica2
ceph fs add_data_pool benchmark benchmark.data.replica3
```

Bind the folder to replicated pool:
```
setfattr -n ceph.dir.layout.pool -v benchmark.data.replica1 replica1
setfattr -n ceph.dir.layout.pool -v benchmark.data.replica2 replica2
setfattr -n ceph.dir.layout.pool -v benchmark.data.replica3 replica3
```

Check with:
```
$ ceph fs ls
name: benchmark, metadata pool: cephfs.benchmark.meta, data pools: [cephfs.benchmark.data benchmark.data.replica1 benchmark.data.replica2 benchmark.data.replica3 ]
```


