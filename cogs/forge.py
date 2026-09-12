import discord
from discord import app_commands
from discord.ext import commands


class Forge(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="forge", description="Open the ESN Forge developer toolkit.")
    async def forge(self, interaction: discord.Interaction):
        e = discord.Embed(title="⚒️ ESN Forge", description="**Build. Create. Deploy.**\nA practical developer toolkit for Discord and coding projects.", color=0x42E8F4)
        e.add_field(name="💻 AI Development", value="`/ask` · `/ai-generate` · `/ai-debug` · `/ai-fix` · `/ai-explain`\n`/ai-improve` · `/ai-review` · `/ai-test` · `/ai-convert`", inline=False)
        e.add_field(name="🧩 Builders", value="`/bot` — download a bot starter\n`/embed` — build/export embeds\n`/embed-json` — preview JSON\n`/server` — generate a server blueprint\n`/server-deploy` — safely deploy a template", inline=False)
        e.add_field(name="🛠️ Developer Tools", value="`/json` · `/regex` · `/timestamp` · `/color` · `/base64` · `/uuid` · `/hash`\n`/permissions` · `/security-audit` · `/health` · `/logs`", inline=False)
        e.add_field(name="📦 Project Workflow", value="Plan → Generate → Inspect → Test → Configure secrets → Deploy", inline=False)
        e.set_footer(text="ESN Forge • Build. Create. Deploy.")
        await interaction.response.send_message(embed=e)

    @app_commands.command(name="forge-status", description="Show the current ESN Forge runtime status.")
    async def forge_status(self, interaction: discord.Interaction):
        latency = round(self.bot.latency * 1000) if self.bot.latency != float("inf") else 0
        guilds = len(self.bot.guilds)
        commands_count = len(self.bot.tree.get_commands())
        embed = discord.Embed(title="⚒️ Forge Status", color=0x42E8F4)
        embed.add_field(name="Bot", value="Online", inline=True)
        embed.add_field(name="Latency", value=f"{latency}ms", inline=True)
        embed.add_field(name="Servers", value=str(guilds), inline=True)
        embed.add_field(name="Loaded commands", value=str(commands_count), inline=True)
        embed.add_field(name="Database", value="SQLite", inline=True)
        embed.add_field(name="AI", value="Configured" if getattr(self.bot, "ai_available", False) else "Configuration dependent", inline=True)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="project", description="Create a practical project plan from a goal.")
    @app_commands.describe(name="Project name", kind="What are you building?", requirements="Key requirements, comma-separated")
    async def project(self, interaction: discord.Interaction, name: str, kind: str, requirements: str = ""):
        reqs = [x.strip() for x in requirements.split(",") if x.strip()][:12]
        plan = [
            "1. Define requirements and acceptance criteria",
            "2. Create the project structure and configuration",
            "3. Implement the core functionality",
            "4. Add validation, permissions, and error handling",
            "5. Add automated tests",
            "6. Configure environment variables and deployment",
            "7. Run a production readiness check",
        ]
        embed = discord.Embed(title=f"🚀 {name[:80]}", description=f"**Type:** {kind[:200]}", color=0x168CFF)
        embed.add_field(name="Requirements", value="\n".join(f"• {x}" for x in reqs)[:1800] or "• No extra requirements supplied", inline=False)
        embed.add_field(name="Execution Plan", value="\n".join(plan), inline=False)
        embed.set_footer(text="Use the AI project commands when you want Forge to generate the actual files.")
        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Forge(bot))
