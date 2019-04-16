# Shinobu Bot main execution
# Written by a few weebs

import discord
import time
import asyncio
import configparser
from discord.ext.commands import Bot
from pathlib import Path

# ConfigFolder = Path("")
# ConfigFile = ConfigFolder / "init.cfg"

CONFIG = configparser.ConfigParser()
CONFIG.read("init.cfg")
TOKEN = CONFIG['DEFAULT']['Token']

prefix = "-"
bot = Bot(command_prefix=prefix)

@bot.event
async def on_ready():
    print('Bot is ready')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

# @bot.event
# async def on_member_join(member):
@bot.command(name="greet")
async def hello(context):
    channel = context.message.channel
    member = context.message.author
    print("Message sent in", channel)
    if str(channel) == 'bot-testin':
        await channel.send(f"""Welcome to the server {member.mention}""")

bot.run(TOKEN)
