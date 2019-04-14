#Shinobu Bot
#It's a bot made of Shinobus, i dunno.
#Client ID for this bot: 566889645653229579,
#Bear, when you get the opportunity, please paste the following hyperlink into your browser bar to allow the bot to join, arigathanks, my guy
# https://discordapp.com/oauth2/authorize?client_id=566889645653229579&scope=bot&permissions=0
import discord
import time
import asynchio

message = joined = 0

TOKEN = 'NTY2ODg5NjQ1NjUzMjI5NTc5.XLLmBw.s5c_X7P5cGHSZJVGYpw5oNpr_-o'
#replace this with the bot token in order for it to work properly

client = discord.Client()

@client.event #fxn decorator
async def on_ready():
    print('Bot is ready')
    print(client.user.name)
    print(client.user.id)
    print('------')

@client.event
async def on_member_join(member):
    for channel in member.server.channels:
        if str(channel) == "general":
            await client.send_message(f"""Welcome to the server {member.mention}""")

@client.event
async def on_member_update(before, after):
    n = after.nick
    if n:
        if n.lower().count("tim") > 0:
            last = before.nick
            if last:
                await after.edit(nick=last)
            else:
                await after.edit(nick="NO STOP THAT")


@client.event
async def on_member_join(member):
    global joined
    joined += 1
    for channel in member.server.channels:
        if str(channel) == "general":
            await channel.send(f"""Welcome to the server {member.mention}""")


@client.event
async def on_message(message):
    global messages
    messages += 1
    
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return

    id = client.get_guild(ID HERE)
    channels = ["commands"]
    valid_users = ["Spacebear#4236"]
    bad_words = [""]

    for word in bad_words:
        if message.content.count(word) > 0:
            print("A bad word was said")
            await message.channel.purge(limit=1)

    if message.content == "!help":
        embed = discord.Embed(title="Help on BOT", description="Some useful commands")
        embed.add_field(name="!hello", value="Greets the user")
        embed.add_field(name="!users", value="Prints number of users")
        await message.channel.send(content=None, embed=embed)

    if str(message.channel) in channels and str(message.author) in valid_users:
        if message.content.find("!hello") != -1:
            await message.channel.send("Hi") 
        elif message.content == "!users":
            await message.channel.send(f"""# of Members: {id.member_count}""")

client.run(TOKEN)
