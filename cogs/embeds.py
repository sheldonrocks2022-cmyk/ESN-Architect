import discord
from discord import app_commands
from discord.ext import commands

class Embeds(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="embed", description="Build a clean Discord embed from a title and message.")
    @app_commands.describe(title="Embed title", message="Embed description")
    async def embed(self, interaction: discord.Interaction, title: str, message: str):
        e = discord.Embed(title=title[:256], description=message[:4096], color=0x42E8F4)
        e.set_footer(text=f"ESN Forge • Requested by {interaction.user.display_name}")
        await interaction.response.send_message(embed=e)

async def setup(bot):
    await bot.add_cog(Embeds(bot))
