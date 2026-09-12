import discord
from discord import app_commands
from discord.ext import commands

LANGS = "Python, JavaScript, TypeScript, HTML/CSS/JS, discord.py, discord.js"

class Code(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @app_commands.command(name="code", description="Get a coding starter, explanation, or implementation plan.")
    @app_commands.describe(request="Describe what you want to build")
    async def code(self, interaction: discord.Interaction, request: str):
        e = discord.Embed(title="💻 Forge Code", description=f"**Request:** {request[:1500]}", color=0x6366F1)
        e.add_field(name="Supported", value=LANGS, inline=False)
        e.add_field(name="Forge approach", value="Break the request into components → choose the runtime → implement → test → secure configuration → deploy.", inline=False)
        e.add_field(name="Tip", value="For AI-generated code, add your preferred language, version, inputs/outputs, and any existing error or code snippet.", inline=False)
        await interaction.response.send_message(embed=e)

    @app_commands.command(name="debug", description="Analyze an error message and suggest a fix path.")
    @app_commands.describe(error="Paste the error or describe the failure")
    async def debug(self, interaction: discord.Interaction, error: str):
        text = error.strip()[:1800]
        hints = []
        low = text.lower()
        if "module" in low and "not found" in low: hints.append("Check that the dependency is installed in the active environment.")
        if "permission" in low or "forbidden" in low: hints.append("Check the bot/user permissions and Discord intent requirements.")
        if "token" in low or "unauthorized" in low: hints.append("Check the secret/configuration without posting the token publicly.")
        if not hints: hints.append("Identify the first meaningful exception, reproduce it with minimal input, then inspect the traceback line that caused it.")
        e = discord.Embed(title="🛠️ Forge Debug", description=f"```text\n{text}\n```", color=0xFFB020)
        e.add_field(name="Likely next steps", value="\n".join(f"• {h}" for h in hints), inline=False)
        e.set_footer(text="Never paste passwords, bot tokens, API keys, or other secrets into Discord.")
        await interaction.response.send_message(embed=e)

async def setup(bot): await bot.add_cog(Code(bot))
