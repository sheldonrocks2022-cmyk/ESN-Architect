import os
import logging
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
PREFIX = os.getenv("PREFIX", "!")

if not TOKEN:
    raise RuntimeError("DISCORD_TOKEN is not configured. Add it to your environment.")

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(name)s | %(message)s")

intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.message_content = True

class ESNForge(commands.Bot):
    async def setup_hook(self):
        await self.load_extension("cogs.forge")
        await self.load_extension("cogs.embeds")
        await self.load_extension("cogs.server")
        await self.load_extension("cogs.code")
        await self.load_extension("cogs.help")
        try:
            synced = await self.tree.sync()
            logging.info("Synced %s application commands", len(synced))
        except Exception:
            logging.exception("Failed to sync application commands")

    async def on_ready(self):
        logging.info("ESN Forge online as %s (%s)", self.user, self.user.id)
        await self.change_presence(activity=discord.Game(name="Building with ESN Forge"))

bot = ESNForge(command_prefix=PREFIX, intents=intents, help_command=None)
bot.run(TOKEN)
