import os, math
from datetime import datetime, date
from typing import Union
from pathlib import Path
from dotenv import load_dotenv
import discord
from discord.ext import commands
from discord.utils import get
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


# Create callable to obtain guild-specific alias for command prefix
async def get_alias(bot, message):
    if message.guild:
        guild = message.guild.id
        prefix = db.get_cfg(guild, 'bot_alias')
        if prefix != None:
            return prefix
    return "-"


# Set up the bot and get the command prefix alias
bot = commands.Bot(command_prefix=get_alias)


# Converter shorthands. These are coroutines, must be awaited.
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


# Checking perms before executing command
def check_perms():
    def predicate(ctx):
        permrole = db.get_cfg(ctx.guild.id, "perm_role")
        gotRole = ctx.guild.get_role(permrole)
        roles = ctx.author.roles
        return gotRole in roles
    return commands.check(predicate)


class Menu:
    def __init__(self, title, desc, fields):
        self.title = title
        self.desc = desc
        self.fields = fields
    
    def embedded(self):
        embed = discord.Embed(title=self.title, description=self.desc)
        for item in self.fields:
#            fieldnum += 1
#            key = f"{fieldnum}. {item['fname']}"
            embed.add_field(name=item['fname'], value=item['fdesc'])
        embed.add_field(name="Exit", value="Type this to exit the menu.")
        return embed
        
    def selected(self, option):
        for item in self.fields:
            if item['fname'].startswith(option) or item['fname'] == option:
                return item


ptitle = "Profile Management Menu"
pdesc = "Reply with the number of the profile option you want to change:"
pfields = [{"fname": "1. Name",
           "fdesc": "Your \"name\", real or otherwise.",
           "prompt": "Submit a name, or send `clear` to reset.",
           "chars": 40,
           "format": "text",
           "dbval": "name"},
           {"fname": "2. Nickname",
           "fdesc": "What you like to be called.",
           "prompt": "Submit a nickname, or send `clear` to reset.",
           "chars": 60,
           "format": "text",
           "dbval": "nickname"},
           {"fname": "3. Age",
           "fdesc": "Your age, if you want it known.",
           "prompt": "Submit a date in the format `YYYY-MM-DD`, or send `clear` to reset.\nNote that this date will *not* show up on your profile, it's just used to calculate age.",
           "chars": 10,
           "format": "date",
           "dbval": "birthday"},
           {"fname": "4. Gender",
           "fdesc": "Whatever you identify as.",
           "prompt": "Submit whatever you want, or send `clear` to reset.",
           "chars": 60,
           "format": "text",
           "dbval": "gender"},
           {"fname": "5. Location",
           "fdesc": "Your location, specific or general.",
           "prompt": "Submit a location, or send `clear` to reset.",
           "chars": 80,
           "format": "text",
           "dbval": "location"},
           {"fname": "6. Description",
           "fdesc": "A big text box for whatever.",
           "prompt": "Submit whatever you want, or send `clear` to reset.",
           "chars": 1024,
           "format": "text",
           "dbval": "description"},
           {"fname": "7. Likes",
           "fdesc": "A list of all the things you like.",
           "prompt": "Submit items separated by commas, or send `clear` to reset.",
           "chars": 1024,
           "format": "list",
           "dbval": "likes"},
           {"fname": "8. Dislikes",
           "fdesc": "A list of all the things you hate.",
           "prompt": "Submit items separated by commas, or send `clear` to reset.",
           "chars": 1024,
           "format": "list",
           "dbval": "dislikes"}]
ProfileMenu = Menu(ptitle, pdesc, pfields)


# Testing command
@bot.command(name='test')
async def hello_world(ctx):
    print(f"Message sent in {ctx.channel} from {ctx.author.id}")
    await ctx.channel.send(f"Hello {ctx.author}!")


