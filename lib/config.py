# Set an alias for the bot prefix
@bot.command(name='PrefixAlias',
             description="Sets an alias for the default command prefix.",
             brief="Set command prefix alias.",
             aliases=['prefix'])
@commands.guild_only()
@commands.is_owner()
async def change_prefix(ctx, prefix):
    await db.set_cfg(ctx.guild.id, 'bot_alias', prefix)
    await ctx.channel.send(f"My command prefix is now \"{prefix}\".")


# Set perm roles for public commands
@bot.command(name='PermissionRoles',
             description="Sets roles that can use basic commands.",
             brief="Set permrole.",
             aliases=['permrole'])
@commands.guild_only()
@commands.is_owner()
async def set_perms(ctx, role: discord.Role):
    await db.set_cfg(ctx.guild.id, 'perm_role', role.id)
    await ctx.channel.send(f"Added \"{role.name}\" to perm roles.")


# Set the channel for join messages
@bot.group(name='GuildJoin',
           description="Enables or disables the automatic join message in a "
                       "specified channel. Pass no channel to disable.",
           brief="Turn join messages on or off.",
           aliases=['gj'],
           invoke_without_command=True)
@commands.guild_only()
@commands.is_owner()
async def gjoin(ctx, channel: discord.TextChannel=None):
    if channel:
        await db.set_cfg(ctx.guild.id, 'join_channel', channel.id)
        await ctx.channel.send(f"Greeting enabled for \"{channel.name}\".")
    else:
        await db.set_cfg(ctx.guild.id, 'join_channel', None)
        await ctx.channel.send("Greeting disabled.")


# Set the join message
@gjoin.command(name='JoinMessage',
               description="Sets the automatic greeting message.",
               brief="Modify join message.",
               aliases=['msg'])
@commands.guild_only()
@commands.is_owner()
async def gjoin_message(ctx, *, message: str):
    await db.set_cfg(ctx.guild.id, 'join_message', message)
    await ctx.channel.send(f"The join message is now: \"{message}\"")


# Set the channel for leave messages
@bot.group(name='GuildLeave',
           description="Enables or disables the automatic leave message in a "
                       "specified channel. Pass no channel to disable.",
           brief="Turn leave message on or off.",
           aliases=['gl'],
           invoke_without_command=True)
@commands.guild_only()
@commands.is_owner()
async def gleave(ctx, channel: discord.TextChannel=None):
    if channel:
        await db.set_cfg(ctx.guild.id, 'leave_channel', channel.id)
        await ctx.channel.send(f"Farewells enabled for \"{channel.name}\".")
    else:
        await db.set_cfg(ctx.guild.id, 'leave_channel', None)
        await ctx.channel.send("Farewells disabled.")


# Set the leave message
@gleave.command(name='LeaveMessage',
                description="Sets the automatic leave message.",
                brief="Modify leave message.",
                aliases=['msg'])
@commands.guild_only()
@commands.is_owner()
async def gleave_message(ctx, *, message: str):
    await db.set_cfg(ctx.guild.id, 'leave_message', message)
    await ctx.channel.send(f"The farewell message is now: \"{message}\"")


