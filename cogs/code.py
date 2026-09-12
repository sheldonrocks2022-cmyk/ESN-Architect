import discord
from discord import app_commands
from discord.ext import commands

class Code(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="code", description="Get a concise coding guidance starter.")
    @app_commands.describe(request="Describe what you want to build or fix")
    async def code(self, interaction: discord.Interaction, request: str):
        embed = discord.Embed(title="⚒️ Code Forge", color=0x6366F1)
        embed.description = f"**Request**\n{request[:3500]}"
        embed.add_field(name="Forge workflow", value="1. Identify the goal\n2. Choose the language/framework\n3. Build the smallest working version\n4. Test it\n5. Improve it")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="debug", description="Analyze an error message and suggest a debugging path.")
    @app_commands.describe(error="Paste the error and relevant context")
    async def debug(self, interaction: discord.Interaction, error: str):
        embed = discord.Embed(title="🧰 Debug Forge", color=0x168CFF)
        embed.description = f"**Error received**\n```\n{error[:3800]}\n```"
        embed.add_field(name="First checks", value="Check the traceback location, confirm imports/dependencies, verify configuration/environment variables, then reproduce the smallest failing case.")
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Code(bot))
