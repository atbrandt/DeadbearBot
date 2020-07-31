# Daily cash award
@bot.command(name='DailyCredits',
             aliases=['daily', 'credits', 'cashme', 'dailycredits', 'getmoney'])
@commands.guild_only()
@check_perms()
async def daily_cash(ctx):
    gID = ctx.guild.id
    member = ctx.author
    now = ctx.message.created_at
    dbprof = await db.get_member(gID, member.id)
    timeformat = '%Y-%m-%d %H:%M:%S.%f'
    if dbprof['daily_timestamp']:
        lastdaily = datetime.strptime(dbprof['daily_timestamp'], timeformat)
        timesince = now - lastdaily
        delta = timedelta(hours=24)
    else:
        timesince = 2
        delta = 1
    if timesince < delta:
        timeleft = delta - timesince
        hours = timeleft.seconds//3600
        minutes = (timeleft.seconds//60)%60
        seconds = math.ceil(timeleft.seconds)
        if hours:
            await ctx.channel.send(
                f"I already gave you money, {member.mention}! If you want "
                f"more, you'll have to wait {hours} hour(s) and {minutes} "
                f"minute(s).")
        elif seconds > 60:
            await ctx.channel.send(
                f"I already gave you money, {member.mention}! If you want "
                f"more, you'll have to wait {minutes} minute(s) and "
                f"{seconds} second(s).")
        else:
            await ctx.channel.send(
                f"I already gave you money, {member.mention}! If you want "
                f"more, you'll have to wait {seconds} second(s).")
    else:
        newcash = dbprof['cash'] + 500
        await db.set_member(gID, member.id, 'cash', newcash)
        await db.set_member(gID, member.id, 'daily_timestamp', now)
        await ctx.channel.send(
            f"Here's a 500 credit freebie, {member.mention}!")


# Shop menu function
@bot.command(name='GuildShop',
             aliases=['shop'])
@commands.guild_only()
@check_perms()
async def shop(ctx):
    temp = await db.get_temp(ctx.author.id)
    if temp:
        await db.del_temp(ctx.author.id)
    title = f"**{ctx.guild.name} Shop**"
    desc = "*Buy somethin, will ya!*"
    cost = {'role': 10000,
            'emoji': 10000,
            'ticket': 1000}
    fields = [{'fname': "Custom Role",
                'fdesc': f"Buy a custom role! You'll be able to pick both "
                         f"the name and the color of the role after purchase."
                         f"\n\nCost: \U0001F48E {cost['role']}",
                'inline': True,
                'prompt': "You've purchased a custom role! Please enter a "
                          "name for your new role.",
                'limit': 40,
                'price': cost['role'],
                'data': 'role'},
               {'fname': "Custom Emoji",
                'fdesc': f"Buy a custom emoji! You'll be able to pick both "
                         f"the image and name for the emoji after purchase."
                         f"\n\nCost: \U0001F48E {cost['emoji']}",
                'inline': True,
                'prompt': "You've purchased a custom emoji! Please upload the "
                          "image for your new emoji.",
                'limit': "256kb (File must be `jpg`, `png`, or `gif`)",
                'price': cost['emoji'],
                'data': 'emoji'}]
#               {'fname': "Raffle Ticket",
#                'fdesc': f"Buy a ticket for a raffle!\n\nCost: \U0001F48E "
#                         f"{cost['ticket']}",
#                'inline': True,
#                'price': cost['ticket'],
#                'data': 'ticket'}
    Shop = Menu(title, desc, fields, 5, True)
    page = 0
    message = await ctx.channel.send(embed=Shop.embeds[page])
    message = await Shop.add_buttons(message, page)
    await menu_seek(message, ctx.author, Shop, page, 55.0)


# Command to return a user's profile
@bot.group(name='Profile',
           description="Display your profile information.",
           brief="Get your profile.",
           aliases=['prof', 'profile'],
           invoke_without_command=True)
@commands.guild_only()
@check_perms()
async def profile(ctx, member: discord.Member=None):
    if member:
        dbprof = await db.get_member(ctx.guild.id, member.id)
    else:
        dbprof = await db.get_member(ctx.guild.id, ctx.author.id)
        member = ctx.author
    if dbprof['birthday']:
        born = datetime.strptime(dbprof['birthday'], '%Y-%m-%d')
        now = date.today()
        age = now.year-born.year-((now.month, now.day)<(born.month, born.day))
    else:
        age = None
    fields = [{'fname': "Total XP",
               'fdesc': f"\U0001F4D6 {dbprof['xp']}",
               'inline': False},
              {'fname': "Total Credits",
               'fdesc': f"\U0001F48E {dbprof['cash']}",
               'inline': False},
              {'fname': "Name",
               'fdesc': dbprof['name'],
               'inline': True},
              {'fname': "Nickname",
               'fdesc': dbprof['nickname'],
               'inline': True},
              {'fname': "Age",
               'fdesc': age,
               'inline': True},
              {'fname': "Gender",
               'fdesc': dbprof['gender'],
               'inline': True},
              {'fname': "Location",
               'fdesc': dbprof['location'],
               'inline': True},
              {'fname': "Description",
               'fdesc': dbprof['description'],
               'inline': False},
              {'fname': "Likes",
               'fdesc': dbprof['likes'],
               'inline': True},
              {'fname': "Dislikes",
               'fdesc': dbprof['dislikes'],
               'inline': True}]
    title = f"Level: **{dbprof['lvl']}**"
    desc = f"Member of *{ctx.guild.name}*"
    avatar = member.avatar_url_as(format='png')
    Profile = Menu(title, desc, fields, 0, False, member.name, avatar)
    page = 0
    message = await ctx.channel.send(embed=Profile.embeds[page])
    message = await Profile.add_buttons(message, page)
    await menu_seek(message, ctx.author, Profile, page, 55.0)


# Command to fill out profile info via DM
@profile.command(name='Edit',
                 description="Edit your member profile information.",
                 brief="Edit profile information.",
                 aliases=['e', 'edit'])
@commands.guild_only()
@check_perms()
async def profile_edit(ctx):
    temp = await db.get_temp(ctx.author.id)
    if temp:
        await db.del_temp(ctx.author.id)
    page = 0
    message = await ctx.channel.send(embed=ProfileEdit.embeds[page])
    message = await ProfileEdit.add_buttons(message, page)
    await menu_seek(message, ctx.author, ProfileEdit, page, 55.0)


# Command to display current guild leaderboard
@bot.command(name='Leaderboard',
             description="Display the guild leaderboard",
             aliases=['lb'])
@commands.guild_only()
@check_perms()
async def leaderboard(ctx):
    def sort(e):
        return e['xp']

    members = await db.get_all_members(ctx.guild.id)
    members.sort(key=sort)
    for i in members:
        member = ctx.guild.get_member(i['member_id'])
        print(member.name)
    title = f"**Leaderboard for {ctx.guild.name}**"
    desc = f"Member of *{ctx.guild.name}*"
    Leaderboard = Menu(title, desc, fields, 0, False, member.name, avatar)
    page = 0
    message = await ctx.channel.send(embed=Leaderboard.embeds[page])
    message = await Leaderboard.add_buttons(message, page)
    await menu_seek(message, ctx.author, Leaderboard, page, 55.0)


