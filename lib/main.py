import os
import math
import asyncio
import random
from datetime import datetime, date, timedelta
from typing import Union, Optional
from pathlib import Path
from dotenv import load_dotenv
import discord
from discord.ext import commands
from discord.utils import get
import db
import migration


# Setting platform-independent path to environment variables
ENVFILE = Path(__file__).parent / "secret.env"
# Path to images directory
IMAGES = Path(__file__).parent / "img"


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
        prefix = await db.get_cfg(guild, 'bot_alias')
        if prefix:
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
    async def predicate(ctx):
        permrole = await db.get_cfg(ctx.guild.id, 'perm_role')
        gotRole = ctx.guild.get_role(permrole)
        roles = ctx.author.roles
        return gotRole in roles
    return commands.check(predicate)


# Class definition for embedded menus
class Menu:
    def __init__(self, title, desc, fields, max, click, name=None, image=None):
        self.close = u"\U0001F1FD"
        self.navleft = u"\u25C0"
        self.navright = u"\u25B6"
        self.buttons = [f"1\N{combining enclosing keycap}",
                        f"2\N{combining enclosing keycap}",
                        f"3\N{combining enclosing keycap}",
                        f"4\N{combining enclosing keycap}",
                        f"5\N{combining enclosing keycap}",
                        f"6\N{combining enclosing keycap}",
                        f"7\N{combining enclosing keycap}",
                        f"8\N{combining enclosing keycap}",
                        f"9\N{combining enclosing keycap}",
                        f"\N{keycap ten}"]
        self.title = title
        self.desc = desc
        self.fields = fields
        empty = self.fields.copy()
        for i in empty:
            if not i['fdesc']:
                self.fields.remove(i)
        self.max = max
        if self.max == 0:
            self.pages = 1
        else:
            self.pages = math.ceil(len(self.fields)/self.max)
        self.click = click
        self.pagefields = []
        if self.pages > 1:
            for i in range(self.pages):
                pagefield = self.fields[i*self.max:(i+1)*self.max]
                self.pagefields.append(pagefield)
        else:
            self.pagefields.append(self.fields)
        self.embeds = []
        for index, page in enumerate(self.pagefields, 1):
            embed = discord.Embed(title=self.title, description=self.desc)
            if self.click:
                for i, item in enumerate(page, 1):
                    embed.add_field(name=f"{i}. {item['fname']}",
                                    value=item['fdesc'],
                                    inline=item['inline'])
            else:
                for item in page:
                    embed.add_field(name=f"{item['fname']}",
                                    value=item['fdesc'],
                                    inline=item['inline'])
            if name:
                embed.set_author(name=name)
            if image:
                embed.set_thumbnail(url=image)
            embed.set_footer(text=f"Page {index}/{self.pages}")
            self.embeds.append(embed)

    async def add_buttons(self, message, page):
        content = "**Updating buttons, please wait...**"
        if not message.reactions:
            await message.edit(content=content)
            await message.add_reaction(self.close)
            if self.pages > 1:
                await message.add_reaction(self.navleft)
                await message.add_reaction(self.navright)
            message = await message.channel.fetch_message(message.id)
        if not self.click:
            await message.edit(content=None)
            return message
        if self.pages > 1:
            size = len(message.reactions) - 3
        else:
            size = len(message.reactions) - 1
        options = len(self.pagefields[page])
        if options == size:
            return message
        else:
            await message.edit(content=content)
        if options > size:
            for index, item in enumerate(self.pagefields[page][size:options],
                                         size):
                await message.add_reaction(self.buttons[index])
        elif options < size:
            for index, item in enumerate(self.buttons[options:size],
                                         options):
                await message.remove_reaction(self.buttons[index],
                                              message.author)
        await message.edit(content=None)
        message = await message.channel.fetch_message(message.id)
        return message

    def temp_select(self, option):
        return next((i for i in self.fields if i['fname'] == option), None)


