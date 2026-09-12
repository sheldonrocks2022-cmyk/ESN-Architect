# ⚒️ ESN Forge

**Build. Create. Deploy.**

ESN Forge is an ESN developer toolkit for Discord communities, creators, and developers. It combines coding helpers, AI-assisted generation, downloadable bot projects, embed building/export, server architecture and deployment, security checks, utilities, configuration, diagnostics, and production operations.

## AI Forge

When `OPENAI_API_KEY` is configured, Forge provides real AI-assisted development through the OpenAI Responses API:

- `/ask` — general developer/project assistant
- `/ai-generate` — generate an implementation
- `/ai-debug` — diagnose an error
- `/ai-fix` — produce a fix
- `/ai-explain` — explain code/concepts
- `/ai-improve` — refactor code
- `/ai-review` — security/quality review
- `/ai-test` — generate tests
- `/ai-convert` — convert languages/frameworks
- `/ai-docs` — generate documentation
- `/ai-file` — analyze a text/code attachment
- `/ai-project` — generate a multi-file project ZIP
- `/ai-project-plan` — plan a project
- `/ai-status` — inspect AI configuration

Secrets are never hardcoded. Use `OPENAI_API_KEY` and optionally `OPENAI_MODEL` in the private runtime environment.

## Forge Builders

### Bot Forge
- `/bot` — generate a real downloadable Python or JavaScript Discord bot starter
- `/bot-create` — additional starter export
- `/bot-command` — command template
- `/bot-event` — event template
- `/bot-feature` — feature implementation plan
- `/bot-structure` — project structure
- `/bot-config` — secure configuration guidance
- `/bot-export` — project export

### Embed Forge
- `/embed` — build and preview an embed with JSON export
- `/embed-json` — preview an embed from JSON
- `/embed-code` — Python embed code
- `/embed-template` — reusable templates

### Server Forge
- `/server` — generate a complete server blueprint
- `/server-deploy` — create categories/channels/roles from a template without duplicating existing items
- `/server-plan` — detailed planning
- `/server-roles` — role hierarchy
- `/server-channels` — channel structure
- `/server-permissions` — permission checklist
- `/server-rules` — rules builder
- `/server-audit` — server audit
- `/server-setup` — dry-run setup preview

## Developer Toolkit

- `/forge` — complete Forge dashboard
- `/forge-status` — runtime summary
- `/project` — project execution plan
- `/code` — coding workflow
- `/generate` — local starter generator
- `/debug` — error diagnosis helper
- `/explain` — explanation helper
- `/improve` — refactoring checklist
- `/review` — quality/security review
- `/convert` — conversion workflow
- `/docs` — documentation template
- `/json` — validate/format JSON
- `/regex` — validate regex
- `/timestamp` — Discord timestamp formatter
- `/color` — hex/RGB converter
- `/base64` — Base64 encoder/decoder
- `/uuid` — UUID generator
- `/hash` — SHA-256 hashing

## Security & Operations

- `/permissions` — inspect Forge's current guild permissions
- `/security-audit` — lightweight server security checklist
- `/health` — runtime health
- `/deploy-check` — production readiness check
- `/invite` — generate a permission-scoped bot invite
- `/logs` — owner diagnostics
- `/backup-db` — owner-only SQLite SQL backup
- `/shutdown` — owner-only safe shutdown
- `/stats` — Forge statistics
- `/ping` — latency check
- `/about` — Forge information

## Configuration

Guild administrators can configure supported server settings through the configuration commands. Owner-only operations use `OWNER_IDS`; server management operations use Discord permissions rather than relying only on command visibility.

## Setup

1. Install Python 3.11+.
2. Run `pip install -r requirements.txt`.
3. Create a private `.env` file or configure equivalent host environment variables.
4. Set `DISCORD_TOKEN`.
5. Set `OWNER_IDS` to comma-separated Discord user IDs.
6. Set `OPENAI_API_KEY` for AI features and optionally `OPENAI_MODEL`.
7. Enable Discord intents required by the features you use.
8. Run `python bot.py`.

The repository intentionally does **not** contain `.env` or `.env.example`. Never commit credentials.

### Development

Install `requirements-dev.txt` and run `pytest -q`. CI also runs compilation and the test suite automatically.

### Docker

Build with `docker build -t esn-forge .` and run with your private environment variables. The included `docker-compose.yml` persists the SQLite `data/` directory.

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
│   ├── ops.py
│   ├── config.py
│   ├── help.py
│   └── tools.py
├── utils/
│   └── database.py
├── tests/
├── data/                 # runtime SQLite database; do not commit
├── requirements.txt
├── requirements-dev.txt
├── Dockerfile
├── docker-compose.yml
├── .github/workflows/ci.yml
├── .gitignore
└── README.md
```

**ESN Forge — Powering creators. Elevating communities.**
