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


# Set up converter shorthands. These must be awaited
convMember = commands.MemberConverter()
convMessage = commands.MessageConverter()
convUser = commands.UserConverter()
convChannel = commands.TextChannelConverter()
convVoice = commands.VoiceChannelConverter()
convCategory = commands.CategoryChannelConverter()
convRole = commands.RoleConverter()
convInvite = commands.InviteConverter()
convEmoji = commands.EmojiConverter()
convPartialEmoji = commands.PartialEmojiConverter()
convGame = commands.GameConverter()
convColour = commands.ColourConverter()


# Check something before executing command
# def check_perms(invoker):
#    def predicate(ctx):
#        return ctx.foo.bar == something
#    return commands.check(predicate)


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
@commands.is_owner()
async def change_prefix(ctx, option):
    write_cfg('Settings', Prefix=option)
    bot.command_prefix = option
    await ctx.channel.send(f"My command prefix is now \"{option}\".")


# Allow users to self-assign roles
@bot.command(name='GiveMeRole',
             description=("Assigns or removes a specified role name or ID "
                          "to yourself."),
             brief="Assign or remove role.",
             aliases=["gimmie"])
@commands.is_owner()
async def set_role(ctx, role: discord.Role):
    if role not in ctx.author.roles:
        await ctx.author.add_roles(role, reason="SetRole")
        await ctx.channel.send(f"Gave you the \"{role.name}\" role.")
    else:
        await ctx.author.remove_roles(gotRole, reason="SetRole")
        await ctx.channel.send(f"Removed your \"{role.name}\" role.")
# ctx.channel.send("No role found! Check the name or ID entered.")


# Manage a role to be assigned upon joining guild
@bot.command(name='AutoRole',
             description=("Sets a role that users get automatically upon "
                          "joining the server. Usage is `-arole set "
                          "\(Role name or ID string\)`. Pass \"enable\" or"
                          " \"disable\" to turn the auto-role on or off."),
             brief="Modify auto-role settings.",
             aliases=["arole"])
@commands.is_owner()
async def auto_role(ctx, *role):
    if role:
        role = await convRole.convert(ctx, role[0])
        write_cfg('Settings', AutoRoleID=str(role.id))
        await ctx.channel.send(f"Added \"{role.name}\" the auto-role list.")
# ctx.channel.send("No role found! Check the name or ID entered.")
    else:
        write_cfg('Settings', AutoRoleID='')
        await ctx.channel.send("The auto-role is now cleared.")


# Set the greet message channel
@bot.command(name='GuildGreet',
             description=("Configures the automatic greeting message when "
                          "users join the server."),
             brief="Modify greet message settings.",
             aliases=["gg"])
@commands.is_owner()
async def guild_greet_channel(ctx):
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
@commands.is_owner()
async def guild_greet_message(ctx, message):
    write_cfg('Settings', GreetMessage=message)
    await ctx.channel.send(f"The greet message is now: \"{message}\"")


# Set the leave message channel
@bot.command(name='GuildLeave',
             description=("Configures the automatic greeting message when "
                          "users join the server."),
             brief="Modify greet message settings.",
             aliases=["gl"])
@commands.is_owner()
async def guild_farewell_channel(ctx):
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
@commands.is_owner()
async def guild_farewell_message(ctx, message):
    write_cfg('Settings', LeaveMessage=message)
    await ctx.channel.send(f"The leave message is now: \"{message}\"")


# Command to set a message as a hook for reaction roles
@bot.command(name='ReactionRoleHook',
             description=("Sets a given message in a given channel as a "
                          "source hook for reaction roles."),
             brief="Set reaction role hook",
             aliases=['rrhook'])
@commands.is_owner()
async def add_rr_hook(ctx, message):
    # ctx.channel.send("No message found! Check the ID and make sure
    # I have access to the right channel.")
    rrhookID = db.add_reaction_role_hook(message)
    await ctx.channel.send(f"Added a reaction role hook. ID = {rrhookID}")


# Command to delete a message hook for reaction roles
@bot.command(name='DeleteReactionRoleHook',
             description=("Deletes a reaction role hook by its id."),
             brief="Delete reaction role hook",
             aliases=['delrrhook'])
