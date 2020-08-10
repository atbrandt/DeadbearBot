import math
import random
from typing import Union, Optional
import discord
from discord.ext import commands
from app import db


class Config(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    # Set an alias for the bot prefix
    @commands.command(name='PrefixAlias',
                      description="Sets an alias for the default command prefix.",
                      brief="Set command prefix alias.",
                      aliases=['prefix'])
    @commands.guild_only()
    @commands.is_owner()
    async def change_prefix(self, ctx, prefix):
        await db.set_cfg(ctx.guild.id, 'bot_alias', prefix)
        await ctx.channel.send(f"My command prefix is now \"{prefix}\".")


    # Set perm roles for public commands
    @commands.command(name='PermissionRoles',
                      description="Sets roles that can use basic commands.",
                      brief="Set permrole.",
                      aliases=['permrole'])
    @commands.guild_only()
    @commands.is_owner()
    async def set_perms(self, ctx, role: discord.Role):
        await db.set_cfg(ctx.guild.id, 'perm_role', role.id)
        await ctx.channel.send(f"Added \"{role.name}\" to perm roles.")


    # Set the channel for join messages
    @commands.group(name='GuildJoin',
               description="Enables or disables the automatic join message in a "
                           "specified channel. Pass no channel to disable.",
               brief="Turn join messages on or off.",
               aliases=['gj'],
               invoke_without_command=True)
    @commands.guild_only()
    @commands.is_owner()
    async def gjoin(self, ctx, channel: discord.TextChannel=None):
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
    async def gjoin_message(self, ctx, *, message: str):
        await db.set_cfg(ctx.guild.id, 'join_message', message)
        await ctx.channel.send(f"The join message is now: \"{message}\"")


    # Set the channel for leave messages
    @commands.group(name='GuildLeave',
               description="Enables or disables the automatic leave message in a "
                           "specified channel. Pass no channel to disable.",
               brief="Turn leave message on or off.",
               aliases=['gl'],
               invoke_without_command=True)
    @commands.guild_only()
    @commands.is_owner()
    async def gleave(self, ctx, channel: discord.TextChannel=None):
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
    async def gleave_message(self, ctx, *, message: str):
        await db.set_cfg(ctx.guild.id, 'leave_message', message)
        await ctx.channel.send(f"The farewell message is now: \"{message}\"")


    # Set the currency symbol
    @commands.command(name='Set Currency Symbol',
                      description="Sets the server currency symbol.",
                      aliases=['setcur'])
    @commands.guild_only()
    @commands.is_owner()
    async def set_currency(self, ctx, emoji: Union[discord.Emoji, str]):
        if type(emoji) is str:
            await db.set_cfg(ctx.guild.id, 'currency', emoji)
        else:
            await db.set_cfg(ctx.guild.id, 'currency', emoji.id)            
        await ctx.channel.send(f"The currency symbol is now: \"{emoji}\"")


    # Toggle guild stat tracking
    @commands.command(name='Stats',
                      description="Toggles guild stats.",
                      aliases=['stats'])
    @commands.guild_only()
    @commands.is_owner()
    async def stats(self, ctx):
        stats = await db.get_cfg(ctx.guild.id, 'guild_stats')
        if stats:
            reply = "Guild stats have been disabled!"
            await db.set_cfg(ctx.guild.id, 'guild_stats', None)
        else:
            reply = "Guild stats have been enabled!"
            await db.set_cfg(ctx.guild.id, 'guild_stats', 'enabled')
        await ctx.channel.send(reply)


    # Manage starboard settings
    @commands.command(name='Starboard',
                 description="Sets the configuration for starred messages.",
                 brief="Modify starboard settings.",
                 aliases=['star'])
    @commands.guild_only()
    @commands.is_owner()
    async def starboard(self, ctx, channel: discord.TextChannel=None):
        starboard = await db.get_cfg(ctx.guild.id, 'star_channel')
        if starboard is None:
            await db.set_cfg(ctx.guild.id, 'star_channel', channel.id)
            await ctx.channel.send(f"Set \"{channel.name}\" as the star board.")
        else:
            await db.set_cfg(ctx.guild.id, 'star_channel', None)
            await ctx.channel.send(f"Starboard disabled.")


    # Event hook for reactions being added to messages
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.user_id == self.bot.user.id:
            return
        elif payload.guild_id:
            await self.star_check(payload, 'add')


    # Event hook for reactions being removed from messages
    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        if payload.user_id == self.bot.user.id:
            return
        elif payload.guild_id:
            await self.star_check(payload, 'rem')


    # Do stuff when a message is sent
    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.author.bot and message.guild:
            stats = await db.get_cfg(message.guild.id, 'guild_stats')
            if stats == 'enabled':
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
                    await channel.send(f"**{member.name}** has leveled up to "
                                       f"**level {nextlevel}!**")
                    await db.set_member(guildID, member.id, 'lvl', nextlevel)


    # Handler for guild reaction events
    async def star_check(self, payload, event):
        starboard = await db.get_cfg(payload.guild_id, 'star_channel')
        if not starboard:
            return
        starnsfw = await db.get_cfg(payload.guild_id, 'star_nsfw')
        guild = self.bot.get_guild(payload.guild_id)
        channel = guild.get_channel(payload.channel_id)
        if channel.is_nsfw() and not starnsfw:
            return
        message = await channel.fetch_message(payload.message_id)
        if message.author.bot:
            return
        threshold = await db.get_cfg(guild.id, 'star_threshold')
        starred = await db.get_starred(message.id)
        starchannel = guild.get_channel(starboard)
        if not starred:
            for react in message.reactions:
                if react.count >= threshold:                    
                    await self.star_add(message, starchannel)
                    break
        else:
            if len(message.reactions) < 2:
                await self.star_remove(starchannel, starred)
            else:
                for react in message.reactions:
                    if react.count < threshold:
                        await self.star_remove(starchannel, starred)
                        break


    # Add star to starboard
    async def star_add(self, message, starchannel):
        star = discord.Embed(description=message.content,
                              color=0xf1c40f)
        star.set_author(name=message.author.display_name,
                         icon_url=message.author.avatar_url)
        if message.attachments:
            images = []
            files = []
            filetypes = ('png', 'jpeg', 'jpg', 'gif', 'webp')
            for attachment in message.attachments:
                if attachment.url.lower().endswith(filetypes):
                    images.append(attachment)
                else:
                    files.append(attachment)
            for i, file in enumerate(files):
                star.add_field(name=f"Attachment {i + 1}",
                               value=f"[{file.filename}]({file.url})",
                               inline=True)
            star.set_thumbnail(url=files[0].url)
        star.add_field(name="--",
                       value=f"[Jump to original...]({message.jump_url})",
                       inline=False)
        star.set_footer(text="Originally sent")
        star.timestamp = message.created_at
        newstar = await starchannel.send(embed=star)
        await db.add_starred(message.guild.id, message.id, newstar.id)


    # Remove star from starboard
    async def star_remove(self, starchannel, starred):
        oldstar = await starchannel.fetch_message(starred['starred_id'])
        await oldstar.delete()
        await db.del_starred(starred['original_id'])

