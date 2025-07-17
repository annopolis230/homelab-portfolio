# Terraform Auto-Updater for unRAID

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
