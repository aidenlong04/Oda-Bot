# Oda-Bot Docker

This repository includes Docker configuration to run the Discord bot in a container.

Quick start:

1. Copy `.env.example` to `.env` and set `DISCORD_TOKEN`.
2. Build and run with docker-compose:

```bash
docker compose up --build -d
```

3. Check logs:

```bash
docker compose logs -f oda-bot
```

CI/CD

The workflow `.github/workflows/ci-deploy.yml` will build and push the image to GitHub Container Registry on pushes to `main`.

Optional remote deploy: set the following repository secrets in GitHub to enable SSH deployment:
- `DEPLOY_HOST` - remote host
- `DEPLOY_USER` - ssh user
- `DEPLOY_KEY` - private key contents

The workflow will pull the new image on the target host and restart the container. Ensure Docker is installed on the target host and the path to `.env` in the workflow matches where you place your environment file.