# Set an alias for the bot prefix
@bot.command(name='AliasPrefix',
             description="Sets an alias for the default command prefix.",
             brief="Set command prefix alias.",
             aliases=['prefix'])
@commands.guild_only()
@commands.is_owner()
async def change_prefix(ctx, prefix):
    db.set_cfg(ctx.guild.id, "bot_alias", prefix)
    await ctx.channel.send(f"My command prefix is now \"{prefix}\".")


# Set perm roles for public commands
@bot.command(name='PermissionRoles',
             description="Sets roles that can use basic commands.",
             brief="Set permrole.",
             aliases=['permrole'])
@commands.guild_only()
@commands.is_owner()
async def set_perms(ctx, role: discord.Role):
    db.set_cfg(ctx.guild.id, "perm_role", role.id)
    await ctx.channel.send(f"Added \"{role.name}\" to perm roles.")


# Assign specific roles to specific users
@bot.group(name='ToggleRole',
           description="Toggles a role for a member. Pass a role's `name` "
                       "or `id` and the member's `name` or `id` to add or "
                       "remove the role.",
           brief="Assign or remove member role by name or ID",
           aliases=['trole'])
@commands.guild_only()
@commands.is_owner()
async def toggle_role(ctx, role: discord.Role, member: discord.Member):
    author = ctx.author.name
    if role not in member.roles:
        await member.add_roles(role, reason=f"ToggleRole by {author}")
        await ctx.channel.send(f"Gave {member.name} the \"{role.name}"
                               f"\" role.")
    else:
        await member.remove_roles(role, reason=f"ToggleRole by {author}")
        await ctx.channel.send(f"Removed the \"{role.name}\" role from "
                               f"{member.name}.")


# Manage a role to be assigned upon joining guild
@bot.command(name='AutoRole',
             description="Sets a role that users get automatically when "
                         "joining the guild. Pass a role's `name` or `id` to "
                         "enable or disable the auto-role.",
             brief="Modify auto-role settings.",
             aliases=["arole"])
@commands.guild_only()
@commands.is_owner()
async def auto_role(ctx, role: discord.Role):
    autorole = db.get_cfg(ctx.guild.id, "auto_role")
    if autorole is None:
        db.set_cfg(ctx.guild.id, "auto_role", role.id)
        await ctx.channel.send(f"Added \"{role.name}\" to auto-role.")
    else:
        db.set_cfg(ctx.guild.id, "auto_role", None)
        await ctx.channel.send(f"Removed \"{role.name}\" from auto-role.")
# ctx.channel.send("No role found! Check the name or ID entered.")


# Set the greet message channel
@bot.command(name='GuildGreet',
             description="Configures the automatic greeting message when "
                         "users join the server.",
             brief="Modify greet message settings.",
             aliases=["gg"])
@commands.guild_only()
@commands.is_owner()
async def guild_greet_channel(ctx):
    greetchnl = db.get_cfg(ctx.guild.id, "greet_channel")
    if greetchnl is None:
        db.set_cfg(ctx.guild.id, "greet_channel", ctx.channel.id)
        await ctx.channel.send(f"Greeting enabled in \"{ctx.channel}\".")
    elif greetchnl == ctx.channel.id:
        db.set_cfg(ctx.guild.id, "greet_channel", None)
        await ctx.channel.send("Greeting disabled.")
    else:
        gotChannel = bot.get_channel(greetchnl)
        await ctx.channel.send("Disable the greeting by running this command "
                               f"in \"{gotChannel.name}\".")


# Set the greet message
@bot.command(name='GuildGreetMessage',
             description="Sets the automatic greeting message.",
             brief="Modify greet message.",
             aliases=["ggmsg"])
@commands.guild_only()
@commands.is_owner()
async def guild_greet_message(ctx, *, message: str):
    db.set_cfg(ctx.guild.id, "greet_message", message)
    await ctx.channel.send(f"The greet message is now: \"{message}\"")


