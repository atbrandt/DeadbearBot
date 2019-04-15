import discord
import configparser
import asyncio
from discord.ext.commands import Bot
from pathlib import Path

# ConfigFolder = Path("")
# ConfigFile = ConfigFolder / "init.cfg"

CONFIG = configparser.ConfigParser()
CONFIG.read("init.cfg")
TOKEN = CONFIG['Bot']['Token']

prefix = "-"
bot = Bot(command_prefix=prefix)

@bot.command(name='greet')
async def hello(command):
    await command.send("hello world")

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

bot.run(TOKEN)
