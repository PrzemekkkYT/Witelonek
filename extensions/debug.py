import datetime
import os
from typing import Optional

# discord import
import discord
from discord import app_commands
from discord.app_commands import locale_str
from discord.ext import commands

# local import
from utils.discord_extension import ExtEmbedGenerator

PRZEMEKKK = 183242057882664961


class Debug(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client: commands.Bot = client
        self.embedGenerator = ExtEmbedGenerator(
            translator=client.tree.translator, locale=discord.Locale.polish
        )
        self.translate = self.client.tree.translator.translate

    async def cog_check(self, ctx):
        return ctx.author.id == PRZEMEKKK

    @app_commands.command()
    async def check_permissions(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            f"Bot Permissions: {interaction.guild.me.guild_permissions.value}\nPrzemekkk Permissions: {interaction.guild.get_member(PRZEMEKKK).guild_permissions.value}"
        )

    @app_commands.command()
    async def uptime(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            f"Bot is online for {datetime.datetime.now() - self.client.startTime if hasattr(self.client, 'startTime') else '-1'}"
        )

    @app_commands.command()
    async def reload_cog(self, interaction: discord.Interaction, cog: Optional[str]):
        if cog is None:
            for filename in os.listdir("./extensions"):
                if filename.endswith(".py"):
                    await self.client.reload_extension(f"extensions.{filename[:-3]}")
            return
        await self.client.reload_extension(f"extensions.{cog}")
        await interaction.response.send_message(f"Reloaded {cog}")


async def setup(client: commands.Bot):
    await client.add_cog(Debug(client))
