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
greet = CFGPARSE['DEFAULT']['Greet']
greetChannel = CFGPARSE['DEFAULT']['GreetChannel']
bot = commands.Bot(command_prefix = CFGPARSE['DEFAULT']['Prefix'])


# Function to reinitialize the Bot
def update_prefix():
    if CFGPARSE['DEFAULT']['Prefix'] == "":
        bot.command_prefix = '-'
    else:
        bot.command_prefix = CFGPARSE['DEFAULT']['Prefix']


# Function for writing to cfg
def write_cfg(category, entry, value):
    CFGPARSE.set(category, entry, value)
    with open('init.cfg', 'w') as configfile:
        CFGPARSE.write(configfile)


# Output info to console once bot is initialized and ready
@bot.event
async def on_ready():
    print(f"{bot.user.name} is ready, user ID is {bot.user.id}")
    print("------")


# Testing command
@bot.command(name = 'test')
async def hello_world(context):
    channel = context.channel
    author = context.author
    print(f"Message sent in {channel}")
    await channel.send(f"Hello {author}!")


# Set the greet channel
@bot.command(name = 'ChangeGreet',
             description = ("Sets the current channel for greet messages. "
                            "Pass \"enable\" or \"disable\" to turn the greet message on or off."),
             brief = "Modify greet message settings.",
             aliases = ["greet"])
async def change_greet(context, *opt_arg):
    channel = context.channel
    opt_arg = ''.join(opt_arg)
    options = {'enable', 'disable'}
    
    if opt_arg is ():
        write_cfg('DEFAULT', 'GreetChannel', str(context.channel.id))
        await channel.send(f"Set {channel} as the greeting channel.")
    elif opt_arg in options:
        write_cfg('DEFAULT', 'Greet', str(opt_arg))
        await channel.send(f"The greet message is now {opt_arg}d!")


# Greet new users upon joining guild
@bot.event
async def on_member_join(member):
    if greet == "enable":
        channel = bot.get_channel(int(greetChannel))
        await channel.send(f"Welcome to the server {member.mention}!")


# Change the default bot prefix
@bot.command(name = 'ChangePrefix',
             description = ("Changes the default bot command prefix. "
                            "Default prefix is set in init.cfg."),
             brief = "Change bot prefix",
             aliases = ['prefix'])
async def change_prefix(context):
    author = context.message.author
    channel = context.message.channel
    
    def check(reply):
        return reply.author == author and reply.channel == channel

    await channel.send("What prefix would you like me to respond to? \[Auto timeout in 10 seconds.\]")

    try:
        newprefix = await bot.wait_for('message', check=check, timeout=10.0)
    except asyncio.TimeoutError:
        await channel.send("Timed out! Exiting...")
    else:
        write_cfg('DEFAULT', 'Prefix', str(newprefix.content))
        update_prefix()
        await channel.send(f"My command prefix is now \"{newprefix.content}\".")


# Execute the Bot
bot.run(TOKEN)
