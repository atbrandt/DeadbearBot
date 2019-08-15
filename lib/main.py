import discord
import asyncio
import aiohttp
import configparser
import db
import re
from discord.ext import commands
from discord.utils import get
from pathlib import Path


# Setting platform-independent path to config file
CONFIG = Path(__file__).parent / "init.cfg"


# Initialize configparser settings
CFGPARSER = configparser.ConfigParser(empty_lines_in_values=False)
CFGPARSER.optionxform = lambda option: option


# Set a reference of default options that must exist in config
CFGDEFAULT = {'Token': '',
              'Prefix': '-',
              'AutoRoleID': '',
              'ReactChannelID': '',
              'ReactMessageID': '',
              'GreetChannelID': '',
              'GreetMessage': '',
              'LeaveChannelID': '',
              'LeaveMessage': ''}


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
        write_cfg('Settings', Token=input("Enter your bot's token: "))


# Initialize the bot and set the default command prefix
bot = commands.Bot(command_prefix=CFGPARSER['Settings']['Prefix'])


# Check permissions before executing command
def check_perms(invoker):
    print(invoker)
    if invoker != 198945101739851776:
        return False
    else:
        return True


# Testing command
@bot.command(name='test')
async def hello_world(ctx):
    print(f"Message sent in {ctx.channel} from {ctx.author.id}")
    await ctx.channel.send(f"Hello {ctx.author}!")


# Describe item by name in database
@bot.command(name='describe')
async def describe_item(ctx, item):
    gotItem = get_item(item)

    if item is not None:
        await ctx.channel.send(gotItem['description'])
    else:
        await ctx.channel.send(f"Item not found")


# Change the default bot prefix
@bot.command(name='ChangePrefix',
             description=("Changes the default bot command prefix. Usage is "
                          "\`{bot.command_prefix}prefix \(New prefix\)\`."),
             brief="Change bot prefix",
             aliases=['prefix'])
async def change_prefix(ctx, option):
    if not check_perms(ctx.author.id):
        await ctx.channel.send("YOU LACK PERMISSION")
        return
    write_cfg('Settings', Prefix=option)
    bot.command_prefix = option
    await ctx.channel.send(f"My command prefix is now \"{option}\".")


# Allow users to self-assign roles
@bot.command(name='GiveMeRole',
             description=("Assigns or removes a specified role name or ID "
                          "to yourself."),
             brief="Assign or remove role.",
             aliases=["gimmie"])
async def set_role(ctx, role):
    if not check_perms(ctx.author.id):
        await ctx.channel.send("YOU LACK PERMISSION")
        return
    if role.isdigit():
        gotRole = ctx.guild.get_role(int(role))
    else:
        gotRole = get(ctx.guild.roles, name=role)

    if gotRole is not None:
        if gotRole not in ctx.author.roles:
            await ctx.author.add_roles(gotRole, reason="SetRole")
            await ctx.channel.send(f"Gave you the \"{gotRole.name}\" role.")
        else:
            await ctx.author.remove_roles(gotRole, reason="SetRole")
            await ctx.channel.send(f"Removed your \"{gotRole.name}\" role.")
    else:
        await ctx.channel.send("No role found! Check the name or ID entered.")


# Manage a role to be assigned upon joining guild
@bot.command(name='AutoRole',
             description=("Sets a role that users get automatically upon "
                          "joining the server. Usage is `-arole set "
                          "\(Role name or ID string\)`. Pass \"enable\" or"
                          " \"disable\" to turn the auto-role on or off."),
             brief="Modify auto-role settings.",
             aliases=["arole"])
async def auto_role(ctx, *role):
    if not check_perms(ctx.author.id):
        await ctx.channel.send("YOU LACK PERMISSION")
        return
    if role:
        role = role[0]
        if role.isdigit():
            gotRole = ctx.guild.get_role(int(role))
        else:
            gotRole = get(ctx.guild.roles, name=role)

        if gotRole is not None:
            write_cfg('Settings', AutoRoleID=str(gotRole.id))
            await ctx.channel.send(f"Added \"{gotRole.name}\" the auto-role "
                                    "list.")
        else:
            await ctx.channel.send("No role found! Check the name or ID "
                                   "entered.")
    else:
        write_cfg('Settings', AutoRoleID='')
        await ctx.channel.send("The auto-role is now cleared.")


# Set the greet message channel
@bot.command(name='GuildGreet',
             description=("Configures the automatic greeting message when "
                          "users join the server."),
             brief="Modify greet message settings.",
             aliases=["gg"])
