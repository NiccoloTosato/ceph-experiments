# Switch journey

## Laptop port setup

We setup the laptop port in order to keep a door open in case of up-link misconfiguration. C

```bash
switch02# show running-configuration interface ethernet 1/1/44
!
interface ethernet1/1/44
 description laptops
 no shutdown
 switchport mode trunk
 switchport access vlan XXXXX
 switchport trunk allowed vlan XXXX,XXXX,XXXX
 flowcontrol receive off
```

## Provision setup port

```
interface ethernet1/1/4
 description ceph16
 no shutdown
 switchport access vlan XXXX
 mtu 9216
 flowcontrol receive off
```


## configure the up-link port channel

In order to allow the right traffic on the uplink we do the following:

```
# interface port-channel 53
# show configuration
# switchport trunk allowed vlan XXXX,XXXX
```

Final result:
```
switch05# show running-configuration interface port-channel 53
!
interface port-channel53
 description to-switch03
 no shutdown
 switchport mode trunk
 switchport access vlan XXXXX
 switchport trunk allowed vlan XXXX,XXXX,XXXX
 mtu 9216
 vlt-port-channel 53
```

## Bare-bone no vlt ceph port configuration

```
switch06# show running-configuration interface ethernet 1/1/1
!
interface ethernet1/1/1
 description ceph13
 no shutdown
 switchport access vlan XXXXX
 mtu 9216
 flowcontrol receive off
```

# Try to setup VLT

## Usefull commands

```
switch05# show topology-map
     TOPOLOGY MAP
-------------------------
Topology ID      : 3
Topology Pattern : chain
Topology User    : VLT
Local Unit ID    : 1
Master Unit ID   : 1
From-Interface| From-Interface | To-Interface |  To-Interface  | Link-Speed  | Link-Status |
   Unit ID    |                |   Unit ID    |                |   (Gb/s)    |             |
--------------------------------------------------------------------------------------------
1             |ethernet1/1/49  |2             |ethernet1/1/49  |100          |up           |
1             |ethernet1/1/51  |2             |ethernet1/1/51  |100          |up           |
2             |ethernet1/1/49  |1             |ethernet1/1/49  |-            |-            |
2             |ethernet1/1/51  |1             |ethernet1/1/51  |-            |-            |
```

```
switch05# show port-channel summary

Flags:  D - Down    I - member up but inactive    P - member up and active
        U - Up (port-channel)    F - Fallback Activated    IND - LACP Individual
--------------------------------------------------------------------------------
Group Port-Channel           Type     Protocol  Member Ports
--------------------------------------------------------------------------------
3    port-channel3    (D)     Eth      DYNAMIC   1/1/1(I)
53   port-channel53   (U)     Eth      DYNAMIC   1/1/53(P)
1000 port-channel1000 (U)     Eth      STATIC    1/1/49(P) 1/1/51(P)
```

```
switch05# show vlt 3
Domain ID                              : 3
Unit ID                                : 1
Role                                   : primary
Version                                : 3.1
Local System MAC address               : 
Role priority                          : 32768
VLT MAC address                        : 00:11:22:33:44:55
IP address                             : 
Delay-Restore timer                    : 90 seconds
Peer-Routing                           : Disabled
Peer-Routing-Timeout timer             : 0 seconds
Multicast peer-routing timer           : 300 seconds
VLTi Link Status
    port-channel1000                   : up

VLT Peer Unit ID    System MAC Address    Status    IP Address             Version
----------------------------------------------------------------------------------
  2                 xxxxxxxxxxxxxxxx      up        xxxxxxxxxxxxxxxxxx     3.1
```

```
switch05# show vlt 3 vlt-port-detail
vlt-port-channel ID : 3
VLT Unit ID    Port-Channel      Status    Configured ports    Active ports
-------------------------------------------------------------------------------
* 1            port-channel3      down      1                   0
  2            port-channel3      down      1                   0
vlt-port-channel ID : 53
VLT Unit ID    Port-Channel      Status    Configured ports    Active ports
-------------------------------------------------------------------------------
* 1            port-channel53     up        1                   1
  2            port-channel53     up        1                   1
```

```
 show interface port-channel summary
LAG     Mode      Status    Uptime              Ports
3       L2-HYBRID up        05:10:02            Eth 1/1/1 (Up)
53      L2-HYBRID up        1 weeks 3 days 00:2 Eth 1/1/53 (Up)
```





    