# Set the leave message channel
@bot.command(name='GuildLeave',
             description="Configures the automatic farewell message when "
                         "users join the server.",
             brief="Modify greet message settings.",
             aliases=["gl"])
@commands.guild_only()
@commands.is_owner()
async def guild_farewell_channel(ctx):
    byechnl = db.get_cfg(ctx.guild.id, "bye_channel")
    if byechnl is None:
        db.set_cfg(ctx.guild.id, "bye_channel", ctx.channel.id)
        await ctx.channel.send(f"Farewell enabled in \"{ctx.channel}\".")
    elif byechnl == ctx.channel.id:
        db.set_cfg(ctx.guild.id, "bye_channel", None)
        await ctx.channel.send("Farewell disabled.")
    else:
        gotChannel = bot.get_channel(byechnl)
        await ctx.channel.send(f"Disable the greeting by running this "
                               f"command in \"{gotChannel.name}\".")


# Set the leave message
@bot.command(name='GuildLeaveMessage',
             description="Sets the automatic farewell message.",
             brief="Modify greet message.",
             aliases=["glmsg"])
@commands.guild_only()
@commands.is_owner()
async def guild_farewell_message(ctx, *, message: str):
    db.set_cfg(ctx.guild.id, "bye_message", message)
    await ctx.channel.send(f"The leave message is now: \"{message}\"")


# Command to set a reaction role
@bot.command(name='ReactionRole',
             description="Create a reaction role using a channel-messsage id, "
                         "emoji, and role id. To get a channel-message ID, "
                         "open the 3-dot menu for a message and shift-click "
                         "the \"Copy ID\" button.",
             brief="Create a reaction role",
             aliases=['rr'])
@commands.guild_only()
@commands.is_owner()
async def add_rr(ctx, message: discord.Message,
                emoji: Union[discord.Emoji, str],
                role: discord.Role):
    guildID = ctx.guild.id
    hookID = str(message.channel.id) + "-" + str(message.id)
    if type(emoji) is str:
        exists, rrID = db.add_reaction_role(guildID, hookID, emoji, role.id)
    else:
        exists, rrID = db.add_reaction_role(guildID, hookID, emoji.id, role.id)

    if not exists:
        await message.add_reaction(emoji)
        await ctx.channel.send(f"Set \"{emoji}\" to give the \"{role.name}\" " 
                               f"role.\nID = {rrID}")
    else:
        await ctx.channel.send(f"That already exists! ID = {rrID}")
# Note to self: Add warning for emoji that the bot doesn't have access to.


# Command to delete a reaction role
@bot.command(name='DeleteReactionRole',
             description="Removes a reaction role by its ID.",
             brief="Remove a reaction role",
             aliases=['delrr'])
@commands.guild_only()
@commands.is_owner()
async def delete_rr(ctx, rrID):
    exists = db.delete_reaction_role(rrID)
    if exists:
        await ctx.channel.send(f"Removed reaction role entry {rrID}.")
    else:
        await ctx.channel.send("No reaction role found for that ID!")


# Command to list all reaction roles
@bot.command(name='ListReactRoles',
             description="Lists all reaction roles for this guild.",
             brief="List reaction roles",
             aliases=['listrr'])
@commands.guild_only()
@commands.is_owner()
async def list_rr(ctx):
    roles = dict(db.get_reaction_roles(ctx.guild.id))
    await ctx.channel.send(roles)


# Command to add a voice chat role
@bot.command(name='VoiceRole',
             description="Sets a role to be added to anyone that joins a "
                         "specified voice channel. Pass a voice channel "
                         "`name` or `id` and a role `name` or `id`.",
             brief="Add a voice role",
             aliases=['vr'])