async def guild_greet_channel(ctx):
    if not check_perms(ctx.author.id):
        await ctx.channel.send("YOU LACK PERMISSION")
        return

    if CFGPARSER['Settings']['GreetChannelID'] == '':
        write_cfg('Settings', GreetChannelID=str(ctx.channel.id))
        await ctx.channel.send(f"Greeting enabled in \"{ctx.channel}\".")
    elif CFGPARSER['Settings']['GreetChannelID'] == str(ctx.channel.id):
        write_cfg('Settings', GreetChannelID='')
        await ctx.channel.send("Greeting disabled.")
    else:
        curGreetChannel = int(CFGPARSER['Settings']['GreetChannelID'])
        gotChannel = bot.get_channel(curGreetChannel)
        await ctx.channel.send(f"Disable the greeting by running this "
                               f"command in \"{gotChannel.name}\".")


# Set the greet message
@bot.command(name='GuildGreetMessage',
             description=("Sets the automatic greeting message."),
             brief="Modify greet message.",
             aliases=["ggmsg"])
async def guild_greet_message(ctx, message):
    if not check_perms(ctx.author.id):
        await ctx.channel.send("YOU LACK PERMISSION")
        return

    write_cfg('Settings', GreetMessage=message)
    await ctx.channel.send(f"The greet message is now: \"{message}\"")


# Set the leave message channel
@bot.command(name='GuildLeave',
             description=("Configures the automatic greeting message when "
                          "users join the server."),
             brief="Modify greet message settings.",
             aliases=["gl"])
async def guild_farewell_channel(ctx):
    if not check_perms(ctx.author.id):
        await ctx.channel.send("YOU LACK PERMISSION")
        return

    if CFGPARSER['Settings']['LeaveChannelID'] == '':
        write_cfg('Settings', LeaveChannelID=str(ctx.channel.id))
        await ctx.channel.send(f"Farewell enabled in \"{ctx.channel}\".")
    elif CFGPARSER['Settings']['LeaveChannelID'] == str(ctx.channel.id):
        write_cfg('Settings', LeaveChannelID='')
        await ctx.channel.send("Farewell disabled.")
    else:
        curLeaveChannel = int(CFGPARSER['Settings']['LeaveChannelID'])
        gotChannel = bot.get_channel(curLeaveChannel)
        await ctx.channel.send(f"Disable the greeting by running this "
                               f"command in \"{gotChannel.name}\".")


# Set the leave message
@bot.command(name='GuildLeaveMessage',
             description=("Sets the automatic greeting message."),
             brief="Modify greet message.",
             aliases=["glmsg"])
async def guild_farewell_message(ctx, message):
    if not check_perms(ctx.author.id):
        await ctx.channel.send("YOU LACK PERMISSION")
        return

    write_cfg('Settings', LeaveMessage=message)
    await ctx.channel.send(f"The leave message is now: \"{message}\"")


# Command to set a message as a hook for reaction roles
@bot.command(name='ReactionRoleHook',
             description=("Sets a given message in a given channel as a "
                          "source hook for reaction roles."),
             brief="Set reaction roles hook",
             aliases=['rrhook'])
async def add_rr_hook(ctx, channelID: int, messageID: int):
    if not check_perms(ctx.author.id):
        await ctx.channel.send("YOU LACK PERMISSION")
        return

    try:
        await bot.get_channel(channelID).fetch_message(messageID)
    except NotFound:
        await ctx.channel.send("No message found! Check the IDs and make "
                               "sure I have access to the right channel.")
        return

    rrhookID = db.add_reaction_role_hook(channelID, messageID)
    await ctx.channel.send(f"Added a reaction role hook, ID = {rrhookID}")


# Command to set a reaction role
@bot.command(name='ReactionRole',
             description=("Adds a reaction role using a given emoji and "
                          "role id."),
             brief="Create a reaction role",
             aliases=['rr'])
