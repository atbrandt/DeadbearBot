import os, math
from datetime import datetime, date
from typing import Union, Optional
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
# Usage is convSomething.convert(ctx, arg)
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
        permrole = db.get_cfg(ctx.guild.id, 'perm_role')
        gotRole = ctx.guild.get_role(permrole)
        roles = ctx.author.roles
        return gotRole in roles
    return commands.check(predicate)


# Class definition for embedded menus
class Menu:
    def __init__(self, title, desc, fields):
        self.title = title
        self.desc = desc
        self.fields = fields
        fmax = 9
        self.pages = math.ceil(len(self.fields)/fmax)
        self.pfields = [self.fields[i*fmax:(i+1)*fmax] for i in range(self.pages)]
    
    def embedded(self):
        embeds = []
        for index, page in enumerate(self.pagefields, 1):
            embed = discord.Embed(title=self.title, description=self.desc)
            for item in page:
                embed.add_field(name=item['fname'], value=item['fdesc'])
            embed.set_footer(text=f"Page {index}/{self.pages}")
            embeds.append(embed)
        return embeds

    def tempselect(self, option):
        return next((i for i in self.fields if i['fname'] == option), None)


# Setup profile management menu
ptitle = "**Manage Your Profile**"
pdesc = (
    "**Please wait until all reactions are added to the message!**\n\n"
    "Click the emoji number below that matches to the option you want to "
    "change, then follow the instructions that appear above. Use the arrows "
    "to navigate to another page, if available.\n\n"
    "For any option, sending \"clear\" will reset the option.")
pfields = [{'fname': "1. Name",
            'fdesc': "Your \"name\", real or otherwise.",
            'prompt': "Submit a name!",
            'chars': 40,
            'format': 'text',
            'dbval': 'name'},
           {'fname': "2. Nickname",
            'fdesc': "What you like to be called.",
            'prompt': "Submit a nickname!",
            'chars': 60,
            'format': 'text',
            'dbval': 'nickname'},
           {'fname': "3. Age",
            'fdesc': "Your age, if you want it known.",
            'prompt': "Submit a date, using the format `YYYY-MM-DD`\nNote that "
                      "this date will *not* show up on your profile, it's only "
                      "used to calculate age.",
            'chars': 10,
            'format': 'date',
            'dbval': 'birthday'},
           {'fname': "4. Gender",
            'fdesc': "Whatever you identify as.",
            'prompt': "Submit whatever gender you want!",
            'chars': 60,
            'format': 'text',
            'dbval': 'gender'},
           {'fname': "5. Location",
            'fdesc': "Your location, specific or general.",
            'prompt': "Submit a location!",
            'chars': 80,
            'format': 'text',
            'dbval': 'location'},
           {'fname': "6. Description",
            'fdesc': "A big text box for whatever.",
            'prompt': "Submit whatever description you want!",
            'chars': 1024,
            'format': 'text',
            'dbval': 'description'},
           {'fname': "7. Likes",
            'fdesc': "A list of all the things you like.",
            'prompt': "Submit a list of things you don't like, separated by "
                      "commas with no spaces, e.g.\n"
                      "`one thing,anotherthing,this_thing`",
            'chars': 1024,
            'format': 'list',
            'dbval': 'likes'},
           {'fname': "8. Dislikes",
            'fdesc': "A list of all the things you hate.",
            'prompt': "Submit a list of things you don't like, separated by "
                      "commas with no spaces, e.g.\n"
                      "`one thing,anotherthing,this_thing`",
            'chars': 1024,
            'format': 'list',
            'dbval': 'dislikes'}]
ProfileMenu = Menu(ptitle, pdesc, pfields)
menubuttons = [f"1\N{combining enclosing keycap}",
               f"2\N{combining enclosing keycap}",
               f"3\N{combining enclosing keycap}",
               f"4\N{combining enclosing keycap}",
               f"5\N{combining enclosing keycap}",
               f"6\N{combining enclosing keycap}",
               f"7\N{combining enclosing keycap}",
               f"8\N{combining enclosing keycap}",
               f"9\N{combining enclosing keycap}"]


