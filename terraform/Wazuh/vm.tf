resource "libvirt_domain" "domain" {
    name = "wazuh-server"
    vcpu = "4"
    memory = "4096"
    running = true
    cloudinit = libvirt_cloudinit_disk.wazuh.id
    qemu_agent = true

    network_interface {
        bridge = "br0"
        wait_for_lease = true
        mac = "52:54:00:66:4a:bb"
    }

    cpu {
        mode = "host-passthrough"
    }

    disk {
        volume_id = libvirt_volume.ubuntu_vm_disk.id
    }

    console {
        type        = "pty"
        target_port = "0"
        target_type = "serial"
    }

    graphics {
        type        = "spice"
        listen_type = "address"
        autoport    = true
    }
}