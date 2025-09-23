#!/usr/bin/env bash
set -euo pipefail

# run_local.sh - simple helper to create a venv, install requirements, and run oda_bot.py

if [ ! -f .env ]; then
  echo ".env not found. Copy .env.example to .env and set DISCORD_TOKEN before running."
  echo "cp .env.example .env && edit .env"
  exit 1
fi

PY=python3
if ! command -v $PY >/dev/null 2>&1; then
  echo "$PY not found. Please install Python 3.10+"
  exit 2
fi

if [ ! -d venv ]; then
  echo "Creating virtualenv..."
  $PY -m venv venv
fi

echo "Activating venv and installing requirements..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "Starting Oda-Bot (Ctrl-C to stop)..."
exec venv/bin/python oda_bot.py
