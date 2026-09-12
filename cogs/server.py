import discord
from discord import app_commands
from discord.ext import commands

TEMPLATES = {
    "community": {"categories": {"START HERE": ["welcome", "rules", "announcements", "information"], "COMMUNITY": ["general", "media", "suggestions", "support"], "VOICE": ["General Voice", "Gaming", "Chill"], "STAFF": ["staff-chat", "reports", "logs", "mod-tools"]}, "roles": ["Administrator", "Management", "Moderator", "Staff", "Member"]},
    "gaming": {"categories": {"WELCOME": ["welcome", "rules", "announcements"], "GAMING": ["general", "lfg", "clips", "screenshots", "game-chat"], "SUPPORT": ["help", "suggestions", "reports"], "STAFF": ["staff-chat", "logs"]}, "roles": ["Administrator", "Moderator", "Event Team", "Content Creator", "Member"]},
    "creator": {"categories": {"INFO": ["welcome", "rules", "announcements"], "CREATOR HUB": ["showcase", "feedback", "collabs", "resources"], "COMMUNITY": ["general", "media", "support"], "STAFF": ["staff-chat", "reports", "logs"]}, "roles": ["Administrator", "Moderator", "Creator", "Verified", "Member"]},
}


def make_blueprint(template: str, size: str) -> tuple[dict, list[str]]:
    data = TEMPLATES[template]
    factor = {"small": .65, "medium": 1, "large": 1.35}[size]
    categories = {}
    for name, channels in data["categories"].items():
        count = max(1, round(len(channels) * factor))
        categories[name] = channels[:count]
    return categories, data["roles"]


class ConfirmView(discord.ui.View):
    def __init__(self, author_id: int):
        super().__init__(timeout=60)
        self.author_id = author_id
        self.value = None

    async def interaction_check(self, interaction):
        if interaction.user.id != self.author_id:
            await interaction.response.send_message("Only the command author can confirm this deployment.", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Deploy", style=discord.ButtonStyle.success, emoji="🚀")
    async def confirm(self, interaction, button):
        self.value = True
        self.stop()
        await interaction.response.defer()

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.danger, emoji="✖")
    async def cancel(self, interaction, button):
        self.value = False
        self.stop()
        await interaction.response.edit_message(content="Deployment cancelled.", embed=None, view=None)


class Server(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @app_commands.command(name="server", description="Generate a complete Discord server blueprint.")
    @app_commands.describe(theme="Server purpose", size="small, medium, or large", template="community, gaming, or creator")
    @app_commands.choices(template=[app_commands.Choice(name=x.title(), value=x) for x in TEMPLATES], size=[app_commands.Choice(name=x.title(), value=x) for x in ("small", "medium", "large")])
    async def server(self, interaction, theme: str, size: app_commands.Choice[str], template: app_commands.Choice[str]):
        categories, roles = make_blueprint(template.value, size.value)
        body = "\n\n".join(f"**{cat}**\n" + "\n".join(f"• #{c}" for c in channels) for cat, channels in categories.items())
        embed = discord.Embed(title="🏗️ Server Forge Blueprint", description=f"**Theme:** {theme[:200]}\n**Template:** {template.name}\n**Size:** {size.name}", color=0x168CFF)
        embed.add_field(name="Channels", value=body[:3900], inline=False)
        embed.add_field(name="Roles", value=" → ".join(["Owner", *roles, "Bots"]), inline=False)
        embed.set_footer(text="/server-deploy creates only missing items and never deletes existing channels or roles.")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="server-deploy", description="Safely create a server structure from a Forge template.")
    @app_commands.default_permissions(manage_guild=True)
    @app_commands.describe(template="Template", create_roles="Create recommended roles")
    @app_commands.choices(template=[app_commands.Choice(name=x.title(), value=x) for x in TEMPLATES])
    async def server_deploy(self, interaction, template: app_commands.Choice[str], create_roles: bool = True):
        guild = interaction.guild
        if not guild or not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message("❌ You need **Manage Server**.", ephemeral=True); return
        me = guild.me
        if not me or not me.guild_permissions.manage_channels:
            await interaction.response.send_message("❌ I need **Manage Channels**.", ephemeral=True); return
        categories, roles = make_blueprint(template.value, "medium")
        embed = discord.Embed(title="🚀 Confirm Server Forge deployment", description=f"Template: **{template.name}**\nThis will create missing categories/channels{(' and roles' if create_roles else '')}. Nothing will be deleted.", color=0xF59E0B)
        view = ConfirmView(interaction.user.id)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
        await view.wait()
        if view.value is not True: return
        created_channels = 0
        existing_channels = {c.name.casefold() for c in guild.channels}
        category_map = {c.name.casefold(): c for c in guild.categories}
        for category_name, channel_names in categories.items():
            category = category_map.get(category_name.casefold())
            if category is None:
                category = await guild.create_category(category_name, reason="ESN Forge deployment")
                category_map[category_name.casefold()] = category
            for channel_name in channel_names:
                if channel_name.casefold() in existing_channels: continue
                if channel_name in {"General Voice", "Gaming", "Chill"}:
                    await guild.create_voice_channel(channel_name, category=category, reason="ESN Forge deployment")
                else:
                    await guild.create_text_channel(channel_name, category=category, reason="ESN Forge deployment")
                existing_channels.add(channel_name.casefold()); created_channels += 1
        created_roles = 0
        if create_roles and me.guild_permissions.manage_roles:
            existing_roles = {r.name.casefold() for r in guild.roles}
            for role_name in roles:
                if role_name.casefold() not in existing_roles:
                    await guild.create_role(name=role_name, reason="ESN Forge deployment")
                    created_roles += 1
        await interaction.edit_original_response(content=f"✅ Deployment complete — **{created_channels} channels** and **{created_roles} roles** created.", embed=None, view=None)


async def setup(bot): await bot.add_cog(Server(bot))
