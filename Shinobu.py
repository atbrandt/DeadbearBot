# Shinobu Bot main execution
# Written by a few weebs

import discord
import asyncio
import aiohttp
import configparser
from discord.ext import commands
from pathlib import Path
#from discord.ext.commands import Bot

#Client = Bot('-')

# Setting platform-independent path to working directory and config file
CURRENTDIR = Path.cwd()
CONFIG = CURRENTDIR / "init.cfg"

# Initialize configparser settings
CFGPARSE = configparser.ConfigParser(allow_no_value = True,
                                     empty_lines_in_values = False)

# Function for writing to the config file
def write_cfg(*args, **kwargs):
    for key, value in kwargs.items():
        CFGPARSE.set(args, key, value)
    with Path.open(CONFIG, 'w') as configfile:
        CFGPARSE.write(configfile)

# Initialize config
if not Path.exists(CONFIG):
    CFGPARSE['DEFAULT'] = {'Token': '',
                           'Prefix': '-',
                           'Greet': 'disable',
                           'GreetChannel': ''}
    TOKEN = input("Enter your bot's token: ")
    write_cfg(Token=TOKEN)
else:
    CFGPARSE.read(CONFIG)

# Initialize the bot and set the default command prefix
bot = commands.Bot(command_prefix = CFGPARSE['DEFAULT']['Prefix'])

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

# # Admin-only command to purge chunks of text
# @bot.command(name = 'purge')
# async def purge_text(context, num):
#     messages = [] #empty list to put all the messages in the log
#     number = int(num) #converting the number of messages to delete to an integer
#     async for x in Client.logs_from(context.message.channel, limit = number)
#         messages.append(x)
#     await Client.delete_messages(messages)


# # command to self-assign a role
# @bot.command(name = 'giveme',
#              pass_context = True,
#              no_pm = True)
# async def assignme(self, context, role : discord.Role)
#     user = context.message.author #get user that typed the commands
#     error = False
#     for srole in context.message.server.roles:
#         if srole.name == role.name:
#             if role.id in self.selfrole_list:
#                 try:
#                     await self.bot.add_roles(user, role)
#                     await channel.send("You now have the " + role.name + " role.")
#                 except discord.Forbidden:
#                     await channel.send("There appears to be an error with setting that role.")
#             else:
#                 await channel.send("That is not in the list of roles you can assign yourself!")

# Set the greet channel
@bot.command(name = 'ChangeGreet',
             description = ("Sets the current channel for greet messages. "
                            "Pass \"enable\" or \"disable\" to turn "
                            "the greet message on or off."),
             brief = "Modify greet message settings.",
             aliases = ["greet"])
async def change_greet(context, *opt_arg):
    channel = context.channel
    opt_arg = ''.join(opt_arg)
    options = {'enable', 'disable'}

    if opt_arg == '':
        write_cfg(GreetChannel=str(context.channel.id))
        await channel.send(f"Set {channel} as the greeting channel.")
    elif opt_arg in options:
        write_cfg(Greet=str(opt_arg))
        await channel.send(f"The greet message is now {opt_arg}d!")


# Greet new users upon joining guild
@bot.event
async def on_member_join(member):
    if CFGPARSE['DEFAULT']['Greet'] == "enable":
        channel = bot.get_channel(int(CFGPARSE['DEFAULT']['GreetChannel']))
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
        write_cfg(Prefix=str(newprefix.content))
        bot.command_prefix = newprefix.content
        await channel.send(f"My command prefix is now \"{newprefix.content}\".")

# Execute the Bot
try:
    bot.run(CFGPARSE['DEFAULT']['Token'])
except:
    print("Something's wrong with the token! Check the config file.")

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
