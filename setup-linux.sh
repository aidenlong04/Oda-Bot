#!/bin/bash

# Oda Bot Setup Script for Linux/VPS
# This script sets up the bot as a systemd service

set -e

echo "🤖 Setting up Oda Discord Bot..."

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   echo "❌ This script should not be run as root. Please run as a regular user with sudo privileges."
   exit 1
fi

# Variables
BOT_USER="oda-bot"
BOT_DIR="/opt/oda-bot"
SERVICE_NAME="oda-bot"

echo "📋 This script will:"
echo "   - Create a dedicated user for the bot"
echo "   - Install the bot to $BOT_DIR"
echo "   - Set up systemd service"
echo "   - Install Python dependencies"
echo ""
read -p "Continue? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 1
fi

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    echo "Install it with: sudo apt install python3 python3-pip"
    exit 1
fi

# Create bot user
echo "👤 Creating bot user..."
if ! id "$BOT_USER" &>/dev/null; then
    sudo useradd -r -s /bin/false -d "$BOT_DIR" "$BOT_USER"
    echo "✅ Created user $BOT_USER"
else
    echo "ℹ️  User $BOT_USER already exists"
fi

# Create bot directory
echo "📁 Creating bot directory..."
sudo mkdir -p "$BOT_DIR"
sudo mkdir -p "$BOT_DIR/logs"

# Copy bot files
echo "📥 Installing bot files..."
sudo cp bot.py "$BOT_DIR/"
sudo cp requirements.txt "$BOT_DIR/"
sudo cp .env.example "$BOT_DIR/"

# Set permissions
sudo chown -R "$BOT_USER:$BOT_USER" "$BOT_DIR"
sudo chmod 755 "$BOT_DIR"
sudo chmod 644 "$BOT_DIR"/*.py
sudo chmod 644 "$BOT_DIR"/requirements.txt

# Install Python dependencies
echo "🐍 Installing Python dependencies..."
sudo -u "$BOT_USER" python3 -m pip install --user -r "$BOT_DIR/requirements.txt"

# Install systemd service
echo "⚙️  Installing systemd service..."
sudo cp oda-bot.service /etc/systemd/system/
sudo systemctl daemon-reload

echo "🔧 Setup complete!"
echo ""
echo "📝 Next steps:"
echo "1. Copy your environment file:"
echo "   sudo cp .env $BOT_DIR/.env"
echo "   sudo chown $BOT_USER:$BOT_USER $BOT_DIR/.env"
echo "   sudo chmod 600 $BOT_DIR/.env"
echo ""
echo "2. Edit the environment file with your bot token:"
echo "   sudo -u $BOT_USER nano $BOT_DIR/.env"
echo ""
echo "3. Start the bot service:"
echo "   sudo systemctl enable $SERVICE_NAME"
echo "   sudo systemctl start $SERVICE_NAME"
echo ""
echo "4. Check bot status:"
echo "   sudo systemctl status $SERVICE_NAME"
echo "   sudo journalctl -u $SERVICE_NAME -f"