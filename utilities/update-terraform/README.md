Terraform Auto-Updater for unRAID
This script automatically checks for the latest version of Terraform, compares it with the currently installed version, and downloads and installs it if an update is available.

Features
Fetches the latest stable Terraform version from HashiCorp.

Compares with the currently installed version (if any).

Downloads the Linux AMD64 binary.

Installs the binary to /usr/local/bin/terraform.

Designed specifically for unRAID, which does not support traditional package managers like apt or yum.

unRAID Requirements
1. Python Is Not Preinstalled
unRAID does not ship with Python by default. To use this script, you must install a working Python 3 environment.

Recommended Plugin:
This plugin provides a stable Python 3 setup with working SSL support:

Plugin: Python 3 for unRAID 6.11+

Install this plugin first, or the script won't run.

2. Broken OpenSSL in Other Plugins
Many community Python plugins ship with a broken OpenSSL library that causes issues when using pip. You'll typically see errors when trying to install packages like requests.

If you're experiencing issues with pip, you're likely using a plugin that has broken SSL support.

3. Cleanup Old Python/Pip Versions (if necessary)
If you're still having problems:

Run:

bash
Copy
Edit
which pip3
If the result is something like /usr/bin/pip3, but there's no Python plugin currently installed, it's likely a leftover binary.

Manually delete it:

bash
Copy
Edit
rm /usr/bin/pip3
Then reinstall the recommended Python plugin.

Required Python Packages
Install the required Python package via pip:

bash
Copy
Edit
pip install requests
If pip does not work, refer to the cleanup section above.

How to Use
Make the script executable:

bash
Copy
Edit
chmod +x terraform_update.py
Run the script:

bash
Copy
Edit
python3 terraform_update.py
The script will:

Create a temporary folder (/tmp/terraform_update)

Download and extract the latest Terraform binary

Replace the existing /usr/local/bin/terraform binary (if it exists)

Clean up the temporary directory

File Structure
bash
Copy
Edit
terraform_update.py    # Main script file
/boot/extra/           # (Optional) Place to install persistent tools in unRAID
Troubleshooting
If terraform still runs an older version after update:

Run which terraform to make sure it's picking up the correct binary from /usr/local/bin/.

You may need sudo depending on your unRAID security settings when moving files to /usr/local/bin.

