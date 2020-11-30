# DeadbearBot
![Example Image](https://puu.sh/GlPqj/136b74f98e.gif)

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
The current to-do list can be found in Issues under the "Enhancement" tag. In addition to these, I'd also like to eventually add:
* A deployment system that allows the bot to be easily set up with no fuss (docker maybe?)
* A pre-hosted version of the bot that can simply be invited to a server, no self-hosting required

## How do I use it?
1. Create a bot application through the ![Discord Developer Portal](https://discord.com/developers/applications/)
2. Under the "Bot" tab, toggle on the "Presence" and "Server Members" intents
3. Invite your bot to your server with administrator privileges
4. Clone this repository, or download and extract the files manually
5. Install Python (v3.8.6 is recommended) and the requirements from requirements.txt
6. In a terminal, navigate to the directory where you saved the repo and run `python main.py`
7. When prompted, enter your bot's secret token (found in the "Bot" tab of the Developer Portal, under "Token")

## Command List ##
[-help] - Display information about available commands  

### Profile Commands
[-prof / -profile] - Display your profile information  
[-prof e / edit] - Bring up the profile management menu to change your profile display  
[-lb / -leaderboard] - Display the server leaderboard  

### Shop Commands
[-shop] - Bring up the shop  
[-daily / -cashme / -getmoney] - Get a free boost of credits, available once every 24 hours  

### Basic Config Commands (owner only)
[-prefix] - Change the [prefix] for bot commands (default: '-')  
[-stats] - Enable or disable XP tracking and level-ups for the server  
[-permrole / -permissionrole] - Set a [role_id] that's required to be able to use non-owner commands  

### Utility Commands (owner only)
[-say / -botsay] - Have the bot send some [text] in an embed  
[-say e / edit] - Edit a [message_id] with a different set of [text]  
[-tr / -togglerole] - Give or remove a [role_id] to yourself or a [member]  
[-roles] - Get a list of all roles on the guild  
[-channels] - Get a list of all channels on the guild  
[-emojis] - Get a list of all custom emojis on the guild  

### Star Board Commands (owner only)
[-star / -starboard] - Enable saving messages by setting a [channel_id] for them to go to  
[-star t / threshold] - Set [threshold] of emoji reacts before a message is starred  

### Shop Config Commands (owner only)
[-csymbol / -currencysymbol] - Set the [emoji] to use as the currency symbol  
[-shop a role / available role] - Set the number of custom roles available for purchase in the shop  
[-shop p role / price role] - Set the price of custom roles  
[-shop a emoji / available emoji] - Set the number of custom emoji slots available for purchase in the shop  
[-shop p emoji / price emoji] - Set the price of custom emoji slots  

### Join/Leave Commands (owner only)
[-gj / -guildjoin] - Set a [channel_id] for greeting messages to be sent when new people join  
[-gj msg / message] - Set the [text] to be sent when new people join  
[-gl / -guildleave] - Set a [channel_id] for greeting messages to be sent when new people join  
[-gl msg / message] - Set the [text] to be sent when new people join  
[-ar / -autorole] - Set a [role_id] to be added to any member that joins the server  

### Role Alert Commands (owner only)
[-ra / -rolealert] - Empty command, requires a subcommand.
[-ra g / gain] - Pass a [role_id], [channel_id], and a [message] to have that message sent to that channel when a user gains that role  
[-ra l / lose] - Pass a [role_id], [channel_id], and a [message] to have that message sent to that channel when a user loses that role  

### Reaction Role Commands (owner only)
[-rr / -reactionrole] - Set a [channel-message] to have a react [emoji] that when clicked gives a role by its [role_id]  
[-rr d / delete] - Deletes a reaction role by its [unique_id]  
[-rr l / list] - Lists all reaction roles and their id's  

### Voice Auto-role Commands (owner only)
[-vr / -voicerole] - Set a [voice channel_id] to have a [role_id] that gets automatically added/removed when that channel is joined or left  
[-vr d / delete] - Deletes a voice role by its [unique_id]  
[-vr l / list] - Lists all voice roles and their id's  

## Credits
This bot is made possible thanks to:  
- The ![discord.py project](https://github.com/Rapptz/discord.py)  
- The ![aiosqlite module](https://github.com/jreese/aiosqlite)  
- The ![python-dotenv module](https://github.com/theskumar/python-dotenv)  
- The ![PyYAML module](https://github.com/yaml/pyyaml)  
- Inspiration from the project [NadekoBot](https://nadeko.bot/)

If you like this project, consider donating to any of the projects listed above!  
If you'd like to contribute to this project directly, you can find me on [Patreon](https://www.patreon.com/DEADBEAR)  
