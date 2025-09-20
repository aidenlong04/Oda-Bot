# Oda-Bot
Discord bot designed for the Golden Pagoda Server

## Features
- **Oda Reactions**: Responds to mentions of "oda" with Breaking Bad GIFs
- **Oda Jokes**: Random Warframe-themed jokes via `/pun` command
- **Message Search**: Find messages in channels with `/find` command
- **IGN Sync**: Sync Discord nicknames to in-game names from channel messages /sync_ign for server wide /sync_user for individual user

## Setup
### 3. Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run the bot
python bot.py
```

## Hosting Options

### Option 1: Railway (Recommended - Free Tier Available)
1. Fork this repository
2. Sign up at [Railway](https://railway.app)
3. Create new project from GitHub repo
4. Add environment variable: `DISCORD_TOKEN=your_token`
5. Deploy automatically

### Option 2: Heroku
1. Install [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli)
2. Login and create app:
   ```bash
   heroku login
   heroku create your-bot-name
   ```
3. Set environment variable:
   ```bash
   heroku config:set DISCORD_TOKEN=your_token
   ```
4. Deploy:
   ```bash
   git push heroku main
   ```

### Option 3: Docker
1. Build the image:
   ```bash
   docker build -t oda-bot .
   ```
2. Run with environment variable:
   ```bash
   docker run -e DISCORD_TOKEN=your_token oda-bot
   ```

### Option 4: Docker Compose
1. Create `.env` file with your token
2. Run:
   ```bash
   docker-compose up -d
   ```

### Option 5: VPS/Self-Hosted
1. Install Python 3.11+
2. Clone repository:
   ```bash
   git clone https://github.com/yourusername/Oda-Bot.git
   cd Oda-Bot
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create `.env` file with your token
5. Run with process manager (e.g., PM2, systemd):
   ```bash
   # Using PM2
   npm install -g pm2
   pm2 start bot.py --name oda-bot --interpreter python3

   # Or using nohup
   nohup python bot.py &
   ```

## Commands
- `/pun` - Get a random Ordis joke
- `/find <keywords> <channel>` - Find message with keywords in a channel (Admin only)
- `/sync_ign <channel>` - Sync all user nicknames to their IGNs from a channel (Admin only)
- `/sync_user <user> <channel>` - Sync specific user's nickname to their IGN (Admin only)

## Requirements
- Python 3.11+
- discord.py 2.3.0+
- python-dotenv 1.0.0+

## Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request
