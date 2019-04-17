#Shinobu Bot
#It's a bot made of Shinobus, i dunno. .-.
#Client ID for this bot: 566889645653229579,
#Bear, when you get the opportunity, please paste the following hyperlink into your browser bar to allow the bot to join, arigathanks, my guy
# https://discordapp.com/oauth2/authorize?client_id=566889645653229579&scope=bot&permissions=0
import discord
import time
import asynchio

messages = joined = 0 #For update_stats() fxn

#This fxn is to read the token.txt file,
#Then assign it to the variable token
def read_token();
    with open("token.txt", "r") as f:
        lines = f.readlines()
        return lines[0].strip()

token = read_token()
#Lets us connect to our bot.
client = discord.Client()

#async fxn for logging and storing information/data
@client.event
async def update_stats():
    await client.wait_until_ready()
    global messages, joined

    while not client.is_closed():
        try:
            with open("stats.txt", "a") as f:
                f.write(f"Time: {int(time.time())}, Messages: {messages}, Members joined: {joined}\n")

            messages = 0
            joined = 0

            await asyncio.sleep(5)
        except Exception as e:
            print(e)
            await asyncio.sleep(5)

#Async fxn designed to change nicknames
async def on_member_update(before, after):
    n = after.nick
    if n:
        if n.lower().count("staff") > 0: # If username contains staff
            last = before.nick
            if last: # if they had a username before change it back to that.
                await after.edit(nick=last)
            else: #Otherwise set it to Cheeky Breeky.
                await after.edit(nick = "Cheeky Breeky")

#An async fxn where a welcome msg pops up
@client.event
async def on_member_join(member):
    global joined
    joined += 1
    for channel in member.server.channels:
        #we check to make sure we are sending the message in the general channel
        if str(channel) == "general":
            await client.send_message(f"""Welcome to the server, {member.mention}!""")

#async fxn that evokes bot commands
@client.event
async def on_message(message):
    global messages
    messages += 1

    id = client.get_guild(ID HERE) #your server ID goes here.
    channels = ["commands"];
    required_prefix = ":" #Need to start a cmd with this. Otherwise, it won't work.
    #valid_users = ["ABCD#1234"] #<--- only allows users in this list to use commands
    #no-no_words = ["Sosa", "Pengu"] <--- Certain words not allowed in the server

#    for word in no-no_words:
#        if message.content.count(word)>0:
#            print("Whoa, don't say that.")
#            await message.channel.purge(limit = 1)

    if message.content == "1"
    #if str(message.channel) in channels and str(message.author) in valid_users: (only for it you want specific USERS to use commands in commands channel)
    if str(message.channel) in channels: # Check if its in correct channel
        if message.content.find(required_prefix + "hello") != -1:
            await message.channel.send("Hello! :wave: ") # if the user says !hello we will send back hi
        elif message.content == (required_prefix + "users"):
            await message.channel.send(f"""# of Members: {id.member_count}""") #we can use id.member_count

client.loop.create_task(update_stats())
client.run(token)