@commands.guild_only()
@commands.is_owner()
async def add_vr(ctx, vchannel: discord.VoiceChannel, role: discord.Role):
    guildID = ctx.guild.id
    exists, vrID = db.add_voice_role(guildID, vchannel.id, role.id)
    if not exists:
        await ctx.channel.send(f"Users joining \"{vchannel.name}\" will "
                               f"automatically get the \"{role.name}\" "
                               f"role.\nID = {vrID}")
    else:
        await ctx.channel.send(f"That already exists! ID = {vrID}")


# Command to delete a voice chat role
@bot.command(name='DeleteVoiceRole',
             description="Removes a voice role by its ID.",
             brief="Remove a vc role",
             aliases=['delvr'])
@commands.guild_only()
@commands.is_owner()
async def delete_vr(ctx, vrID):
    exists = db.delete_voice_role(vrID)
    if exists:
        await ctx.channel.send(f"Removed reaction role entry {vrID}.")
    else:
        await ctx.channel.send("No reaction role found for that ID!")


# Command to list all voice chat roles
@bot.command(name='ListVoiceRoles',
             description="Lists all voice chat roles for this guild.",
             brief="List voice chat roles",
             aliases=['listvr'])
@commands.guild_only()
@commands.is_owner()
async def list_vr(ctx):
    roles = dict(db.get_voice_roles(ctx.guild.id))
    await ctx.channel.send(roles)


# Command to return a user's profile
@bot.group(name='Profile',
           description="Display your profile information.",
           brief="Get your profile.",
           aliases=['prof'],
           invoke_without_command=True)
@commands.guild_only()
@check_perms()
async def profile(ctx, member: discord.Member=None):
#    if ctx.invoked_subcommand is None:
    if member is not None:
        dbprof = db.get_member_profile(ctx.guild.id, member.id)
    else:
        dbprof = db.get_member_profile(ctx.guild.id, ctx.author.id)
        member = ctx.author
    if dbprof['birthday'] is not None:
        born = datetime.strptime(dbprof['birthday'], "%Y-%m-%d")
        now = date.today()
        age = now.year-born.year-((now.month, now.day)<(born.month, born.day))
    else:
        age = None
    fields = {"Total XP": f"{dbprof['xp']} XP",
              "Cash On Hand": f"${dbprof['cash']}",
              "Name": f"{dbprof['name']}",
              "Nickname": f"{dbprof['nickname']}",
              "Age": f"{age}",
              "Gender": f"{dbprof['gender']}",
              "Location": f"{dbprof['location']}",
              "Description": f"{dbprof['description']}",
              "Likes": f"{dbprof['likes']}",
              "Dislikes": f"{dbprof['dislikes']}"}
    empty = fields.copy()
    for k, v in empty.items():
        if v == "None":
            fields.pop(k)
    embtitle = f"Level: **{dbprof['level']}**"
    embdesc = f"Member of *{ctx.guild.name}*"
    profile = discord.Embed(title=embtitle, description=embdesc)
    profile.set_author(name=member.name)
    profile.set_thumbnail(url=member.avatar_url)
    for k, v in fields.items():
        if v == None:
            profile.add_field(name=k)
        else:
            profile.add_field(name=k, value=v)
    await ctx.channel.send(embed=profile)


# Command to fill out profile info via DM
@profile.command(name='Edit',
                 description="Edit your member profile information.",
                 brief="Edit profile information.",
                 aliases=['e'])
@commands.guild_only()
@check_perms()
async def profile_edit(ctx):
    await ctx.author.send(embed=ProfileMenu.embedded())
    db.set_temp(ctx.guild.id, ctx.author.id, ProfileMenu.title)
    await ctx.channel.send("Check your messages, I just sent you a DM!")


# Get list of roles (with IDs) on guild
@bot.command(name='GetRoleIDs',
             description="Returns list of roles on server with IDs.",
             brief="Get all roles with IDs",
             aliases=['roles'])
@commands.guild_only()
@commands.is_owner()
async def get_roles(ctx):
    await ctx.channel.send(f"```{ctx.guild.roles}```")