@commands.is_owner()
async def delete_rr_hook(ctx, hookID):
    if hookID.isdigit():
        db.delete_reaction_role_hook(hookID)
        await ctx.channel.send(f"Removed reaction role entry {hookID}.")
    else:
        await ctx.channel.send("You must give the ID of the entry to remove.")


# Command to list all reaction role hooks
@bot.command(name='ListReactRoleHooks',
             description=("Lists all reaction role hooks in database."),
             brief="List reaction roles",
             aliases=['listrrhook'])
@commands.is_owner()
async def list_rr_hook(ctx):
    hookList = db.get_all_hooks()
    await ctx.channel.send(hookList)


# Command to set a reaction role
@bot.command(name='ReactionRole',
             description=("Adds a reaction role using a given emoji and "
                          "role id."),
             brief="Create a reaction role",
             aliases=['rr'])
@commands.is_owner()
async def add_rr(ctx, hookID, emoji, role: discord.Role):
    rrHook = db.get_hook_by_id(hookID)
    if rrHook is not None:
        message = await convMessage.convert(ctx, rrHook['channel_message_id'])
# ctx.channel.send("Can't find the reaction role hook!")
        if "<" in emoji:
            emoji = await convEmoji.convert(ctx, emoji)
            rrID = db.add_reaction_role(str(emoji.id), role.id, rrHook['id'])
        else:
            rrID = db.add_reaction_role(emoji, role.id, rrHook['id'])
        await message.add_reaction(emoji)
        await ctx.channel.send(f"Set the \"{emoji}\" to give the {role.name} "
                               f"role. ID = {rrID}")
# ctx.channel.send("No role found! Check the name or ID entered.")
    else:
        await ctx.channel.send("No hook found for that ID.")


# Command to delete a reaction role
@bot.command(name='DeleteReactionRole',
             description=("Removes a reaction role by its ID."),
             brief="Remove a reaction role",
             aliases=['delrr'])
@commands.is_owner()
async def delete_rr(ctx, rrID):
    if rrID.isdigit():
        db.delete_reaction_role(rrID)
        await ctx.channel.send(f"Removed reaction role entry {rrID}.")
    else:
        await ctx.channel.send("You must give the ID of the entry to remove.")


# Command to list all reaction roles
@bot.command(name='ListReactRoles',
             description=("Lists all reaction roles in database."),
             brief="List reaction roles",
             aliases=['listrr'])
@commands.is_owner()
async def list_rr(ctx):
    rrList = db.get_all_reaction_roles()
    await ctx.channel.send(rrList)


# Command to add a voice chat role
@bot.command(name='VoiceChatRole',
             description=("Sets a given role to be added to anyone that "
                          "joins a specified voice channel."),
             brief="Add voice chat role",
             aliases=['vcr'])
@commands.is_owner()
async def add_vcr(ctx, vchannel: discord.VoiceChannel, role: discord.Role):
    db.add_voice_channel_role(vchannel.id, role.id)
    await ctx.channel.send(f"Users joining \"{vchannel.name}\" will "
                           f"automatically get the \"{role.name}\" role.")
# ctx.channel.send("One of the IDs is malformed!")


# Command to delete a voice chat role
@bot.command(name='DeleteVoiceChatRole',
             description=("Removes a voice chat role by its ID."),
             brief="Remove a vc role",
             aliases=['delvcr'])
@commands.is_owner()
async def delete_vcr(ctx, vcrID):
    if vcrID.isdigit():
        db.delete_voice_channel_role(vcrID)
        await ctx.channel.send("Removed that entry.")
    else:
        await ctx.channel.send("You must give the ID of the entry to remove.")


# Command to list all voice chat roles
@bot.command(name='ListVoiceChatRoles',
             description=("Lists all voice chat roles in database."),
             brief="List voice chat roles",
             aliases=['listvcr'])
@commands.is_owner()
async def list_vcr(ctx):
    vcrList = db.get_all_voice_channel_roles()
    await ctx.channel.send(vcrList)


# Get list of roles (with IDs) on guild
@bot.command(name='GetRoleIDs',
             description=("Returns list of roles on server with IDs."),
             brief="Get all roles with IDs",
             aliases=['roles'])