async def add_rr(ctx, emoji, role, messageID):
    if not check_perms(ctx.author.id):
        await ctx.channel.send("YOU LACK PERMISSION")
        return

    emojiID = re.sub('(<|>|:.*?:)', '', emoji)

    if emojiID.isdigit():
        emoji = bot.get_emoji(emojiID)

    msgHook = db.get_hook_by_message(messageID)

    if msgHook is not None:
        messageID = int(msgHook['message_id'])
        channelID = int(msgHook['channel_id'])

        try:
            gotMsg = await bot.get_channel(channelID).fetch_message(messageID)
        except NotFound:
            await ctx.channel.send("Can't find the reaction role hook!")
            return

        if role.isdigit():
            gotRole = ctx.guild.get_role(int(role))
        else:
            gotRole = get(ctx.guild.roles, name=role)

        if gotRole is not None:
            rrID = db.add_reaction_role(emoji, gotRole.id, msgHook['id'])
            await gotMsg.add_reaction(emoji)
            await ctx.channel.send(f"Set the \"{emoji}\" to give the "
                                   f"{gotRole.name} role. ID = {rrID}")
        else:
            await ctx.channel.send("No role found! Check the name or ID "
                                   "entered.")
    else:
        await ctx.channel.send("You need to configure a 'rrhook' first!")


# Command to delete a reaction role
@bot.command(name='DeleteReactionRole',
             description=("Removes a reaction role by its ID."),
             brief="Remove a reaction role",
             aliases=['rrdel'])
async def delete_rr(ctx, rrID):
    if not check_perms(ctx.author.id):
        await ctx.channel.send("YOU LACK PERMISSION")
        return
    if rrID.isdigit():
        db.delete_reaction_role(rrID)
        await ctx.channel.send(f"Removed that entry.")
    else:
        await ctx.channel.send("You must give the ID of the entry to remove.")


# Command to list all reaction roles
@bot.command(name='ListReactRoles',
             description=("Lists all reaction roles in database."),
             brief="List reaction roles",
             aliases=['rrlist'])
async def list_rr(ctx):
    if not check_perms(ctx.author.id):
        await ctx.channel.send("YOU LACK PERMISSION")
        return
    await ctx.channel.send(db.get_all_reaction_roles())


# Command to add a voice chat role
@bot.command(name='VoiceChatRole',
             description=("Sets a given role to be added to anyone that "
                          "joins a specified voice channel."),
             brief="Add voice chat role",
             aliases=['vcr'])
async def add_vcr(ctx, vchannelID, role):
    if not check_perms(ctx.author.id):
        await ctx.channel.send("YOU LACK PERMISSION")
        return
    gotChannel = bot.get_channel(int(vchannelID))

    if role.isdigit():
        gotRole = ctx.guild.get_role(int(role))
    else:
        gotRole = get(ctx.guild.roles, name=role)

    if gotRole is not None and gotChannel is not None:
        db.add_voice_channel_role(gotChannel.id, gotRole.id)
        await ctx.channel.send(f"Users joining {gotChannel.name} will "
                               f"automatically get the {gotRole.name} role.")
    else:
        await ctx.channel.send("One of the IDs is malformed!")


# Command to delete a voice chat role
@bot.command(name='DeleteVoiceChatRole',
             description=("Removes a voice chat role by its ID."),
             brief="Remove a vc role",
             aliases=['vcrdel'])
async def delete_vcr(ctx, vcrID):
    if not check_perms(ctx.author.id):
        await ctx.channel.send("YOU LACK PERMISSION")
        return
    if vcrID.isdigit():
        db.delete_voice_channel_role(vcrID)
        await ctx.channel.send("Removed that entry.")
    else:
        await ctx.channel.send("You must give the ID of the entry to remove.")


# Command to list all voice chat roles
@bot.command(name='ListVoiceChatRoles',
             description=("Lists all voice chat roles in database."),
             brief="List voice chat roles",
             aliases=['vcrlist'])
async def list_vcr(ctx):
    if not check_perms(ctx.author.id):
        await ctx.channel.send("YOU LACK PERMISSION")
        return
    await ctx.channel.send(db.get_all_voice_channel_roles())


# Get list of roles (with IDs) on guild
@bot.command(name='GetRoleIDs',
             description=("Returns list of roles on server with IDs."),
             brief="Get all roles with IDs",
             aliases=['roles'])
async def get_roles(ctx):
    if not check_perms(ctx.author.id):
        await ctx.channel.send("YOU LACK PERMISSION")
        return
    await ctx.channel.send(f"```{ctx.guild.roles}```")


# Get list of emojis (with IDs) on guild
@bot.command(name='GetEmojiIDs',
             description=("Returns list of emojis on server with IDs."),
             brief="Get all emojis with IDs",
             aliases=['emojis'])
async def get_emojis(ctx):
    if not check_perms(ctx.author.id):
        await ctx.channel.send("YOU LACK PERMISSION")
        return
    await ctx.channel.send(f"```{ctx.guild.emojis}```")


