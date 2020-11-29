import discord
from discord.ext import commands


class Generic(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


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

# add blurbs, reminders, birthday alerts