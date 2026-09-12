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
        allowed = {"prefix", "log_channel", "welcome_channel", "ai_enabled", "ai_model"}
        if setting not in allowed:
            return await interaction.response.send_message("Valid settings: `prefix`, `log_channel`, `welcome_channel`, `ai_enabled`, `ai_model`.", ephemeral=True)
        if setting == "prefix":
            if not 1 <= len(value) <= 5:
                return await interaction.response.send_message("Prefix must be 1–5 characters.", ephemeral=True)
            parsed = value
        elif setting in {"log_channel", "welcome_channel"}:
            try:
                parsed = int(value)
            except ValueError:
                return await interaction.response.send_message("Channel settings require a numeric channel ID, or `0` to clear.", ephemeral=True)
            if parsed == 0:
                parsed = None
            elif interaction.guild.get_channel(parsed) is None:
                return await interaction.response.send_message("That channel ID is not in this server.", ephemeral=True)
        elif setting == "ai_enabled":
            normalized = value.lower().strip()
            if normalized not in {"on", "off", "true", "false", "1", "0", "yes", "no"}:
                return await interaction.response.send_message("Use `on` or `off` for AI.", ephemeral=True)
            parsed = normalized in {"on", "true", "1", "yes"}
        else:
            parsed = value.strip()
            if not 1 <= len(parsed) <= 100:
                return await interaction.response.send_message("AI model name must be 1–100 characters.", ephemeral=True)

        self.bot.db.set_config(interaction.guild.id, **{setting: parsed})
        await interaction.response.send_message(f"✅ `{setting}` updated.", ephemeral=True)

    @app_commands.command(name="config-show", description="Show the current Forge server configuration.")
    @app_commands.default_permissions(manage_guild=True)
    async def config_show(self, interaction: discord.Interaction):
        if not interaction.guild:
            return await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
        cfg = self.bot.db.get_config(interaction.guild.id)
        embed = discord.Embed(title="⚙️ ESN Forge Configuration", color=0x42E8F4)
        embed.add_field(name="Prefix", value=f"`{cfg['prefix']}`", inline=True)
        embed.add_field(name="AI", value="🟢 Enabled" if cfg.get("ai_enabled", True) else "🔴 Disabled", inline=True)
        embed.add_field(name="AI Model", value=f"`{cfg.get('ai_model') or os.getenv('OPENAI_MODEL', 'gpt-5.6-luna')}`", inline=True)
        embed.add_field(name="Log Channel", value=f"`{cfg['log_channel']}`" if cfg.get("log_channel") else "Not configured", inline=True)
        embed.add_field(name="Welcome Channel", value=f"`{cfg['welcome_channel']}`" if cfg.get("welcome_channel") else "Not configured", inline=True)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="owner", description="Check whether your account is configured as a Forge owner.")
    async def owner(self, interaction: discord.Interaction):
        status = interaction.user.id in OWNER_IDS
        await interaction.response.send_message(f"Owner access: **{'enabled' if status else 'not configured'}**.", ephemeral=True)


async def setup(bot):
    await bot.add_cog(Config(bot))