# Setup global profile management menu
ptitle = "**Profile Management**"
pdesc = ("Click the emoji that matches to the option you want to change, "
         "then follow the instructions that appear above. Use the "
         "arrows to navigate to another page, if available.")
pfields = [{'fname': "Name",
            'fdesc': "Your **name**, real or otherwise.",
            'inline': True,
            'prompt': "Submit a name, or send `clear` to reset.",
            'limit': 40,
            'format': 'text',
            'data': 'name'},
           {'fname': "Nickname",
            'fdesc': "The **nickname** you like to be called.",
            'inline': True,
            'prompt': "Submit a nickname, or send `clear` to reset.",
            'limit': 60,
            'format': 'text',
            'data': 'nickname'},
           {'fname': "Age",
            'fdesc': "Your **age**, if you want it known.",
            'inline': True,
            'prompt': "Submit a date, using the format `YYYY-MM-DD`, or send "
                      "`clear` to reset.\nNote that this date will *not* show "
                      "up on your profile, it's only used to calculate age.",
            'limit': 10,
            'format': 'date',
            'data': 'birthday'},
           {'fname': "Gender",
            'fdesc': "Your **gender**, whatever it may be.",
            'inline': True,
            'prompt': "Submit a gender, or send `clear` to reset.",
            'limit': 60,
            'format': 'text',
            'data': 'gender'},
           {'fname': "Location",
            'fdesc': "Your **location**, if you want it known.",
            'inline': True,
            'prompt': "Submit a location, or send `clear` to reset.",
            'limit': 80,
            'format': 'text',
            'data': 'location'},
           {'fname': "Description",
            'fdesc': "Your **description**, for general info.",
            'inline': True,
            'prompt': "Submit a description, or send `clear` to reset.",
            'limit': 1024,
            'format': 'text',
            'data': 'description'},
           {'fname': "Likes",
            'fdesc': "A list of **likes**, loves, and interests.",
            'inline': True,
            'prompt': "Submit a list of things you like, separated by commas, "
                      "e.g. `one thing, something, this_thing`, or send "
                      "`clear` to reset.",
            'limit': 1024,
            'format': 'list',
            'data': 'likes'},
           {'fname': "Dislikes",
            'fdesc': "A list of **dislikes**, despises, and disinterests.",
            'inline': True,
            'prompt': "Submit a list of things you don't like, separated by "
                      "commas, e.g. `one thing, something, this_thing`, or "
                      "send `clear` to reset.",
            'limit': 1024,
            'format': 'list',
            'data': 'dislikes'}]
ProfileEdit = Menu(ptitle, pdesc, pfields, 3, True)


