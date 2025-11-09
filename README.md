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

## Docker Deployment

For Docker deployment instructions, see [README_DOCKER.md](README_DOCKER.md).

## License

This project is open source and available under the terms specified in the repository.
