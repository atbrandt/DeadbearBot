# DeadbearBot
A [Discord](https://discordapp.com/) server management bot, inspired by [NadekoBot](https://nadekobot.me/) and written in Python (version 3.5.3+) using the [discord.py module](https://github.com/Rapptz/discord.py).

## How do I use it?
1. Clone the repo
2. Install requirements from requirements.txt
3. Run the main.py script in a terminal
4. Enter your bot's secret token

## What's it do?
Currently, DeadbearBot can:
* Say things in nicely formatted embeds, which can be edited later
* Track user profiles and allow users to customize with personal info
* Track user xp and levels as part of their profile
* "Star" messages in a channel, preserving them even if they are modified or deleted later
* Assign or unassign a role
* Automatically assign a role to users when joining your server
* Set a configurable greeting and/or leave message to be sent when users join or leave your server
* Automatically assign a role to a user when connecting to a voice channel
* Allow users to assign roles to themselves by clicking emoji reactions
* Set a configurable alert message to be sent when users gain or lose a role

## What's planned for the future?
The current todo list includes:
* Make the bot programmatically log certain events in a server to a specified channel
* Add mute/kick/ban functions to the bot
* A configurable permission system that allows enabling/disabling commands for users, roles, or channels
* A currency system that allows buying things in a configurable shop
* A raffling system that allows submitting steam keys to the bot to be raffled out to users or bought with currency
* Some kind of image manipulation system a-la the defunct NotSoBot?
* A deployment system that allows the bot to be easily set up with no fuss (docker maybe?)
* A hosted version of the bot that can simply be invited to a server, no host computer required
* Other fun things...

## Why are you rewriting bot functionality that already exists?
[Wikipedia: Reinventing the wheel](https://en.wikipedia.org/wiki/Reinventing_the_wheel)


## Command List ##
Profile Commands
[-prof / -profile] - Display your profile information
[-prof e / -profile edit] - Bring up the profile management menu to change your profile display
[-lb / -leaderboard] - Display the server leaderboard

Shop Commands
[-shop] - Bring up the shop
[-daily / -cashme / -getmoney] - Get a free boost of credits, available once every 24 hours

Config Commands (owner only)
[-prefix] - Change the [prefix] for bot commands (default: '-')
[-stats] - Enable or disable XP tracking and level-ups for the server.
[-say] - Have the bot send some [text] in an embed.
[-say e] - Edit a [message_id] with a different set of [text]

[-gj / -guildjoin] - Set a [channel_id] for greeting messages to be sent when new people join.
[-gj msg / -guildjoin message] - Set the [text] to be sent when new people join.
[-gl / -guildleave] - Set a [channel_id] for greeting messages to be sent when new people join.
[-gj msg / -guildleave message] - Set the [text] to be sent when new people join.

[-setcur / -setcurrency] - Set the [emoji] to use as the currency symbol
[-shop avail / -shop available] - Set an [item] to have a [number] available in shop
[-shop price] - Set [price] of [item] in the shop

[-star / -starboard] - Enable saving messages by setting a [channel_id] for them to go to.
[-star threshold / -starboard threshold] - Set [threshold] of emoji reacts before a message is starred.

[-trole / -togglerole] - Give or remove a [role_id] to yourself or a [member].
[-arole / -autorole] - Set a [role_id] to be added to any member that joins the server.
[-permrole / -permissionrole] - Set the [role_id] required to be able to use non-owner commands.

[-rr / -reactionrole] - Set a [channel-message] to have a react [emoji] that when clicked gives a role by its[role_id].
[-rr del] - Deletes a reaction role by its [unique_id]
[-rr list] - Lists all reaction roles and their id's

[-vr / -voicerole] - Set a [voice channel_id] to have a [role_id] that gets automatically added/removed when that channel is joined or left.
[-vr del] - Deletes a voice role by its [unique_id]
[-vr list] - Lists all voice roles and their id's


### If you like this project, consider tipping me on [Patreon](https://www.patreon.com/DEADBEAR)
