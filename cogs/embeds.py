import math
import sys
import asyncio

if sys.version_info[0] == 3 and sys.version_info[1] >= 8 and sys.platform.startswith('win'):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from datetime import datetime, date, timedelta
from pathlib import Path
from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper
import discord
from discord.ext import commands
from .utils import db
from .utils import checks


# Path to images directory
IMAGES = Path(__file__).parent / "img"
STRINGPATH = Path(__file__).parent / "resource" / "embeds.yaml"


class Embeds(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    # Class definition for embedded menus
    class MenuEmbed(discord.Embed):
        def __init__(self, user, head, desc, fields, numbers=False):
            self.numbtns = [f"1\N{combining enclosing keycap}",
                            f"2\N{combining enclosing keycap}",
                            f"3\N{combining enclosing keycap}",
                            f"4\N{combining enclosing keycap}",
                            f"5\N{combining enclosing keycap}",
                            f"6\N{combining enclosing keycap}",
                            f"7\N{combining enclosing keycap}",
                            f"8\N{combining enclosing keycap}",
                            f"9\N{combining enclosing keycap}",
                            f"\N{keycap ten}"]
            self.numbers = numbers
            self.navbtns = [u"\u25C0", u"\u25B6"]
            self.nav = False
            self.closebtn = u"\U0001F1FD"
            max = len(self.numbtns)
            self.pages = []
            for i in range((len(fields)+max-1)//max):
                self.pages.append(fields[i*max:(i+1)*max])
            self.page = 1
            self.selected = None
            self.user = user
            self.validemoji = None
            super().__init__(title=head, description=desc)
            super().set_footer(text=f"Page {self.page}/{len(self.pages)}")


        async def add_fields(self):
            if self.numbers:
                for i, item in enumerate(self.pages[self.page-1]):
                    super().add_field(
                        name=f"{i+1}. {item['fname']}",
                        value=item['fdesc'],
                        inline=item['inline'])
                self.validemoji = self.numbtns[:len(self.pages[self.page-1])]
            else:
                for item in self.pages[self.page - 1]:
                    super().add_field(
                        name=f"{item['fname']}",
                        value=item['fdesc'],
                        inline=item['inline'])


        async def add_control(self, message):
            self.message = message
            content = "**Updating reactji buttons, please wait...**"
            await self.message.edit(content=content)
            await self.message.add_reaction(self.closebtn)
            if not self.nav and len(self.pages) > 1:
                for item in self.navbtns:
                    await self.message.add_reaction(item)
                self.nav = True
            if self.numbers:
                for index, item in enumerate(self.pages[self.page-1]):
                    await self.message.add_reaction(self.numbtns[index])
            await self.message.edit(content=None)
            return True


        async def process_reaction(self, emoji):
            if emoji == self.closebtn:
                return False
            elif self.numbers:
                if emoji in self.validemoji:
                    index = self.validemoji.index(emoji)
                    self.selected = self.pages[self.page-1][index]
            elif self.nav and (emoji in self.navbtns):
                if emoji == self.navbtns[0]:
                    if self.page > 1:
                        self.page -= 1
                elif self.page < len(self.pages):
                    self.page += 1
                self.clear_fields()
                await self.add_fields()
                self.set_footer(text=f"Page {self.page}/{len(self.pages)}")
                await self.message.edit(embed=self)



    # Make the bot say things in a nice embedded way
    @commands.group(
        name='BotSay',
        description="Make the bot create an embedded message.",
        brief="Make the bot talk.",
        aliases=['botsay', 'say'],
        invoke_without_command=True)
    @commands.guild_only()
    @commands.is_owner()
    async def say(self, ctx, *, content: str=None):
        embed = discord.Embed(description=content)
        # Create a list of valid image formats for upload
        validfiles = [".jpg", ".jpeg", ".gif", ".png", ".bmp"]
        # If the message had an attachment, make sure it's a valid image
        # If it is, preserve the original message so the url stays valid
        if ctx.message.attachments[0]:
            attachment = Path(ctx.message.attachments[0].filename)
            if attachment.suffix in validfiles:
                imageurl = ctx.message.attachments[0].url
                embed.set_image(url=imageurl)
            else:
                await ctx.message.delete()
        else:
            await ctx.message.delete()
        await ctx.channel.send(embed=embed)


    # Edit an embedded message from the bot
    @say.command(
        name='Edit',
        description="Edit a previously created embedded message.",
        brief="Change a bot message.",
        aliases=['edit', 'e'])
    @commands.guild_only()
    @commands.is_owner()
    async def edit_say(self, ctx, message: discord.Message, *, content: str=None):
        # Only allow editing of the bot's messages
        if message.author != self.bot.user:
            await ctx.channel.send("I can't edit messages that aren't mine!")
            return
        # If no new text is passed in, preserve the original text as-is
        if content:
            embed = discord.Embed(description=content)
        else:
            embedlist = message.embeds
            content = embedlist[0].description
            if content:
                embed = discord.Embed(description=content)
            else:
                embed = discord.Embed()
        # If changing the attachment, get new image and leave invoke message
        if ctx.message.attachments:
            imageurl = ctx.message.attachments[0].url
            embed.set_image(url=imageurl)
        elif message.embeds[0].image:
            imageurl = message.embeds[0].image.url
            embed.set_image(url=imageurl)
            await ctx.message.delete()
        await message.edit(embed=embed)


    # Command to return a user's profile
    @commands.group(
        name='Profile',
        description="Display your profile information.",
        brief="Get your profile.",
        aliases=['profile', 'prof'],
        invoke_without_command=True)
    @commands.guild_only()
    @checks.check_perms()
    async def profile(self, ctx, *, member: discord.Member=None):
        # If a member was passed in, make sure it's not a bot
        if member:
            if member.bot:
                await ctx.channel.send("Bots don't have profiles!")
                return
        # If no member was passed in or found, assume invoker is target
        else:
            member = ctx.author
        # Get the DB profile info of the target
        dbprof = await db.get_member(ctx.guild.id, member.id)
        # Get the strings for the Profile menu from resources
        strings = await self.get_strings('Profile')
        # Input target's level and guild name
        head = strings['head'].format(dbprof['lvl'])
        desc = strings['desc'].format(ctx.guild.name)
        # If the target has set their birthday, replace the date with their age
        if dbprof['birthday']:
            dbprof = dict(dbprof)
            dt = datetime.strptime(dbprof['birthday'], '%Y-%m-%d')
            now = date.today()
            age = now.year-dt.year-((now.month, now.day)<(dt.month, dt.day))
            dbprof['birthday'] = age
        # Add any existing profile info to strings, then append it to fields
        fields = []
        for field in strings['fields']:
            key = field['data']
            if dbprof[key] is not None:
                field['fdesc'] = f"{field['fdesc']}{dbprof[key]}"
                fields.append(field)
        # Create Profile menu using the updated strings
        Profile = self.MenuEmbed(ctx.author, head, desc, fields)
        await Profile.add_fields()
        # Fill out remaining un-set fields using target info
        Profile.set_author(name=f"{member.name}'s Profile")
        avatar = member.avatar_url_as(format='png')
        Profile.set_thumbnail(url=avatar)
        # Send embed, add controls, and then loop
        message = await ctx.channel.send(embed=Profile)
        controls = await Profile.add_control(message)
        if controls:
            await self.wait_for_select(Profile, 55.0)


    # Command to fill out profile info via DM
    @profile.command(
        name='Edit',
        description="Edit your member profile information.",
        brief="Edit profile information.",
        aliases=['edit', 'e'])
    @commands.guild_only()
    @checks.check_perms()
    async def profile_manager(self, ctx):
        strings = await self.get_strings('Manager')
        head = strings['head']
        desc = strings['desc']
        fields = strings['fields']
        PM = self.MenuEmbed(ctx.author, head, desc, fields, True)
        await PM.add_fields()
        message = await ctx.channel.send(embed=PM)
        controls = await PM.add_control(message)
        if controls:
            await self.wait_for_select(PM, 55.0)
        if not PM.selected:
            return
        edit = "**Instructions being sent via DM, check your messages.**"
        await message.edit(content=edit, delete_after=5.0)
        reply = (f"{PM.selected['prompt']}\n\n"
                 f"Character limit: {PM.selected['limit']}\n")
        await ctx.author.send(content=reply)
        await db.add_temp(ctx.guild.id,
                          ctx.author.id,
                          "Manager",
                          PM.selected['data'])


    # Command for obtaining a daily cash award
    @commands.command(
        name='DailyCredits',
        aliases=['dailycredits', 'daily', 'credits', 'cashme', 'getmoney'])
    @commands.guild_only()
    @checks.check_perms()
    async def daily_cash(self, ctx):
        gID = ctx.guild.id
        member = ctx.author
        now = ctx.message.created_at
        dbprof = await db.get_member(gID, member.id)
        timeformat = '%Y-%m-%d %H:%M:%S.%f'
        if dbprof['daily_timestamp']:
            lastdaily = datetime.strptime(dbprof['daily_timestamp'],
                                          timeformat)
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
                str = (f"I already gave you money, {member.mention}! If you "
                       f"want more, you'll have to wait {hours} hour(s) and "
                       f"{minutes} minute(s).")
            elif seconds > 60:
                str = (f"I already gave you money, {member.mention}! If you "
                       f"want more, you'll have to wait {minutes} minute(s) "
                       f"and {seconds} second(s).")
            else:
                str = (f"I already gave you money, {member.mention}! If you "
                       f"want more, you'll have to wait {seconds} second(s).")
            await ctx.channel.send(str)
        else:
            newcash = dbprof['cash'] + 500
            await db.set_member(gID, member.id, 'cash', newcash)
            await db.set_member(gID, member.id, 'daily_timestamp', now)
            await ctx.channel.send(
                f"Here's a 500 credit freebie, {member.mention}!")


    # Command to transfer currency from one user to another
    @commands.command(
        name='Transfer',
        description="Transfer credits from one user to another.",
        aliases=['transfer'])
    @commands.guild_only()
    @checks.check_perms()
    async def transfer(self, ctx, amount: int, member: discord.Member):
        if member.bot:
            await ctx.channel.send("Bots don't have profiles!")
            return
        if amount < 1:
            await ctx.channel.send(
                "Minumum amount of credits to transfer is 1.")
            return
        if ctx.author == member:
            await ctx.channel.send("Can't transfer credits to yourself.")
            return
        dbprof_author = await db.get_member(ctx.author.guild.id, ctx.author.id)
        if amount > dbprof_author['cash']:
            await ctx.channel.send(
                "Provided amount is higher than owned credits.")
            return
        await db.transfer_currency(ctx.guild.id, ctx.author.id, member.id, amount)
        await ctx.channel.send(
            f"{ctx.author.mention} has given {amount} credits to {member.mention}.")


    # Error handler for transfer
    @transfer.error
    async def transfer_handler(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            if error.param.name == 'amount':
                await ctx.send(
                    "You forgot to give an amount of credits to transfer.")
                return
            elif error.param.name == 'member':
                await ctx.send(
                    "You forgot to mention a member you wish to transfer.")
                return
        elif isinstance(error, commands.BadArgument):
            if error.args[0] == 'Converting to "int" failed for parameter "amount".':
                await ctx.channel.send(
                    "Please provide a valid amount of credits.")
                return
            else:
                await ctx.send("Member not found.")
                return
        else:
            raise error


    # Command to award currency to a user
    @commands.command(
        name='Award',
        description="Award a user with credits.",
        aliases=['award'])
    @commands.guild_only()
    @commands.is_owner()
    async def award(self, ctx, amount: int, member: discord.Member):
        if member.bot:
            await ctx.channel.send("Bots don't have profiles!")
            return
        if amount < 1:
            await ctx.channel.send(
                "Minumum amount of credits to award is 1.")
            return
        await db.add_currency(ctx.guild.id, member.id, amount)
        await ctx.channel.send(
            f"Awarded {amount} credits to {member.mention}.")


    # Command to remove currency from a user
    @commands.command(
        name='Seize',
        description="Remove credits from a user.",
        aliases=['seize'])
    @commands.guild_only()
    @commands.is_owner()
    async def seize(self, ctx, amount: int, member: discord.Member):
        if member.bot:
            await ctx.channel.send("Bots don't have profiles!")
            return
        if amount < 1:
            await ctx.channel.send(
                "Minumum amount of credits to remove is 1.")
            return
        await db.remove_currency(ctx.guild.id, member.id, amount)
        await ctx.channel.send(
            f"Removed {amount} credits from {member.mention}.")


    # Shop menu function. This is hacky and needs a lot of refinement.
    @commands.group(
        name='GuildShop',
        aliases=['guildshop', 'shop'],
        invoke_without_command=True)
    @commands.guild_only()
    @checks.check_perms()
    async def shop(self, ctx):
        # Get invoker profile for display of current balance
        dbprof = await db.get_member(ctx.guild.id, ctx.author.id)
        # Get guild-specific data for the shop values and currency symbol
        dbcfg = await db.get_cfg(ctx.guild.id)
        if dbcfg['currency'].isdigit():
            try:
                dbcfg['currency'] = await commands.EmojiConverter().convert(
                    ctx,
                    dbcfg['currency'])
            except:
                dbcfg['currency'] = u"\U0001F48E"
        elif not dbcfg['currency']:
            dbcfg['currency'] = u"\U0001F48E"
        # Get default strings for the shop menu
        strings = await self.get_strings('Shop')
        # Set header and description of embed based on guild and invoker info
        head = strings['head'].format(ctx.guild.name)
        desc = strings['desc'].format(
            ctx.author.name,
            dbcfg['currency'],
            dbprof['cash'])
        # Modify strings to include guild-specific data
        fields = []
        for item in strings['fields']:
            # Set price and availability of item
            if item['data'] == 'role':
                item['available'] = dbcfg['crole_available']
                item['price'] = dbcfg['crole_price']
            elif item['data'] == 'emoji':
                item['available'] = dbcfg['cemoji_available']
                item['price'] = dbcfg['cemoji_price']
            # Add availability to item description
            if item['available'] == 0:
                item['fdesc'] = (
                    f"{item['fdesc']}\n\n"
                    f"Available: None")
            elif item['available'] < 0:
                item['fdesc'] = (
                    f"{item['fdesc']}\n\n"
                    f"Available: \u221E")
            else:
                item['fdesc'] = (
                    f"{item['fdesc']}\n\n"
                    f"Available: {item['available']}")
            # Add price to item description
            if item['price'] == 0:
                item['fdesc'] = (
                    f"{item['fdesc']}\n"
                    f"Price: {currency} Free")
            else:
                item['fdesc'] = (
                    f"{item['fdesc']}\n"
                    f"Price: {currency} {item['price']}")
            # Add file size and type limits to prompt
            if item['format'] == 'text':
                item['prompt'] = (
                    f"{item['prompt']}\n\n"
                    f"Max length: {item['limit']} characters")
            elif item['format'] == 'image':
                item['prompt'] = (
                    f"{item['prompt']}\n\n"
                    f"Max size: {int(item['limit']/1000)}kb\n"
                    f"File types accepted: {item['types']}")
            # Append the modified item to fields list
            fields.append(item)
        # Create instance of Shop menu, add fields and controls, and then loop
        Shop = self.MenuEmbed(ctx.author, head, desc, fields, True)
        await Shop.add_fields()
        message = await ctx.channel.send(embed=Shop)
        controls = await Shop.add_control(message)
        if controls:
            bought = False
            while not bought:
                await self.wait_for_select(Shop, 55.0)
                # If no item was purchased, exit the command
                if not Shop.selected:
                    break
                # If none of selected item are available, throw error to user
                elif Shop.selected['available'] == 0:
                    edit = (f"**{Shop.selected['fname']} is not currently "
                            f"available. Please select another item.**")
                    await message.edit(content=edit)
                # If user doesn't have enough credits, throw error to user
                elif dbprof['cash'] < Shop.selected['price']:
                    edit = (f"**You don't have enough credits for "
                            f"{Shop.selected['fname']}!**")
                    await message.edit(content=edit)
                # If checks pass, process purchase and set bought to true
                else:
                    await db.remove_currency(
                        ctx.guild.id,
                        ctx.author.id,
                        Shop.selected['price'])
                    if Shop.selected['data'] == 'role':
                        if Shop.selected['available'] > 0:
                            await db.set_cfg(
                                ctx.guild.id,
                                'crole_available',
                                Shop.selected['available'] - 1)
                    bought = True
            if not bought:
                return
            # If the item purchased requires a second step, send prompt2
            if Shop.selected['prompt2']:
                edit = f"**{Shop.selected['fname']} bought! Check your DM's.**"
                await message.edit(content=edit, delete_after=5.0)
                await db.add_temp(
                    ctx.guild.id,
                    ctx.author.id,
                    "Shop",
                    Shop.selected['data'])
                await ctx.author.send(content=Shop.selected['prompt'])
            else:
                edit = f"**{Shop.selected['fname']} bought!**"
                await message.edit(content=edit, delete_after=5.0)


    # Command to set item availability in the shop
    @shop.command(
        name='Available',
        aliases=['available', 'a'])
    @commands.guild_only()
    @checks.check_perms()
    async def available(self, ctx, data: str, input: int):
        strings = await self.get_strings('Shop')
        for item in strings['fields']:
            if item['data'] == data.lower():
                selected = item
        if not selected:
            await ctx.channel.send("Shop item not found!")
            return
        if selected['data'] == 'emoji':
            if 'MORE_EMOJI' in ctx.guild.features:
                emojilimit = 200
            else:
                emojilimit = 50
            if (emojilimit - len(ctx.guild.emojis)) > 0:
                max = emojilimit - len(ctx.guild.emojis)
                if input > max or input < 0:
                    await db.set_cfg(ctx.guild.id, 'cemoji_available', max)
                    reply = (f"Available custom emoji in the shop set to "
                             f"{max} (maximum available for this guild).")
                else:
                    await db.set_cfg(ctx.guild.id, 'cemoji_available', input)
                    reply = (f"Available custom emoji in the shop set to "
                             f"{input}.")
            else:
                await ctx.channel.send("Max custom emoji slots reached!")
                return
        elif selected['data'] == 'role':
            await db.set_cfg(ctx.guild.id, 'crole_available', input)
            if input < 0:
                reply = (f"Set number of {selected['fname']} available in "
                         f"the shop to infinite.")
            else:
                reply = (f"Set number of {selected['fname']} available in "
                         f"the shop to {input}.")
        await ctx.channel.send(content=reply)


    # Command to set item price in the shop
    @shop.command(
        name='Price',
        aliases=['price', 'Cost', 'cost', 'p', 'c'])
    @commands.guild_only()
    @checks.check_perms()
    async def price(self, ctx, data: str, input: int):
        strings = await self.get_strings('Shop')
        for item in strings['fields']:
            if item['data'] == data.lower():
                selected = item
        if not selected:
            await ctx.channel.send("Shop item not found!")
            return
        if input <= 0:
            await db.set_cfg(ctx.guild.id, 'crole_price', 0)
            reply = f"Set price of {selected['fname']} to free."
        else:
            await db.set_cfg(ctx.guild.id, 'crole_price', input)
            reply = f"Set price of {selected['fname']} to {input}"
        await ctx.channel.send(content=reply)


    # Command to display current guild leaderboard
    @commands.command(
        name='Leaderboard',
        description="Display the guild leaderboard",
        aliases=['leaderboard', 'lb'])
    @commands.guild_only()
    @checks.check_perms()
    async def leaderboard(self, ctx):
        head = f"Leaderboard for **{ctx.guild.name}**"
        members = await db.get_all_members(ctx.guild.id)
        members.sort(key=lambda member : member['xp'], reverse=True)
        fields = []
        rank = 1
        for member in members:
            gmember = ctx.guild.get_member(member['member_id'])
            if not gmember:
                continue
                # fields.append({'fname': f"#{rank} - "
                #                        f"{member['member_id']} (Not Found)",
                #               'fdesc': f"**Level: {member['lvl']}** "
                #                        f"- {member['xp']} xp",
                #               'inline': False})
            else:
                fields.append({'fname': f"#{rank} - {gmember.display_name}",
                               'fdesc': f"**Level: {member['lvl']}** "
                                        f"- {member['xp']} xp",
                               'inline': False})
                if gmember == ctx.author:
                    desc = f"Your rank: **#{rank} - {gmember.display_name}**"
                rank += 1
        LB = self.MenuEmbed(ctx.author, head, desc, fields)
        await LB.add_fields()
        message = await ctx.channel.send(embed=LB)
        controls = await LB.add_control(message)
        if controls:
            await self.wait_for_select(LB, 55.0)


    # Do stuff when a message is sent
    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.author.bot and not message.guild:
            temp = await db.get_temp(message.author.id)
            if temp:
                strings = await self.get_strings(temp['menu'])
                for item in strings['fields']:
                    if item['data'] == temp['selected']:
                        selected = item
                        break
                if temp['menu'] == 'Shop':
                    await self.purchase(message, selected, temp)
                elif temp['menu'] == 'Manager':
                    await self.manage_profile(message, selected, temp)


    # Remove a custom role when it's deleted
    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):
        await db.del_custom_role(role.guild.id, role.id)


    # Adjust custom emoji available in shop when emojis are modified
    @commands.Cog.listener()
    async def on_guild_emojis_update(self, guild, before, after):
        curshoplimit = await db.get_cfg(guild.id, 'cemoji_available')
        if curshoplimit == 0:
            return
        elif curshoplimit < 0:
            if 'MORE_EMOJI' in guild.features:
                emojilimit = 200
            else:
                emojilimit = 50
            if (emojilimit - len(guild.emojis)) > 0:
                newshoplimit = emojilimit - len(guild.emojis)
            else:
                newshoplimit = 0
        else:
            if len(before) == len(after):
                return
            elif len(before) < len(after):
                newshoplimit = curshoplimit - 1
            else:
                newshoplimit = curshoplimit + 1
        await db.set_cfg(guild.id, 'cemoji_available', newshoplimit)


    # Looping to wait for a raw_reaction event that meets the expected criteria
    async def wait_for_select(self, Menu, time=None):
        def check(payload):
            return (payload.user_id == Menu.user.id and
                    payload.message_id == Menu.message.id)

        while not Menu.selected:
            try:
                payload = await self.bot.wait_for(
                    'raw_reaction_add',
                    timeout=time,
                    check=check)
                await Menu.message.remove_reaction(payload.emoji, Menu.user)
                if payload.emoji.name == Menu.closebtn:
                    raise asyncio.TimeoutError()
            except asyncio.TimeoutError:
                await Menu.message.clear_reactions()
                await Menu.message.edit(
                    content="Menu closing in 5 seconds...",
                    delete_after=5.0)
                break
            else:
                await Menu.process_reaction(payload.emoji.name)


    # Method for processing profile changes
    async def manage_profile(self, message, selected, temp):
        if len(message.content) > selected['limit']:
            await message.author.send(content="Over character limit!")
            return
        if message.content.lower() == "clear":
            await db.set_member(temp['guild_id'],
                                temp['member_id'],
                                selected['data'],
                                None)
            await db.del_temp(message.author.id)
            alert = f"Your profile's `{selected['fname']}` has been cleared!"
            await message.author.send(content=alert)
            return
        if selected['format'] == 'date':
            try:
                entered = datetime.strptime(message.content, '%Y-%m-%d')
                option = entered.date()
                alert = f"Your profile's `{selected['fname']}` has been set!"
            except ValueError:
                await message.author.send("Date in wrong format!")
                return
        elif selected['format'] == 'list':
            option = message.content.replace(", ", "\n")
            alert = f"Profile `{selected['fname']}` will show as `{option}`!"
        else:
            option = message.content
            alert = f"Profile `{selected['fname']}` will show as `{option}`!"
        await db.set_member(temp['guild_id'],
                            temp['member_id'],
                            selected['data'],
                            str(option))
        await db.del_temp(message.author.id)
        await message.author.send(content=alert)


    # Method to process multi-stage shop purchases
    async def purchase(self, message, selected, temp):
        if selected['data'] == 'role':
            if not temp['storage']:
                if len(message.content) > selected['limit']:
                    await message.author.send(content="Over character limit!")
                    return
                file = discord.File(IMAGES / "color_examples.png")
                await message.author.send(content=selected['prompt2'],
                                          file=file)
                await db.update_temp(temp, message.content)
            else:
                color = message.content.lower()
                converted = await self.convert_color(color)
                if not converted:
                    fail = "That's not a valid color! Please try again."
                    await message.author.send(content=fail)
                    return
                guild = self.bot.get_guild(temp['guild_id'])
                role = await guild.create_role(reason="Shop purchase",
                                               name=temp['storage'],
                                               color=converted, 
                                               mentionable=True)
                botRoleID = await db.get_cfg(guild.id, 'bot_role')
                botRole = guild.get_role(botRoleID)
                position = botRole.position - 1
                try:
                    await role.edit(position=position, reason="Shop purchase")
                except:
                    print("bing")
                member = guild.get_member(temp['member_id'])
                await db.add_custom_role(guild.id, member.id, role.id)
                await member.add_roles(role, reason="Shop purchase")
                await db.del_temp(member.id)
                await member.send("Role set! Enjoy your fancy new title!")
        elif selected['data'] == 'emoji':
            if not temp['storage']:
                upload = message.attachments[0]
                filetype = Path(upload.filename).suffix
                if filetype not in selected['types']:
                    await message.author.send("Wrong filetype!")
                    return
                elif upload.size > selected['limit']:
                    await message.author.send("File too big!")
                    return
                emoji = await upload.read()
                await message.author.send(content=selected['prompt2'])
                await db.update_temp(temp, emoji)
            else:
                name = message.content.replace(":", "").replace(" ", "")
                guild = self.bot.get_guild(temp['guild_id'])
                await guild.create_custom_emoji(name=name,
                                                image=temp['storage'],
                                                reason="Shop purchase")
                await db.del_temp(message.author.id)
                await message.author.send("Emoji set! Try it out in the server!")
        elif selected['data'] == 'ticket':
            pass
        else:
            pass


    # Method to convert a user-entered color to a discord.Color object
    async def convert_color(self, color):
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
        if color in colors.keys():
            convert = discord.Color(colors[color])
        else:
            try:
                color = int(f"0x{color}", 0)
                convert = discord.Color(color)
            except ValueError:
                try:
                    color = int(f"{color}", 0)
                    convert = discord.Color(color)
                except TypeError:
                    return
        return convert


    # Method for grabbing fields for embed strings.
    async def get_strings(self, name):
        with open(STRINGPATH, 'r') as stream:
            loaded = load(stream, Loader=Loader)
        for item in loaded['embeds']:
            if item['name'] == name:
                return item


    # Method for modifying fields for embed strings. Not currently used.
    async def set_strings(self, name, data, key, value):
        with open(STRINGPATH, 'r') as stream:
            loaded = load(stream, Loader=Loader)
        for item in loaded['embeds']:
            if item['name'] == name:
                for field in item['fields']:
                    if field['data'] == data:
                        field[key] = value
        with open(STRINGPATH, 'w') as stream:
            dump(loaded, stream, Dumper=Dumper, sort_keys=False, indent=4)
