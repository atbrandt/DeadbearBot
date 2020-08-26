# DeadbearBot
A [Discord](https://discordapp.com/) server management bot, inspired by [NadekoBot](https://nadekobot.me/) and written in Python (version 3.5.3+) using the [discord.py module](https://github.com/Rapptz/discord.py).

## How do I use it?
1. Clone the repo
2. Install requirements from requirements.txt
3. Run the main.py script in a terminal
4. Enter your bot's secret token

## What's it do?
Currently, DeadbearBot can:
* Track and display configurable user profiles!
* Award XP, levels, and currency to users automatically!
* Allow users to buy custom roles and submit custom emojis through a configurable shop!
* Preserve popular messages (i.e. ones with lots of reactions) to a "Star Board"!
* Assign or unassign roles, either manually or automatically!
* Set custom greeting and/or leave messages!
* Automatically change a user's roles when connecting to voice channels!
* Allow users to give themselves roles by clicking emoji reactions!
* Set custom messages to be sent when users gain or lose a role!
* Take a message and put it in an nicely-formatted embed!

## What's planned for the future?
The current todo list includes:
* Allow users to create their own custom messages to be repeated by the bot on command
* Add birthday alerts for users that want the bot to wish them a happy birthday
* Add configurable logging functionality
* Add mute/kick/ban functions to the bot
* A configurable permission system that allows enabling/disabling commands for users, roles, or channels
* More configuration options for the shop, like a raffling system that allows buying tickets to receive user-submitted rewards
* A deployment system that allows the bot to be easily set up with no fuss (docker maybe?)
* A pre-hosted version of the bot that can simply be invited to a server, no self-hosting required
* Some kind of image manipulation system a-la the defunct NotSoBot?
* Other fun things...

## Command List ##
[-help] - Display information about available commands  

#Profile Commands (requires permrole)  
[-prof / -profile] - Display your profile information  
[-prof e / -profile edit] - Bring up the profile management menu to change your profile display  
[-lb / -leaderboard] - Display the server leaderboard  

#Shop Commands (requires permrole)  
[-shop] - Bring up the shop  
[-daily / -cashme / -getmoney] - Get a free boost of credits, available once every 24 hours  

#Basic Config Commands (owner only)  
[-prefix] - Change the [prefix] for bot commands (default: '-')  
[-stats] - Enable or disable XP tracking and level-ups for the server  
[-permrole / -permissionrole] - Set the [role_id] required to be able to use non-owner commands  

#Utility Commands (owner only)  
[-say] - Have the bot send some [text] in an embed  
[-say e] - Edit a [message_id] with a different set of [text]  
[-trole / -togglerole] - Give or remove a [role_id] to yourself or a [member]  
[-roles] - Get a list of all roles on the guild  
[-channels] - Get a list of all channels on the guild  
[-emojis] - Get a list of all custom emojis on the guild  

#Star Board Commands (owner only)  
[-star / -starboard] - Enable saving messages by setting a [channel_id] for them to go to  
[-star threshold / -starboard threshold] - Set [threshold] of emoji reacts before a message is starred  

#Shop Config Commands (owner only)  
[-setcur / -setcurrency] - Set the [emoji] to use as the currency symbol  
[-shop avail / -shop available] - Set an [item] to have a [number] available in shop  
[-shop price] - Set [price] of [item] in the shop  

#Join/Leave Commands (owner only)  
[-gj / -guildjoin] - Set a [channel_id] for greeting messages to be sent when new people join  
[-gj msg / -guildjoin message] - Set the [text] to be sent when new people join  
[-gl / -guildleave] - Set a [channel_id] for greeting messages to be sent when new people join  
[-gl msg / -guildleave message] - Set the [text] to be sent when new people join  
[-arole / -autorole] - Set a [role_id] to be added to any member that joins the server  

#Role Alert Commands (owner only)  
[-alert gain] - Pass a [role_id], [channel_id], and a [message] to have that message sent to that channel when a user gains that role  
[-alert lose] - Pass a [role_id], [channel_id], and a [message] to have that message sent to that channel when a user loses that role  

#Reaction Role Commands (owner only)  
[-rr / -reactionrole] - Set a [channel-message] to have a react [emoji] that when clicked gives a role by its [role_id]  
[-rr del] - Deletes a reaction role by its [unique_id]  
[-rr list] - Lists all reaction roles and their id's  

#Voice Auto-role Commands (owner only)  
[-vr / -voicerole] - Set a [voice channel_id] to have a [role_id] that gets automatically added/removed when that channel is joined or left  
[-vr del] - Deletes a voice role by its [unique_id]  
[-vr list] - Lists all voice roles and their id's  


## Why are you rewriting bot functionality that already exists?
[Wikipedia: Reinventing the wheel](https://en.wikipedia.org/wiki/Reinventing_the_wheel)


### If you like this project, consider tipping me on [Patreon](https://www.patreon.com/DEADBEAR)
