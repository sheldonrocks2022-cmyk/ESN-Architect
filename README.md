# ⚒️ ESN Forge

**Build. Create. Deploy.**

ESN Forge is an ESN developer toolkit for Discord communities, creators, and developers. It combines coding helpers, AI-assisted generation, bot project exports, embed tools, server architecture, security checks, utilities, and owner diagnostics.

## AI Forge

Forge can use the OpenAI Responses API for real AI-assisted development when `OPENAI_API_KEY` is configured. Current AI commands:

- `/ask` — general developer/project assistant
- `/ai-generate` — generate a real implementation
- `/ai-debug` — diagnose an error and produce a fix
- `/ai-explain` — explain code/concepts at a chosen level
- `/ai-improve` — refactor code
- `/ai-review` — security/quality/code review
- `/ai-convert` — convert between languages/frameworks
- `/ai-docs` — generate documentation
- `/ai-project` — generate a multi-file project and download a ZIP
- `/ai-status` — check AI configuration

API keys are never hardcoded in source code. Configure `OPENAI_API_KEY` through the runtime environment. `OPENAI_MODEL` selects the configured model.

## Command toolkit

### Forge & coding
- `/forge` — main Forge dashboard
- `/project` — project blueprint
- `/code` — coding workflow
- `/generate` — local starter implementation generator
- `/debug` — local error diagnosis
- `/explain` — local explanation helper
- `/improve` — local refactoring checklist
- `/review` — local quality/security review
- `/convert` — conversion workflow
- `/docs` — documentation template

### Bot Forge
- `/bot` — bot starter specification
- `/bot-create` — downloadable starter bot ZIP
- `/bot-command` — command template
- `/bot-event` — event template
- `/bot-feature` — feature implementation plan
- `/bot-structure` — project structure
- `/bot-config` — secure configuration guidance
- `/bot-export` — starter project export

### Embed Forge
- `/embed` — create an embed
- `/embed-json` — embed configuration JSON
- `/embed-code` — Python embed code
- `/embed-template` — reusable template

### Server Forge
- `/server` — server architecture plan
- `/server-plan` — detailed plan
- `/server-roles` — role hierarchy
- `/server-channels` — channel structure
- `/server-permissions` — permission checklist
- `/server-rules` — server rules builder
- `/server-audit` — server audit
- `/server-setup` — safe dry-run setup preview

### Developer utilities
- `/json` — validate/format JSON
- `/regex` — validate regex
- `/timestamp` — Discord timestamp formatter
- `/color` — hex/RGB converter
- `/base64` — Base64 encoder/decoder
- `/uuid` — UUID generator
- `/hash` — SHA-256 hashing

### Security & diagnostics
- `/permissions` — inspect Forge permissions
- `/security-audit` — lightweight security checklist
- `/health` — runtime health
- `/logs` — owner diagnostics
- `/stats` — Forge statistics
- `/ping` — latency check
- `/about` — Forge information

### Owner tools
- `/owner` — owner access check
- `/owner-status` — owner runtime status
- `/owner-guilds` — connected guild list
- `/owner-broadcast` — controlled owner broadcast
- `/owner-maintenance` — maintenance information
- `/owner-shutdown` — safe shutdown guidance

## Setup

1. Install Python 3.11+.
2. Run `pip install -r requirements.txt`.
3. Create a local `.env` file containing the runtime configuration required by `bot.py`.
4. Set `DISCORD_TOKEN` to the bot token through your private host environment or local `.env`.
5. Set `OWNER_IDS` to comma-separated Discord user IDs.
6. Set `OPENAI_API_KEY` for AI features and optionally set `OPENAI_MODEL`.
7. Enable the Discord intents required by the features you use.
8. Run `python bot.py`.

The repository intentionally does not contain an `.env.example`. Never commit `.env` or expose credentials in GitHub, Discord, or chat.

## Security

Never post a Discord bot token, OpenAI API key, password, or other secret in chat, GitHub, or Discord. If a secret is exposed, rotate it immediately. Generated projects use environment variables rather than hardcoded credentials.

## Project layout

```text
ESN-Forge/
├── bot.py
├── cogs/
│   ├── ai.py
│   ├── forge.py
│   ├── code.py
│   ├── botbuilder.py
│   ├── embeds.py
│   ├── server.py
│   ├── config.py
│   ├── help.py
│   └── tools.py
├── utils/
│   └── database.py
├── data/                 # runtime SQLite database; do not commit
├── requirements.txt
├── .gitignore
└── README.md
```

**ESN Forge — Powering creators. Elevating communities.**
