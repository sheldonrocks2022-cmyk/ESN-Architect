import os

import discord
from discord import app_commands
from discord.ext import commands

OWNER_IDS = {int(x) for x in os.getenv("OWNER_IDS", "").split(",") if x.strip().isdigit()}


class Config(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="config", description="Configure Forge for this server.")
    @app_commands.describe(setting="prefix, log_channel, welcome_channel, ai_enabled, or ai_model", value="Setting value; use 0 to clear channel IDs")
    @app_commands.default_permissions(manage_guild=True)
    async def config(self, interaction: discord.Interaction, setting: str, value: str):
        if not interaction.guild:
            return await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
        setting = setting.lower().strip()
        if setting not in {"prefix", "log_channel", "welcome_channel", "ai_enabled", "ai_model"}:
            return await interaction.response.send_message("Valid settings: `prefix`, `log_channel`, `welcome_channel`, `ai_enabled`, `ai_model`.", ephemeral=True)
        if setting == "prefix":
            if len(value) > 5:
                return await interaction.response.send_message("Prefix must be 5 characters or fewer.", ephemeral=True)
            parsed = value
        elif setting in {"log_channel", "welcome_channel"}:
            try:
                parsed = int(value)
            except ValueError:
                return await interaction.response.send_message("Channel settings require a numeric channel ID, or `0` to clear.", ephemeral=True)
            if parsed == 0:
                parsed = None
        elif setting == "ai_enabled":
            parsed = value.lower() in {"1", "true", "yes", "on", "enabled"}
        else:
            if len(value) > 100:
                return await interaction.response.send_message("AI model name is too long.", ephemeral=True)
            parsed = value or None
        self.bot.db.set_config(interaction.guild.id, **{setting: parsed})
        await interaction.response.send_message(f"✅ `{setting}` updated.", ephemeral=True)

    @app_commands.command(name="config-show", description="Show the current Forge server configuration.")
    @app_commands.default_permissions(manage_guild=True)
    async def config_show(self, interaction: discord.Interaction):
        if not interaction.guild:
            return await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
        cfg = self.bot.db.get_config(interaction.guild.id)
        await interaction.response.send_message(
            "**ESN Forge Configuration**\n"
            f"Prefix: `{cfg['prefix']}`\n"
            f"Log channel: `{cfg['log_channel'] or 'not set'}`\n"
            f"Welcome channel: `{cfg['welcome_channel'] or 'not set'}`\n"
            f"AI enabled: `{'yes' if cfg.get('ai_enabled', True) else 'no'}`\n"
            f"AI model: `{cfg.get('ai_model') or os.getenv('OPENAI_MODEL', 'gpt-5.6-luna')}`",
            ephemeral=True,
        )

    @app_commands.command(name="owner", description="Check whether your account is configured as a Forge owner.")
    async def owner(self, interaction: discord.Interaction):
        status = interaction.user.id in OWNER_IDS
        await interaction.response.send_message(f"Owner access: **{'enabled' if status else 'not configured'}**.", ephemeral=True)


async def setup(bot):
    await bot.add_cog(Config(bot))
