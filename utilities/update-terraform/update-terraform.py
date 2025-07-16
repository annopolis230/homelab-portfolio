import os
import sys
import shutil
import zipfile
import subprocess
import requests
import json
from pathlib import Path
from urllib.request import urlretrieve

INSTALL_DIR = "/usr/local/bin"
TMP_DIR = "/tmp/terraform_update"
TERRAFORM_BIN = os.path.join(INSTALL_DIR, "terraform")

def getLatestTerraformVersion():
    url = "https://checkpoint-api.hashicorp.com/v1/check/terraform"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json().get("current_version")
    except Exception as e:
        print(f"Failed to get Terraform version: {e}")
        sys.exit(1)

def getInstalledVersion():
    try:
        out = subprocess.check_output(["terraform","version","-json"], text=True)
        data = json.loads(out)
        return data.get("terraform_version")
    except Exception:
        return None

def downloadTerraform(version, tmp_dir):
    filename = f"terraform_{version}_linux_amd64.zip"
    url = f"https://releases.hashicorp.com/terraform/{version}/{filename}"
    dest_path = os.path.join(tmp_dir, filename)

    print(f"Downloading Terraform {version}")
    try:
        urlretrieve(url, dest_path)
        return dest_path
    except Exception as e:
        print(f"Download failed: {e}")
        sys.exit(1)


def extractAndInstall(zip_path, install_dir):
    with zipfile.ZipFile(zip_path, 'r') as zip:
        zip.extractall(TMP_DIR)
    
    terraform_path = os.path.join(TMP_DIR, "terraform")
    if not os.path.exists(terraform_path):
        print("Terraform binary not found!")
        sys.exit(1)

    try:
        shutil.move(terraform_path, TERRAFORM_BIN)
        os.chmod(TERRAFORM_BIN, 0o755)
        print(f"Terraform installed at {TERRAFORM_BIN}")
    except PermissionError:
        print(f"Permission denied")
        sys.exit(1)

def main():
    os.makedirs(TMP_DIR, exist_ok=True)
    latest = getLatestTerraformVersion()
    current = getInstalledVersion()

    if current == latest:
        print(f"Terraform {latest} is already installed")
        shutil.rmtree(TMP_DIR)
        return
    
    print(f"Updating Terraform {current or 'not installed'} to {latest}")
    zip_path = downloadTerraform(latest, TMP_DIR)
    extractAndInstall(zip_path, INSTALL_DIR)

    shutil.rmtree(TMP_DIR)
    print(f"Terraform {latest} installed")

if __name__ == "__main__":
    main()