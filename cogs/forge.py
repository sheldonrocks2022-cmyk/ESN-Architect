import discord
from discord import app_commands
from discord.ext import commands

class Forge(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="forge", description="Open the ESN Forge developer toolkit.")
    async def forge(self, interaction: discord.Interaction):
        embed = discord.Embed(title="⚒️ ESN Forge", description="Build. Create. Deploy.", color=0x168CFF)
        embed.add_field(name="/code", value="Coding help and explanations", inline=True)
        embed.add_field(name="/debug", value="Troubleshoot an error", inline=True)
        embed.add_field(name="/project", value="Plan a project structure", inline=True)
        embed.add_field(name="/embed", value="Create an embed", inline=True)
        embed.add_field(name="/server", value="Design a Discord server", inline=True)
        embed.set_footer(text="ESN Forge • ESN Network")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="project", description="Generate a starter project plan.")
    @app_commands.describe(idea="What are you building?")
    async def project(self, interaction: discord.Interaction, idea: str):
        embed = discord.Embed(title="⚒️ Project Forge", color=0x42E8F4)
        embed.description = f"**Project:** {idea}\n\n**Suggested structure**\n`src/` — application code\n`config/` — safe configuration\n`tests/` — tests\n`README.md` — setup and usage\n`.env.example` — environment variables"
        embed.add_field(name="Next step", value="Use `/code` to build a specific component or `/debug` when something breaks.")
        await interaction.response.send_message(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(Forge(bot))
