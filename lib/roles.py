# Assign specific roles to specific users
@bot.command(name='ToggleRole',
             description="Toggles a role for a member. Pass a role's `name` "
                         "or `id` and the member's `name` or `id` to add or "
                         "remove the role.",
             brief="Assign or remove member role by name or ID",
             aliases=['trole'])
@commands.guild_only()
@commands.is_owner()
async def toggle_role(ctx, role: discord.Role, member: discord.Member):
    author = ctx.author.name
    if role not in member.roles:
        await member.add_roles(role, reason=f"ToggleRole by {author}")
        await ctx.channel.send(f"Gave {member.name} the \"{role.name}"
                               f"\" role.")
    else:
        await member.remove_roles(role, reason=f"ToggleRole by {author}")
        await ctx.channel.send(f"Removed the \"{role.name}\" role from "
                               f"{member.name}.")


# Manage a role to be assigned upon joining guild
@bot.command(name='AutoRole',
             description="Sets a role that users get automatically when "
                         "joining the guild. Pass a role's `name` or `id` to "
                         "enable or disable the auto-role.",
             brief="Modify auto-role settings.",
             aliases=['arole'])
@commands.guild_only()
@commands.is_owner()
async def auto_role(ctx, role: discord.Role):
    autorole = await db.get_cfg(ctx.guild.id, 'auto_role')
    if autorole is None:
        await db.set_cfg(ctx.guild.id, 'auto_role', role.id)
        await ctx.channel.send(f"Added \"{role.name}\" to auto-role.")
    else:
        await db.set_cfg(ctx.guild.id, 'auto_role', None)
        await ctx.channel.send(f"Removed \"{role.name}\" from auto-role.")
# ctx.channel.send("No role found! Check the name or ID entered.")


# Command to set a reaction role
@bot.command(name='ReactionRole',
             description="Create a reaction role using a channel-messsage id, "
                         "emoji, and role id. To get a channel-message ID, "
                         "open the 3-dot menu for a message and shift-click "
                         "the \"Copy ID\" button.",
             brief="Create a reaction role",
             aliases=['rr'])
@commands.guild_only()
@commands.is_owner()
async def add_rr(ctx,
                 message: discord.Message,
                 emoji: Union[discord.Emoji, str],
                 role: discord.Role):
    gID = ctx.guild.id
    hookID = str(message.channel.id) + "-" + str(message.id)
    if type(emoji) is str:
        exists, rrID = await db.add_react_role(gID, hookID, emoji, role.id)
    else:
        exists, rrID = await db.add_react_role(gID, hookID, emoji.id, role.id)
    if not exists:
        await message.add_reaction(emoji)
        await ctx.channel.send(f"Set \"{emoji}\" to give the \"{role.name}\" "
                               f"role.\nID = {rrID}")
    else:
        await ctx.channel.send(f"That already exists! ID = {rrID}")
# Note to self: Add warning for emoji that the bot doesn't have access to.


# Command to delete a reaction role
@bot.command(name='DeleteReactionRole',
             description="Removes a reaction role by its ID.",
             brief="Remove a reaction role",
             aliases=['delrr'])
@commands.guild_only()
@commands.is_owner()
async def delete_rr(ctx, rrID):
    exists = await db.del_react_role(rrID)
    if exists:
        await ctx.channel.send(f"Removed reaction role entry {rrID}.")
    else:
        await ctx.channel.send("No reaction role found for that ID!")


# Command to list all reaction roles
@bot.command(name='ListReactRoles',
             description="Lists all reaction roles for this guild.",
             brief="List reaction roles",
             aliases=['listrr'])
@commands.guild_only()
@commands.is_owner()
async def list_rr(ctx):
    roles = dict(await db.get_react_roles(ctx.guild.id))
    await ctx.channel.send(roles)


# Command to add a voice chat role
@bot.command(name='VoiceRole',
             description="Sets a role to be added to anyone that joins a "
                         "specified voice channel. Pass a voice channel "
                         "`name` or `id` and a role `name` or `id`.",
             brief="Add a voice role",
             aliases=['vr'])
@commands.guild_only()
@commands.is_owner()
async def add_vr(ctx, vchannel: discord.VoiceChannel, role: discord.Role):
    gID = ctx.guild.id
    exists, vrID = await db.add_voice_role(gID, vchannel.id, role.id)
    if not exists:
        await ctx.channel.send(f"Users joining \"{vchannel.name}\" will "
                               f"automatically get the \"{role.name}\" "
                               f"role.\nID = {vrID}")
    else:
        await ctx.channel.send(f"That already exists! ID = {vrID}")


# Command to delete a voice chat role
@bot.command(name='DeleteVoiceRole',
             description="Removes a voice role by its ID.",
             brief="Remove a vc role",
             aliases=['delvr'])
@commands.guild_only()
@commands.is_owner()
async def delete_vr(ctx, vrID):
    exists = await db.del_voice_role(vrID)
    if exists:
        await ctx.channel.send(f"Removed reaction role entry {vrID}.")
    else:
        await ctx.channel.send("No reaction role found for that ID!")


# Command to list all voice chat roles
@bot.command(name='ListVoiceRoles',
             description="Lists all voice chat roles for this guild.",
             brief="List voice chat roles",
             aliases=['listvr'])
@commands.guild_only()
@commands.is_owner()
async def list_vr(ctx):
    roles = dict(await db.get_voice_roles(ctx.guild.id))
    await ctx.channel.send(roles)


# Group command to add a role alert
@bot.group(name='RoleAlert',
           description="Sets an alert for a role",
           brief="Sets an alert for a role",
           aliases=['alert'])
@commands.guild_only()
@commands.is_owner()
async def role_alert(ctx):
    pass


# Command to add a role alert when a role is gained
@role_alert.command(name='Gain',
                    aliases=['gain'])
@commands.guild_only()
@commands.is_owner()
async def alert_gain(ctx,
                     role: discord.Role,
                     channel: discord.TextChannel,
                     *, message: str):
    gID = ctx.guild.id
    arID = await db.add_role_alert(ctx.guild.id,
                                   role.id,
                                   'gain_role',
                                   channel.id,
                                   message)
    await ctx.channel.send(f"When a user gains \"{role.name}\", an alert will "
                           f"be sent to \"{channel.name}\" with the message: "
                           f"{message}.\nID = {arID}")


# Command to add a role alert when a role is lost
@role_alert.command(name='Lose',
                    aliases=['lose'])
@commands.guild_only()
@commands.is_owner()
async def alert_lose(ctx,
                     role: discord.Role,
                     channel: discord.TextChannel,
                     *, message: str):
    arID = await db.add_role_alert(ctx.guild.id,
                                   role.id,
                                   'lose_role',
                                   channel.id,
                                   message)
    await ctx.channel.send(f"When a user loses \"{role.name}\", an alert will "
                           f"be sent to \"{channel.name}\" with the message: "
                           f"{message}.\nID = {arID}")


# Command to delete a role alert
@role_alert.command(name='Delete',
                    description="Removes a role alert by its ID.",
                    brief="Remove a role alert",
                    aliases=['del'])
@commands.guild_only()
@commands.is_owner()
async def delete_alert(ctx, uuID):
    exists = await db.del_role_alert(uuID)
    if exists:
        await ctx.channel.send(f"Removed reaction role entry {uuID}.")
    else:
        await ctx.channel.send("No reaction role found for that ID!")