# Testing command
@bot.command(name='test')
async def hello_world(ctx):
    print(f"Message sent in {ctx.channel} from {ctx.author.id}")
    await ctx.channel.send(f"Hello {ctx.author}!")


# Set an alias for the bot prefix
@bot.command(name='PrefixAlias',
             description="Sets an alias for the default command prefix.",
             brief="Set command prefix alias.",
             aliases=['prefix'])
@commands.guild_only()
@commands.is_owner()
async def change_prefix(ctx, prefix):
    db.set_cfg(ctx.guild.id, 'bot_alias', prefix)
    await ctx.channel.send(f"My command prefix is now \"{prefix}\".")


# Set perm roles for public commands
@bot.command(name='PermissionRoles',
             description="Sets roles that can use basic commands.",
             brief="Set permrole.",
             aliases=['permrole'])
@commands.guild_only()
@commands.is_owner()
async def set_perms(ctx, role: discord.Role):
    db.set_cfg(ctx.guild.id, 'perm_role', role.id)
    await ctx.channel.send(f"Added \"{role.name}\" to perm roles.")


# Make the bot say things in a nice embedded way
@bot.group(name='BotSay',
           description="Make the bot create an embedded version of a message.",
           brief="Make the bot talk.",
           aliases=['say'],
           invoke_without_command=True)
@commands.guild_only()
@commands.is_owner()
async def say(ctx, *, content: str=None):
    embed = discord.Embed(description=content)
    if ctx.message.attachments:
        attachments = ctx.message.attachments
        imageurl = attachments[0].url
        embed.set_image(url=imageurl)
    # message.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
    await ctx.channel.send(embed=embed)
    await ctx.message.delete()


# Edit an embedded message from the bot
@say.command(name='EditBotSay',
             description="Edit a previously created bot embedded message.",
             brief="Change a bot message.",
             aliases=['e','edit'])
@commands.guild_only()
@commands.is_owner()
async def edit_say(ctx, message: discord.Message, *, content: str=None):
    if content is not None:
        embed = discord.Embed(description=content)
    else:
        embedlist = message.embeds
        content = embedlist[0].description
        if content:
            embed = discord.Embed(description=content)
        else:
            embed = discord.Embed()
    if ctx.message.attachments:
        attachments = ctx.message.attachments
        imageurl = attachments[0].url
        embed.set_image(url=imageurl)
    else:
        embedlist = message.embeds
        imageurl = embedlist[0].image.url
        if imageurl:
            embed.set_image(url=imageurl)
    await message.edit(embed=embed)
    await ctx.message.delete()


# Assign specific roles to specific users
@bot.command(name='ToggleRole',
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
             aliases=['arole'])
@commands.guild_only()
@commands.is_owner()
async def auto_role(ctx, role: discord.Role):
    autorole = db.get_cfg(ctx.guild.id, 'auto_role')
    if autorole is None:
        db.set_cfg(ctx.guild.id, 'auto_role', role.id)
        await ctx.channel.send(f"Added \"{role.name}\" to auto-role.")
    else:
        db.set_cfg(ctx.guild.id, 'auto_role', None)
        await ctx.channel.send(f"Removed \"{role.name}\" from auto-role.")
# ctx.channel.send("No role found! Check the name or ID entered.")


# Manage starboard settings
@bot.command(name='Starboard',
             description="Sets the configuration for starred messages.",
             brief="Modify starboard settings.",
             aliases=['star'])
@commands.guild_only()
@commands.is_owner()
async def starboard(ctx, channel: discord.TextChannel=None):
    starboard = db.get_cfg(ctx.guild.id, 'star_channel')
    if starboard is None:
        db.set_cfg(ctx.guild.id, 'star_channel', channel.id)
        await ctx.channel.send(f"Set \"{channel.name}\" as the star board.")
    else:
        db.set_cfg(ctx.guild.id, 'star_channel', None)
        await ctx.channel.send(f"Starboard disabled.")


