<!--
SPDX-FileCopyrightText: 2025 2025 Isac Pasianotto <isac.pasianotto@phd.units.it>
SPDX-FileCopyrightText: 2025 2025 Niccolo Tosato <niccolo.tosato@phd.units.it>
SPDX-FileCopyrightText: 2025 2025 Ruggero Lot <ruggero.lot@areasciencepark.it>

SPDX-License-Identifier: CC-BY-4.0
-->

# Notes about deployment with cobbler

Notes to keep track what I did in order to deploy fedora for the ceph nodes.

# step 0: Distro

First step should be to create a distro.
At the moment:

```
root@cobbler:~# cobbler distro list
   coreos39-x86_64
   fedora39-x86_64
   fedora40-x86_64
```

I just used the ~fedora40-x86_64~ distro.

# Step 1: Profile

In the kickstart directory: ~/var/lib/cobbler/templates~ I created a ~ceph.ks~ file with the content of the [[./guiinstall-ks.cfg][./guiinstall-ks.cfg]] file (edited from the ~anaconda-ks.cfg~ of a first installation done with the gui the first time)

Then I created a new profile with:

```
$ cobbler profile add --name=ceph-f40-x86_64 \
    --distro=fedora40-x86_64  \
    --enable-menu=true # to enable pxe

# change the profile kickstart
$ cobbler profile edit --name ceph-f40-x86_64 \
  --autoinstall ceph.ks
```

* Step 2: System

Register the system.

```
  cobbler system add --name ceph15-node \
    --profile ceph-f40-x86_64 \
    --hostname ceph15 \
    --netboot-enabled=true \
    --name-servers xx.xx.xx.xx

  cobbler system edit --name ceph15-node \
    --interface bond0 \
    --interface-type bond \
    --ip-address xxxxxxxxxxxxxxxx \
    --bonding-opts "mode=802.3ad" \
    --netmask 255.255.255.0 \
    --if-gateway xxxxxxxxxxxxxxxxxx

  cobbler system edit --name ceph15-node \
    --interface  eno12399np0 \
    --interface-type bond_slave \
    --mac-address xxxxxxxxxxxxxxxxxx \
    --interface-master bond0

  cobbler system edit --name ceph15-node \
    --interface  eno12409np1 \
    --interface-type bond_slave \
    --mac-address  xxxxxxxxxxxxxxxxxxx \
    --interface-master bond0
```


* Step 3: Save and run

To save the modification just run

```
cobbler sync
```


