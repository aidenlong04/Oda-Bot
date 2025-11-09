# Oda-Bot

A Discord bot for server management and community engagement.

## Repository

**GitHub Repository:** [https://github.com/aidenlong04/Oda-Bot](https://github.com/aidenlong04/Oda-Bot)

## Features

- **Ordis Jokes** - Get random jokes from Ordis with the `/pun` command
- **Message Search** - Find messages containing specific text in a channel using `/find`
- **IGN Sync** - Automatically sync in-game names (IGN) from a channel and set them as Discord nicknames with `/sync_ign`
- **"Oda" Response** - The bot responds with Breaking Bad GIFs when "oda" is mentioned in chat

## Commands

- `/pun` - Ordis will tell you a random joke
- `/find <text> <channel>` - Find messages containing specific text in a channel (Admin only)
- `/sync_ign <channel>` - Sync IGNs from a channel and set as nicknames for all found users (Admin only)

## Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/aidenlong04/Oda-Bot.git
   cd Oda-Bot
   ```

2. Create a `.env` file from the example:
   ```bash
   cp .env.example .env
   ```

3. Add your Discord bot token to the `.env` file:
   ```
   DISCORD_TOKEN=your_token_here
   ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Run the bot:
   ```bash
   python oda_bot.py
   ```

## Running with Docker Desktop

### Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed on your computer
- A Discord bot token (see [Discord Developer Portal](https://discord.com/developers/applications))

### Step-by-Step Instructions

1. **Clone the repository:**
   ```bash
   git clone https://github.com/aidenlong04/Oda-Bot.git
   cd Oda-Bot
   ```

2. **Create your environment file:**
   - Copy `.env.example` to `.env`:
     ```bash
     cp .env.example .env
     ```
   - Open `.env` in a text editor and replace the token with your actual Discord bot token:
     ```
     DISCORD_TOKEN=your_actual_discord_token_here
     ```

3. **Start Docker Desktop:**
   - Open Docker Desktop application on your computer
   - Wait for it to fully start (the Docker icon should show "running")

4. **Build and run the bot:**
   ```bash
   docker compose up --build -d
   ```
   This will:
   - Build the Docker image for Oda-Bot
   - Start the container in detached mode (runs in background)
   - The bot will automatically restart if it crashes

5. **View the bot logs:**
   ```bash
   docker compose logs -f oda-bot
   ```
   Press `Ctrl+C` to exit the logs view

6. **Stop the bot:**
   ```bash
   docker compose down
   ```

### Managing in Docker Desktop UI

You can also manage the bot directly in Docker Desktop:
1. Open Docker Desktop
2. Go to the "Containers" tab
3. Find "oda-bot" in the list
4. Use the play/stop/restart buttons to control the bot
5. Click on the container to view logs and details

### Troubleshooting

- If the bot doesn't start, check the logs: `docker compose logs oda-bot`
- Make sure your Discord token is correct in the `.env` file
- Ensure Docker Desktop is running before executing docker commands

For advanced deployment options and CI/CD setup, see [README_DOCKER.md](README_DOCKER.md).

## License

This project is open source and available under the terms specified in the repository.
