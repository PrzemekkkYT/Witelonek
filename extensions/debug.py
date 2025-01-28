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
        self.bot_config = client.bot_config or {}

    async def cog_check(self, ctx):
        return ctx.author.id == PRZEMEKKK

    async def send_priv(self, ctx: commands.Context, msg: str):
        await ctx.author.send(
            f"Command **{ctx.message.content}** executed on **{ctx.guild.name}** with output:\n{msg}"
        )

    # region Commands
    @commands.command()
    async def check_permissions(self, ctx: commands.Context):
        await self.send_priv(
            ctx,
            f"Bot Permissions: {ctx.guild.me.guild_permissions.value}\nPrzemekkk Permissions: {ctx.guild.get_member(PRZEMEKKK).guild_permissions.value}",
        )

    @commands.command()
    async def uptime(self, ctx: commands.Context):
        await self.send_priv(
            ctx,
            f"Bot is online for {datetime.datetime.now() - self.client.startTime if hasattr(self.client, 'startTime') else '-1'}",
        )

    @commands.command()
    async def reload_cog(self, ctx: commands.Context, cog: Optional[str]):
        if cog is None:
            for filename in os.listdir("./extensions"):
                if filename.endswith(".py"):
                    await self.client.reload_extension(f"extensions.{filename[:-3]}")
            await self.send_priv(ctx, "Reloaded all cogs")
            return
        await self.client.reload_extension(f"extensions.{cog}")
        await self.send_priv(ctx, f"Reloaded {cog}")

    @commands.command()
    async def get_commands(self, ctx: commands.Context):
        msg: str = "Avaliable commands:```"
        for command in self.client.commands:
            msg += f"\n{command.name}"
        msg += "```"
        await self.send_priv(ctx, msg)

    @commands.command()
    async def status(self, ctx: commands.Context, status: str):
        await self.client.change_presence(activity=discord.CustomActivity(name=status))
        await self.send_priv(ctx, f"Changed status to {status}")

    @commands.command()
    async def delete_message(self, ctx: commands.Context, id: int):
        message = await ctx.channel.fetch_message(id)
        await message.delete()
        await self.send_priv(ctx, f"Deleted message with id {id}")

    # endregion
    # region Listeners
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.id == PRZEMEKKK and message.content.startswith(
            self.bot_config["prefix"]
        ):
            await message.delete()

    # endregion


async def setup(client: commands.Bot):
    await client.add_cog(Debug(client))
