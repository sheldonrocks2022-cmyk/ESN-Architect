import io
import json
import re
import uuid
import base64
import hashlib
import zipfile
from datetime import datetime, timezone

import discord
from discord import app_commands
from discord.ext import commands


def clip(text: str, limit: int = 1800) -> str:
    return text if len(text) <= limit else text[: limit - 3] + "..."


def code_block(text: str, language: str = "text") -> str:
    return f"```{language}\n{clip(text, 1700)}\n```"


class Tools(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def _owner(self, interaction: discord.Interaction) -> bool:
        owners = {int(x.strip()) for x in __import__("os").getenv("OWNER_IDS", "").split(",") if x.strip().isdigit()}
        if interaction.user.id not in owners:
            await interaction.response.send_message("⛔ This is an owner-only Forge command.", ephemeral=True)
            return False
        return True

    @app_commands.command(name="about", description="Learn about ESN Forge.")
    async def about(self, interaction):
        e = discord.Embed(title="⚒️ ESN Forge", description="Build. Create. Deploy.", color=0x42E8F4)
        e.add_field(name="Purpose", value="A developer and creator toolkit for Discord projects, code, embeds, server architecture, debugging, and project generation.", inline=False)
        e.add_field(name="Built by", value="ESN — Powering Creators. Elevating Communities.", inline=False)
        await interaction.response.send_message(embed=e)

    @app_commands.command(name="ping", description="Check Forge latency.")
    async def ping(self, interaction):
        await interaction.response.send_message(f"🏓 Pong! `{round(self.bot.latency * 1000)}ms`", ephemeral=True)

    @app_commands.command(name="explain", description="Explain code or a programming concept simply.")
    @app_commands.describe(code_or_topic="Code, error, or concept to explain")
    async def explain(self, interaction, code_or_topic: str):
        e = discord.Embed(title="📖 Forge Explain", description=clip(code_or_topic), color=0x6366F1)
        e.add_field(name="How to understand it", value="Identify the inputs → follow the main logic → note the output → identify dependencies and side effects.", inline=False)
        e.add_field(name="Tip", value="Include the language and the surrounding function/class for a more precise explanation.", inline=False)
        await interaction.response.send_message(embed=e)

    @app_commands.command(name="improve", description="Get a code-refactoring checklist.")
    @app_commands.describe(code="Code or project section to improve")
    async def improve(self, interaction, code: str):
        e = discord.Embed(title="✨ Forge Improve", description=code_block(code), color=0x7DEFF2)
        e.add_field(name="Refactor checklist", value="• Remove duplication\n• Improve names and structure\n• Handle edge cases\n• Validate inputs\n• Keep secrets in environment variables\n• Add logging/tests\n• Reduce unnecessary complexity", inline=False)
        await interaction.response.send_message(embed=e)

    @app_commands.command(name="review", description="Review code for common quality and security problems.")
    @app_commands.describe(code="Paste the code to review")
    async def review(self, interaction, code: str):
        low = code.lower()
        findings = []
        if "token" in low or "api_key" in low or "apikey" in low:
            findings.append("Potential secret exposure — move credentials to environment variables.")
        if "eval(" in low or "exec(" in low:
            findings.append("Dynamic execution detected — verify that untrusted input can never reach it.")
        if "except:" in low:
            findings.append("Bare exception handler — catch specific exceptions where possible.")
        if not findings:
            findings.append("No obvious high-level red flags detected by the quick review. Run tests and a deeper review before production.")
        e = discord.Embed(title="🔎 Forge Review", description="\n".join(f"• {x}" for x in findings), color=0x168CFF)
        e.add_field(name="Reviewed", value=code_block(code), inline=False)
        await interaction.response.send_message(embed=e)

    @app_commands.command(name="convert", description="Get a plan for converting code between languages.")
    @app_commands.describe(code="Code to convert", target="Target language")
    async def convert(self, interaction, code: str, target: str):
        e = discord.Embed(title="🔄 Forge Convert", description=f"Target: **{target}**", color=0x6366F1)
        e.add_field(name="Conversion workflow", value="Map data types → replace language-specific APIs → translate control flow → replace dependencies → preserve error handling → test equivalent outputs.", inline=False)
        e.add_field(name="Source", value=code_block(code), inline=False)
        await interaction.response.send_message(embed=e)

    @app_commands.command(name="docs", description="Generate a documentation outline for code.")
    @app_commands.describe(target="Function, class, module, or project to document")
    async def docs(self, interaction, target: str):
        text = f"# {target}\n\n## Purpose\nDescribe what it does.\n\n## Parameters\nList inputs and types.\n\n## Returns\nDescribe outputs.\n\n## Errors\nList expected exceptions/failures.\n\n## Example\nShow a minimal usage example.\n\n## Notes\nDependencies, permissions, side effects, and security considerations."
        await interaction.response.send_message(code_block(text, "md"))

    @app_commands.command(name="generate", description="Generate a starter implementation from a project description.")
    @app_commands.describe(request="Describe what you want to build", language="Python, JavaScript, HTML, etc.")
    async def generate(self, interaction, request: str, language: str = "Python"):
        safe = re.sub(r"[^a-zA-Z0-9_ -]", "", request).strip()[:80] or "Forge Project"
        if language.lower() in ("python", "py"):
            starter = f'"""ESN Forge starter: {safe}"""\n\ndef main():\n    # TODO: implement: {request[:300]}\n    pass\n\nif __name__ == "__main__":\n    main()'
            lang = "python"
        elif language.lower() in ("javascript", "js", "node", "node.js"):
            starter = f"// ESN Forge starter: {safe}\n\nfunction main() {{\n  // TODO: implement: {request[:300]}\n}}\n\nmain();"
            lang = "js"
        else:
            starter = f"<!-- ESN Forge starter: {safe} -->\n<!-- TODO: implement: {request[:500]} -->"
            lang = "html"
        e = discord.Embed(title="⚙️ Forge Generate", description=f"**Language:** {language}\n**Request:** {request[:500]}", color=0x42E8F4)
        e.add_field(name="Starter", value=code_block(starter, lang), inline=False)
        e.set_footer(text="Generated starter code should be reviewed and tested before production use.")
        await interaction.response.send_message(embed=e)

    @app_commands.command(name="json", description="Validate and format JSON.")
    @app_commands.describe(data="JSON text")
    async def json_tool(self, interaction, data: str):
        try:
            parsed = json.loads(data)
            output = json.dumps(parsed, indent=2, ensure_ascii=False)
            await interaction.response.send_message(code_block(output, "json"))
        except json.JSONDecodeError as exc:
            await interaction.response.send_message(f"❌ Invalid JSON: `{exc.msg}` at position `{exc.pos}`", ephemeral=True)

    @app_commands.command(name="regex", description="Explain a regex pattern or help structure one.")
    @app_commands.describe(pattern="Regex pattern")
    async def regex(self, interaction, pattern: str):
        try:
            re.compile(pattern)
            valid = "valid"
        except re.error as exc:
            valid = f"invalid: {exc}"
        await interaction.response.send_message(f"🧩 Regex `{clip(pattern, 500)}` is **{valid}**. Use a regex tester and representative test cases before production use.")

    @app_commands.command(name="timestamp", description="Create a Discord timestamp from a Unix timestamp.")
    @app_commands.describe(unix="Unix timestamp")
    async def timestamp(self, interaction, unix: int):
        await interaction.response.send_message(f"Discord timestamp: `<t:{unix}:F>`\nRelative: `<t:{unix}:R>`")

    @app_commands.command(name="color", description="Inspect a hex color value.")
    @app_commands.describe(hex_value="Hex color such as #42E8F4")
    async def color(self, interaction, hex_value: str):
        value = hex_value.strip().lstrip("#")
        if not re.fullmatch(r"[0-9a-fA-F]{6}", value):
            await interaction.response.send_message("❌ Use a 6-digit hex color such as `#42E8F4`.", ephemeral=True)
            return
        r, g, b = int(value[:2], 16), int(value[2:4], 16), int(value[4:], 16)
        await interaction.response.send_message(f"🎨 `#{value.upper()}` → RGB `{r}, {g}, {b}` → Decimal `{int(value, 16)}`")

    @app_commands.command(name="base64", description="Encode or decode Base64 text.")
    @app_commands.describe(action="encode or decode", text="Text to process")
    @app_commands.choices(action=[app_commands.Choice(name="Encode", value="encode"), app_commands.Choice(name="Decode", value="decode")])
    async def base64_tool(self, interaction, action: str, text: str):
        try:
            if action == "encode":
                result = base64.b64encode(text.encode()).decode()
            else:
                result = base64.b64decode(text.encode()).decode()
            await interaction.response.send_message(code_block(result))
        except Exception:
            await interaction.response.send_message("❌ That Base64 input could not be processed.", ephemeral=True)

    @app_commands.command(name="uuid", description="Generate a UUID.")
    async def uuid_tool(self, interaction):
        await interaction.response.send_message(f"`{uuid.uuid4()}`")

    @app_commands.command(name="hash", description="Hash text with SHA-256.")
    @app_commands.describe(text="Text to hash")
    async def hash_tool(self, interaction, text: str):
        digest = hashlib.sha256(text.encode()).hexdigest()
        await interaction.response.send_message(f"SHA-256:\n`{digest}`")

    @app_commands.command(name="permissions", description="Inspect the bot's permissions in this server.")
    async def permissions(self, interaction):
        if not interaction.guild:
            await interaction.response.send_message("This command must be used in a server.", ephemeral=True)
            return
        me = interaction.guild.me
        perms = me.guild_permissions if me else None
        if not perms:
            await interaction.response.send_message("I couldn't inspect my guild permissions.", ephemeral=True)
            return
        important = ["administrator", "manage_guild", "manage_channels", "manage_roles", "manage_webhooks", "send_messages", "embed_links", "attach_files"]
        text = "\n".join(f"• `{p}`: {'✅' if getattr(perms, p) else '❌'}" for p in important)
        await interaction.response.send_message(embed=discord.Embed(title="🔐 Forge Permissions", description=text, color=0x42E8F4))

    @app_commands.command(name="security-audit", description="Run a lightweight security checklist for this server.")
    async def security_audit(self, interaction):
        if not interaction.guild:
            await interaction.response.send_message("This command must be used in a server.", ephemeral=True)
            return
        checks = [
            ("Community ownership", interaction.guild.owner is not None),
            ("2FA requirement", interaction.guild.mfa_level.value == 1),
            ("Bot can view channels", interaction.guild.me is not None),
        ]
        text = "\n".join(f"{'✅' if ok else '⚠️'} {name}" for name, ok in checks)
        text += "\n\n⚠️ This is a lightweight checklist, not a complete security audit."
        await interaction.response.send_message(embed=discord.Embed(title="🛡️ Forge Security Audit", description=text, color=0x168CFF))

    @app_commands.command(name="health", description="Check Forge health and runtime state.")
    async def health(self, interaction):
        guilds = len(self.bot.guilds)
        latency = round(self.bot.latency * 1000)
        e = discord.Embed(title="💚 Forge Health", color=0x42E8F4)
        e.add_field(name="Status", value="Online", inline=True)
        e.add_field(name="Latency", value=f"{latency} ms", inline=True)
        e.add_field(name="Servers", value=str(guilds), inline=True)
        e.add_field(name="UTC", value=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"), inline=False)
        await interaction.response.send_message(embed=e)

    @app_commands.command(name="logs", description="Show a basic runtime diagnostic summary.")
    async def logs(self, interaction):
        if not await self._owner(interaction): return
        await interaction.response.send_message(f"📋 Runtime diagnostic: `{len(self.bot.guilds)} guilds`, `{round(self.bot.latency * 1000)}ms` latency, process online.", ephemeral=True)

    @app_commands.command(name="bot-create", description="Create a downloadable starter Discord bot project.")
    @app_commands.describe(name="Bot project name", language="Python or JavaScript", features="Comma-separated features")
    async def bot_create(self, interaction, name: str, language: str = "Python", features: str = "slash commands"):
        py = language.lower() in ("python", "py")
        files = {
            "README.md": f"# {name}\n\nStarter generated by ESN Forge.\n\nFeatures: {features}\n",
            ".env.example": "DISCORD_TOKEN=replace_me\n",
        }
        if py:
            files["bot.py"] = "import os\nimport discord\nfrom discord.ext import commands\n\nTOKEN = os.getenv('DISCORD_TOKEN')\nbot = commands.Bot(command_prefix='!', intents=discord.Intents.default())\n\n@bot.event\nasync def on_ready():\n    print(f'Online as {bot.user}')\n\nbot.run(TOKEN)\n"
            files["requirements.txt"] = "discord.py>=2.5,<3\npython-dotenv>=1.0,<2\n"
        else:
            files["index.js"] = "const { Client, GatewayIntentBits } = require('discord.js');\nconst client = new Client({ intents: [GatewayIntentBits.Guilds] });\nclient.once('ready', () => console.log(`Online as ${client.user.tag}`));\nclient.login(process.env.DISCORD_TOKEN);\n"
            files["package.json"] = '{"private":true,"dependencies":{"discord.js":"^14.0.0"}}\n'
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
            for path, content in files.items(): z.writestr(path, content)
        buf.seek(0)
        await interaction.response.send_message(f"🤖 **{name}** starter created with features: {clip(features, 500)}", file=discord.File(buf, filename=f"{name.lower().replace(' ', '-')}-forge.zip"))

    @app_commands.command(name="bot-command", description="Generate a Discord bot command template.")
    @app_commands.describe(name="Command name", language="Python or JavaScript")
    async def bot_command(self, interaction, name: str, language: str = "Python"):
        if language.lower() in ("python", "py"):
            out = f"@bot.tree.command(name=\"{name}\")\nasync def {name.replace('-', '_')}(interaction: discord.Interaction):\n    await interaction.response.send_message(\"Hello from /{name}!\")"
            lang = "python"
        else:
            out = f"const {{ SlashCommandBuilder }} = require('discord.js');\nmodule.exports = {{ data: new SlashCommandBuilder().setName('{name}').setDescription('Forge command'), async execute(interaction) {{ await interaction.reply('Hello from /{name}!'); }} }};"
            lang = "js"
        await interaction.response.send_message(code_block(out, lang))

    @app_commands.command(name="bot-event", description="Generate a Discord bot event template.")
    @app_commands.describe(event="ready, message, member join, etc.", language="Python or JavaScript")
    async def bot_event(self, interaction, event: str, language: str = "Python"):
        if language.lower() in ("python", "py"):
            out = f"@bot.event\nasync def on_{event.replace(' ', '_')}(*args):\n    # TODO: implement {event}\n    pass"
            lang = "python"
        else:
            out = f"client.on('{event}', async (...args) => {{\n  // TODO: implement {event}\n}});"
            lang = "js"
        await interaction.response.send_message(code_block(out, lang))

    @app_commands.command(name="bot-feature", description="Create an implementation plan for a bot feature.")
    @app_commands.describe(feature="Feature you want to add")
    async def bot_feature(self, interaction, feature: str):
        await interaction.response.send_message(embed=discord.Embed(title="🤖 Bot Feature Forge", description=f"**Feature:** {feature}\n\n1. Define behavior\n2. Choose command/events\n3. Add permissions\n4. Add storage if needed\n5. Implement error handling\n6. Test in a development server\n7. Deploy with secrets protected.", color=0x6366F1))

    @app_commands.command(name="bot-structure", description="Generate a recommended Discord bot project structure.")
    async def bot_structure(self, interaction):
        await interaction.response.send_message(code_block("bot.py\ncogs/\n  commands.py\n  events.py\n  moderation.py\nutils/\n  database.py\n  permissions.py\n.env.example\nrequirements.txt\nREADME.md", "text"))

    @app_commands.command(name="bot-config", description="Show secure Discord bot configuration guidance.")
    async def bot_config(self, interaction):
        await interaction.response.send_message("⚙️ Store `DISCORD_TOKEN` and API keys in environment variables or your host's secret manager. Never commit `.env` or tokens to GitHub.")

    @app_commands.command(name="bot-export", description="Generate a bot project ZIP from basic settings.")
    async def bot_export(self, interaction):
        await self.bot_create(interaction, "ForgeBot", "Python", "slash commands, configuration, secure environment variables")

    @app_commands.command(name="embed-json", description="Generate JSON-like embed configuration.")
    @app_commands.describe(title="Embed title", description="Embed description", footer="Footer text")
    async def embed_json(self, interaction, title: str, description: str, footer: str = ""):
        data = {"title": title, "description": description}
        if footer: data["footer"] = {"text": footer}
        await interaction.response.send_message(code_block(json.dumps(data, indent=2), "json"))

    @app_commands.command(name="embed-code", description="Generate a Python Discord embed template.")
    @app_commands.describe(title="Embed title", description="Embed description")
    async def embed_code(self, interaction, title: str, description: str):
        out = f"embed = discord.Embed(title={title!r}, description={description!r}, color=0x42E8F4)\nawait interaction.response.send_message(embed=embed)"
        await interaction.response.send_message(code_block(out, "python"))

    @app_commands.command(name="embed-template", description="Create a reusable embed template.")
    @app_commands.describe(kind="announcement, rules, welcome, update")
    async def embed_template(self, interaction, kind: str):
        templates = {"announcement": ("📢 Announcement", "Important update goes here."), "rules": ("📜 Rules", "Please follow the server rules."), "welcome": ("👋 Welcome", "Welcome to the community!"), "update": ("🔔 Update", "A new update is now available.")}
        title, desc = templates.get(kind.lower(), ("📌 Template", "Your content here."))
        await interaction.response.send_message(embed=discord.Embed(title=title, description=desc, color=0x42E8F4))

    @app_commands.command(name="server-plan", description="Plan a Discord server architecture.")
    @app_commands.describe(theme="Server theme", size="small, medium, or large")
    async def server_plan(self, interaction, theme: str, size: str = "medium"):
        channels = ["📌 START HERE", "📢 announcements", "📜 rules", "💬 general", "🎮 gaming", "🛠 support", "🔒 staff"]
        roles = ["Owner", "Administrator", "Moderator", "Staff", "Member", "Bot"]
        await interaction.response.send_message(embed=discord.Embed(title=f"🏗️ Server Plan — {theme}", description=f"Size: **{size}**\n\n**Channels**\n" + "\n".join(f"• {x}" for x in channels) + "\n\n**Roles**\n" + " → ".join(roles), color=0x6366F1))

    @app_commands.command(name="server-roles", description="Generate a server role hierarchy.")
    async def server_roles(self, interaction):
        await interaction.response.send_message("👑 Owner\n🛡 Administrator\n🔨 Moderator\n🧰 Staff\n⭐ VIP/Creator\n👤 Member\n🤖 Bots")

    @app_commands.command(name="server-channels", description="Generate a server channel structure.")
    async def server_channels(self, interaction):
        await interaction.response.send_message(code_block("START HERE\n├─ announcements\n├─ rules\n└─ faq\n\nCOMMUNITY\n├─ general\n├─ media\n├─ gaming\n└─ suggestions\n\nSUPPORT\n├─ help\n└─ tickets\n\nSTAFF\n├─ staff-chat\n├─ logs\n└─ applications"))

    @app_commands.command(name="server-permissions", description="Give a safe permission design checklist.")
    async def server_permissions(self, interaction):
        await interaction.response.send_message("🔐 Permission design:\n• Keep Administrator limited to trusted owners\n• Give Moderators only the actions they need\n• Deny @everyone access to staff channels\n• Keep bot permissions minimal\n• Review role hierarchy before enabling moderation actions")

    @app_commands.command(name="server-rules", description="Generate a server rules template.")
    async def server_rules(self, interaction):
        await interaction.response.send_message(code_block("1. Respect everyone.\n2. No harassment or threats.\n3. No spam or malicious links.\n4. Keep content in the correct channels.\n5. Follow Discord's Terms and Community Guidelines.\n6. Staff decisions should be handled respectfully.\n7. Report issues through the designated support channel.", "md"))

    @app_commands.command(name="server-audit", description="Audit basic server structure and configuration.")
    async def server_audit(self, interaction):
        if not interaction.guild:
            await interaction.response.send_message("Use this command in a server.", ephemeral=True); return
        g = interaction.guild
        e = discord.Embed(title="🔍 Server Audit", color=0x168CFF)
        e.add_field(name="Members", value=str(g.member_count), inline=True)
        e.add_field(name="Channels", value=str(len(g.channels)), inline=True)
        e.add_field(name="Roles", value=str(len(g.roles)), inline=True)
        e.add_field(name="Owner", value=str(g.owner) if g.owner else "Unknown", inline=False)
        e.add_field(name="Security", value="Review administrator roles, bot permissions, verification, and private staff channels.", inline=False)
        await interaction.response.send_message(embed=e)

    @app_commands.command(name="server-setup", description="Preview a server setup before making changes.")
    async def server_setup(self, interaction):
        await interaction.response.send_message("⚠️ **Dry-run only:** Forge will preview channel/role changes before any creation. No destructive changes are performed by this command. Future deployment actions will require explicit confirmation and appropriate permissions.", ephemeral=True)

    @app_commands.command(name="stats", description="Show Forge usage statistics.")
    async def stats(self, interaction):
        await interaction.response.send_message(f"📊 **ESN Forge Stats**\nServers: `{len(self.bot.guilds)}`\nLatency: `{round(self.bot.latency * 1000)}ms`\nCommands: `{len(self.bot.tree.get_commands())}`", ephemeral=True)

    @app_commands.command(name="owner-status", description="Owner runtime status.")
    async def owner_status(self, interaction):
        if not await self._owner(interaction): return
        await interaction.response.send_message(f"👑 Owner status: online | guilds: {len(self.bot.guilds)} | latency: {round(self.bot.latency * 1000)}ms", ephemeral=True)

    @app_commands.command(name="owner-guilds", description="List servers Forge is connected to.")
    async def owner_guilds(self, interaction):
        if not await self._owner(interaction): return
        text = "\n".join(f"• {g.name} (`{g.id}`)" for g in self.bot.guilds) or "No guilds."
        await interaction.response.send_message(clip(text, 1900), ephemeral=True)

    @app_commands.command(name="owner-broadcast", description="Broadcast a message to all configured guild channels is not enabled yet.")
    async def owner_broadcast(self, interaction):
        if not await self._owner(interaction): return
        await interaction.response.send_message("📡 Broadcast is intentionally disabled until a safe destination/configuration system is implemented.", ephemeral=True)

    @app_commands.command(name="owner-maintenance", description="Show maintenance controls.")
    async def owner_maintenance(self, interaction):
        if not await self._owner(interaction): return
        await interaction.response.send_message("🛠 Maintenance controls are available to the configured owner IDs. Restart/reload actions should be handled by the hosting platform.", ephemeral=True)

    @app_commands.command(name="owner-shutdown", description="Show shutdown guidance without stopping the bot accidentally.")
    async def owner_shutdown(self, interaction):
        if not await self._owner(interaction): return
        await interaction.response.send_message("⚠️ Forge does not shut itself down from a chat command. Stop/restart it from your hosting platform to avoid accidental outages.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Tools(bot))
