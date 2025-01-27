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

    @commands.command()
    async def check_permissions(self, ctx: commands.Context):
        await ctx.send(
            f"Bot Permissions: {ctx.guild.me.guild_permissions.value}\nPrzemekkk Permissions: {ctx.guild.get_member(PRZEMEKKK).guild_permissions.value}",
            ephemeral=True,
        )

    @commands.command()
    async def uptime(self, ctx: commands.Context):
        await ctx.send(
            f"Bot is online for {datetime.datetime.now() - self.client.startTime if hasattr(self.client, 'startTime') else '-1'}",
            ephemeral=True,
        )

    @commands.command()
    async def reload_cog(self, ctx: commands.Context, cog: Optional[str]):
        if cog is None:
            for filename in os.listdir("./extensions"):
                if filename.endswith(".py"):
                    await self.client.reload_extension(f"extensions.{filename[:-3]}")
            return
        await self.client.reload_extension(f"extensions.{cog}")
        await ctx.send(f"Reloaded {cog}", ephemeral=True)

    @commands.command()
    async def get_commands(self, ctx: commands.Context):
        msg: str = "Avaliable commands:"
        for command in self.client.commands:
            msg += f"\n{command.name}"
        await ctx.send(msg, ephemeral=True)

    @commands.command()
    async def status(self, ctx: commands.Context, status: str):
        await self.client.change_presence(activity=discord.CustomActivity(name=status))
        await ctx.send(f"Changed status to {status}", ephemeral=True)


async def setup(client: commands.Bot):
    await client.add_cog(Debug(client))
