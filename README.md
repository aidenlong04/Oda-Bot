# Oda-Bot

A Discord bot with utilities and fun commands for your server.

## Features

- **IGN Sync**: Automatically sync in-game names from a channel and set them as nicknames
- **Message Search**: Find messages containing specific text in a channel
- **Ordis Jokes**: Random jokes and puns
- **Auto-responses**: Reacts to specific keywords with GIFs

## Quick Start

### Clone the Repository

```bash
git clone https://github.com/aidenlong04/Oda-Bot.git
cd Oda-Bot
```

### Setup

1. Copy `.env.example` to `.env` and set your Discord bot token:

```bash
cp .env.example .env
```

2. Edit `.env` and add your Discord token:

```
DISCORD_TOKEN=your_token_here
```

3. Run the bot:

```bash
python oda_bot.py
```

The bot will automatically install required dependencies on first run.

## Docker Setup

See [README_DOCKER.md](README_DOCKER.md) for Docker deployment instructions.

## Commands

- `/pun` - Get a random Ordis joke
- `/find <text> <channel>` - Find messages containing specific text (Admin only)
- `/sync_ign <channel>` - Sync IGNs from a channel and set as nicknames (Admin only)

## License

This project is open source and available for use and modification.
