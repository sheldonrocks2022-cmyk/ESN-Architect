import discord
from discord import app_commands
from discord.ext import commands

class Help(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @app_commands.command(name="help", description="Show all ESN Forge tools.")
    async def help(self, interaction: discord.Interaction):
        e = discord.Embed(title="⚒️ ESN Forge Help", description="A developer toolkit for creators and communities.", color=0x42E8F4)
        e.add_field(name="Build", value="`/forge` — toolkit home\n`/project` — project blueprint\n`/server` — server architecture", inline=False)
        e.add_field(name="Code", value="`/code` — coding workflow\n`/debug` — troubleshoot errors", inline=False)
        e.add_field(name="Discord", value="`/embed` — create an embed", inline=False)
        e.set_footer(text="ESN Forge • Build. Create. Deploy.")
        await interaction.response.send_message(embed=e)

async def setup(bot): await bot.add_cog(Help(bot))
