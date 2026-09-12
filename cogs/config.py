import os
import discord
from discord import app_commands
from discord.ext import commands

OWNER_IDS = {int(x) for x in os.getenv("OWNER_IDS", "").split(",") if x.strip().isdigit()}

class Config(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @app_commands.command(name="config", description="Configure Forge for this server.")
    @app_commands.describe(setting="prefix, log_channel, or welcome_channel", value="Value; use 0 to clear channel IDs")
    @app_commands.default_permissions(manage_guild=True)
    async def config(self, interaction: discord.Interaction, setting: str, value: str):
        if not interaction.guild:
            return await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
        setting = setting.lower().strip()
        if setting not in {"prefix", "log_channel", "welcome_channel"}:
            return await interaction.response.send_message("Valid settings: `prefix`, `log_channel`, `welcome_channel`.", ephemeral=True)
        if setting == "prefix":
            if len(value) > 5: return await interaction.response.send_message("Prefix must be 5 characters or fewer.", ephemeral=True)
            parsed = value
        else:
            try: parsed = int(value)
            except ValueError: return await interaction.response.send_message("Channel settings require a numeric channel ID, or `0` to clear.", ephemeral=True)
            if parsed == 0: parsed = None
        self.bot.db.set_config(interaction.guild.id, **{setting: parsed})
        await interaction.response.send_message(f"✅ `{setting}` updated.", ephemeral=True)

    @app_commands.command(name="owner", description="Check whether your account is configured as a Forge owner.")
    async def owner(self, interaction: discord.Interaction):
        status = interaction.user.id in OWNER_IDS
        await interaction.response.send_message(f"Owner access: **{'enabled' if status else 'not configured'}**.", ephemeral=True)

async def setup(bot): await bot.add_cog(Config(bot))
