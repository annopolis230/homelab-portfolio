# Wazuh Terraform Config for unRAID

unRAID has some special considerations that make a Wazuh deployment and Terraform more difficult. Namely, no apt or yum package managers. That's why I'm deploying Wazuh in a VM. There's a couple things we need to do first:

## Requirements

- mkisofs binary installed and located in PATH (again, no apt makes this hard. terraform-setup.py will automatically do this by spinning up a temporary docker container, installing the file, then copying it back to the host)
- Libvirt needs to be listening on 0.0.0.0 (by default it's not)
- Terraform installed and in PATH (tested with version 1.12.2)

## Change Libvirt Listening Address

- Edit `/etc/libvirt/libvirtd.conf`
- Change `listen_addr = "127.0.0.1"` to `listen_addr = "0.0.0.0"`

## Install / Update Terraform

- Run `update-terraform.py`, described below.

## Install mkisofs And Ubuntu Cloud Image

- Run `terraform-setup.py`

### Notes

- This downloads a lightweight Ubuntu Cloud Image to `/var/lib/libvirt/images`. This is the directory the Terraform plan looks for the image.

## Install Wazuh Server

1. Generate an SSH keypair:
   ```bash
   ssh-keygen -t ed25519 -C "your_email@example.com"
   ```

2. Add your public key to `cloudinit.cfg` under `ssh_authorized_keys`

3. Run: 
   ```bash
   terraform init
   terraform apply
   ```

4. (Optional) You may at some point encounter an SSH error stating that the host identification has changed. If that happens, edit the known hosts file and delete the entry that corresponds to the server:
   ```bash
   nano /root/.ssh/known_hosts
   ```
### Notes

- The newly provisioned server will get a DHCP lease via the br0 bridge interface. If there is no DHCP server serving that interface, provisioning will fail after 5 minutes due to the wait_for_lease timeout.
- You MUST use your SSH keypair to connect to the server. There is no other way.
- It also assigns a static MAC for the VM, you can change it to whatever you like in `vm.tf`. I would recommend setting up a DHCP reservation.
- This installs Wazuh 4.12. To change the version, change the link in the last runcmd command of `cloudinit.cfg`

### After Deployment

- The Wazuh components (server, indexer, and dashboard) will all be installed automatically after deployment. It will take about 5 minutes for these to finish installing.
- Once the Wazuh components are installed, the web interface will be accessible at `https://<server-ip>:443`. 
- Use the Admin account to login. You have two options to find the admin password after SSHing to the VM:

1. Check the cloud-init logs:
   ```bash
   cat /var/log/cloud-init-output.log
   ```
   This is helpful in case anything went wrong, this will tell you why.

2. Check the `wazuh-passwords.txt` file inside `wazuh-install-files.tar`:
   ```bash
   sudo tar -O -xvf wazuh-install-files.tar wazuh-install-files/wazuh-passwords.txt
   ```
   This option will display every password for every Wazuh user.

# update-terraform.py

This script automatically checks for the latest version of [Terraform](https://www.terraform.io/), compares it with the currently installed version, and downloads and installs it if an update is available.

## Features

- Fetches the latest stable Terraform version from HashiCorp.
- Compares with the currently installed version (if any).
- Downloads the Linux AMD64 binary.
- Installs the binary to `/usr/local/bin/terraform`.
- Designed specifically for **unRAID**, which does not support traditional package managers like `apt` or `yum`.

---

## unRAID Requirements

### 1. Python Is Not Preinstalled

unRAID **does not ship with Python** by default. To use this script, you **must install a working Python 3 environment**.

#### Recommended Plugin:

This plugin provides a stable Python 3 setup with working SSL support:

> [Plugin: Python 3 for unRAID 6.11+](https://forums.unraid.net/topic/175402-plugin-python-3-for-unraid-611/)

Install this plugin first, or the script won't run.

---

### 2. Broken OpenSSL in Other Plugins

Many community Python plugins ship with a broken OpenSSL library that causes issues when using `pip`. You'll typically see errors when trying to install packages like `requests`.

If you're experiencing issues with `pip`, you're likely using a plugin that has **broken SSL support**.

---

### 3. Cleanup Old Python/Pip Versions (if necessary)

If you're still having problems:

1. Run:
   ```bash
   which pip3
   ```
2. If the result is something like /usr/bin/pip3, but there's no Python plugin currently installed, it's likely a leftover binary.
3. Manually delete it:
   ```bash
   rm /usr/bin/pip3
   ```
