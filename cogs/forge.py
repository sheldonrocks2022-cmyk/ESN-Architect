import discord
from discord import app_commands
from discord.ext import commands

class Forge(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @app_commands.command(name="forge", description="Open the ESN Forge developer toolkit.")
    async def forge(self, interaction: discord.Interaction):
        e = discord.Embed(title="⚒️ ESN Forge", description="Build. Create. Deploy.", color=0x42E8F4)
        e.add_field(name="💻 Code", value="`/code` generate or explain code\n`/debug` diagnose an error", inline=True)
        e.add_field(name="🧩 Discord", value="`/embed` design an embed\n`/server` plan a server", inline=True)
        e.add_field(name="🚀 Projects", value="`/project` generate a project blueprint\n`/help` see everything", inline=True)
        e.set_footer(text="ESN Forge • Powered by ESN")
        await interaction.response.send_message(embed=e)

    @app_commands.command(name="project", description="Generate a starter project blueprint.")
    @app_commands.describe(name="Project name", kind="What are you building?")
    async def project(self, interaction: discord.Interaction, name: str, kind: str):
        safe = name.strip()[:80]
        e = discord.Embed(title=f"🚀 {safe}", description=f"**Type:** {kind}", color=0x168CFF)
        e.add_field(name="Recommended structure", value="```text\nproject/\n├── src/\n├── tests/\n├── .env.example\n├── README.md\n└── requirements.txt / package.json\n```", inline=False)
        e.add_field(name="Forge workflow", value="1. Define requirements\n2. Build the core\n3. Test\n4. Configure secrets\n5. Deploy", inline=False)
        await interaction.response.send_message(embed=e)

async def setup(bot): await bot.add_cog(Forge(bot))
