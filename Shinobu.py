# Shinobu Bot main execution
# Written by a few weebs

import discord
import asyncio
import aiohttp
import configparser
from discord.ext import commands
from discord.utils import get
from pathlib import Path

# Setting platform-independent path to working directory and config file
CURRENTDIR = Path.cwd()
CONFIG = CURRENTDIR / "init.cfg"

# Initialize configparser settings
CFGPARSER = configparser.ConfigParser(empty_lines_in_values = False)
CFGPARSER.optionxform = lambda option: option

# Set a reference of default options that must exist in config
CFGDEFAULT = {'Token': '',
              'Prefix': '-',
              'GreetState': 'disable',
              'GreetChannelID': '',
              'AutoRoleState': 'disable',
              'AutoRoleID': ''}

# Function for writing to the config file
def write_cfg(*args, **kwargs):
    args = ''.join(args)
    for key, value in kwargs.items():
        CFGPARSER.set(args, key, value)
    with Path.open(CONFIG, 'w') as configfile:
        CFGPARSER.write(configfile)

# Initialize config
try:
    CFGPARSER.read_file(Path.open(CONFIG))
    cfgcur = list(CFGPARSER.items('Settings'))
    cfgdef = list(CFGDEFAULT.items())
    CFGPARSER['Settings'] = dict(cfgdef + cfgcur)
    write_cfg()
except:
    CFGPARSER.add_section('Settings')
    CFGPARSER['Settings'] = CFGDEFAULT
    write_cfg()
finally:
    if CFGPARSER['Settings']['Token'] == '':
        write_cfg('Settings', Token = input("Enter your bot's token: "))

# Initialize the bot and set the default command prefix
bot = commands.Bot(command_prefix = CFGPARSER['Settings']['Prefix'])

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


# Assign a role upon joining guild
@bot.command(name = 'AutoRole',
             description = ("Sets a role that users get automatically upon "
                            "joining the server. Usage is `-arole set "
                            "\(Role name or ID string\)`. Pass \"enable\" or"
                            " \"disable\" to turn the auto-role on or off."),
             brief = "Modify auto-role settings.",
             aliases = ["arole"])
async def auto_role(context, option : str, *args):
    channel = context.channel
    guild = context.guild
    args = ''.join(args)    
    gotrole = ''

    if args == '':
        if option in ('enable', 'disable'):
            write_cfg('Settings', AutoRoleState = option)
            await channel.send(f"The auto-role is now {option}d!")
        elif option == 'clear':
            write_cfg('Settings', AutoRoleID = '')
            await channel.send(f"The auto-roles are now {option}ed!")
        elif option == 'set':
            await channel.send(f"You need to include a role name or ID!")
    elif args.isdigit():
        gotRole = guild.get_role(args)
    else:
        gotRole = get(guild.roles, name = args)

    if gotRole is not None and option == 'set':
        write_cfg('Settings', AutoRoleID = str(gotRole.id))
        await channel.send(f"Added \"{gotRole.name}\" the auto-role "
                            "list.")
    else:
        await channel.send("No role found! Check the name or ID entered.")


# Error handler for auto_role function
#@auto_role.error
#async def auto_role_error(context, error):
#    if isinstance(error, commands.MissingRequiredArgument):
#        await context.channel.send("You need to include a role name or ID!")
#    if isinstance(error, commands.CommandError):
#        await context.channel.send("Och! Something wrong! Don't worry \;\)")


# Set the greet channel
@bot.command(name = 'ChangeGreet',
             description = ("Sets the current channel for greet messages. "
                            "Pass \"enable\" or \"disable\" to turn "
                            "the greet message on or off."),
             brief = "Modify greet message settings.",
             aliases = ["greet"])
async def change_greet(context, *args):
    channel = context.channel
    args = ''.join(args)
    if args == '':
        write_cfg('Settings', GreetChannelID = str(context.channel.id))
        await channel.send(f"Set {channel} as the greeting channel.")
    elif args in ('enable', 'disable'):
        write_cfg('Settings', GreetState = str(args))
        await channel.send(f"The greet message is now {args}d!")


# Do stuff to new users upon joining guild
@bot.event
async def on_member_join(member):
    if CFGPARSER['Settings']['AutoRoleState'] == 'enable':
        if CFGPARSER['Settings']['AutoRoleID'] != '':
            guild = member.guild
            role = guild.get_role(int(CFGPARSER['Settings']['AutoRoleID']))
            await member.add_roles(role, reason = "AutoRole")
    if CFGPARSER['Settings']['GreetState'] == 'enable':
        if CFGPARSER['Settings']['GreetChannelID'] != '':
            channel = bot.get_channel(int(CFGPARSER['Settings']['GreetChannel']))
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

    await channel.send("What prefix would you like me to respond to? "
                       "\[Auto timeout in 10 seconds.\]")

    try:
        newprefix = await bot.wait_for('message', check=check, timeout=10.0)
    except asyncio.TimeoutError:
        await channel.send("Timed out! Exiting...")
    else:
        write_cfg('Settings', Prefix=str(newprefix.content))
        bot.command_prefix = newprefix.content
        await channel.send(f"My command prefix is now \"{newprefix.content}\".")


# Execute the Bot
bot.run(CFGPARSER['Settings']['Token'])


# messages = joined = 0 #For update_stats() fxn
#
# async fxn for logging and storing information/data
# @client.event
# async def update_stats():
#    await client.wait_until_ready()
#    global messages, joined
#
#    while not client.is_closed():
#        try:
#            with open("stats.txt", "a") as f:
#                f.write(f"Time: {int(time.time())}, Messages: {messages}, Members joined: {joined}\n")
#
#            messages = 0
#            joined = 0
#
#            await asyncio.sleep(5)
#        except Exception as e:
#            print(e)
#            await asyncio.sleep(5)
#
# Async fxn designed to change nicknames
# async def on_member_update(before, after):
#    n = after.nick
#    if n:
#        if n.lower().count("staff") > 0: # If username contains staff
#            last = before.nick
#            if last: # if they had a username before change it back to that.
#                await after.edit(nick=last)
#            else: #Otherwise set it to Cheeky Breeky.
#                await after.edit(nick = "Cheeky Breeky")
#
#    for word in no-no_words:
#        if message.content.count(word)>0:
#            print("Whoa, don't say that.")
#            await message.channel.purge(limit = 1)

