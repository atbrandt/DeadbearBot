import os
from pathlib import Path
from dotenv import load_dotenv
import discord
from discord.ext import commands
from cogs.utils import db
from cogs.utils import migration
from cogs.utils import generic
from cogs import config
from cogs import embeds
from cogs import roles
# from cogs import testing


# Path to environment variables
ENVFILE = Path(__file__).parent / "secret.env"


# Loading environment variables and checking for secret token presence
if ENVFILE.exists():
    load_dotenv(dotenv_path=ENVFILE)
    token = os.getenv('DEADBEAR_TOKEN')
else:
    print("No bot token found!")
    token = input("Enter your bot's token: ")
    with ENVFILE.open('w', encoding='utf-8') as f:
        f.write(f"export DEADBEAR_TOKEN=\'{token}\'")


# Create callable to obtain guild-specific alias for command prefix
async def get_alias(bot, message):
    if message.guild:
        guild = message.guild.id
        prefix = await db.get_cfg(guild, 'bot_alias')
        if prefix:
            return prefix
    return "-"


# Set up the bot, its cogs, and its command prefix alias
intents = discord.Intents.all()
bot = commands.Bot(command_prefix=get_alias, intents=intents)
bot.add_cog(config.Config(bot))
bot.add_cog(generic.Generic(bot))
bot.add_cog(embeds.Embeds(bot))
bot.add_cog(roles.Roles(bot))


# Command to gracefully shut down the bot
@bot.command(name='Shutdown',
             description="Shut down the bot and close all connections.",
             brief="Shut down the bot.",
             aliases=['die'])
@commands.is_owner()
async def shutdown(ctx):
    await ctx.channel.send("Shutting down...")
    await bot.logout()


# Do stuff to members upon joining guild
@bot.event
async def on_member_join(member):
    dbmember = await db.get_member(member.guild.id, member.id)
    if not member.bot and not dbmember:
        await db.add_member(member.guild.id,
                            member.id,
                            member.created_at,
                            member.joined_at)


# Add guild when joining new guild
@bot.event
async def on_guild_join(guild):
    await add_guild(guild)


# Make the bot ignore commands until fully initialized
@bot.event
async def on_connect():
    print(f"{bot.user.name} connected, user ID is {bot.user.id}. Getting ready...")
    await bot.wait_until_ready()


# Output info to console once bot is initialized and ready
@bot.event
async def on_ready():
    for guild in bot.guilds:
        print(f"Ready in {guild.name}")
        await add_guild(guild)
    print("------Bot Ready------")


# Add guild function
async def add_guild(guild):
    await db.add_guild(guild.id)
    botrole = await db.get_cfg(guild.id, 'bot_role')
    if not botrole:
        botmember = guild.get_member(bot.user.id)
        for role in botmember.roles:
            if role.managed and role.name == "DeadbearBot":
                await db.set_cfg(guild.id, 'bot_role', role.id)
                break
    for member in guild.members:
        dbmember = await db.get_member(guild.id, member.id)
        if not member.bot and not dbmember:
            await db.add_member(guild.id,
                                member.id,
                                member.created_at,
                                member.joined_at)


# Run the program
if __name__ == '__main__':
    migration.migrate()
    try:
        bot.run(token)
    except discord.PrivilegedIntentsRequired:
        print("Privileged Intents are required to use this bot. "
            "Enable them through the Discord Developer Portal.")
