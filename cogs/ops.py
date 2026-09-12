import io
import os
import sqlite3
import discord
from discord import app_commands
from discord.ext import commands


class Operations(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def owner_ids(self) -> set[int]:
        return {int(x.strip()) for x in os.getenv("OWNER_IDS", "").split(",") if x.strip().isdigit()}

    async def owner_only(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id not in self.owner_ids():
            await interaction.response.send_message("⛔ Owner-only command.", ephemeral=True)
            return False
        return True

    @app_commands.command(name="deploy-check", description="Run a production readiness check on Forge.")
    async def deploy_check(self, interaction: discord.Interaction):
        checks = []
        checks.append(("DISCORD_TOKEN configured", bool(os.getenv("DISCORD_TOKEN"))))
        checks.append(("OWNER_IDS configured", bool(self.owner_ids())))
        checks.append(("OpenAI configured", bool(os.getenv("OPENAI_API_KEY"))))
        checks.append(("SQLite database", getattr(self.bot, "db", None) is not None))
        if interaction.guild and interaction.guild.me:
            p = interaction.guild.me.guild_permissions
            checks.extend([
                ("View channels", p.view_channel),
                ("Send messages", p.send_messages),
                ("Embed links", p.embed_links),
                ("Manage channels", p.manage_channels),
                ("Manage roles", p.manage_roles),
            ])
        text = "\n".join(f"{'✅' if ok else '❌'} {name}" for name, ok in checks)
        passed = sum(ok for _, ok in checks)
        embed = discord.Embed(title="🚀 Forge Deployment Check", description=text, color=0x42E8F4 if passed == len(checks) else 0xFFB020)
        embed.set_footer(text=f"{passed}/{len(checks)} checks passed • Missing OpenAI only affects AI features.")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="invite", description="Generate a permission-scoped Discord bot invite URL.")
    @app_commands.describe(permissions="Discord permission integer; defaults to basic bot permissions")
    async def invite(self, interaction: discord.Interaction, permissions: int = 2147601408):
        if not self.bot.user:
            await interaction.response.send_message("❌ Bot identity is not ready yet.", ephemeral=True)
            return
        if permissions < 0 or permissions > 2**53 - 1:
            await interaction.response.send_message("❌ Invalid permissions integer.", ephemeral=True)
            return
        url = discord.utils.oauth_url(self.bot.user.id, permissions=discord.Permissions(permissions), scopes=("bot", "applications.commands"))
        await interaction.response.send_message(f"🔗 **Forge Invite**\n{url}\n\nOnly grant permissions the bot actually needs.", ephemeral=True)

    @app_commands.command(name="backup-db", description="Create a private SQLite database backup for the bot owner.")
    async def backup_db(self, interaction: discord.Interaction):
        if not await self.owner_only(interaction):
            return
        db = getattr(self.bot, "db", None)
        path = getattr(db, "path", "data/forge.db") if db else "data/forge.db"
        if not os.path.exists(path):
            await interaction.response.send_message("❌ Database file does not exist yet.", ephemeral=True)
            return
        await interaction.response.defer(ephemeral=True)
        source = sqlite3.connect(path)
        memory = sqlite3.connect(":memory:")
        try:
            source.backup(memory)
            buffer = io.BytesIO()
            for line in memory.iterdump():
                buffer.write((line + "\n").encode())
            buffer.seek(0)
            await interaction.followup.send(file=discord.File(buffer, filename="forge-database-backup.sql"), ephemeral=True)
        finally:
            memory.close()
            source.close()

    @app_commands.command(name="shutdown", description="Safely shut down Forge (owner only).")
    async def shutdown(self, interaction: discord.Interaction):
        if not await self.owner_only(interaction):
            return
        await interaction.response.send_message("🛑 ESN Forge is shutting down now.", ephemeral=True)
        await self.bot.close()


async def setup(bot):
    await bot.add_cog(Operations(bot))
