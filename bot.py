import logging
import os
from pathlib import Path

import discord
from discord.ext import commands
from dotenv import load_dotenv

from utils.database import Database

ROOT = Path(__file__).resolve().parent
ENV_FILE = ROOT / ".env"
DATA_DIR = ROOT / "data"


def ensure_local_environment() -> None:
    """Create a safe local .env template when one does not exist.

    The file contains no secrets and is intended to be filled in locally.
    It is never committed by Forge itself.
    """
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not ENV_FILE.exists():
        ENV_FILE.write_text(
            "# ESN Forge local configuration\n"
            "# Add your real values here. DO NOT COMMIT THIS FILE.\n\n"
            "DISCORD_TOKEN=\n"
            "OWNER_IDS=\n"
            "OPENAI_API_KEY=\n"
            "OPENAI_MODEL=gpt-5.6-luna\n",
            encoding="utf-8",
        )
        print(f"Created {ENV_FILE}. Add your credentials, then start Forge again.")


ensure_local_environment()
load_dotenv(ENV_FILE)
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(name)s | %(message)s")
log = logging.getLogger("esn-forge")
TOKEN = os.getenv("DISCORD_TOKEN", "").strip()
if not TOKEN:
    raise RuntimeError(
        "DISCORD_TOKEN is missing. Forge created .env for you; open it, add your token, and run the bot again."
    )

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True


class ESNForge(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents, help_command=None)
        self.db = Database(str(DATA_DIR / "forge.db"))

    async def setup_hook(self):
        extensions = (
            "cogs.forge", "cogs.code", "cogs.embeds", "cogs.server",
            "cogs.botbuilder", "cogs.config", "cogs.help", "cogs.tools", "cogs.ai",
            "cogs.ops",
        )
        for extension in extensions:
            try:
                await self.load_extension(extension)
                log.info("Loaded %s", extension)
            except Exception:
                log.exception("Failed loading extension %s", extension)
                raise
        synced = await self.tree.sync()
        log.info("ESN Forge synced %s slash commands", len(synced))

    async def on_ready(self):
        log.info("ESN Forge online as %s (%s) in %s guilds", self.user, self.user.id, len(self.guilds))
        await self.change_presence(activity=discord.Game(name="/forge • Build. Create. Deploy."))

    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            return
        log.error("Prefix command error", exc_info=error)

    async def on_app_command_error(self, interaction: discord.Interaction, error: discord.app_commands.AppCommandError):
        log.error("Slash command error: %s", error, exc_info=error)
        message = "❌ Something went wrong while running that command. The error has been logged for the Forge owner."
        try:
            if interaction.response.is_done():
                await interaction.followup.send(message, ephemeral=True)
            else:
                await interaction.response.send_message(message, ephemeral=True)
        except discord.HTTPException:
            log.exception("Could not send slash-command error response")


bot = ESNForge()
bot.run(TOKEN)
