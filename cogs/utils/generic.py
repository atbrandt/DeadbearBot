from datetime import date, datetime

import discord
from discord.ext import commands, tasks

from .db import get_all_guilds, get_all_members


class Generic(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.birthday_alert.start()


    # Testing command
    @commands.command(
        name='test')
    async def hello_world(self, ctx):
        print(f"Message sent in {ctx.channel} from {ctx.author.id}")
        await ctx.channel.send(f"Hello {ctx.author}!")


    # Get list of roles (with IDs) on guild
    @commands.command(
        name='GetRoleIDs',
        description="Returns list of roles on server with IDs.",
        brief="Get all roles with IDs",
        aliases=['roles'])
    @commands.guild_only()
    @commands.is_owner()
    async def get_roles(self, ctx):
        output = ""
        for role in ctx.guild.roles:
            output += f"{role.id} {role.name}\n"
        await ctx.channel.send(f"```{output}```")


    # Get list of emojis (with IDs) on guild
    @commands.command(
        name='GetEmojiIDs',
        description="Returns list of emojis on server with IDs.",
        brief="Get all emojis with IDs",
        aliases=['emojis'])
    @commands.guild_only()
    @commands.is_owner()
    async def get_emojis(self, ctx):
        output = ""
        for emoji in ctx.guild.emojis:
            output += f"{emoji.id} {emoji.name}\n"
        await ctx.channel.send(f"```{output}```")


    # Get list of channels (with IDs) on guild
    @commands.command(
        name='GetChannelIDs',
        description="Returns list of channels on server with IDs.",
        brief="Get all channels with IDs",
        aliases=['channels'])
    @commands.guild_only()
    @commands.is_owner()
    async def get_channels(self, ctx):
        output = ""
        for channel in ctx.guild.channels:
            output += f"{channel.id} {channel.name}\n"
        await ctx.channel.send(f"```{output}```")


    # Send a message to a user on their birth day
    @tasks.loop(hours=24)
    async def birthday_alert(self):
        # List to save id of members who already recieved a msg
        member_ids_sent = []
        guild_ids = await get_all_guilds()
        for guild_id in guild_ids:
            members = await get_all_members(guild_id)
            for member in members:
                member_id = member['member_id']
                if member['birthday'] == None or member_id in member_ids_sent:
                    continue
                bday = datetime.strptime(member['birthday'], '%Y-%m-%d')
                now = date.today()
                if (bday.month, bday.day) == (now.month, now.day):
                    user = self.bot.get_user(member_id)
                    reply = f"Happy birthday, **{user.name}**!"
                    await user.send(content=reply)
                    member_ids_sent.append(member_id)

    # Wait until the bot is ready before the birthday_alert loop starts
    @birthday_alert.before_loop
    async def before_birthday_alert(self):
        await self.bot.wait_until_ready()
        
# add blurbs, reminders