# Get list of channels (with IDs) on guild
@bot.command(name='GetChannelIDs',
             description=("Returns list of channels on server with IDs."),
             brief="Get all channels with IDs",
             aliases=['channels'])
async def get_channels(ctx):
    if not check_perms(ctx.author.id):
        await ctx.channel.send("YOU LACK PERMISSION")
        return
    await ctx.channel.send(f"```{ctx.guild.channels}```")


# Reaction Role hook function
@bot.event
async def on_raw_reaction_add(payload):
    guild = bot.get_guild(payload.guild_id)
    member = guild.get_member(payload.user_id)
    if member.bot:
        return
    rrHookList = db.get_all_hooks()
    print(rrHookList)
    if payload.message_id == int(rrHookList['message_id']):
        emoji = str(payload.emoji)
        gotRR = db.get_reaction_roles_by_hook(rrhooklist['id'], emoji)
        print(gotRR)
        if gotRR is not None:
            gotRole = guild.get_role(gotRR['role_id'])
            if gotRole not in member.roles:
                await member.add_roles(gotRole, reason="ReactionRole")


# Reaction Role hook function
@bot.event
async def on_raw_reaction_remove(payload):
    guild = bot.get_guild(payload.guild_id)
    member = guild.get_member(payload.user_id)
    if member.bot:
        return
    rrHookList = db.get_all_hooks()
    if payload.message_id == int(rrHookList['message_id']):
        emoji = str(payload.emoji)
        gotRR = db.get_reaction_roles_by_hook(rrhooklist['id'], emoji)
        if gotRR is not None:
            gotRole = guild.get_role(gotRR['roleID'])
            if gotRole in member.roles:
                await member.remove_roles(gotRole, reason="ReactionRole")


# Voice Chat Role hook function
@bot.event
async def on_voice_state_update(member, before, after):
    if before.channel is not None:
        gotVCR = db.get_voice_channel_role(before.channel.id)
        if gotVCR is not None:
            guild = bot.get_guild(before.channel.guild.id)
            gotRole = guild.get_role(gotVCR['roleID'])
            await member.remove_roles(gotRole, reason="VCRLeave")
    if after.channel is not None:
        gotVCR = db.get_voice_channel_role(after.channel.id)
        if gotVCR is not None:
            guild = bot.get_guild(after.channel.guild.id)
            gotRole = guild.get_role(gotVCR['roleID'])
            await member.add_roles(gotRole, reason="VCRJoin")


# Do stuff to users upon joining guild
@bot.event
async def on_member_join(member):
    if CFGPARSER['Settings']['AutoRoleID'] != '':
        role = int(CFGPARSER['Settings']['AutoRoleID'])
        guild = member.guild
        getRole = guild.get_role(role)
        await member.add_roles(getRole, reason="AutoRole")
    if CFGPARSER['Settings']['GreetChannelID'] != '':
        channel = int(CFGPARSER['Settings']['GreetChannelID'])
        message = CFGPARSER['Settings']['GreetMessage']
        gotChannel = bot.get_channel(channel)
        await gotChannel.send(message.format(member=member))


# Do stuff to users upon leaving guild
@bot.event
async def on_member_remove(member):
    print(member.name)
    if CFGPARSER['Settings']['LeaveChannelID'] != '':
        channel = int(CFGPARSER['Settings']['LeaveChannelID'])
        message = CFGPARSER['Settings']['LeaveMessage']
        gotChannel = bot.get_channel(channel)
        await gotChannel.send(message.format(member=member))


# Output info to console once bot is initialized and ready
@bot.event
async def on_ready():
    print(f"{bot.user.name} is ready, user ID is {bot.user.id}")
    print("------")


# Run the program
db.setup_database()
bot.run(CFGPARSER['Settings']['Token'])


# Error handler for auto_role function
# @auto_role.error
# async def auto_role_error(ctx, error):
#    if isinstance(error, commands.MissingRequiredArgument):
#        await ctx.channel.send("You need to include a role name or ID!")
#    if isinstance(error, commands.CommandError):
#        await ctx.channel.send("Och! Something wrong! Don't worry \;\)")

# Error handler for prefix function
# @change_prefix.error
# async def change_prefix_error(ctx, error):
#    if isinstance(error, commands.MissingRequiredArgument):
#        await ctx.channel.send("You have to specify a new prefix!")
