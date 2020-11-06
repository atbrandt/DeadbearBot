import os
from pathlib import Path
from dotenv import load_dotenv
import discord
from discord.ext import commands
from app import db
from app import migration
from app import resource
from app.cogs import generic
from app.cogs import config
from app.cogs import embeds
from app.cogs import roles
# from app.tests import testing


# Path to environment variables
ENVFILE = Path(__file__).parent / "secret.env"


# Loading environment variables and checking for secret token presence
if ENVFILE.exists():
    load_dotenv(dotenv_path=ENVFILE)
    token = os.getenv('DEADBEAR_TOKEN')
else:
    print("No bot token found!")
    token = input("Enter your bot's token: ")
    with Path.open(ENVFILE, 'w', encoding='utf-8') as file:
        file.write(f"export DEADBEAR_TOKEN=\'{token}\'")


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
    dbmember = await db.get_member(guild.id, member.id)
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
    await bot.wait_until_ready()


# Output info to console once bot is initialized and ready
@bot.event
async def on_ready():
    print(f"{bot.user.name} is ready, user ID is {bot.user.id}")
    print("------")
    for guild in bot.guilds:
        await add_guild(guild)


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
def main():
    migration.migrate()
    bot.run(token)


if __name__ == '__main__':
    main()
