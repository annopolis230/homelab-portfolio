terraform {
  required_providers {
    libvirt = {
      source  = "dmacvicar/libvirt"
      version = "~> 0.7"
    }
    cloudinit = {
      source = "hashicorp/cloudinit"
      version = "~> 2.3"
    }
  }
}
