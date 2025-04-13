#!/bin/bash -e

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