# Get list of emojis (with IDs) on guild
@bot.command(name='GetEmojiIDs',
             description="Returns list of emojis on server with IDs.",
             brief="Get all emojis with IDs",
             aliases=['emojis'])
@commands.guild_only()
@commands.is_owner()
async def get_emojis(ctx):
    await ctx.channel.send(f"```{ctx.guild.emojis}```")


# Get list of channels (with IDs) on guild
@bot.command(name='GetChannelIDs',
             description="Returns list of channels on server with IDs.",
             brief="Get all channels with IDs",
             aliases=['channels'])
@commands.guild_only()
@commands.is_owner()
async def get_channels(ctx):
    await ctx.channel.send(f"```{ctx.guild.channels}```")


# Command to gracefully shut down the bot
@bot.command(name='Shutdown',
             description="Shut down the bot and close all connections.",
             brief="Shut down the bot.",
             aliases=['die'])
@commands.is_owner()
async def shutdown(ctx):
    await ctx.channel.send("Shutting down...")
    await bot.logout()


# Reaction Role add hook function
@bot.event
async def on_raw_reaction_add(payload):
    if payload.user_id == bot.user.id:
        return
    guildID = payload.guild_id
    roles = db.get_reaction_roles(guildID)
    if roles is not None:
        guild = bot.get_guild(guildID)
        hookID = str(payload.channel_id) + "-" + str(payload.message_id)
        if payload.emoji.is_custom_emoji():
            emoji = str(payload.emoji.id)
        else:
            emoji = payload.emoji.name
        for i in roles:
            if hookID == i["hook_id"] and emoji == i["emoji"]:
                member = guild.get_member(payload.user_id)
                role = guild.get_role(i["role_id"])
                if role not in member.roles:
                    await member.add_roles(role, reason="ReactionRole")


# Reaction Role remove hook function
@bot.event
async def on_raw_reaction_remove(payload):
    if payload.user_id == bot.user.id:
        return
    guildID = payload.guild_id
    roles = db.get_reaction_roles(guildID)
    if roles is not None:
        guild = bot.get_guild(guildID)
        hookID = str(payload.channel_id) + "-" + str(payload.message_id)
        if payload.emoji.is_custom_emoji():
            emoji = str(payload.emoji.id)
        else:
            emoji = payload.emoji.name
        for i in roles:
            if hookID == i['hook_id'] and emoji == i['emoji']:
                member = guild.get_member(payload.user_id)
                role = guild.get_role(i['role_id'])
                if role in member.roles:
                    await member.remove_roles(role, reason="ReactionRole")


# Voice Role hook function
@bot.event
async def on_voice_state_update(member, before, after):
    guildID = member.guild.id
    roles = db.get_voice_roles(guildID)
    if roles is None:
        return
    if before.channel is not None:
        for i in roles:
            if before.channel.id == i['hook_id']:
                role = member.guild.get_role(i['role_id'])
                await member.remove_roles(role, reason="VoiceRoleDisconnect")
    if after.channel is not None:
        for i in roles:
            if after.channel.id == i['hook_id']:
                role = member.guild.get_role(i['role_id'])
                await member.add_roles(role, reason="VoiceRoleConnect")


# Do stuff to members upon joining guild
@bot.event
async def on_member_join(member):
    guildID = member.guild.id
    db.add_member(guildID, member.id, member.created_at, member.joined_at)
    autorole = db.get_cfg(guildID, "auto_role")
    if autorole is not None:
        getRole = member.guild.get_role(autorole)
        await member.add_roles(getRole, reason="AutoRole")
    greetchnl = db.get_cfg(guildID, "greet_channel")
    if greetchnl is not None:
        message = db.get_cfg(guildID, "greet_message")
        gotChannel = bot.get_channel(greetchnl)
        await gotChannel.send(message.format(member=member))