# Command to return a user's profile
@bot.group(name='Profile',
           description="Display your profile information.",
           brief="Get your profile.",
           aliases=['prof','profile'],
           invoke_without_command=True)
@commands.guild_only()
@check_perms()
async def profile(ctx, member: discord.Member=None):
    if member:
        dbprof = db.get_member(ctx.guild.id, member.id)
    else:
        dbprof = db.get_member(ctx.guild.id, ctx.author.id)
        member = ctx.author
    if dbprof['birthday']:
        born = datetime.strptime(dbprof['birthday'], '%Y-%m-%d')
        now = date.today()
        age = now.year-born.year-((now.month, now.day)<(born.month, born.day))
    else:
        age = None
    fields = [{'title': "Total XP",
               'data': f"{dbprof['xp']} XP",
               'inline': True},
              {'title': "Cash On Hand",
               'data': f"${dbprof['cash']}",
               'inline': True},
              {'title': "Name",
               'data': dbprof['name'],
               'inline': True},
              {'title': "Nickname",
               'data': dbprof['nickname'],
               'inline': True},
              {'title': "Age",
               'data': age,
               'inline': True},
              {'title': "Gender",
               'data': dbprof['gender'],
               'inline': True},
              {'title': "Location",
               'data': dbprof['location'],
               'inline': True},
              {'title': "Description",
               'data': dbprof['description'],
               'inline': False},
              {'title': "Likes",
               'data': dbprof['likes'],
               'inline': True},
              {'title': "Dislikes",
               'data': dbprof['dislikes'],
               'inline': True}]
    empty = fields.copy()
    for i in empty:
        if not i['data']:
            fields.remove(i)
    embtitle = f"Level: **{dbprof['lvl']}**"
    embdesc = f"Member of *{ctx.guild.name}*"
    profile = discord.Embed(title=embtitle, description=embdesc)
    profile.set_author(name=member.name)
    profile.set_thumbnail(url=member.avatar_url_as(format='png'))
    for i in fields:
        profile.add_field(name=i['title'], value=i['data'], inline=i['inline'])
    await ctx.channel.send(embed=profile)


# Command to fill out profile info via DM
@profile.command(name='Edit',
                 description="Edit your member profile information.",
                 brief="Edit profile information.",
                 aliases=['e','edit'])
@commands.guild_only()
@check_perms()
async def profile_edit(ctx):
    temp = db.get_temp(ctx.author.id)
    if temp:
        db.del_temp(ctx.author.id)
    embeds = ProfileMenu.embedded()
    message = await ctx.author.send(embed=embeds[0])
    await ctx.channel.send("Check your messages, I just sent you a DM!")
    db.add_temp(ctx.guild.id, ctx.author.id)
    await message.add_reaction(u"\u25C0")
    await message.add_reaction(u"\u25B6")
    for index, item in enumerate(embeds[0].fields):
        await message.add_reaction(menubuttons[index])
    await message.add_reaction(u"\u274C")


# Set the channel for join messages
@bot.group(name='GuildJoin',
           description="Enables or disables the automatic join message in a "
                       "specified channel. Pass no channel to disable.",
           brief="Turn join messages on or off.",
           aliases=['gj'],
           invoke_without_command=True)
@commands.guild_only()
@commands.is_owner()
async def gjoin(ctx, channel: discord.TextChannel=None):
    if channel is not None:
        db.set_cfg(ctx.guild.id, 'join_channel', channel.id)
        await ctx.channel.send(f"Greeting enabled for \"{channel.name}\".")
    else:
        db.set_cfg(ctx.guild.id, 'join_channel', None)
        await ctx.channel.send("Greeting disabled.")


# Set the join message
@gjoin.command(name='JoinMessage',
               description="Sets the automatic greeting message.",
               brief="Modify join message.",
               aliases=['msg'])
@commands.guild_only()
@commands.is_owner()
async def gjoin_message(ctx, *, message: str):
    db.set_cfg(ctx.guild.id, 'join_message', message)
    await ctx.channel.send(f"The join message is now: \"{message}\"")


