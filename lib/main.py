import os
from pathlib import Path
from dotenv import load_dotenv
import discord
from discord.ext import commands
from discord.utils import get
import config
import db


# Setting platform-independent path to environment variables
ENVFILE = Path(__file__).parent / "secret.env"


# Loading environment variables and checking for secret token presence
if ENVFILE.exists():
    load_dotenv(dotenv_path=ENVFILE)
    token = os.getenv('DEADBEAR_TOKEN')
else:
    print("No bot token found!")
    token = input("Enter your bot's token: ")
    with Path.open(ENVFILE, 'w', encoding='utf-8') as file:
        file.write(f"export DEADBEAR_TOKEN=\'{token}\';")    


# Read the bot's config.yml and import it
CONFIG = config.read_cfg()


# Initialize the bot and set the default command prefix
bot = commands.Bot(command_prefix=CONFIG['Global']['Prefix'])


# Set up converter shorthands. These are coroutines, must be awaited.
# Usage is *.convert(ctx, arg)
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


# Example of checking something before executing command
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
    gotItem = db.get_item(item)

    if item is not None:
        await ctx.channel.send(gotItem['description'])
    else:
        await ctx.channel.send(f"Item not found")


# Change the default bot prefix
@bot.command(name='ChangePrefix',
             description="Changes the default bot command prefix.",
             brief="Change bot prefix",
             aliases=['prefix'])
@commands.is_owner()
async def change_prefix(ctx, prefix):
    CONFIG['Global']['Prefix'] = prefix
    config.write_cfg(CONFIG)
    bot.command_prefix = prefix
    await ctx.channel.send(f"My command prefix is now \"{prefix}\".")


# Assign specific roles to specific users
@bot.group(name='ToggleRole',
           description="Assigns or removes a specified role to a specified "
                       "target. Pass a \"user name or ID\" and a \"role "
                       "name or ID\" to toggle that user's role.",
           brief="Assign or remove role by name or ID",
           aliases=['trole'])
@commands.is_owner()
async def toggle_role(ctx, member: discord.Member, role: discord.Role):
    if None not in (member, role):
        if role not in member.roles:
            await member.add_roles(role,
                                   reason=f"GiveRole by {ctx.author.name}")
            await ctx.channel.send(f"Gave {member.name} the \"{role.name}"
                                   f"\" role.")
        else:
            await member.remove_roles(role,
                                      reason=f"GiveRole by {ctx.author.name}")
            await ctx.channel.send(f"Removed the \"{role.name}\" role from "
                                   f"{member.name}.")


# Manage a role to be assigned upon joining guild
@bot.command(name='AutoRole',
             description="Sets a role that users get automatically upon "
                         "join. Pass `\"role name or role ID\"` to enable "
                         "the auto-role. Pass nothing to turn it off.",
             brief="Modify auto-role settings.",
             aliases=["arole"])
@commands.is_owner()
async def auto_role(ctx, role: discord.Role):
    if role.id not in CONFIG['AutoRole']:
        CONFIG['AutoRole'] = role.id
        config.write_cfg(CONFIG)
        await ctx.channel.send(f"Added \"{role.name}\" to auto-role.")
    else:
        CONFIG['AutoRole'] = None
        config.write_cfg(CONFIG)
        await ctx.channel.send(f"Removed \"{role.name}\" from auto-role.")
# ctx.channel.send("No role found! Check the name or ID entered.")


# Set the greet message channel
@bot.command(name='GuildGreet',
             description="Configures the automatic greeting message when "
                         "users join the server.",
             brief="Modify greet message settings.",
             aliases=["gg"])
@commands.is_owner()
async def guild_greet_channel(ctx):
    if CONFIG['Greetings']['ChannelID'] == None:
        CONFIG['Greetings']['ChannelID'] = ctx.channel.id
        config.write_cfg(CONFIG)
        await ctx.channel.send(f"Greeting enabled in \"{ctx.channel}\".")
    elif CONFIG['Greetings']['ChannelID'] == ctx.channel.id:
        CONFIG['Greetings']['ChannelID'] = None
        config.write_cfg(CONFIG)
        await ctx.channel.send("Greeting disabled.")
    else:
        curGreetChannel = int(CONFIG['Greetings']['ChannelID'])
        gotChannel = bot.get_channel(curGreetChannel)
        await ctx.channel.send(f"Disable the greeting by running this "
                               f"command in \"{gotChannel.name}\".")


# Set the greet message
@bot.command(name='GuildGreetMessage',
             description="Sets the automatic greeting message.",
             brief="Modify greet message.",
             aliases=["ggmsg"])
