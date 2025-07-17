resource "libvirt_pool" "pool" {
    name = "pool"
    type = "dir"
    target {
        path = "/mnt/user/images/pool"
    }
}

resource "libvirt_pool" "domains" {
    name = "domains"
    type = "dir"
    target {
        path = "/mnt/user/domains/Wazuh"
    }
}

resource "libvirt_volume" "qcow2" {
    name = "jammy-server-cloud-img-base.qcow2"
    pool = libvirt_pool.pool.name
    source = "/var/lib/libvirt/images/jammy-server-cloudimg-amd64.img"
}

resource "libvirt_volume" "ubuntu_vm_disk" {
    name = "wazuh-vm.qcow2"
    pool = libvirt_pool.domains.name
    base_volume_id = libvirt_volume.qcow2.id
    size = 107374182400
}