# Generic function for seeking through a paginated menu
async def menu_seek(message, user, menu, page, time=None):
    def check(payload):
        return payload.user_id == user.id

    try:
        payload = await bot.wait_for('raw_reaction_add',
                                     timeout=time,
                                     check=check)
    except asyncio.TimeoutError:
        await message.clear_reactions()
        await message.edit(content="Menu closing in 5 seconds...",
                           delete_after=5.0)
    else:
        await message.edit(content=None)
        await message.remove_reaction(payload.emoji, user)
        if payload.emoji.name == menu.navleft:
            if page > 0:
                page -= 1
                await message.edit(embed=menu.embeds[page])
                message = await menu.add_buttons(message, page)
            await menu_seek(message, user, menu, page, time)
            return
        elif payload.emoji.name == menu.navright:
            if page < (menu.pages - 1):
                page += 1
                await message.edit(embed=menu.embeds[page])
                message = await menu.add_buttons(message, page)
            await menu_seek(message, user, menu, page, time)
            return
        elif payload.emoji.name == menu.close:
            await message.clear_reactions()
            await message.edit(content="Menu closing in 5 seconds...",
                               delete_after=5.0)
            return
        elif menu.title == ProfileEdit.title:
            options = menu.pagefields[page]
            index = menu.buttons.index(payload.emoji.name)
            selected = options[index]
            await db.add_temp(user.guild.id,
                              user.id,
                              menu.title,
                              selected['fname'])
            edit = "**Instructions being sent via DM, check your messages.**"
            await message.edit(content=edit)
            reply = (f"{selected['prompt']}\n\n"
                     f"Character limit: {selected['limit']}\n")
            await user.send(content=reply)
            await menu_seek(message, user, menu, page, time)
            return
        elif 'Shop' in menu.title:
            options = menu.pagefields[page]
            index = menu.buttons.index(payload.emoji.name)
            selected = options[index]
            profile = await db.get_member(user.guild.id, user.id)
            if profile['cash'] < selected['price']:
                edit = f"**Not enough credits for a {selected['fname']}!**"
                await message.edit(content=edit)
                await menu_seek(message, user, menu, page, time)
                return
            if selected['data'] == 'role':
                await db.add_temp(user.guild.id,
                                  user.id,
                                  menu.title,
                                  selected['fname'])
                reply = (f"{selected['prompt']}\n\n"
                         f"Character limit: {selected['limit']}\n")
                await user.send(content=reply)
            elif selected['data'] == 'emoji':
                if 'MORE_EMOJI' in user.guild.features:
                    elimit = 200
                else:
                    elimit = 50
                if len(user.guild.emojis) >= elimit:
                    edit = ("The custom emoji limit for this server has been "
                            "reached!")
                    await message.edit(content=edit)
                    await menu_seek(message, user, menu, page, time)
                    return
                else:
                    await db.add_temp(user.guild.id,
                                      user.id,
                                      menu.title,
                                      selected['fname'])
                    reply = (f"{selected['prompt']}\n\n"
                             f"Size limit: {selected['limit']}\n")
                    await user.send(content=reply)
            elif selected['data'] == 'ticket':
                pass
            newbalance = profile['cash'] - selected['price']
            await db.set_member(user.guild.id,
                                user.id,
                                'cash',
                                newbalance)
            edit = f"**{selected['fname']} bought! Check your messages.**"
            await message.edit(content=edit)
            await menu_seek(message, user, menu, page, time)


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
    await db.set_cfg(ctx.guild.id, 'bot_alias', prefix)
    await ctx.channel.send(f"My command prefix is now \"{prefix}\".")


# Set perm roles for public commands
@bot.command(name='PermissionRoles',
             description="Sets roles that can use basic commands.",
             brief="Set permrole.",
             aliases=['permrole'])
@commands.guild_only()
@commands.is_owner()
async def set_perms(ctx, role: discord.Role):
    await db.set_cfg(ctx.guild.id, 'perm_role', role.id)
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
             aliases=['e', 'edit'])
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
    autorole = await db.get_cfg(ctx.guild.id, 'auto_role')
    if autorole is None:
        await db.set_cfg(ctx.guild.id, 'auto_role', role.id)
        await ctx.channel.send(f"Added \"{role.name}\" to auto-role.")
    else:
        await db.set_cfg(ctx.guild.id, 'auto_role', None)
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
    starboard = await db.get_cfg(ctx.guild.id, 'star_channel')
    if starboard is None:
        await db.set_cfg(ctx.guild.id, 'star_channel', channel.id)
        await ctx.channel.send(f"Set \"{channel.name}\" as the star board.")
    else:
        await db.set_cfg(ctx.guild.id, 'star_channel', None)
        await ctx.channel.send(f"Starboard disabled.")


# Daily cash award
@bot.command(name='DailyCredits',
             aliases=['daily', 'credits', 'cashme', 'dailycredits', 'getmoney'])
