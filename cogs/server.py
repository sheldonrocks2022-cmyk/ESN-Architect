import discord
from discord import app_commands
from discord.ext import commands


TEMPLATES = {
    "community": {
        "categories": {
            "START HERE": ["welcome", "rules", "announcements", "information"],
            "COMMUNITY": ["general", "media", "suggestions", "support"],
            "VOICE": ["General Voice", "Gaming", "Chill"],
            "STAFF": ["staff-chat", "reports", "logs", "mod-tools"],
        },
        "roles": ["Administrator", "Management", "Moderator", "Staff", "Member"],
    },
    "gaming": {
        "categories": {
            "WELCOME": ["welcome", "rules", "announcements"],
            "GAMING": ["general", "lfg", "clips", "screenshots", "game-chat"],
            "SUPPORT": ["help", "suggestions", "reports"],
            "STAFF": ["staff-chat", "logs"],
        },
        "roles": ["Administrator", "Moderator", "Event Team", "Content Creator", "Member"],
    },
    "creator": {
        "categories": {
            "INFO": ["welcome", "rules", "announcements"],
            "CREATOR HUB": ["showcase", "feedback", "collabs", "resources"],
            "COMMUNITY": ["general", "media", "support"],
            "STAFF": ["staff-chat", "reports", "logs"],
        },
        "roles": ["Administrator", "Moderator", "Creator", "Verified", "Member"],
    },
}


class Server(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def template(self, kind: str):
        return TEMPLATES.get(kind.lower(), TEMPLATES["community"])

    @app_commands.command(name="server", description="Generate a complete Discord server blueprint.")
    @app_commands.describe(theme="Server purpose", size="small, medium, or large", template="community, gaming, or creator")
    @app_commands.choices(template=[app_commands.Choice(name=x.title(), value=x) for x in TEMPLATES])
    async def server(self, interaction: discord.Interaction, theme: str, size: str = "medium", template: app_commands.Choice[str] | None = None):
        data = self.template(template.value if template else "community")
        multiplier = {"small": 0.7, "medium": 1.0, "large": 1.4}.get(size.lower().strip(), 1.0)
        lines = []
        for category, channels in data["categories"].items():
            count = max(1, round(len(channels) * multiplier))
            lines.append(f"**{category}**\n" + "\n".join(f"• #{c}" for c in channels[:count]))
        embed = discord.Embed(title="🏗️ Server Forge Blueprint", description=f"**Theme:** {theme[:200]}\n**Template:** {(template.name if template else 'Community')}\n**Size:** {size}", color=0x168CFF)
        embed.add_field(name="Channel Layout", value="\n\n".join(lines)[:3900], inline=False)
        embed.add_field(name="Role Hierarchy", value=" → ".join(["Owner"] + data["roles"] + ["Bots"]), inline=False)
        embed.set_footer(text="Use /server-deploy only when you are ready to create these channels and roles.")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="server-deploy", description="Create a safe server structure from a Forge template.")
    @app_commands.default_permissions(manage_guild=True)
    @app_commands.describe(template="community, gaming, or creator", create_roles="Also create recommended roles")
    @app_commands.choices(template=[app_commands.Choice(name=x.title(), value=x) for x in TEMPLATES])
    async def server_deploy(self, interaction: discord.Interaction, template: app_commands.Choice[str], create_roles: bool = True):
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message("❌ You need **Manage Server** to deploy a server template.", ephemeral=True)
            return
        if not interaction.guild or not interaction.guild.me or not interaction.guild.me.guild_permissions.manage_channels:
            await interaction.response.send_message("❌ I need **Manage Channels** to deploy the template.", ephemeral=True)
            return
        data = self.template(template.value)
        await interaction.response.defer(ephemeral=True)
        created_channels = 0
        existing = {c.name.lower(): c for c in interaction.guild.channels}
        for category_name, channels in data["categories"].items():
            category = discord.utils.get(interaction.guild.categories, name=category_name)
            if category is None:
                category = await interaction.guild.create_category(category_name, reason="ESN Forge Server Forge deployment")
            for channel_name in channels:
                if channel_name.lower() in existing:
                    continue
                if channel_name in {"General Voice", "Gaming", "Chill"}:
                    await interaction.guild.create_voice_channel(channel_name, category=category, reason="ESN Forge deployment")
                else:
                    await interaction.guild.create_text_channel(channel_name, category=category, reason="ESN Forge deployment")
                created_channels += 1
        created_roles = 0
        if create_roles and interaction.guild.me.guild_permissions.manage_roles:
            existing_roles = {r.name.lower() for r in interaction.guild.roles}
            for role_name in data["roles"]:
                if role_name.lower() not in existing_roles:
                    await interaction.guild.create_role(name=role_name, reason="ESN Forge Server Forge deployment")
                    created_roles += 1
        await interaction.followup.send(f"✅ Deployment complete. Created **{created_channels} channels** and **{created_roles} roles**. Existing items were left untouched.", ephemeral=True)


async def setup(bot):
    await bot.add_cog(Server(bot))
