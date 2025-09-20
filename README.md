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

### Option 3: Docker (Recommended for Self-Hosting)

#### Quick Deploy Script:
```bash
git clone https://github.com/aidenlong04/Oda-Bot.git
cd Oda-Bot

# Optional: Validate setup first
./validate.sh

# Deploy the bot
./deploy.sh
```
The scripts will guide you through the setup process.

#### Manual Setup:
1. **Clone the repository:**
   ```bash
   git clone https://github.com/aidenlong04/Oda-Bot.git
   cd Oda-Bot
   ```

2. **Create environment file:**
   ```bash
   cp .env.example .env
   # Edit .env and add your Discord token
   ```

3. **Build and run:**
   ```bash
   docker build -t oda-bot .
   docker run -d --name oda-bot --env-file .env --restart unless-stopped oda-bot
   ```

#### Using Docker Compose (Recommended):
1. **Create environment file:**
   ```bash
   cp .env.example .env
   # Edit .env and add your Discord token
   ```

2. **Run with Docker Compose:**
   ```bash
   # Development
   docker-compose up -d
   
   # Production (with resource limits)
   docker-compose -f docker-compose.prod.yml up -d
   ```

3. **View logs:**
   ```bash
   docker-compose logs -f discord-bot
   ```

4. **Stop the bot:**
   ```bash
   docker-compose down
   ```

#### Docker Commands Reference:
```bash
# Build image
docker build -t oda-bot .

# Run container with environment file
docker run -d --name oda-bot --env-file .env --restart unless-stopped oda-bot

# Run container with inline environment variable
docker run -d --name oda-bot -e DISCORD_TOKEN=your_token --restart unless-stopped oda-bot

# View logs
docker logs -f oda-bot

# Stop and remove container
docker stop oda-bot && docker rm oda-bot

# Check container health
docker inspect --format='{{.State.Health.Status}}' oda-bot
```

### Option 4: Docker Compose
1. **Create environment file:**
   ```bash
   cp .env.example .env
   # Edit .env and add your Discord token
   ```
2. **Run:**
   ```bash
   # Development
   docker-compose up -d
   
   # Production with resource limits
   docker-compose -f docker-compose.prod.yml up -d
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

## Docker Requirements
- Docker 20.10+ or Docker Desktop
- Docker Compose v2.0+ (optional but recommended)

## Troubleshooting

### Quick Validation:
Run the validation script to check your setup:
```bash
./validate.sh
```

### Docker Issues:
- **Build fails**: Ensure Docker has internet access and sufficient disk space
- **Container exits immediately**: Check that `DISCORD_TOKEN` environment variable is set correctly
- **Permission errors**: Make sure the bot user has proper permissions in your Discord server
- **Health check failures**: Verify the Discord token is valid and not expired

### Discord Bot Setup:
1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application
3. Go to Bot section and create a bot
4. Copy the bot token
5. Invite bot to your server with appropriate permissions

## Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request
