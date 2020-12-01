from datetime import date

import discord
from discord.ext import commands, tasks

from .db import get_members_by_bday


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


    # Do stuff when a message is deleted
    @commands.Cog.listener()
    async def on_message_delete(self, message):
        pass


    # Send a message to a user on their birthday
    @tasks.loop(hours=24)
    async def birthday_alert(self):
        members = await get_members_by_bday(date.today())
        for member in members:
            member_id = member['member_id']
            user = self.bot.get_user(member_id)
            reply = f"Happy birthday, **{user.name}**!"
            await user.send(content=reply)


    # Wait until the bot is ready before the birthday_alert loop starts
    @birthday_alert.before_loop
    async def before_birthday_alert(self):
        await self.bot.wait_until_ready()
        
# add blurbs, reminders