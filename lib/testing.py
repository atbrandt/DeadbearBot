from pathlib import Path
import discord
from discord.ext import commands
from discord.utils import get


# Testing command
@bot.command(name='test')
async def hello_world(ctx):
    print(f"Message sent in {ctx.channel} from {ctx.author.id}")
    await ctx.channel.send(f"Hello {ctx.author}!")


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


