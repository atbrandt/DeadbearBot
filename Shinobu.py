# Shinobu Bot main execution
# Written by a few weebs

import discord
import asyncio
import aiohttp
import configparser
from discord.ext import commands
from pathlib import Path

# Path variables for importing files cleanly regardless of deploy environment
# ConfigFolder = Path("")
# ConfigFile = ConfigFolder / "init.cfg"

# Initialize global variables and functions
CFGPARSE = configparser.ConfigParser()
CFGPARSE.read('init.cfg')
TOKEN = CFGPARSE['DEFAULT']['Token']
botPrefix = CFGPARSE['DEFAULT']['Prefix']
greet = CFGPARSE['DEFAULT']['Greet']
greetChannel = CFGPARSE['DEFAULT']['GreetChannel']

# Create an instance of the Bot
bot = commands.Bot(command_prefix=botPrefix)

# Output info to console once bot is initialized and ready
@bot.event
async def on_ready():
    print(f"{bot.user.name} is ready, user ID is {bot.user.id}")
    print("------")

# Testing command
@bot.command(name='test')
async def hello_world(context):
    channel = context.channel
    author = context.author
    print(f"Message sent in {channel}")
    await channel.send(f"Hello {author}!")

# Set the greet channel
@bot.command(name='greet')
async def greet_channel(context):
    channel = context.channel
    CFGPARSE.set('DEFAULT', 'GreetChannel', str(context.channel.id))
    with open('init.cfg', 'w') as configfile:
        CFGPARSE.write(configfile)
    await channel.send(f"Set {channel} as the greeting channel.")

# Greet new users upon joining guild (may change to upon joining channel)
@bot.event
async def on_member_join(member):
    channel = bot.get_channel(int(greetChannel))
    await channel.send(f"Welcome to the server {member.mention}!")

# Execute the Bot
bot.run(TOKEN)
