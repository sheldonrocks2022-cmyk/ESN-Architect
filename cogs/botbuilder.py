import discord
from discord import app_commands
from discord.ext import commands

class BotBuilder(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @app_commands.command(name="bot", description="Generate a Discord bot starter specification.")
    @app_commands.describe(name="Bot name", language="Python or JavaScript", features="Comma-separated features")
    async def bot_builder(self, interaction: discord.Interaction, name: str, language: str = "Python", features: str = "slash commands, embeds, logging"):
        language = language.strip().lower()
        runtime = "discord.py" if language.startswith("py") else "discord.js" if language.startswith("js") else "Choose discord.py or discord.js"
        feature_list = [x.strip() for x in features.split(",") if x.strip()][:12]
        e = discord.Embed(title=f"🤖 {name[:80]}", description=f"**Framework:** {runtime}", color=0x6366F1)
        e.add_field(name="Features", value="\n".join(f"• {x}" for x in feature_list) or "• Core bot", inline=False)
        e.add_field(name="Starter structure", value="```text\napp/\n├── cogs/\n├── utils/\n├── data/\n├── .env.example\n├── requirements.txt\n└── bot.py\n```", inline=False)
        e.add_field(name="Security", value="Keep tokens/API keys in environment variables. Never hard-code or share secrets.", inline=False)
        await interaction.response.send_message(embed=e)

async def setup(bot): await bot.add_cog(BotBuilder(bot))
