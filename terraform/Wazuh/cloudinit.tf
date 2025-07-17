data "template_file" "user_data" {
    template = file("${path.module}/cloudinit.cfg")
}

data "template_file" "network_config" {
    template = file("${path.module}/networkconfig.cfg")
}

resource "libvirt_cloudinit_disk" "wazuh" {
    name = "wazuh-server-cloudinit.iso"
    pool = libvirt_pool.domains.name

    user_data = data.template_file.user_data.rendered
    network_config = data.template_file.network_config.rendered
}