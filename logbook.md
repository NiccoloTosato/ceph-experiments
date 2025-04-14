<!--
SPDX-FileCopyrightText: 2025 2025 Isac Pasianotto <isac.pasianotto@phd.units.it>
SPDX-FileCopyrightText: 2025 2025 Niccolo Tosato <niccolo.tosato@phd.units.it>
SPDX-FileCopyrightText: 2025 2025 Ruggero Lot <ruggero.lot@areasciencepark.it>

SPDX-License-Identifier: CC-BY-4.0
-->

# 27/10/2024

Waiting for xfs, btrfs, ext4 results. 
The delay is due: the maximum number of job that fio can run and the fact that all the files are created in advance and i didn't manage to create file on open (0 R/W bandwidth**. 
So I renamed all the jobs with the same name, shouldt' be any side effect. 

**Usefull material to know when IO scheduler can merge requests**:

https://serverfault.com/questions/849958/why-is-io-scheduler-not-merging-requests


# Experiments Logbook

## 15/10/2024 - Network setup and test

We finished the set up of the Ethernet network, adopting `LACP` in mode `802.3ad`, we used `layer3+4` hash policy. The iperf3 achieve ~ **47 Gbit/s**. Need to test that in a more robust way in future.
The cheatsheet to setup the network could be found in: `switch.md`.


## 17/10/2024 - Single machine benchmark outline

The idea is to assess the performance of a single storage nodes, this will give us an upper bound of the performance, helping us highlithing possible bottlenecks and misconfiguration.

### Benchmark

To test the single machine we will use `fio`.

### Performance

- We want to assess the **IOPS** performance, using a legacy definition: **4KiB** in R,W and RW, **randomly**. Usually is the smallest block that we can write. 
- Sequential R,W

### Filesystem 

- raw performance (no FS at all)
- `xfs`
- `ext4`
- `btrfs` +- cow
- `zfs` +- deduplication

### Hardware overview

- **CPU**: 2 x `Intel(R) Xeon(R) Gold 6426Y`
- **RAM**:  12 x 16 GB @ 4800MT/s PN: `MTC10F1084S1RC48BA1`
- **Controller** (HDDs): `Dell HBA355i Adp`
- **HDDs**: 12  x 22TB, SAS, 7200 RPM,  PN: `WUH722222AL5200` Vendor: `WDC`
- **NVME** 2 x `Dell NVMe ISE PS1010 RI U.2 15.36TB`
- **Infiniband NIC**: 1 x `Nvidia ConnectX-7 Single Port Infiniband NDR200 OSFP Adapter MT2910 Family` PN:`0M8XMC`
- **Ethernet NIC** 1 x `Broadcom Adv. Dual 25Gb Ethernet`

## 18/10/2024 - Setup the CPU and RAW performance

### CPU setup

Since the cpu frenquency could be important in latency critical workload, setting a reasonable policy could be usefull. There are no anymore governon on Intel CPUs, but a complex intel stuff called  **Dynamic SST-Performance Profile** , it must be active. Then use `intel-speed-select --info`.

