# Oda-Bot
Discord bot designed for the Golden Pagoda Server

## Features
- 🎭 **Message Responses**: Responds to "oda" mentions with Breaking Bad themed GIFs
- 🎲 **Random Jokes**: `/pun` command tells Ordis jokes from Warframe
- 🔍 **Message Search**: `/find` command to search for messages in channels
- 👥 **IGN Sync**: `/sync_ign` and `/sync_user` commands to sync Discord nicknames with in-game names

## Hosting Options

This bot can be hosted in multiple ways. Choose the method that best fits your needs:

### 🐳 Docker (Recommended)

The easiest way to host the bot is using Docker:

1. **Clone the repository:**
   ```bash
   git clone https://github.com/aidenlong04/Oda-Bot.git
   cd Oda-Bot
   ```

2. **Set up environment:**
   ```bash
   cp .env.example .env
   # Edit .env and add your DISCORD_TOKEN
   ```

3. **Run with Docker Compose:**
   ```bash
   docker-compose up -d
   ```

4. **View logs:**
   ```bash
   docker-compose logs -f oda-bot
   ```

### ☁️ Cloud Platforms

#### Railway
1. Fork this repository
2. Connect your Railway account to GitHub
3. Create a new project and connect your fork
4. Add environment variable: `DISCORD_TOKEN`
5. Deploy automatically!

#### Heroku
1. Fork this repository
2. Create new Heroku app
3. Connect GitHub repository
4. Add config var: `DISCORD_TOKEN`
5. Deploy from GitHub

#### Render
1. Fork this repository
2. Create new Web Service on Render
3. Connect your GitHub repository
4. Add environment variable: `DISCORD_TOKEN`
5. Use start command: `python bot.py`

### 🖥️ VPS/Linux Server

For VPS or dedicated server hosting:

1. **Automated Setup:**
   ```bash
   git clone https://github.com/aidenlong04/Oda-Bot.git
   cd Oda-Bot
   ./setup-linux.sh
   ```

2. **Manual Setup:**
   ```bash
   # Install dependencies
   sudo apt update
   sudo apt install python3 python3-pip
   
   # Clone and setup
   git clone https://github.com/aidenlong04/Oda-Bot.git
   cd Oda-Bot
   pip3 install -r requirements.txt
   
   # Configure environment
   cp .env.example .env
   # Edit .env with your token
   
   # Run bot
   python3 bot.py
   ```

3. **As a Service (systemd):**
   ```bash
   # After running setup-linux.sh or manual setup
   sudo systemctl enable oda-bot
   sudo systemctl start oda-bot
   sudo systemctl status oda-bot
   ```

### 💻 Windows

1. **Install Python 3.8+** from python.org
2. **Clone repository:**
   ```cmd
   git clone https://github.com/aidenlong04/Oda-Bot.git
   cd Oda-Bot
   ```
3. **Install dependencies:**
   ```cmd
   pip install -r requirements.txt
   ```
4. **Configure environment:**
   ```cmd
   copy .env.example .env
   # Edit .env with your DISCORD_TOKEN
   ```
5. **Run bot:**
   ```cmd
   python bot.py
   ```
6. **Auto-restart (optional):**
   ```cmd
   run-bot-loop.bat
   ```

## Configuration

### Environment Variables
- `DISCORD_TOKEN` - Your Discord bot token (required)

### Getting a Discord Bot Token
1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application
3. Go to "Bot" section
4. Create a bot and copy the token
5. Add to your `.env` file: `DISCORD_TOKEN=your_token_here`

### Bot Permissions
The bot needs the following permissions:
- Send Messages
- Use Slash Commands
- Read Message History
- Manage Nicknames (for IGN sync features)
- Embed Links

## Monitoring

### Docker
```bash
# View logs
docker-compose logs -f oda-bot

# Restart bot
docker-compose restart oda-bot

# Update bot
git pull
docker-compose down
docker-compose up -d --build
```

### Linux Service
```bash
# Check status
sudo systemctl status oda-bot

# View logs
sudo journalctl -u oda-bot -f

# Restart
sudo systemctl restart oda-bot
```

## Troubleshooting

### Common Issues

1. **Bot doesn't respond to commands:**
   - Check if bot is online in Discord
   - Verify bot has necessary permissions
   - Check logs for errors

2. **"Invalid token" error:**
   - Verify DISCORD_TOKEN in .env file
   - Ensure no extra spaces or quotes around token

3. **Permission errors:**
   - Check bot role hierarchy in Discord server
   - Verify bot has required permissions listed above

4. **Import errors:**
   - Run: `pip install -r requirements.txt`
   - Check Python version (3.8+ required)

### Support
For issues, please check the logs first and create an issue on GitHub with:
- Error message
- Steps to reproduce
- Hosting method used