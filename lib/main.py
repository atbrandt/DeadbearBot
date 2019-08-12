# Shinobu Bot main execution
# Written by a few weebs

import discord
import asyncio
import aiohttp
import configparser
import db
import re
from discord.ext import commands
from discord.utils import get
from pathlib import Path


# Setting platform-independent path to working directory and config file
CONFIG = Path(__file__).parent / "init.cfg"


# Initialize configparser settings
CFGPARSER = configparser.ConfigParser(empty_lines_in_values = False)
CFGPARSER.optionxform = lambda option: option


# Set a reference of default options that must exist in config
CFGDEFAULT = {'Token': '',
              'Prefix': '-',
              'AutoRoleID': '',
              'ReactMessageID': '',
              'ReactChannelID': '',
              'GreetChannelID': '',
              'GreetMessage': ''
             }


# Function for writing to the config file
def write_cfg(*args, **kwargs):
    args = ''.join(args)
    for key, value in kwargs.items():
        CFGPARSER.set(args, key, value)
    with Path.open(CONFIG, 'w', encoding='utf-8') as configfile:
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


# Testing command
@bot.command(name = 'test')
async def hello_world(ctx):
    print(f"Message sent in {ctx.channel} from {ctx.author.id}")
    await ctx.channel.send(f"Hello {ctx.author}!")


# Describe item by name in database
@bot.command(name = 'describe')
async def describe_item(ctx, itemName: str):
    item = getItemByName(itemName)

    if(item is not None):
        await ctx.channel.send(item['description'])
    else:
        await ctx.channel.send(f"Item not found")


# Allow users to self-assign roles
@bot.command(name = 'GiveMeRole',
             description = ("Assigns or removes a specified role name or ID "
                            "to yourself."),
             brief = "Assign or remove role.",
             aliases = ["gimmie"])
async def set_role(ctx, role):    
    if role.isdigit():
        gotRole = ctx.guild.get_role(int(role))
    else:
        gotRole = get(ctx.guild.roles, name = role)

    if gotRole is not None:
        if gotRole not in ctx.author.roles:
            await ctx.author.add_roles(gotRole, reason = "SetRole")
            await ctx.channel.send(f"Gave you the \"{gotRole.name}\" role.")
        else:
            await ctx.author.remove_roles(gotRole, reason = "SetRole")
            await ctx.channel.send(f"Removed your \"{gotRole.name}\" role.")
    else:
        await ctx.channel.send("No role found! Check the name or ID entered.")


# Manage a role to be assigned upon joining guild
@bot.command(name = 'AutoRole',
             description = ("Sets a role that users get automatically upon "
                            "joining the server. Usage is `-arole set "
                            "\(Role name or ID string\)`. Pass \"enable\" or"
                            " \"disable\" to turn the auto-role on or off."),
             brief = "Modify auto-role settings.",
             aliases = ["arole"])
async def auto_role(ctx, option, *args):
    role = ' '.join(args)

    if role.isdigit():
        gotRole = ctx.guild.get_role(int(role))
    else:
        gotRole = get(ctx.guild.roles, name = role)

    if option == 'set':
        if gotRole is not None:
            write_cfg('Settings', AutoRoleID = str(gotRole.id))
            await ctx.channel.send(f"Added \"{gotRole.name}\" the auto-role "
                                    "list.")
        else:
            await ctx.channel.send("No role found! Check the name or ID "
                                   "entered.")
    elif option == 'clear':
        write_cfg('Settings', AutoRoleID = '')
        await ctx.channel.send("The auto-role is now cleared.")


# Set the greet channel
@bot.command(name = 'SetGreet',
             description = ("Configures the automatic greeting message when users "
                            "join the server. Pass \"enable\" or \"disable\" to "
                            "turn the greet message on or off."),
             brief = "Modify greet message settings.",
             aliases = ["greet"])
async def change_greet(ctx, *args):
    greetmsg = ' '.join(args)

    if greetmsg == 'enable':
        write_cfg('Settings', GreetChannelID = str(ctx.channel.id))
        await ctx.channel.send(f"Greetings enabled in \"{ctx.channel}\".")        
    elif greetmsg == 'disable':
        write_cfg('Settings', GreetChannelID = '')
        await ctx.channel.send("Greetings disabled.")
    elif greetmsg is not '':
        write_cfg('Settings', GreetMessage = greetmsg)
        await ctx.channel.send("Set that as the greet message.")


# Change the default bot prefix
@bot.command(name = 'ChangePrefix',
             description = ("Changes the default bot command prefix. Usage is "
                            "\`{bot.command_prefix}prefix \(New prefix\)\`."),
             brief = "Change bot prefix",
             aliases = ['prefix'])
async def change_prefix(ctx, option):
    write_cfg('Settings', Prefix = option)
    bot.command_prefix = option
    await ctx.channel.send(f"My command prefix is now \"{option}\".")


# Command to set a message as a hook for reaction roles
@bot.command(name = 'ReactRoleMessage',
             description = ("Sets a given message in a given channel as a "
                            "source hook for react roles."),
             brief = "Set ReactRoles Message",
             aliases = ['rrhook'])
async def rr_msg_set(ctx, targetChannel, targetMessage):
    channelID = int(targetChannel)
    messageID = int(targetMessage)
    
    try:
        await bot.get_channel(channelID).fetch_message(messageID)
    except NotFound:
        await ctx.channel.send("No message found! Check the IDs and make "
                               "sure I have access to the right channel.")
    else:
        write_cfg('Settings', ReactMessageID = targetMessage)
        write_cfg('Settings', ReactChannelID = targetChannel)
        await ctx.channel.send("Set that message as the react role hook!")


