import discord
from discord import app_commands
from discord.ext import commands

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="help", description="Show ESN Forge commands.")
    async def help(self, interaction: discord.Interaction):
        e = discord.Embed(title="⚒️ ESN Forge Help", description="Build. Create. Deploy.", color=0x42E8F4)
        e.add_field(name="Developer Tools", value="`/code` — coding guidance\n`/debug` — troubleshoot errors\n`/project` — project planning", inline=False)
        e.add_field(name="Discord Tools", value="`/embed` — embed builder\n`/server` — server layout generator\n`/forge` — main toolkit", inline=False)
        e.set_footer(text="ESN Network • ESN Forge")
        await interaction.response.send_message(embed=e)

async def setup(bot):
    await bot.add_cog(Help(bot))
