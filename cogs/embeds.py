import discord
from discord import app_commands
from discord.ext import commands

class Embeds(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @app_commands.command(name="embed", description="Generate a clean Discord embed from your content.")
    @app_commands.describe(title="Embed title", description="Embed body", footer="Optional footer")
    async def embed(self, interaction: discord.Interaction, title: str, description: str, footer: str = ""):
        e = discord.Embed(title=title[:256], description=description[:4096], color=0x42E8F4)
        if footer: e.set_footer(text=footer[:2048])
        await interaction.response.send_message(embed=e)

async def setup(bot): await bot.add_cog(Embeds(bot))
