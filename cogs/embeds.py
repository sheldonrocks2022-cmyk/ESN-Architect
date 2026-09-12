import json
import discord
from discord import app_commands
from discord.ext import commands


class Embeds(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="embed", description="Build and preview a Discord embed with export data.")
    @app_commands.describe(title="Embed title", description="Embed body", footer="Optional footer", color="Hex color such as #42E8F4", url="Optional URL")
    async def embed(self, interaction: discord.Interaction, title: str, description: str, footer: str = "", color: str = "#42E8F4", url: str = ""):
        raw = color.strip().lstrip("#")
        try:
            value = int(raw, 16)
            if not 0 <= value <= 0xFFFFFF:
                raise ValueError
        except ValueError:
            await interaction.response.send_message("❌ Invalid color. Use a 6-digit hex value such as `#42E8F4`.", ephemeral=True)
            return
        embed = discord.Embed(title=title[:256], description=description[:4096], color=value, url=url[:2048] or discord.Embed.Empty)
        if footer:
            embed.set_footer(text=footer[:2048])
        payload = {
            "embeds": [{"title": title[:256], "description": description[:4096], "color": value, **({"url": url[:2048]} if url else {}), **({"footer": {"text": footer[:2048]}} if footer else {})}]
        }
        export = "```json\n" + json.dumps(payload, indent=2)[:3600] + "\n```"
        embed.add_field(name="📦 Export JSON", value=export, inline=False)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="embed-json", description="Create a preview from a Discord embed JSON payload.")
    @app_commands.describe(payload="Discord-compatible JSON containing an embeds array")
    async def embed_json(self, interaction: discord.Interaction, payload: str):
        try:
            data = json.loads(payload)
            item = (data.get("embeds") or [data])[0]
            if not isinstance(item, dict):
                raise ValueError
        except (json.JSONDecodeError, ValueError, AttributeError, TypeError, IndexError):
            await interaction.response.send_message("❌ Invalid JSON. Provide an object or an object containing an `embeds` array.", ephemeral=True)
            return
        embed = discord.Embed.from_dict(item)
        await interaction.response.send_message(content="**Embed preview**", embed=embed)


async def setup(bot):
    await bot.add_cog(Embeds(bot))
