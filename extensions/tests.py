# discord import
import discord
from discord import app_commands
from discord.app_commands import locale_str
from discord.ext import commands


class Tests(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client: commands.Bot = client

    @app_commands.command(name="test")
    async def test(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            content="test",
            ephemeral=True,
        )


async def setup(client: commands.Bot):
    await client.add_cog(Tests(client))
