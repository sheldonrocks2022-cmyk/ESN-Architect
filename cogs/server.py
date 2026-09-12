import discord
from discord import app_commands
from discord.ext import commands

class Server(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="server", description="Generate a Discord server layout plan.")
    @app_commands.describe(theme="The community theme or purpose")
    async def server(self, interaction: discord.Interaction, theme: str):
        embed = discord.Embed(title="⚒️ Server Forge", description=f"Layout for **{theme}**", color=0x168CFF)
        embed.add_field(name="📌 INFORMATION", value="welcome\nrules\nannouncements\nfaq", inline=True)
        embed.add_field(name="💬 COMMUNITY", value="general\nmedia\noff-topic\nsuggestions", inline=True)
        embed.add_field(name="🛠️ SUPPORT", value="help\ntickets\nfeedback", inline=True)
        embed.add_field(name="🔐 STAFF", value="staff-chat\nmod-logs\napplications", inline=True)
        embed.set_footer(text="ESN Forge • Review permissions before deploying")
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Server(bot))
