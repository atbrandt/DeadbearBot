import discord
from discord.ext import commands
from . import db


# Checking perms before executing command
def check_perms():
    async def predicate(ctx):
        return await check_perm_role(ctx)
    return commands.check(predicate)


async def check_perm_role(ctx):
    if ctx.author.id == ctx.bot.owner_id:
        return True
    permrole = await db.get_cfg(ctx.guild.id, 'perm_role')
    if not permrole:
        return True
    gotRole = ctx.guild.get_role(permrole)
    roles = ctx.author.roles
    return gotRole in roles