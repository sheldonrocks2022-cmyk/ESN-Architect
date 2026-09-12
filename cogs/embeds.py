import json
import discord
from discord import app_commands
from discord.ext import commands
from utils.validation import parse_hex_color, valid_http_url


class Embeds(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="embed", description="Build and preview a Discord embed with export data.")
    @app_commands.describe(title="Embed title", description="Embed body", footer="Optional footer", color="6-digit hex", url="Optional http(s) URL", thumbnail="Optional image URL", image="Optional large image URL")
    async def embed(self, interaction: discord.Interaction, title: str, description: str, footer: str = "", color: str = "#42E8F4", url: str = "", thumbnail: str = "", image: str = ""):
        try:
            color_value = parse_hex_color(color)
            if not valid_http_url(url) or not valid_http_url(thumbnail) or not valid_http_url(image):
                raise ValueError("URLs must use http or https.")
        except ValueError as exc:
            await interaction.response.send_message(f"❌ {exc}", ephemeral=True)
            return
        embed = discord.Embed(title=title[:256], description=description[:4096], color=color_value, url=url.strip()[:2048] if url.strip() else discord.Embed.Empty)
        if footer.strip(): embed.set_footer(text=footer[:2048])
        if thumbnail.strip(): embed.set_thumbnail(url=thumbnail.strip()[:2048])
        if image.strip(): embed.set_image(url=image.strip()[:2048])
        payload = {"embeds": [embed.to_dict()]}
        export = "```json\n" + json.dumps(payload, indent=2)[:3600] + "\n```"
        embed.add_field(name="📦 Export JSON", value=export, inline=False)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="embed-json", description="Create a preview from Discord embed JSON.")
    @app_commands.describe(payload="Discord-compatible embed JSON")
    async def embed_json(self, interaction: discord.Interaction, payload: str):
        try:
            data = json.loads(payload)
            item = (data.get("embeds") or [data])[0] if isinstance(data, dict) else None
            if not isinstance(item, dict): raise ValueError
            embed = discord.Embed.from_dict(item)
        except (json.JSONDecodeError, ValueError, TypeError, IndexError, AttributeError):
            await interaction.response.send_message("❌ Invalid Discord embed JSON.", ephemeral=True)
            return
        await interaction.response.send_message(content="**Embed preview**", embed=embed)

    @app_commands.command(name="embed-export", description="Validate and normalize an embed JSON payload for copying.")
    async def embed_export(self, interaction: discord.Interaction, payload: str):
        try:
            data = json.loads(payload)
            item = (data.get("embeds") or [data])[0] if isinstance(data, dict) else None
            if not isinstance(item, dict): raise ValueError
            normalized = discord.Embed.from_dict(item).to_dict()
        except (json.JSONDecodeError, ValueError, TypeError, IndexError, AttributeError):
            await interaction.response.send_message("❌ Invalid embed payload.", ephemeral=True)
            return
        text = json.dumps({"embeds": [normalized]}, indent=2)
        await interaction.response.send_message(f"```json\n{text[:3900]}\n```", ephemeral=True)


async def setup(bot):
    await bot.add_cog(Embeds(bot))