@commands.is_owner()
async def guild_greet_message(ctx, message):
    CONFIG['Greetings']['Message'] = message
    config.write_cfg(CONFIG)
    await ctx.channel.send(f"The greet message is now: \"{message}\"")


# Set the leave message channel
@bot.command(name='GuildLeave',
             description="Configures the automatic greeting message when "
                         "users join the server.",
             brief="Modify greet message settings.",
             aliases=["gl"])
@commands.is_owner()
async def guild_farewell_channel(ctx):
    if CONFIG['Farewells']['ChannelID'] == None:
        CONFIG['Farewells']['ChannelID'] = ctx.channel.id
        config.write_cfg(CONFIG)
        await ctx.channel.send(f"Farewell enabled in \"{ctx.channel}\".")
    elif CONFIG['Farewells']['ChannelID'] == ctx.channel.id:
        CONFIG['Farewells']['ChannelID'] = None
        config.write_cfg(CONFIG)
        await ctx.channel.send("Farewell disabled.")
    else:
        curLeaveChannel = int(CONFIG['Farewells']['ChannelID'])
        gotChannel = bot.get_channel(curLeaveChannel)
        await ctx.channel.send(f"Disable the greeting by running this "
                               f"command in \"{gotChannel.name}\".")


# Set the leave message
@bot.command(name='GuildLeaveMessage',
             description="Sets the automatic greeting message.",
             brief="Modify greet message.",
             aliases=["glmsg"])
@commands.is_owner()
async def guild_farewell_message(ctx, message):
    CONFIG['Farewells']['Message'] = message
    config.write_cfg(CONFIG)
    await ctx.channel.send(f"The leave message is now: \"{message}\"")


# Command to set a message as a hook for reaction roles
@bot.command(name='ReactionRoleHook',
             description="Sets a given message in a given channel as a "
                         "source hook for reaction roles.",
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
             description="Deletes a reaction role hook by its id.",
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
             description="Lists all reaction role hooks in database.",
             brief="List reaction roles",
             aliases=['listrrhook'])
@commands.is_owner()
async def list_rr_hook(ctx):
    hookList = dict(db.get_all_hooks())
    await ctx.channel.send(hookList)


# Command to set a reaction role
@bot.command(name='ReactionRole',
             description="Adds a reaction role using a given emoji and "
                         "role id.",
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
             description="Removes a reaction role by its ID.",
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
             description="Lists all reaction roles in database.",
             brief="List reaction roles",
             aliases=['listrr'])
@commands.is_owner()
async def list_rr(ctx):
    rrList = dict(db.get_all_reaction_roles())
    await ctx.channel.send(rrList)


# Command to add a voice chat role
@bot.command(name='VoiceChatRole',
             description="Sets a given role to be added to anyone that "
                         "joins a specified voice channel.",
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
             description="Removes a voice chat role by its ID.",
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
             description="Lists all voice chat roles in database.",
             brief="List voice chat roles",
             aliases=['listvcr'])
@commands.is_owner()
async def list_vcr(ctx):
    vcrList = dict(db.get_all_voice_channel_roles())
    await ctx.channel.send(vcrList)


# Get list of roles (with IDs) on guild
@bot.command(name='GetRoleIDs',
             description="Returns list of roles on server with IDs.",
             brief="Get all roles with IDs",
             aliases=['roles'])
@commands.is_owner()
async def get_roles(ctx):
    await ctx.channel.send(f"```{ctx.guild.roles}```")


# Get list of emojis (with IDs) on guild
@bot.command(name='GetEmojiIDs',
             description="Returns list of emojis on server with IDs.",
             brief="Get all emojis with IDs",
             aliases=['emojis'])
@commands.is_owner()
async def get_emojis(ctx):
    await ctx.channel.send(f"```{ctx.guild.emojis}```")


# Get list of channels (with IDs) on guild
@bot.command(name='GetChannelIDs',
             description="Returns list of channels on server with IDs.",
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
            await member.add_roles(role, reason="VCRJoin")


# Do stuff to users upon joining guild
@bot.event
async def on_member_join(member):
    if CONFIG['AutoRole'] != '':
        role = int(CONFIG['AutoRole'])
        getRole = member.guild.get_role(role)
        await member.add_roles(getRole, reason="AutoRole")
    if CONFIG['Greetings']['ChannelID'] != None:
        channel = int(CONFIG['Greetings']['ChannelID'])
        message = CONFIG['Greetings']['Message']
        gotChannel = bot.get_channel(channel)
        await gotChannel.send(message.format(member=member))


# Do stuff to users upon leaving guild
@bot.event
async def on_member_remove(member):
    if CONFIG['Farewells']['ChannelID'] != None:
        channel = int(CONFIG['Farewells']['ChannelID'])
        message = CONFIG['Farewells']['Message']
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
bot.run(token)


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
