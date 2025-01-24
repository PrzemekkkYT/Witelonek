from typing import Optional

# discord import
import discord
from discord import app_commands
from discord.ext import commands
from discord.app_commands import locale_str

from utils.discord_extension import ExtEmbedGenerator
from orms.configs import GuildConfigs


class Config(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client: commands.Bot = client
        self.embedGenerator = ExtEmbedGenerator(translator=self.client.tree.translator)
        self.translate = self.client.tree.translator.translate

    @app_commands.command(
        name=locale_str("config"), description=locale_str("config_description")
    )
    @app_commands.rename(
        events_channel=locale_str("config_events_channel"),
        logging_channel=locale_str("config_logging_channel"),
    )
    @app_commands.describe(
        events_channel=locale_str("config_events_channel_description"),
        logging_channel=locale_str("config_logging_channel_description"),
    )
    async def config(
        self,
        interaction: discord.Interaction,
        events_channel: Optional[discord.TextChannel] = None,
        logging_channel: Optional[discord.TextChannel] = None,
    ):
        if all(x is None for x in [events_channel, logging_channel]):
            guild_config = GuildConfigs.get(interaction.guild_id)
            embed = self.embedGenerator.embed(
                title=locale_str("config_embed_title"),
                fields=[
                    ExtEmbedGenerator.Field(
                        name=locale_str("config_events_channel"),
                        value=(
                            f"<#{guild_config.events_channel_id}>"
                            if guild_config.events_channel_id
                            else await self.translate(locale_str("none"))
                        ),
                    ),
                    ExtEmbedGenerator.Field(
                        name=locale_str("config_logging_channel"),
                        value=(
                            f"<#{guild_config.logging_channel_id}>"
                            if guild_config.logging_channel_id
                            else await self.translate(locale_str("none"))
                        ),
                    ),
                ],
                thumbnail=(
                    interaction.guild.icon.url
                    if interaction.guild.icon
                    else self.client.user.avatar.url
                ),
                color=discord.Color.dark_blue(),
            )
            await interaction.response.send_message(embed=embed)
            return
        if events_channel is not None:
            embed = self.embedGenerator.embed(
                title=locale_str(
                    "config_events_channel_success", channel_name=events_channel.id
                ),
                color=discord.Color.green(),
            )
            if discord.Permissions(permissions=2048).is_subset(
                events_channel.permissions_for(interaction.guild.me)
            ):
                GuildConfigs.update(events_channel_id=events_channel.id).where(
                    GuildConfigs.guild_id == interaction.guild_id
                ).execute()
            else:
                embed = self.embedGenerator.embed(
                    title=locale_str(
                        "config_events_channel_fail", channel_name=events_channel.id
                    ),
                    color=discord.Color.red(),
                )

            if interaction.response.is_done():
                await interaction.followup.send(embed=embed, ephemeral=True)
            else:
                await interaction.response.send_message(embed=embed, ephemeral=True)
        if logging_channel is not None:
            embed = self.embedGenerator.embed(
                title=locale_str(
                    "config_logging_channel_success", channel_name=logging_channel.id
                ),
                color=discord.Color.green(),
            )
            if discord.Permissions(permissions=2048).is_subset(
                events_channel.permissions_for(interaction.guild.me)
            ):
                GuildConfigs.update(logging_channel_id=logging_channel.id).where(
                    GuildConfigs.guild_id == interaction.guild_id
                ).execute()
            else:
                embed = self.embedGenerator.embed(
                    title=locale_str(
                        "config_logging_channel_fail", channel_name=logging_channel.id
                    ),
                    color=discord.Color.red(),
                )

            if interaction.response.is_done():
                await interaction.followup.send(embed=embed, ephemeral=True)
            else:
                await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(client: commands.Bot):
    await client.add_cog(Config(client))
