# Oda-Bot
Discord bot designed for the Golden Pagoda Server

## Run locally (Python)

1. Copy `.env.example` to `.env` and set `DISCORD_TOKEN` (and optionally `GUILD_ID` for fast slash command registration):

```bash
cp .env.example .env
# edit .env and set DISCORD_TOKEN and optionally GUILD_ID
```

2. Run the helper script which creates a virtualenv, installs dependencies, and runs the bot:

```bash
./run_local.sh
```

3. To stop the bot: Ctrl-C in the terminal where it's running.

For containerized instructions see `README_DOCKER.md`.
