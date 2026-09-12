import discord
from discord import app_commands
from discord.ext import commands

class Help(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @app_commands.command(name="help", description="Show all ESN Forge tools.")
    async def help(self, interaction: discord.Interaction):
        e = discord.Embed(title="⚒️ ESN Forge Help", description="A developer toolkit for creators and communities.", color=0x42E8F4)
        e.add_field(name="Build", value="`/forge` — toolkit home\n`/project` — project blueprint\n`/server` — server architecture", inline=False)
        e.add_field(name="AI", value="`/ask` — AI developer assistant\n`/ai-generate` — generate implementation\n`/ai-debug` — diagnose and fix\n`/ai-project` — generate a multi-file ZIP\n`/ai-status` — AI configuration", inline=False)
        e.add_field(name="Code", value="`/code` — coding workflow\n`/debug` — troubleshoot errors\n`/generate` — starter implementation\n`/review` — quick code review", inline=False)
        e.add_field(name="Discord", value="`/embed` — create an embed\n`/bot-create` — downloadable bot starter\n`/server-setup` — safe server setup preview", inline=False)
        e.set_footer(text="ESN Forge • Build. Create. Deploy.")
        await interaction.response.send_message(embed=e)

async def setup(bot): await bot.add_cog(Help(bot))
