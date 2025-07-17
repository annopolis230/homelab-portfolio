#!/bin/bash

img="/mnt/user/images/pool/jammy-server-cloud-img-base.qcow2"
state=$(virsh domstate "wazuh-server")

if [ "$state" == "running" ]; then
    echo "Stopping VM"
    virsh destroy "wazuh-server"
else
    echo "VM already stopped"
fi

if [ -f "$img" ]; then
    echo "Skipping resize"
else
    qemu-img resize "$img" +20G
fi

virsh start "wazuh-server"
