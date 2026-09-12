import os
import logging
import discord
from discord.ext import commands
from dotenv import load_dotenv
from utils.database import Database

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    raise RuntimeError("DISCORD_TOKEN is missing. Put it in .env when you are ready to run Forge.")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

class ESNForge(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents, help_command=None)
        self.db = Database("data/forge.db")

    async def setup_hook(self):
        extensions = ("cogs.forge", "cogs.code", "cogs.embeds", "cogs.server", "cogs.botbuilder", "cogs.config", "cogs.help")
        for extension in extensions:
            await self.load_extension(extension)
        synced = await self.tree.sync()
        logging.info("ESN Forge synced %s slash commands", len(synced))

    async def on_ready(self):
        logging.info("ESN Forge online as %s (%s)", self.user, self.user.id)
        await self.change_presence(activity=discord.Game(name="/forge • Build. Create. Deploy."))

bot = ESNForge()
bot.run(TOKEN)
