#!/bin/bash
# Docker deployment script for Oda-Bot

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🤖 Oda-Bot Docker Deployment Script"
echo "===================================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed or not in PATH"
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Creating from template..."
    cp .env.example .env
    echo "📝 Please edit .env file and add your Discord token:"
    echo "   DISCORD_TOKEN=your_discord_bot_token_here"
    echo ""
    read -p "Press Enter after you've updated the .env file..."
fi

# Check if Discord token is set
if ! grep -q "^DISCORD_TOKEN=" .env || grep -q "your_discord_bot_token_here" .env; then
    echo "❌ Please set a valid DISCORD_TOKEN in .env file"
    exit 1
fi

echo "🔧 Building Docker image..."
docker build -t oda-bot .

echo "🚀 Starting Oda-Bot..."
if command -v docker-compose &> /dev/null; then
    docker-compose up -d
    echo "✅ Bot started with Docker Compose"
    echo "📝 View logs: docker-compose logs -f discord-bot"
    echo "🛑 Stop bot: docker-compose down"
else
    # Fallback to plain docker
    docker run -d --name oda-bot --env-file .env --restart unless-stopped oda-bot
    echo "✅ Bot started with Docker"
    echo "📝 View logs: docker logs -f oda-bot"
    echo "🛑 Stop bot: docker stop oda-bot && docker rm oda-bot"
fi

echo ""
echo "🎉 Oda-Bot is now running!"
echo "🔗 Add the bot to your Discord server if you haven't already"