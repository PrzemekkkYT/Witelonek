import json
import os
import logging
import datetime
import random


# discord import
import discord
from discord.ext import commands, tasks

# local import
from utils.utils import JSONTranslator

### wymagane permisje ###
# - wysyłanie wiadomości
# - oznaczanie @everyone
# - tworzenie kanałów
# - tworzenie ról
#######################

# ray.init(object_store_memory=78643200)

logger = logging.getLogger("discord")
handler = logging.FileHandler(filename="logs/bot.log", encoding="utf-8", mode="a+")

bot_config = json.load(open("./config.json", "r+"))

MY_GUILD = discord.Object(id=bot_config["test_guild"])
# MY_GUILD = discord.Object(id=891009215102074950)


class MyClient(commands.Bot):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(
            command_prefix="w!",
            intents=intents,
            status=discord.Status.idle,
            # activity=discord.CustomActivity(name=""),
        )

    async def setup_hook(self):
        await self.tree.set_translator(translator=JSONTranslator())

        for filename in os.listdir("./extensions"):
            if filename.endswith(".py"):
                await self.load_extension(f"extensions.{filename[:-3]}")

        self.tree.copy_global_to(guild=MY_GUILD)
        await self.tree.sync()

    async def on_ready(self):
        # change_status.start()
        # print("ready")
        logger.info("========== bot is ready ==========")


@tasks.loop(time=datetime.time(hour=0, minute=0, tzinfo=datetime.timezone.utc))
async def change_status():
    await client.change_presence(
        status=discord.Status.idle,
        activity=discord.CustomActivity(name=random.choice(bot_config["statuses"])),
    )


intents = discord.Intents.all()
client = MyClient(intents=intents)

client.local_config = bot_config


@client.command()
async def ping(ctx: commands.Context):
    await ctx.send(f"Ping: {round(client.latency*1000)}ms")


client.run(bot_config["token"], log_handler=handler, log_level=logging.INFO)