@commands.is_owner()
async def get_roles(ctx):
    await ctx.channel.send(f"```{ctx.guild.roles}```")


# Get list of emojis (with IDs) on guild
@bot.command(name='GetEmojiIDs',
             description=("Returns list of emojis on server with IDs."),
             brief="Get all emojis with IDs",
             aliases=['emojis'])
@commands.is_owner()
async def get_emojis(ctx):
    await ctx.channel.send(f"```{ctx.guild.emojis}```")


# Get list of channels (with IDs) on guild
@bot.command(name='GetChannelIDs',
             description=("Returns list of channels on server with IDs."),
             brief="Get all channels with IDs",
             aliases=['channels'])
@commands.is_owner()
async def get_channels(ctx):
    await ctx.channel.send(f"```{ctx.guild.channels}```")


# Reaction Role add hook function
@bot.event
async def on_raw_reaction_add(payload):
    if payload.user_id != bot.user.id:
        chnlmsgID = str(payload.channel_id) + "-" + str(payload.message_id)
        rrHook = db.get_hook_by_message(chnlmsgID)
    else:
        return

    if rrHook is not None:
        if payload.emoji.is_custom_emoji():
            emoji = str(payload.emoji.id)
        else:
            emoji = payload.emoji.name
        gotRR = db.get_reaction_role(rrHook['id'], emoji)
    else:
        return

    if gotRR is not None:
        guild = bot.get_guild(payload.guild_id)
        member = guild.get_member(payload.user_id)
        role = guild.get_role(gotRR['role_id'])
        if role not in member.roles:
            await member.add_roles(role, reason="ReactionRole")


# Reaction Role remove hook function
@bot.event
async def on_raw_reaction_remove(payload):
    if payload.user_id != bot.user.id:
        chnlmsgID = str(payload.channel_id) + "-" + str(payload.message_id)
        rrHook = db.get_hook_by_message(chnlmsgID)
    else:
        return

    if rrHook is not None:
        if payload.emoji.is_custom_emoji():
            emoji = str(payload.emoji.id)
        else:
            emoji = payload.emoji.name
        gotRR = db.get_reaction_role(rrHook['id'], emoji)
    else:
        return

    if gotRR is not None:
        guild = bot.get_guild(payload.guild_id)
        member = guild.get_member(payload.user_id)
        role = guild.get_role(gotRR['role_id'])
        if role in member.roles:
            await member.remove_roles(role, reason="ReactionRole")


# Voice Chat Role hook function
@bot.event
async def on_voice_state_update(member, before, after):
    if before.channel is not None:
        gotVCR = db.get_voice_channel_role(before.channel.id)
        if gotVCR is not None:
            role = member.guild.get_role(gotVCR['role_id'])
            await member.remove_roles(role, reason="VCRLeave")
    if after.channel is not None:
        gotVCR = db.get_voice_channel_role(after.channel.id)
        if gotVCR is not None:
            role = member.guild.get_role(gotVCR['role_id'])
            await member.add_roles(gotRole, reason="VCRJoin")


# Do stuff to users upon joining guild
@bot.event
async def on_member_join(member):
    if CFGPARSER['Settings']['AutoRoleID'] != '':
        role = int(CFGPARSER['Settings']['AutoRoleID'])
        getRole = member.guild.get_role(role)
        await member.add_roles(getRole, reason="AutoRole")
    if CFGPARSER['Settings']['GreetChannelID'] != '':
        channel = int(CFGPARSER['Settings']['GreetChannelID'])
        message = CFGPARSER['Settings']['GreetMessage']
        gotChannel = bot.get_channel(channel)
        await gotChannel.send(message.format(member=member))


# Do stuff to users upon leaving guild
@bot.event
async def on_member_remove(member):
    if CFGPARSER['Settings']['LeaveChannelID'] != '':
        channel = int(CFGPARSER['Settings']['LeaveChannelID'])
        message = CFGPARSER['Settings']['LeaveMessage']
        gotChannel = bot.get_channel(channel)
        await gotChannel.send(message.format(member=member))


# Global error handler as temp solution
@bot.event
async def on_command_error(ctx, error):
    await ctx.channel.send(error)


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
