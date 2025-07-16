terraform {
  required_providers {
    libvirt = {
      source  = "dmacvicar/libvirt"
      version = "~> 0.7"
    }
  }
}

provider "libvirt" {
  uri = "qemu:///system"
}

resource "libvirt_volume" "jammy_base" {
  name   = "jammy-server-cloudimg-base"
  pool   = "default"
  source = "/var/lib/libvirt/images/jammy-server-cloudimg-amd64.img"
  format = "qcow2"
}

resource "libvirt_volume" "jammy_vm" {
  name           = "jammy-wazuh-server.qcow2"
  pool           = "default"
  base_volume_id = libvirt_volume.jammy_base.id
  format         = "qcow2"
}

resource "libvirt_cloudinit_disk" "wazuh_ci" {
  name       = "wazuh-server-cloudinit.iso"
  pool       = "default"

  user_data = <<-EOF
    #cloud-config
    hostname: wazuh-server
    fqdn: wazuh-server.localdomain

    package_update: true
    packages:
      - curl

    runcmd:
      # Import Wazuh GPG key & repo, then install the manager
      - curl -s https://packages.wazuh.com/key/GPG-KEY-WAZUH | apt-key add -
      - echo "deb https://packages.wazuh.com/4.x/apt/ stable main" \
          | tee /etc/apt/sources.list.d/wazuh.list
      - apt-get update
      - apt-get install -y wazuh-manager
  EOF

  meta_data = <<-EOF
    instance-id: wazuh-server
    local-hostname: wazuh-server
  EOF
}

resource "libvirt_domain" "wazuh_server" {
  name   = "wazuh-server"
  memory = "2048"
  vcpu   = 2

  # hook up our cloud-init ISO
  cloudinit = libvirt_cloudinit_disk.wazuh_ci.id

  # root disk
  disk {
    volume_id = libvirt_volume.jammy_vm.id
  }

  # default NAT network
  network_interface {
    network_name = "default"
  }

  # enable serial console
  console {
    type        = "pty"
    target_port = "0"
    target_type = "serial"
  }

  # optional GUI access via SPICE
  graphics {
    type        = "spice"
    listen_type = "address"
    autoport    = true
  }
}
