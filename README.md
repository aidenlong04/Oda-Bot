# Oda-Bot

A Discord bot for server management and community engagement.

## Repository

**GitHub Repository:** [https://github.com/aidenlong04/Oda-Bot](https://github.com/aidenlong04/Oda-Bot)

### Download Options

**Option 1: Using GitHub Desktop**
1. Click the green "Code" button on the [repository page](https://github.com/aidenlong04/Oda-Bot)
2. Select "Open with GitHub Desktop"
3. Choose a local path to save the repository
4. GitHub Desktop will clone the repository for you

**Option 2: Direct Download (ZIP)**
1. Click the green "Code" button on the [repository page](https://github.com/aidenlong04/Oda-Bot)
2. Select "Download ZIP"
3. Extract the ZIP file to your desired location

**Option 3: Git Command Line**
```bash
git clone https://github.com/aidenlong04/Oda-Bot.git
cd Oda-Bot
```

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

### Prerequisites
- Python 3.12 or higher (for local installation)
- Docker Desktop (for Docker installation)
- A Discord bot token from the [Discord Developer Portal](https://discord.com/developers/applications)

### Local Installation

1. **Download the repository** (see [Download Options](#download-options) above)

2. Navigate to the repository folder:
   ```bash
   cd Oda-Bot
   ```

3. Create a `.env` file from the example:
   ```bash
   cp .env.example .env
   ```

4. Add your Discord bot token to the `.env` file:
   ```
   DISCORD_TOKEN=your_token_here
   ```

5. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

6. Run the bot:
   ```bash
   python oda_bot.py
   ```

## Running with Docker Desktop

### Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed on your computer
- A Discord bot token (see [Discord Developer Portal](https://discord.com/developers/applications))

### Step-by-Step Instructions

1. **Download the repository** (see [Download Options](#download-options) above)

2. **Navigate to the repository folder:**
   ```bash
   cd Oda-Bot
   ```

3. **Create your environment file:**
   - Copy `.env.example` to `.env`:
     ```bash
     cp .env.example .env
     ```
   - Open `.env` in a text editor and replace the token with your actual Discord bot token:
     ```
     DISCORD_TOKEN=your_actual_discord_token_here
     ```

4. **Start Docker Desktop:**
   - Open Docker Desktop application on your computer
   - Wait for it to fully start (the Docker icon should show "running")

5. **Build and run the bot:**
   ```bash
   docker compose up --build -d
   ```
   This will:
   - Build the Docker image for Oda-Bot
   - Start the container in detached mode (runs in background)
   - The bot will automatically restart if it crashes

6. **View the bot logs:**
   ```bash
   docker compose logs -f oda-bot
   ```
   Press `Ctrl+C` to exit the logs view

7. **Stop the bot:**
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

### CI/CD Deployment

The repository includes a GitHub Actions workflow (`.github/workflows/ci-deploy.yml`) that automatically builds and pushes the Docker image to GitHub Container Registry on pushes to `main`.

For optional remote deployment via SSH, set these repository secrets in GitHub:
- `DEPLOY_HOST` - remote host address
- `DEPLOY_USER` - SSH username
- `DEPLOY_KEY` - private SSH key contents

## License

This project is open source and available under the terms specified in the repository.
