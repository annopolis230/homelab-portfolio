import os
import sys
import hashlib
import subprocess
import tempfile
import shutil
from urllib.request import urlopen

IMG_URL = "https://cloud-images.ubuntu.com/jammy/current/jammy-server-cloudimg-amd64.img"
HASH_URL = "https://cloud-images.ubuntu.com/jammy/current/SHA256SUMS"
DEST_DIR = "/var/lib/libvirt/images"
FILENAME = os.path.basename(IMG_URL)
DEST_PATH = os.path.join(DEST_DIR, FILENAME)

def runCommand(cmd_list):
    try:
        result = subprocess.run(cmd_list, check=True, capture_output=True, text=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print("Command failed:", ' '.join(cmd_list))
        print("Error: ", e.stderr.strip())
        return None
    
def dockerExec(container_name, *args):
    return runCommand(['docker', 'exec', container_name] + list(args))

def getChecksum():
    with urlopen(HASH_URL) as response:
        for raw in response:
            line = raw.decode('utf-8').strip()
            if line.endswith(FILENAME):
                return line.split()[0]
    print(f"Could not find checksum for {FILENAME} in {HASH_URL}")
    sys.exit(1)

def computeSha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            h.update(chunk)
    return h.hexdigest()

def downloadAndVerify():
    expected = getChecksum()

    if os.path.isfile(DEST_PATH):
        print(f"File already exists at {DEST_PATH}")
        return
    
    fd, tmp_path = tempfile.mkstemp(prefix=FILENAME + '.', suffix='.tmp')
    os.close(fd)
    print(f"Downloading image...")

    try:
        subprocess.run(['wget', IMG_URL, '-O', tmp_path], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Download failed: {e}")
        os.remove(tmp_path)
        sys.exit(1)

    print("Verifying checksum")
    actual = computeSha256(tmp_path)
    if actual != expected:
        print(f"Checksum verification failed. Expected: {expected}, Actual: {actual}")
        os.remove(tmp_path)
        sys.exit(1)

    os.makedirs(DEST_DIR, exist_ok=True)
    os.replace(tmp_path, DEST_PATH)

    print(f"Download complete and verified. Installed at {DEST_PATH}")

def downloadMkisofs():
    container_id = runCommand([
         'docker', 'run', '--rm', '-d', '--name', 'tmp-deb', 'debian:stable-slim', 'sleep', 'infinity'
    ])

    if container_id:
        dockerExec('tmp-deb','apt-get','update')
        dockerExec('tmp-deb','apt-get','install','-y','genisoimage')
        runCommand([
            'docker', 'cp', 'tmp-deb:/usr/bin/genisoimage','/usr/local/bin/mkisofs'
        ])
        runCommand([
            'docker','rm','-f','tmp-deb'
        ])

def main():
    # Download the correct image and verify checksum
    downloadAndVerify()

    # Check if mkisofs binary is installed
    if not shutil.which('mkisofs'):
        print(f"mkisofs binary not found; installing now...")
        downloadMkisofs()
    else:
        print(f"mkisofs binary already installed.")


if __name__ == '__main__':
    main()