# Set the channel for leave messages
@bot.group(name='GuildLeave',
           description="Enables or disables the automatic leave message in a "
                       "specified channel. Pass no channel to disable.",
           brief="Turn leave message on or off.",
           aliases=['gl'],
           invoke_without_command=True)
@commands.guild_only()
@commands.is_owner()
async def gleave(ctx, channel: discord.TextChannel=None):
    if channel is not None:
        db.set_cfg(ctx.guild.id, 'leave_channel', channel.id)
        await ctx.channel.send(f"Farewells enabled for \"{channel.name}\".")
    else:
        db.set_cfg(ctx.guild.id, 'leave_channel', None)
        await ctx.channel.send("Farewells disabled.")


# Set the leave message
@gleave.command(name='LeaveMessage',
               description="Sets the automatic leave message.",
               brief="Modify leave message.",
               aliases=['msg'])
@commands.guild_only()
@commands.is_owner()
async def gleave_message(ctx, *, message: str):
    db.set_cfg(ctx.guild.id, 'leave_message', message)
    await ctx.channel.send(f"The farewell message is now: \"{message}\"")


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
async def add_rr(ctx,
                 message: discord.Message,
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
    exists = db.del_reaction_role(rrID)
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
    exists = db.del_voice_role(vrID)
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


# Group command to add a role alert
@bot.group(name='RoleAlert',
           description="Sets an alert for a role",
           brief="Sets an alert for a role",
           aliases=['alert'])
@commands.guild_only()
@commands.is_owner()
async def role_alert(ctx):
    pass


# Command to add a role alert when a role is gained
@role_alert.command(name='Gain',
                    aliases=['gain'])
@commands.guild_only()
@commands.is_owner()
async def alert_gain(ctx,
                     role: discord.Role,
                     channel: discord.TextChannel,
                     *, message: str):
    guildID = ctx.guild.id
    arID = db.add_role_alert(guildID, role.id, 'gain_role', channel.id, message)
    await ctx.channel.send(f"When a user gains \"{role.name}\", an alert will "
                           f"be sent to \"{channel.name}\" with the message: "
                           f"{message}.\nID = {arID}")


# Command to add a role alert when a role is lost
@role_alert.command(name='Lose',
                    aliases=['lose'])
@commands.guild_only()
@commands.is_owner()
async def alert_lose(ctx,
                     role: discord.Role,
                     channel: discord.TextChannel,
                     *, message: str):
    guildID = ctx.guild.id
    arID = db.add_role_alert(guildID, role.id, 'lose_role', channel.id, message)
    await ctx.channel.send(f"When a user loses \"{role.name}\", an alert will "
                           f"be sent to \"{channel.name}\" with the message: "
                           f"{message}.\nID = {arID}")


# Command to delete a role alert
@role_alert.command(name='Delete',
                    description="Removes a role alert by its ID.",
                    brief="Remove a role alert",
                    aliases=['del'])
@commands.guild_only()
@commands.is_owner()
async def delete_alert(ctx, uuID):
    exists = db.del_role_alert(uuID)
    if exists:
        await ctx.channel.send(f"Removed reaction role entry {uuID}.")
    else:
        await ctx.channel.send("No reaction role found for that ID!")


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


# Event hook for reactions being added to messages
@bot.event
async def on_raw_reaction_add(payload):
    await convert_payload(payload, 'reaction', 'add')


# Event hook for reactions being removed from messages
@bot.event
async def on_raw_reaction_remove(payload):
    await convert_payload(payload, 'reaction', 'rem')


# Converter for payloads from Raw events
async def convert_payload(payload, type, event=None):
    if type == 'reaction':
        if payload.user_id == bot.user.id:
            return
        if payload.emoji.is_custom_emoji():
            emoji = payload.emoji.id
        else:
            emoji = payload.emoji.name
        channel = await bot.fetch_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        if payload.guild_id:
            guild = bot.get_guild(payload.guild_id)
            member = guild.get_member(payload.user_id)
            if member.bot:
                return
            await greact_event(guild, member, channel, message, emoji, event)
        else:
            user = bot.get_user(payload.user_id)
            if user.bot:
                return
            await preact_event(user, channel, message, emoji, event)


# Handler for guild reaction events
async def greact_event(guild, member, channel, message, emoji, event):
    reactionroles = db.get_reaction_roles(guild.id)
    if reactionroles:
        hookID = f"{channel.id}-{message.id}"
        for item in reactionroles:
            if hookID == item['hook_id'] and str(emoji) == item['emoji']:
                role = guild.get_role(item['role_id'])
                if event == 'add':
                    await member.add_roles(role, reason="ReactionRole")
                else:
                    await member.remove_roles(role, reason="ReactionRole")
    if emoji != u"\U0001F31F":
        return
    starboard = db.get_cfg(guild.id, 'star_channel')
    if starboard:
        threshold = db.get_cfg(guild.id, 'star_threshold')
        reacts = message.reactions
        reaction = next((i for i in reacts if i.emoji == emoji), 0)
        if reaction.count >= threshold:
            await star_add(message)
        else:
            await star_remove(message)


# Handler for dm reaction events
async def preact_event(user, channel, message, emoji, event):
    embed = message.embeds[0]
    if not embed:
        return
    if emoji == u"\u274C":
        db.del_temp(user.id)
        await message.delete()
        await channel.send("Menu closed.")
        return
    reacts = message.reactions
    reaction = next((i for i in reacts if i.emoji == emoji), None)
    if not reaction:
        return
    if emoji not in menubuttons:
        return
    else:
        index = menubuttons.index(emoji)
    page = int(embed.footer.text[5:6]) - 1
    if embed.title == ProfileMenu.title:
        if event == 'add':
            options = ProfileMenu.pfields[page]
            selected = options[index]
            reply = (
                f"{selected['prompt']} \n\n "
                f"Character limit: {selected['chars']}")
            await message.edit(content=reply, embed=embed)
            db.set_temp(user.id, selected['fname'])
        else:
            await message.edit(content=None, embed=embed)
            db.set_temp(user.id, None)


# Add star to starboard
async def star_add(message):
    starred = db.get_starred(message.id)
    if not starred:
        embed = discord.Embed(description=message.content)
        embed.set_author(name=message.author.display_name,
                         icon_url=message.author.avatar_url_as(format='png'))
        if message.embeds:
            data = message.embeds[0]
            if data.type == 'image':
                embed.set_image(url=data.url)
        if message.attachments:
            file = message.attachments[0]
            filetypes = ('png', 'jpeg', 'jpg', 'gif', 'webp')
            if file.url.lower().endswith(filetypes):
                embed.set_thumbnail(url=file.url)
            else:
                embed.add_field(name='Attachment',
                                value=f'[{file.filename}]({file.url})',
                                inline=False)
        embed.add_field(name="--",
                        value=f"[Jump to original...]({message.jump_url})",
                        inline=False)
        embed.set_footer(text=f"Originally sent {message.created_at}")
        newstar = await message.channel.send(embed=embed)
        db.add_starred(message.guild.id, message.id, newstar.id)


# Remove star from starboard
async def star_remove(message):
    starred = db.get_starred(message.id)
    if starred:
        oldstar = await message.channel.fetch_message(starred['starred_id'])  
        await oldstar.delete()
        db.delete_starred(message.id)


# Do stuff to members upon joining guild
@bot.event
async def on_member_join(member):
    guildID = member.guild.id
    if not member.bot:
        db.add_member(guildID, member.id, member.created_at, member.joined_at)
    autorole = db.get_cfg(guildID, 'auto_role')
    if autorole:
        role = member.guild.get_role(autorole)
        await member.add_roles(role, reason="AutoRole")
    joinalert = db.get_cfg(guildID, 'join_channel')
    if joinalert:
        message = db.get_cfg(guildID, 'join_message')
        channel = bot.get_channel(joinalert)
        await channel.send(message.format(member=member))


# Do stuff to members upon leaving guild
@bot.event
async def on_member_remove(member):
    guildID = member.guild.id
    leavealert = db.get_cfg(guildID, 'leave_channel')
    if leavealert is not None:
        message = db.get_cfg(guildID, 'leave_message')
        channel = bot.get_channel(leavealert)
        await channel.send(message.format(member=member))


# Do stuff when members are updated
@bot.event
async def on_member_update(before, after):
    if before.roles == after.roles:
        return
    if len(before.roles) < len(after.roles):
        s = set(before.roles)
        roles = [i for i in after.roles if i not in s]
        alerts = []
        for role in roles:
            alerts.append(db.get_role_alert(role.id, 'gain_role'))
    else:
        s = set(after.roles)
        roles = [i for i in before.roles if i not in s]
        alerts = []
        for role in roles:
            alerts.append(db.get_role_alert(role.id, 'lose_role'))
    if len(alerts):
        for alert in alerts:
            channel = after.guild.get_channel(alert['channel_id'])
            await channel.send(alert['message'].format(member=after))


# Voice Role hook function
@bot.event
async def on_voice_state_update(member, before, after):
    roles = db.get_voice_roles(member.guild.id)
    if not roles:
        return
    if before.channel:
        for i in roles:
            if i['hook_id'] == before.channel.id:
                role = member.guild.get_role(i['role_id'])
                await member.remove_roles(role, reason="VoiceRoleDisconnect")
    if after.channel:
        for i in roles:
            if i['hook_id'] == after.channel.id:
                role = member.guild.get_role(i['role_id'])
                await member.add_roles(role, reason="VoiceRoleConnect")


# Do stuff when a message is sent
@bot.event
async def on_message(message):
    if not message.author.bot:
        if message.guild:
            stats = db.get_cfg(message.guild.id, 'guild_stats')
            if stats == 'enabled':
                await guild_stats(message)
        else:
            temp = db.get_temp(message.author.id)
            if temp:
                await edit_profile_option(message, temp)
    await bot.process_commands(message)


# Guild stats handler
async def guild_stats(message):
    member = message.author
    guildID = message.guild.id
    profile = db.get_member(guildID, member.id)
    curxp = profile['xp'] + 1
    db.set_member(guildID, member.id, option='xp', value=curxp)
    nextlevel = profile['lvl'] + 1
    levelup = math.floor(curxp / ((2 * nextlevel) ** 2))
    if levelup == 1:
        channel = message.channel
        await channel.send(f"**{member.name}** has leveled up to **level "
                           f"{nextlevel}!**")
        db.set_member(guildID, member.id, option='lvl', value=nextlevel)


# Profile edit function
async def edit_profile_option(message, temp):
    option = ProfileMenu.tempselect(temp['selected'])
    if message.content.lower() == "clear":
        db.set_member(guild, member, option['dbval'], None)
        db.set_temp(message.author.id, None)
        await message.channel.send("Option cleared!")
    elif len(message.content) <= option['chars']:
        if option['format'] == 'list':
            setting = message.content.replace(", ", "\n")
        elif option['format'] == 'date':
            try:
                datetime.strptime(message.content, '%Y-%m-%d')
                setting = message.content
            except ValueError:
                await message.channel.send("Date formatted wrong!")
                return
        else:
            setting = message.content
        db.set_member(temp['guild_id'], temp['member_id'], option['dbval'], setting)
        db.set_temp(message.author.id, None)
        await message.channel.send("Option set!")
    else:
        await message.channel.send("Over character limit!")
        return


# Do stuff when a message is deleted
@bot.event
async def on_message_delete(message):
    pass


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
            if not member.bot:
                mID = member.id
                created = member.created_at
                joined = member.joined_at
                db.add_member(gID, mID, created, joined)
    print(f"{bot.user.name} is ready, user ID is {bot.user.id}")
    print("------")


# Run the program
db.setup_db()
bot.run(token)
