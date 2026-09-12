# ⚒️ ESN Forge

**Build. Create. Deploy.**

ESN Forge is an ESN developer toolkit for Discord communities, creators, and developers. It provides practical generators, troubleshooting helpers, server architecture guidance, embed creation, and project planning from one bot.

## Features

- `/forge` — Forge dashboard and toolkit
- `/code` — coding workflow and implementation guidance
- `/debug` — error diagnosis and troubleshooting hints
- `/bot` — Discord bot starter specification
- `/embed` — instantly create a Discord embed
- `/server` — generate a server architecture plan
- `/project` — create a project blueprint
- `/config` — configure guild settings
- `/owner` — check configured owner access
- `/help` — command reference
- SQLite-backed guild configuration
- Environment-based secrets; tokens are never stored in source code
- Modular `cogs/` architecture for future expansion

## Setup

1. Install Python 3.11+.
2. Run `pip install -r requirements.txt`.
3. Copy `.env.example` to `.env`.
4. Set `DISCORD_TOKEN` to the bot token locally. Never commit `.env`.
5. Set `OWNER_IDS` to comma-separated Discord user IDs.
6. Enable the Message Content and Server Members intents in the Discord Developer Portal if your deployment needs them.
7. Run `python bot.py`.

## Security

Never post a Discord bot token, API key, password, or other secret in chat, GitHub, or Discord. If a token is ever exposed, rotate it immediately in the Discord Developer Portal.

## Project layout

```text
ESN-Forge/
├── bot.py
├── cogs/
│   ├── forge.py
│   ├── code.py
│   ├── botbuilder.py
│   ├── embeds.py
│   ├── server.py
│   ├── config.py
│   └── help.py
├── utils/
│   └── database.py
├── data/                 # runtime SQLite database
├── .env.example
├── requirements.txt
└── README.md
```

## Roadmap

The architecture is ready for richer AI-assisted code generation, interactive builders, reusable templates, permission-aware server deployment, project exports, logging, and additional creator/developer tools without changing the core bot structure.

**ESN Forge — Powering creators. Elevating communities.**
