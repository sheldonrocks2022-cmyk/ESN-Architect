import discord
from discord import app_commands
from discord.ext import commands

class Server(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @app_commands.command(name="server", description="Generate a Discord server structure plan.")
    @app_commands.describe(theme="Server purpose/theme", size="Small, medium, or large")
    async def server(self, interaction: discord.Interaction, theme: str, size: str = "medium"):
        size = size.lower().strip()
        scale = {"small": "3–5", "medium": "6–10", "large": "10+"}.get(size, "6–10")
        e = discord.Embed(title="🏗️ Server Forge", description=f"**Theme:** {theme}\n**Recommended category count:** {scale}", color=0x168CFF)
        e.add_field(name="📌 START HERE", value="# welcome\n# rules\n# announcements\n# information", inline=True)
        e.add_field(name="💬 COMMUNITY", value="# general\n# media\n# suggestions\n# support", inline=True)
        e.add_field(name="🔒 STAFF", value="# staff-chat\n# reports\n# logs\n# mod-tools", inline=True)
        e.add_field(name="Roles", value="Owner → Administrator → Management → Moderator → Staff → Member → Bots", inline=False)
        e.set_footer(text="Review permissions before deploying. Give bots only the permissions they actually need.")
        await interaction.response.send_message(embed=e)

async def setup(bot): await bot.add_cog(Server(bot))
