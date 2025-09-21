#!/usr/bin/env bash
set -euo pipefail

echo "This script helps install systemd service files for Oda-Bot."

cat <<'USAGE'
Usage (run on target host as root or with sudo):

# 1) For Docker-based service (recommended if you're running via GHCR):
sudo mkdir -p /etc/oda-bot
# Copy your .env to /etc/oda-bot/.env (contains DISCORD_TOKEN etc)
sudo cp .env /etc/oda-bot/.env
sudo cp deploy/systemd/oda-bot.service /etc/systemd/system/oda-bot.service
sudo systemctl daemon-reload
sudo systemctl enable --now oda-bot.service
sudo journalctl -u oda-bot -f

# 2) For Python venv service (if you prefer running without Docker):
sudo useradd -r -s /usr/sbin/nologin oda || true
sudo mkdir -p /opt/oda-bot
# Copy repo contents to /opt/oda-bot and create a venv, install requirements
# Adjust paths in deploy/systemd/oda-bot-venv.service as needed
sudo cp deploy/systemd/oda-bot-venv.service /etc/systemd/system/oda-bot-venv.service
sudo systemctl daemon-reload
sudo systemctl enable --now oda-bot-venv.service
sudo journalctl -u oda-bot-venv -f

USAGE

echo
echo "Note: This script only prints instructions. Run the commands above on your target host (or copy this script and run it there)."