Intel speed select [docs](https://www.kernel.org/doc/Documentation/admin-guide/pm/intel-speed-select.rst** .

Enable also the  System Profile performance and the Workload profile low latency.

Since I've no clue about the possible effects, i've enabled that on one node, and I use the default on another one as control group. So I will run all the raw drive test on both machines.

**Important: I've just discovered that with Performance profile and low latency workload, is not possible to manage frequency from OS**. I would say that get stick with one machine on default and another one in perfmance and low latency workload.  

If you enable `Intel SST-CP` on iDRAC the tool doesn't start to work again.

Conclusion: use the low latency profile and avoid setting frequency from OS, this will reduce the number of parameters to control.

## Raw disks tests

### HDD

Query device status, only few starts reported below:

```bash
$ smartctl -x /dev/sda
=== START OF INFORMATION SECTION ===
Vendor:               WDC
Product:              WUH722222AL5200
Revision:             WS03
Compliance:           SPC-5
User Capacity:        22,000,969,973,760 bytes [22.0 TB]
Logical block size:   512 bytes
Physical block size:  4096 bytes

Read Cache is:        Enabled
Writeback Cache is:   Disabled
```

### NVME

```
$ smartctl -x /dev/nvme1
=== START OF INFORMATION SECTION ===
Model Number:                       Dell NVMe ISE PS1010 RI U.2 15.36TB
Serial Number:                      AID2N0026I0702N20
Firmware Version:                   1.0.0

Supported Power States
St Op     Max   Active     Idle   RL RT WL WT  Ent_Lat  Ex_Lat
 0 +    25.00W       -        -    0  0  0  0    30000   30000
 1 +    20.00W       -        -    1  1  1  1    30000   30000
 2 +    17.00W       -        -    2  2  2  2    30000   30000
 3 +    14.00W       -        -    3  3  3  3    30000   30000
 4 -     5.00W       -        -    4  4  4  4    30000   30000
```

Check that the power state is set to max:

```
$ nvme get-feature /dev/nvme2 -f 2 -H
get-feature:0x02 (Power Management), Current value:00000000
	Workload Hint (WH): 0 - No Workload
	Power State   (PS): 0
```

### Results


## 21/10/2024 Cobbler setup polishing and FIO results

Changed cobbler kickstart, to clear the disk from the old partitions, on `ceph.ks`:

```bash
# Generated using Blivet version 3.9.1
clearpart --drives=nvme0n1 --all
ignoredisk --only-use=nvme0n1
autopart

```

## 24/10/2024

### Fio issue

Start debugging `fio`, since the result obtained are not consistent with the theretical bw. More info in [debugging](extra/debug/debugging.md).

Issue solved, using `bw_bytes` inside the json instead of `bw_mean`.

### Cgroup blkio idea

**Random idea**: `https://andrestc.com/post/cgroups-io/

We can use cgroup to limit the IO of the disk emulating slower disks ? YES !

How cgroup blkio work:

```bash
$ mkdir cgroup-io
$ mount -t cgroup -o blkio none $(pwd)/cgroup-io
$ cat /proc/partitions
$ echo "8:0 1048576" > cgroup-io/blkio.throttle.write_bps_device
$ fio raw-spin.fio --cgroup=blkio
```

### Profile optimization

All machines have been setted up to work with a performance profile and low-latency workload


# 28/10/2024

Reduce bs: 4,8,16,32,256,1024,4096
Reduce process count to 16.
Test posix backend on fio.
Eventually change offset.

# 29/10/2024

The results with zfs show the same cache behaviour of btrfs.

## How to address ZFS cache during reading:

**Solution 1:**
Disable the cache in a specific pool.
```bash
$ zfs set primarycache=none poolname/dataset
$ zfs set secondarycache=none poolname/dataset
```

**Solution 2:**
Reduce the cache size to 0 GB (size in bytes).
```bash
$ echo "o" > /sys/module/zfs/parameters/zfs_arc_max
```

This should be enought to fix the issues.

## Summary of test to launch 

Warm up and check the results:

- With bs 4,8,16,32,256,1024,4096
- With process 1,2,4,8,16
- With engine libaio,posixaio,io_uring,sync
- Iodepth in random = 32
- Iodept in sequential = 4


# 5/11/2024

## Observation

- [write|read] in raw + 10GB offset with >1 processes is ~ rand[write|read] with single one. We expect the same behaviour. 
- Increasing the blocksize while rand[read|write] mean decreasing the random pattern, so the seek is masked by the operation.


## Cobbler 
- Fix route
- Install the new driver after the the provisioning, otherwiser the reboot will not work. 

## bpftrace 

- Get the syscall args + raw trace

# Single node result

All the result concerning only a single machine are available [here](https://github.com/NiccoloTosato/ceph-experiments/tree/main/single-node).

Results and plot are reported in a [notebook](https://github.com/NiccoloTosato/ceph-experiments/blob/main/single-node/plot.ipynb)

# 6/11/2024

## Infiniband

Test infiniband (no IPoIB):
- install infiniband diagnostic tools and verbs

```
$ dnf install infiniband-diags
$ dnf install libibverbs-utils
```

Use the `ibv_` toolset to test the connection:

Host 1 (server):
```
$  ibv_srq_pingpong -m 4096 -s 16384 -n 10000 -q 32
....
remote address: LID 0x0057, QPN 0x00015f, PSN 0xd3b8c9, GID ::
remote address: LID 0x0057, QPN 0x000160, PSN 0xc16a84, GID ::
327680000 bytes in 0.01 seconds = 199182.43 Mbit/sec
10000 iters in 0.01 seconds = 1.32 usec/iter
```

Host 2 (client):
```
$ ibv_srq_pingpong xx.xx.xx.xx -m 4096 -s 16384 -n 10000 -q 32
...
remote address: LID 0x0055, QPN 0x00010f, PSN 0xe8057c, GID ::
327680000 bytes in 0.01 seconds = 357729.26 Mbit/sec
10000 iters in 0.01 seconds = 0.73 usec/iter
```

The result on client is weird.
The result on server is OKAY.

# 22/11/2024

The idea is to perform 2 set of exeperiments:
- Change CPU/RAM 
- Change the HDD speed

## Exp 1

Perform all the experiments using the cartesian product between:

- cpu count: 8,16,32,64
- ram size: 32,64,96,128,192

### Offline cores:

Script used for the tests: [here](https://github.com/NiccoloTosato/ceph-experiments/tree/main/script/cpu).

Key idea:

```
[root@wally cpu]# nproc
8
[root@wally cpu]# echo 0 > /sys/devices/system/cpu/cpu1/online
[root@wally cpu]# nproc
7
[root@wally cpu]# echo 1 > /sys/devices/system/cpu/cpu1/online
[root@wally cpu]# nproc
8
```

Linux kernel docs: [CPU hotplug](https://docs.kernel.org/core-api/cpu_hotplug.html)

**Warning**: In case of multisocket Intel use round-robin enumeration by default. Offlining sequential core mean reduce the number of core on both sockets. So first check the core id using `lscpu`. Moreover in case of NUMA architectures, you want offline cores in a round robin fashion respect the numa regions. 

### Offline memory:

Scripts used for the tests: [here](https://github.com/NiccoloTosato/ceph-experiments/tree/main/script/ram)

Key idea:
```
[root@wally ram]# lsmem
RANGE                                  SIZE  STATE REMOVABLE  BLOCK
0x0000000000000000-0x0000000097ffffff  2.4G online       yes   0-18
0x0000000100000000-0x000000085fffffff 29.5G online       yes 32-267

Memory block size:       128M
Total online memory:    31.9G
Total offline memory:      0B

[root@wally ram]# echo offline >  /sys/devices/system/memory/memory3/state;
[root@wally ram]# lsmem
RANGE                                  SIZE   STATE REMOVABLE  BLOCK
0x0000000000000000-0x0000000017ffffff  384M  online       yes    0-2
0x0000000018000000-0x000000001fffffff  128M offline                3
0x0000000020000000-0x0000000097ffffff  1.9G  online       yes   4-18
0x0000000100000000-0x000000085fffffff 29.5G  online       yes 32-267

Memory block size:       128M
Total online memory:    31.8G
Total offline memory:    128M

[root@wally ram]# echo online >  /sys/devices/system/memory/memory3/state;
[root@wally ram]# lsmem
RANGE                                  SIZE  STATE REMOVABLE  BLOCK
0x0000000000000000-0x0000000097ffffff  2.4G online       yes   0-18
0x0000000100000000-0x000000085fffffff 29.5G online       yes 32-267

Memory block size:       128M
Total online memory:    31.9G
Total offline memory:      0B
```

Linux kernel docs: [Memory Hot(Un)Plug](https://docs.kernel.org/admin-guide/mm/memory-hotplug.html)

**Warning**: page locked memory cannot be put offline, so if the kernel allocate some blocks is not possible to migrate page and offline memory. An idea is to boot the machine with less memory and increase it during the tests. 

## Exp 2

Given the maximum ram and cpu count:
- range(100,275+25,25)

### Use blkio

To limit the IO towards the device we will use the cgroup interface. Since all the OSD daemon run with a podman container, we will use podman to apply cgroup limitations.

Official kernel docs: [here](https://www.kernel.org/doc/Documentation/cgroup-v1/blkio-controller.txt)

We will use `podman update` with the flags:
```
   --device-read-bps=path:rate
       Limit read rate (in bytes per  second)  from  a  device  (e.g.
       --device-read-bps=/dev/sda:1mb).

       On  some  systems, changing the resource limits may not be al‐
       lowed   for   non-root   users.   For   more   details,    see
       https://github.com/containers/podman/blob/main/troubleshoot‐
       ing.md#26-running-containers-with-resource-limits-fails-with-
       a-permissions-error

       This option is not supported on cgroups V1 rootless systems.

   --device-write-bps=path:rate
       Limit write rate (in bytes per second) to a device (e.g. --de‐
       vice-write-bps=/dev/sda:1mb).

       On some systems, changing the resource limits may not  be  al‐
       lowed    for   non-root   users.   For   more   details,   see
       https://github.com/containers/podman/blob/main/troubleshoot‐
       ing.md#26-running-containers-with-resource-limits-fails-with-
       a-permissions-error
```

**idea**: Will this work with NIC ? Moreover, take a look at IOPS limits.

The script used to update all the container can be found [here](https://github.com/NiccoloTosato/ceph-experiments/tree/main/script/blkio).

# Results

The results are reported in this [notebook](https://github.com/NiccoloTosato/ceph-experiments/blob/main/multi-node/scaling.ipynb).
