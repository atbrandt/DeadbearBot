from pathlib import Path
import discord
from discord.ext import commands
from discord.utils import get


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
        if ctx.message.attachments[0].filename:
        embed.set_image(url=ctx.message.attachments[0].url)
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


