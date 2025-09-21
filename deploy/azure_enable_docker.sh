#!/usr/bin/env bash
set -euo pipefail

echo "Install and enable Docker Engine on an Ubuntu-based Azure VM"

# Safety checks: ensure we're on a system with systemd (Cloud Shell won't work)
if ! command -v systemctl >/dev/null 2>&1; then
  cat <<'MSG'
This environment does not appear to have systemd available.
Azure Cloud Shell is a managed container and cannot run the Docker daemon.
Run this script on an actual VM (Ubuntu 20.04/22.04) with systemd.
MSG
  exit 2
fi

if [ "$(id -u)" -ne 0 ]; then
  echo "This script requires root. Re-run with sudo. Example: sudo ./azure_enable_docker.sh"
  exit 3
fi

echo "Updating apt and installing prerequisite packages..."
apt-get update -y
apt-get install -y ca-certificates curl gnupg lsb-release apt-transport-https software-properties-common

echo "Adding Docker official GPG key and repository..."
mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
ARCH=$(dpkg --print-architecture)
CODENAME=$(lsb_release -cs)
echo "deb [arch=${ARCH} signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu ${CODENAME} stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

echo "Installing Docker Engine and docker-compose plugin..."
apt-get update -y
apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

echo "Enabling and starting Docker service..."
systemctl enable --now docker

echo "Adding current default user to docker group (so sudo is not required to run docker)."
DEFAULT_USER=${SUDO_USER:-$(logname 2>/dev/null || echo root)}
if id "$DEFAULT_USER" >/dev/null 2>&1; then
  usermod -aG docker "$DEFAULT_USER" || true
  echo "Added $DEFAULT_USER to docker group. That user may need to re-login to apply the group change."
else
  echo "Could not detect a non-root user to add to docker group. You can add users manually later."
fi

echo "Testing Docker by running hello-world image (this will pull the image)."
set +e
docker run --rm hello-world
EXIT=$?
set -e
if [ $EXIT -ne 0 ]; then
  echo "Warning: hello-world container failed to run (exit $EXIT). Inspect 'sudo journalctl -u docker -n 200' for details."
else
  echo "Docker test passed. Docker is installed and running."
fi

cat <<'END'
Done.

Notes:
- Do NOT run this script in Azure Cloud Shell; use an Azure VM or other host with systemd.
- If you created a VM using the Azure Portal, you can run this script by copying it to the VM and executing:
    sudo bash azure_enable_docker.sh
- After this, you can run docker compose commands or start the systemd service unit that pulls your bot image.
END