# Command to set a reaction role
@bot.command(name = 'ReactRole',
             description = ("Adds a reaction role using a given emoji and role "
                            "id."),
             brief = "Create a reaction role",
             aliases = ['rr'])
async def rr_create(ctx, emoji, *args):
    role = ' '.join(args)
    emojiID = re.sub('(<|>|:.*?:)','',emoji)
    
    if CFGPARSER['Settings']['ReactMessageID'] != '':
        messageID = int(CFGPARSER['Settings']['ReactMessageID'])
        channelID = int(CFGPARSER['Settings']['ReactChannelID'])
        try:
            gotMsg = await bot.get_channel(channelID).fetch_message(messageID)
        except NotFound:
            await ctx.channel.send("Can't find the reaction role hook!")
        else:
            if role.isdigit():
                gotRole = ctx.guild.get_role(int(role))
            else:
                gotRole = get(ctx.guild.roles, name = role)

            if gotRole is not None:
                db.addRR(emoji, gotRole.id)
                await gotMsg.add_reaction(emojiID)
                await ctx.channel.send(f"Set the \"{emoji}\" to give the "
                                       f"{gotRole.name} role.")
            else:
                await ctx.channel.send("No role found! Check the name or ID "
                                       "entered.")
    else:
        await ctx.channel.send("You need to configure the 'rrhook' first!")


# Command to delete a reaction role
@bot.command(name = 'DeleteReactRole',
             description = ("Removes a reaction role by its ID."),
             brief = "Remove a reaction role",
             aliases = ['rrdel'])
async def rr_delete(ctx, id):
    if id.isdigit():
        db.removeRR(id)
        await ctx.channel.send("Removed that entry.")
    else:
        await ctx.channel.send("You must give the ID of the entry to remove.")


# Command to list all reaction roles
@bot.command(name = 'ListReactRoles',
             description = ("Lists all reaction roles in database."),
             brief = "List reaction roles",
             aliases = ['rrlist'])
async def rr_list(ctx):    
    await ctx.channel.send(db.getAllRR())


# Get list of roles (with IDs) on guild
@bot.command(name = 'GetRoleIDs',
             description = ("Returns list of roles on server with IDs."),
             brief = "Get all roles with IDs",
             aliases = ['roles'])
async def get_roles(ctx):
    await ctx.channel.send(f"```{ctx.guild.roles}```")
    

# Get list of emojis (with IDs) on guild
@bot.command(name = 'GetEmojiIDs',
             description = ("Returns list of emojis on server with IDs."),
             brief = "Get all emojis with IDs",
             aliases = ['emojis'])
async def get_emojis(ctx):
    await ctx.channel.send(f"```{ctx.guild.emojis}```")


# Get list of channels (with IDs) on guild
@bot.command(name = 'GetChannelIDs',
             description = ("Returns list of channels on server with IDs."),
             brief = "Get all channels with IDs",
             aliases = ['channels'])
async def get_channels(ctx):
    await ctx.channel.send(f"```{ctx.guild.channels}```")


# Reaction Role hook function
@bot.event
async def on_raw_reaction_add(payload):
    if payload.message_id == int(CFGPARSER['Settings']['ReactMessageID']):
        rrlist = db.getAllRR()
        emoji = str(payload.emoji)
        gotRR = next((item for item in rrlist if item['emoji'] == emoji), None)
        if gotRR is not None:
            guild = bot.get_guild(payload.guild_id)
            member = guild.get_member(payload.user_id)
            gotRole = guild.get_role(gotRR['roleID'])
            if gotRole not in member.roles:
                await member.add_roles(gotRole, reason = "ReactionRole")


# Reaction Role hook function
@bot.event
async def on_raw_reaction_remove(payload):
    if payload.message_id == int(CFGPARSER['Settings']['ReactMessageID']):
        rrlist = db.getAllRR()
        emoji = str(payload.emoji)
        gotRR = next((item for item in rrlist if item['emoji'] == emoji), None)
        if gotRR is not None:
            guild = bot.get_guild(payload.guild_id)
            member = guild.get_member(payload.user_id)
            gotRole = guild.get_role(gotRR['roleID'])
            if gotRole in member.roles:
                await member.remove_roles(gotRole, reason = "ReactionRole")


# Do stuff to new users upon joining guild
@bot.event
async def on_member_join(member):
    if CFGPARSER['Settings']['AutoRoleID'] != '':
        guild = member.guild
        role = guild.get_role(int(CFGPARSER['Settings']['AutoRoleID']))
        await member.add_roles(role, reason = "AutoRole")
    if CFGPARSER['Settings']['GreetChannelID'] != '':
        channel = bot.get_channel(int(CFGPARSER['Settings']['GreetChannel']))
        await channel.send(CFGPARSER['Settings']['GreetMessage'])


# Output info to console once bot is initialized and ready
@bot.event
async def on_ready():
    print(f"{bot.user.name} is ready, user ID is {bot.user.id}")
    print("------")


# Execute the Bot
db.setupDatabase()
bot.run(CFGPARSER['Settings']['Token'])


# Error handler for auto_role function
#@auto_role.error
#async def auto_role_error(ctx, error):
#    if isinstance(error, commands.MissingRequiredArgument):
#        await ctx.channel.send("You need to include a role name or ID!")
#    if isinstance(error, commands.CommandError):
#        await ctx.channel.send("Och! Something wrong! Don't worry \;\)")

# Error handler for prefix function
#@change_prefix.error
#async def change_prefix_error(ctx, error):
#    if isinstance(error, commands.MissingRequiredArgument):
#        await ctx.channel.send("You have to specify a new prefix!")