@commands.guild_only()
@check_perms()
async def daily_cash(ctx):
    gID = ctx.guild.id
    member = ctx.author
    now = ctx.message.created_at
    dbprof = await db.get_member(gID, member.id)
    timeformat = '%Y-%m-%d %H:%M:%S.%f'
    if dbprof['daily_timestamp']:
        lastdaily = datetime.strptime(dbprof['daily_timestamp'], timeformat)
        timesince = now - lastdaily
        delta = timedelta(hours=24)
    else:
        timesince = 2
        delta = 1
    if timesince < delta:
        timeleft = delta - timesince
        hours = timeleft.seconds//3600
        minutes = (timeleft.seconds//60)%60
        seconds = math.ceil(timeleft.seconds)
        if hours:
            await ctx.channel.send(
                f"I already gave you money, {member.mention}! If you want "
                f"more, you'll have to wait {hours} hour(s) and {minutes} "
                f"minute(s).")
        elif seconds > 60:
            await ctx.channel.send(
                f"I already gave you money, {member.mention}! If you want "
                f"more, you'll have to wait {minutes} minute(s) and "
                f"{seconds} second(s).")
        else:
            await ctx.channel.send(
                f"I already gave you money, {member.mention}! If you want "
                f"more, you'll have to wait {seconds} second(s).")
    else:
        newcash = dbprof['cash'] + 500
        await db.set_member(gID, member.id, 'cash', newcash)
        await db.set_member(gID, member.id, 'daily_timestamp', now)
        await ctx.channel.send(
            f"Here's a 500 credit freebie, {member.mention}!")


# Shop menu function
@bot.command(name='GuildShop',
             aliases=['shop'])
@commands.guild_only()
@check_perms()
async def shop(ctx):
    temp = await db.get_temp(ctx.author.id)
    if temp:
        await db.del_temp(ctx.author.id)
    title = f"**{ctx.guild.name} Shop**"
    desc = "*Buy somethin, will ya!*"
    cost = {'role': 10000,
            'emoji': 10000,
            'ticket': 1000}
    fields = [{'fname': "Custom Role",
                'fdesc': f"Buy a custom role! You'll be able to pick both "
                         f"the name and the color of the role after purchase."
                         f"\n\nCost: \U0001F48E {cost['role']}",
                'inline': True,
                'prompt': "You've purchased a custom role! Please enter a "
                          "name for your new role.",
                'limit': 40,
                'price': cost['role'],
                'data': 'role'},
               {'fname': "Custom Emoji",
                'fdesc': f"Buy a custom emoji! You'll be able to pick both "
                         f"the image and name for the emoji after purchase."
                         f"\n\nCost: \U0001F48E {cost['emoji']}",
                'inline': True,
                'prompt': "You've purchased a custom emoji! Please upload the "
                          "image for your new emoji.",
                'limit': "256kb (File must be `jpg`, `png`, or `gif`)",
                'price': cost['emoji'],
                'data': 'emoji'}]
#               {'fname': "Raffle Ticket",
#                'fdesc': f"Buy a ticket for a raffle!\n\nCost: \U0001F48E "
#                         f"{cost['ticket']}",
#                'inline': True,
#                'price': cost['ticket'],
#                'data': 'ticket'}
    Shop = Menu(title, desc, fields, 5, True)
    page = 0
    message = await ctx.channel.send(embed=Shop.embeds[page])
    message = await Shop.add_buttons(message, page)
    await menu_seek(message, ctx.author, Shop, page, 55.0)


# Command to return a user's profile
@bot.group(name='Profile',
           description="Display your profile information.",
           brief="Get your profile.",
           aliases=['prof', 'profile'],
           invoke_without_command=True)
@commands.guild_only()
@check_perms()
async def profile(ctx, member: discord.Member=None):
    if member:
        dbprof = await db.get_member(ctx.guild.id, member.id)
    else:
        dbprof = await db.get_member(ctx.guild.id, ctx.author.id)
        member = ctx.author
    if dbprof['birthday']:
        born = datetime.strptime(dbprof['birthday'], '%Y-%m-%d')
        now = date.today()
        age = now.year-born.year-((now.month, now.day)<(born.month, born.day))
    else:
        age = None
    fields = [{'fname': "Total XP",
               'fdesc': f"\U0001F4D6 {dbprof['xp']}",
               'inline': False},
              {'fname': "Total Credits",
               'fdesc': f"\U0001F48E {dbprof['cash']}",
               'inline': False},
              {'fname': "Name",
               'fdesc': dbprof['name'],
               'inline': True},
              {'fname': "Nickname",
               'fdesc': dbprof['nickname'],
               'inline': True},
              {'fname': "Age",
               'fdesc': age,
               'inline': True},
              {'fname': "Gender",
               'fdesc': dbprof['gender'],
               'inline': True},
              {'fname': "Location",
               'fdesc': dbprof['location'],
               'inline': True},
              {'fname': "Description",
               'fdesc': dbprof['description'],
               'inline': False},
              {'fname': "Likes",
               'fdesc': dbprof['likes'],
               'inline': True},
              {'fname': "Dislikes",
               'fdesc': dbprof['dislikes'],
               'inline': True}]
    title = f"Level: **{dbprof['lvl']}**"
    desc = f"Member of *{ctx.guild.name}*"
    avatar = member.avatar_url_as(format='png')
    Profile = Menu(title, desc, fields, 0, False, member.name, avatar)
    page = 0
    message = await ctx.channel.send(embed=Profile.embeds[page])
    message = await Profile.add_buttons(message, page)
    await menu_seek(message, ctx.author, Profile, page, 55.0)


# Command to fill out profile info via DM
@profile.command(name='Edit',
                 description="Edit your member profile information.",
                 brief="Edit profile information.",
                 aliases=['e', 'edit'])
@commands.guild_only()
@check_perms()
async def profile_edit(ctx):
    temp = await db.get_temp(ctx.author.id)
    if temp:
        await db.del_temp(ctx.author.id)
    page = 0
    message = await ctx.channel.send(embed=ProfileEdit.embeds[page])
    message = await ProfileEdit.add_buttons(message, page)
    await menu_seek(message, ctx.author, ProfileEdit, page, 55.0)


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
    if channel:
        await db.set_cfg(ctx.guild.id, 'join_channel', channel.id)
        await ctx.channel.send(f"Greeting enabled for \"{channel.name}\".")
    else:
        await db.set_cfg(ctx.guild.id, 'join_channel', None)
        await ctx.channel.send("Greeting disabled.")


# Set the join message
@gjoin.command(name='JoinMessage',
               description="Sets the automatic greeting message.",
               brief="Modify join message.",
               aliases=['msg'])
@commands.guild_only()
@commands.is_owner()
async def gjoin_message(ctx, *, message: str):
    await db.set_cfg(ctx.guild.id, 'join_message', message)
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
    if channel:
        await db.set_cfg(ctx.guild.id, 'leave_channel', channel.id)
        await ctx.channel.send(f"Farewells enabled for \"{channel.name}\".")
    else:
        await db.set_cfg(ctx.guild.id, 'leave_channel', None)
        await ctx.channel.send("Farewells disabled.")


# Set the leave message
@gleave.command(name='LeaveMessage',
                description="Sets the automatic leave message.",
                brief="Modify leave message.",
                aliases=['msg'])
@commands.guild_only()
@commands.is_owner()
async def gleave_message(ctx, *, message: str):
    await db.set_cfg(ctx.guild.id, 'leave_message', message)
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
    gID = ctx.guild.id
    hookID = str(message.channel.id) + "-" + str(message.id)
    if type(emoji) is str:
        exists, rrID = await db.add_react_role(gID, hookID, emoji, role.id)
    else:
        exists, rrID = await db.add_react_role(gID, hookID, emoji.id, role.id)
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
    exists = await db.del_react_role(rrID)
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
    roles = dict(await db.get_react_roles(ctx.guild.id))
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
    gID = ctx.guild.id
    exists, vrID = await db.add_voice_role(gID, vchannel.id, role.id)
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
    exists = await db.del_voice_role(vrID)
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
    roles = dict(await db.get_voice_roles(ctx.guild.id))
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
    gID = ctx.guild.id
    arID = await db.add_role_alert(ctx.guild.id,
                                   role.id,
                                   'gain_role',
                                   channel.id,
                                   message)
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
    arID = await db.add_role_alert(ctx.guild.id,
                                   role.id,
                                   'lose_role',
                                   channel.id,
                                   message)
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
    exists = await db.del_role_alert(uuID)
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
    if payload.user_id == bot.user.id:
        return None
    if payload.guild_id:
        await greact_event(payload, 'add')
    else:
        await preact_event(payload, 'add')


# Event hook for reactions being removed from messages
@bot.event
async def on_raw_reaction_remove(payload):
    if payload.user_id == bot.user.id:
        return None
    if payload.guild_id:
        await greact_event(payload, 'rem')
    else:
        await preact_event(payload, 'rem')


# Converter for payloads from Raw events
async def convert_payload(payload, type):
    if type == 'reaction':
        if payload.user_id == bot.user.id:
            return None
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
                return None
            else:
                converted = {'guild': guild,
                             'member': member,
                             'channel': channel,
                             'message': message,
                             'emoji': emoji}
                return converted
        else:
            user = bot.get_user(payload.user_id)
            if user.bot:
                return None
            else:
                converted = {'user': user,
                             'channel': channel,
                             'message': message,
                             'emoji': emoji}
                return converted


# Handler for guild reaction events
async def greact_event(payload, event):
    if payload.emoji.is_custom_emoji():
        emoji = payload.emoji.id
    else:
        emoji = payload.emoji.name
    guild = bot.get_guild(payload.guild_id)
    reactionroles = await db.get_react_roles(guild.id)
    if reactionroles:
        hookID = f"{channel.id}-{message.id}"
        for item in reactionroles:
            if hookID == item['hook_id'] and str(emoji) == item['emoji']:
                role = guild.get_role(item['role_id'])
                member = guild.get_member(payload.user_id)
                if event == 'add':
                    await member.add_roles(role, reason="ReactionRole")
                else:
                    await member.remove_roles(role, reason="ReactionRole")
    if emoji != u"\U0001F31F":
        return
    starboard = await db.get_cfg(guild.id, 'star_channel')
    if starboard:
        channel = guild.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        starchannel = guild.get_channel(starboard)
        threshold = await db.get_cfg(guild.id, 'star_threshold')
        reacts = message.reactions
        count = next((i.count for i in reacts if i.emoji == emoji), 0)
        if count >= threshold:
            await star_add(message, starchannel)
        else:
            await star_remove(message, starchannel)


# Handler for dm reaction events
async def preact_event(payload, event):
    pass


# Add star to starboard
async def star_add(message, starboard):
    starred = await db.get_starred(message.id)
    if not starred:
        embed = discord.Embed(description=message.content,
                              color=0xf1c40f)
        embed.set_author(name=message.author.display_name,
                         icon_url=message.author.avatar_url_as(format='png'))
        if message.embeds:
            data = message.embeds[0]
            if data.type == 'image':
                embed.set_thumbnail(url=data.url)
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
        embed.set_footer(text="Originally sent")
        embed.timestamp = message.created_at
        newstar = await starboard.send(embed=embed)
        await db.add_starred(message.guild.id, message.id, newstar.id)


# Remove star from starboard
async def star_remove(message, starboard):
    starred = await db.get_starred(message.id)
    if starred:
        oldstar = await starboard.fetch_message(starred['starred_id'])
        await oldstar.delete()
        await db.del_starred(message.id)


# Do stuff to members upon joining guild
@bot.event
async def on_member_join(member):
    if not member.bot:
        await db.add_member(member.guild.id,
                            member.id,
                            member.created_at,
                            member.joined_at)
    autorole = await db.get_cfg(member.guild.id, 'auto_role')
    if autorole:
        role = member.guild.get_role(autorole)
        await member.add_roles(role, reason="AutoRole")
    joinalert = await db.get_cfg(member.guild.id, 'join_channel')
    if joinalert:
        message = await db.get_cfg(member.guild.id, 'join_message')
        channel = bot.get_channel(joinalert)
        await channel.send(message.format(member=member))


# Do stuff to members upon leaving guild
@bot.event
async def on_member_remove(member):
    gID = member.guild.id
    leavealert = await db.get_cfg(gID, 'leave_channel')
    if leavealert is not None:
        message = await db.get_cfg(gID, 'leave_message')
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
            alert = await db.get_role_alert(role.id, 'gain_role')
            if alert:
                alerts.append(alert)
    else:
        s = set(after.roles)
        roles = [i for i in before.roles if i not in s]
        alerts = []
        for role in roles:
            alert = await db.get_role_alert(role.id, 'lose_role')
            if alert:
                alerts.append(alert)
    for alert in alerts:
        channel = after.guild.get_channel(alert['channel_id'])
        await channel.send(alert['message'].format(member=after))


# Voice Role hook function
@bot.event
async def on_voice_state_update(member, before, after):
    roles = await db.get_voice_roles(member.guild.id)
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
            stats = await db.get_cfg(message.guild.id, 'guild_stats')
            if stats == 'enabled':
                await guild_stats(message)
        else:
            temp = await db.get_temp(message.author.id)
            if temp['menu'] == ProfileEdit.title:
                await edit_profile_option(message, temp)
            elif 'Shop' in temp['menu']:
                await shop_purchase(message, temp)
    await bot.process_commands(message)


# Guild stats handler
async def guild_stats(message):
    guildID = message.guild.id
    member = message.author
    profile = await db.get_member(guildID, member.id)
    cashmin = await db.get_cfg(guildID, 'min_cash')
    cashmax = await db.get_cfg(guildID, 'max_cash')
    cashaward = random.randrange(cashmin, cashmax)
    newcash = profile['cash'] + cashaward
    await db.set_member(guildID, member.id, 'cash', newcash)    
    curxp = profile['xp'] + 1
    await db.set_member(guildID, member.id, 'xp', curxp)
    nextlevel = profile['lvl'] + 1
    levelup = math.floor(curxp / ((2 * nextlevel) ** 2))
    if levelup == 1:
        channel = message.channel
        await channel.send(f"**{member.name}** has leveled up to **level "
                           f"{nextlevel}!**")
        await db.set_member(guildID, member.id, 'lvl', nextlevel)


# Profile edit function
async def edit_profile_option(message, temp):
    option = ProfileEdit.temp_select(temp['selected'])
    if message.content.lower() == "clear":
        await db.set_member(temp['guild_id'],
                            temp['member_id'],
                            option['data'],
                            None)
        await db.del_temp(message.author.id)
        await message.channel.send("Option cleared!", delete_after=5.0)
    elif len(message.content) > option['limit']:
        await message.channel.send(content="Over character limit!",
                                   delete_after=5.0)
        return
    else:
        if option['format'] == 'list':
            setting = message.content.replace(", ", "\n")
        elif option['format'] == 'date':
            try:
                datetime.strptime(message.content, '%Y-%m-%d')
                setting = message.content
            except ValueError:
                await message.channel.send("Wrong format!", delete_after=5.0)
                return
        else:
            setting = message.content
        await db.set_member(temp['guild_id'],
                            temp['member_id'],
                            option['data'],
                            setting)
        await db.del_temp(message.author.id)
        await message.channel.send("Option set!", delete_after=5.0)


# Shop purchase function
async def shop_purchase(message, temp):
    guild = bot.get_guild(temp['guild_id'])
    member = guild.get_member(message.author.id)
    if temp['selected'] == "Custom Role":
        if not temp['storage']:
            option = Shop.temp_select(temp['selected'])
            if len(message.content) > option['limit']:
                await message.channel.send(content="Over character limit!",
                                           delete_after=5.0)
                return
            prompt = ("Next, select a color for your role. You may enter a "
                      "name from the example image below, or a hex code for "
                      "a specific custom color, e.g. `0F0F0F`")
            file = discord.File(IMAGES / "color_examples.png")
            await message.channel.send(content=prompt, file=file)
            await db.set_temp(guild.id, member.id, message.content)
            return
        else:
            colors = {'green': 0x2ecc71,
                      'dark green': 0x1f8b4c,
                      'teal': 0x1abc9c,
                      'dark teal': 0x11806a,
                      'blue': 0x3498db,
                      'dark blue': 0x206694,
                      'blurple': 0x7289da,
                      'purple': 0x9b59b6,
                      'dark purple': 0x71368a,
                      'magenta': 0xe91e63,
                      'dark magenta': 0xad1457,
                      'red': 0xe74c3c,
                      'dark red': 0x992d22,
                      'orange': 0xe67e22,
                      'dark orange': 0xa84300,
                      'gold': 0xf1c40f,
                      'dark gold': 0xc27c0e,
                      'white': 0xdcddde,
                      'lighter grey': 0x95a5a6,
                      'light grey': 0x979c9f,
                      'greyple': 0x99aab5,
                      'dark grey': 0x607d8b,
                      'darker grey': 0x546e7a,
                      'black': 0x18191c}
            color = message.content.lower()
            fail = "That's not a valid color! Please try again."
            if color in colors.keys():
                color = discord.Color(colors[color])
            else:
                try:
                    color = int(f"0x{color}", 0)
                    color = discord.Color(color)
                except ValueError:
                    try:
                        color = int(f"{color}", 0)
                        color = discord.Color(color)
                    except TypeError:
                        await member.send(content=fail, delete_after=5.0)
                        return
            role = await guild.create_role(reason="Shop purchase",
                                           name=temp['storage'],
                                           color=color, 
                                           mentionable=True)
            botRoleID = await db.get_cfg(guild.id, 'bot_role')
            botRole = guild.get_role(botRoleID)
            position = botRole.position - 1
            await role.edit(position=position, reason="Shop purchase")
            await db.add_custom_role(guild.id, member.id, role.id)
            await member.add_roles(role, reason="Shop purchase")
            await db.del_temp(message.author.id)
            await member.send("Role set! Enjoy your fancy new title!",
                              delete_after=5.0)
    elif temp['selected'] == "Custom Emoji":
        if not temp['storage']:
            upload = message.attachments[0]
            filetype = Path(upload.filename).suffix
            if filetype not in ['.jpeg', '.jpg', '.png', '.gif']:
                member.send("Wrong filetype!", delete_after=5.0)
                return
            if upload.size > 256000:
                member.send("File too big!", delete_after=5.0)
                return
            file = await upload.read()
            await db.set_temp(guild.id, member.id, file)
            await member.send("Enter a name for the emoji, with or without "
                              "`::` around it.")
        else:
            emoji = message.content.replace(":", "").replace(" ", "")
            file = temp['storage']
            await guild.create_custom_emoji(name=emoji,
                                            image=file,
                                            reason="Shop purchase")
            await db.del_temp(message.author.id)
            await member.send("Emoji set! Try it out in the server!",
                              delete_after=5.0)


# Do stuff when a message is deleted
@bot.event
async def on_message_delete(message):
    pass


# Remove a custom role when it's deleted
@bot.event
async def on_guild_role_delete(role):
    await db.del_custom_role(role.guild.id, role.id)


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


# Add guild function
async def add_guild(guild):
    await db.add_guild(guild.id)
    for member in guild.members:
        if not member.bot:
            await db.add_member(guild.id,
                                member.id,
                                member.created_at,
                                member.joined_at)
        elif member.id == bot.user.id:
            for role in member.roles:
                if role.managed and role.name == bot.user.name:
                    await db.set_cfg(guild.id, 'bot_role', role.id)


# Add guild when joining new guild
@bot.event
async def on_guild_join(guild):
    await add_guild(guild)


# Make the bot ignore commands until fully initialized
@bot.event
async def on_connect():
    await bot.wait_until_ready()


# Output info to console once bot is initialized and ready
@bot.event
async def on_ready():
    for guild in bot.guilds:
        await add_guild(guild)
    print(f"{bot.user.name} is ready, user ID is {bot.user.id}")
    print("------")


# Run the program
def main():
    migration.migrate()
    bot.run(token)

if __name__ == '__main__':
    main()