# Do stuff to members upon leaving guild
@bot.event
async def on_member_remove(member):
    guildID = member.guild.id
    byechnl = db.get_cfg(guildID, "bye_channel")
    if byechnl is not None:
        message = db.get_cfg(guildID, "bye_message")
        gotChannel = bot.get_channel(byechnl)
        await gotChannel.send(message.format(member=member))


# Do stuff when a message is sent
@bot.event
async def on_message(message):
    if message.author != bot.user:
        if str(message.channel.type) == 'private':
            await private_message_handler(message)
        else:
            await guild_message_handler(message)
    await bot.process_commands(message)


# Handler for direct messages
async def private_message_handler(message):
    temp = db.get_temp(message.author.id)
    if temp == None:
        return
    if message.content.lower() == "exit":
        db.del_temp(message.author.id)
        await message.channel.send("Menu exited.")
        return
    if temp['menu'] == ProfileMenu.title:
        if temp['selected'] == None:
            option = ProfileMenu.selected(message.content)
            if option is None:
                return
            response = f"{option['prompt']} Character limit: {option['chars']}"
            db.update_temp(message.author.id, option['fname'])
            await message.channel.send(response)
        else:
            option = ProfileMenu.selected(temp['selected'])
            guild = temp['guild_id']
            member = temp['member_id']
            if message.content.lower() == "clear":
                db.set_member_profile(guild, member, option['dbval'], None)
                db.update_temp(message.author.id, None)
                await message.channel.send("Option cleared! Enter another "
                                           "number to continue or send `exit` " 
                                           "to quit.")
                return
            if len(message.content) <= option['chars']:
                if option['format'] == "list":
                    setting = message.content.replace(", ", "\n")
                elif option['format'] == "date":
                    try:
                        datetime.strptime(message.content, '%Y-%m-%d')
                        setting = message.content
                    except ValueError:
                        await message.channel.send("Date formatted wrong!")
                        return
                else:
                    setting = message.content
                db.set_member_profile(guild, member, option['dbval'], setting)
                db.update_temp(message.author.id, None)
                await message.channel.send("Set! Enter another number to "
                                           "continue or send `exit` to quit.")
            else:
                await message.channel.send("Over character limit!")


# Handler for guild messages
async def guild_message_handler(message):
    member = message.author
    guild = message.guild
    profile = db.get_member_profile(guild.id, member.id)
    curxp = profile['xp'] + 1
    nlevel = profile['level'] + 1
    levelup = math.floor(curxp / ((2 * nlevel) ** 2))
    if levelup == 1:
        channel = message.channel
        await channel.send(f"**{member.name}** has leveled up to **level "
                           f"{nlevel}!**")
        db.set_member_stats(guild.id, member.id, lvl=nlevel, xp=curxp)
    else:
        db.set_member_stats(guild.id, member.id, lvl=profile['level'], xp=curxp)


# Global error handler as temp solution
# @bot.event
# async def on_command_error(ctx, error):
#    await ctx.channel.send(error)


# Error handler for auto_role function
# @auto_role.error
# async def auto_role_error(ctx, error):
#    if isinstance(error, commands.MissingRequiredArgument):
#        await ctx.channel.send("You need to include a role name or ID!")
#    if isinstance(error, commands.CommandError):
#        await ctx.channel.send("Och! Something wrong! Don't worry \;\)")


# Make the bot ignore commands until fully initialized
@bot.event
async def on_connect():
    await bot.wait_until_ready()


# Output info to console once bot is initialized and ready
@bot.event
async def on_ready():
    guilds = bot.guilds
    for guild in guilds:
        gID = guild.id
        db.add_guild(gID)
        members = guild.members
        for member in members:
            mID = member.id
            created = member.created_at
            joined = member.joined_at
            db.add_member(gID, mID, created, joined)
    print(f"{bot.user.name} is ready, user ID is {bot.user.id}")
    print("------")


# Run the program
db.setup_database()
bot.run(token)
