from typing import Union, Optional
import discord
from discord.ext import commands
from .utils import db
from .utils import checks


class Roles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    # Assign specific roles to specific users
    @commands.command(
        name='ToggleRole',
        description="Toggles a role for a member. Pass a role's `name` "
                    "or `id` and the member's `name` or `id` to add or "
                    "remove the role.",
        brief="Assign or remove member role by name or ID",
        aliases=['togglerole', 'trole', 'tr'])
    @commands.guild_only()
    @commands.is_owner()
    async def toggle_role(self, ctx, role: discord.Role, member: discord.Member):
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
    @commands.command(
        name='AutoRole',
        description="Sets a role that users get automatically when "
                    "joining the guild. Pass a role's `name` or `id` to "
                    "enable or disable the auto-role.",
        brief="Modify auto-role settings.",
        aliases=['autorole', 'arole', 'ar'])
    @commands.guild_only()
    @commands.is_owner()
    async def auto_role(self, ctx, role: discord.Role):
        autorole = await db.get_cfg(ctx.guild.id, 'auto_role')
        if autorole is None:
            await db.set_cfg(ctx.guild.id, 'auto_role', role.id)
            await ctx.channel.send(f"Added \"{role.name}\" to auto-role.")
        else:
            await db.set_cfg(ctx.guild.id, 'auto_role', None)
            await ctx.channel.send(f"Removed \"{role.name}\" from auto-role.")
    # ctx.channel.send("No role found! Check the name or ID entered.")


    # Command to set a reaction role
    @commands.group(
        name='ReactionRole',
        description="Create a reaction role using a channel-messsage id, "
                    "emoji, and role id. To get a channel-message ID, "
                    "open the 3-dot menu for a message and shift-click "
                    "the \"Copy ID\" button.",
        brief="Create a reaction role",
        aliases=['reactionrole', 'rr'],
        invoke_without_command=True)
    @commands.guild_only()
    @commands.is_owner()
    async def reaction_role(self, ctx, message: discord.Message, emoji: Union[discord.Emoji, str], role: discord.Role):
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
    @reaction_role.command(
        name='Delete',
        description="Removes a reaction role by its ID.",
        brief="Remove a reaction role",
        aliases=['delete', 'del', 'd'])
    @commands.guild_only()
    @commands.is_owner()
    async def rr_delete(self, ctx, rrID):
        exists = await db.del_react_role(rrID)
        if exists:
            await ctx.channel.send(f"Removed reaction role entry {rrID}.")
        else:
            await ctx.channel.send("No reaction role found for that ID!")


    # Command to list all reaction roles
    @reaction_role.command(
        name='List',
        description="Lists all reaction roles for this guild.",
        brief="List reaction roles",
        aliases=['list', 'l'])
    @commands.guild_only()
    @commands.is_owner()
    async def rr_list(self, ctx):
        roles = dict(await db.get_react_roles(ctx.guild.id))
        await ctx.channel.send(roles)


    # Command to add a voice chat role
    @commands.group(
        name='VoiceRole',
        description="Sets a role to be added to anyone that joins a "
                    "specified voice channel. Pass a voice channel "
                    "`name` or `id` and a role `name` or `id`.",
        brief="Add a voice role",
        aliases=['voicerole', 'vr'],
        invoke_without_command=True)
    @commands.guild_only()
    @commands.is_owner()
    async def voice_role(self, ctx, vchannel: discord.VoiceChannel, role: discord.Role):
        gID = ctx.guild.id
        exists, vrID = await db.add_voice_role(gID, vchannel.id, role.id)
        if not exists:
            await ctx.channel.send(f"Users joining \"{vchannel.name}\" will "
                                   f"automatically get the \"{role.name}\" "
                                   f"role.\nID = {vrID}")
        else:
            await ctx.channel.send(f"That already exists! ID = {vrID}")


    # Command to delete a voice chat role
    @voice_role.command(
        name='Delete',
        description="Removes a voice role by its ID.",
        brief="Remove a vc role",
        aliases=['delete', 'del', 'd'])
    @commands.guild_only()
    @commands.is_owner()
    async def vr_delete(self, ctx, vrID):
        exists = await db.del_voice_role(vrID)
        if exists:
            await ctx.channel.send(f"Removed reaction role entry {vrID}.")
        else:
            await ctx.channel.send("No reaction role found for that ID!")


    # Command to list all voice chat roles
    @voice_role.command(
        name='List',
        description="Lists all voice chat roles for this guild.",
        brief="List voice chat roles",
        aliases=['list', 'l'])
    @commands.guild_only()
    @commands.is_owner()
    async def vr_list(self, ctx):
        roles = dict(await db.get_voice_roles(ctx.guild.id))
        await ctx.channel.send(roles)


    # Group command to add a role alert
    @commands.group(
        name='RoleAlert',
        description="Sets an alert for a role",
        brief="Sets an alert for a role",
        aliases=['rolealert', 'ralert', 'ra'])
    @commands.guild_only()
    @commands.is_owner()
    async def role_alert(self, ctx):
        pass


    # Command to add a role alert when a role is gained
    @role_alert.command(
        name='Gain',
        aliases=['gain', 'g'])
    @commands.guild_only()
    @commands.is_owner()
    async def alert_gain(self, ctx, role: discord.Role, channel: discord.TextChannel, *, message: str):
        arID = await db.add_role_alert(ctx.guild.id,
                                       role.id,
                                       'gain_role',
                                       channel.id,
                                       message)
        await ctx.channel.send(f"When a user gains \"{role.name}\", an alert will "
                               f"be sent to \"{channel.name}\" with the message: "
                               f"{message}.\nID = {arID}")


    # Command to add a role alert when a role is lost
    @role_alert.command(
        name='Lose',
        aliases=['lose', 'l'])
    @commands.guild_only()
    @commands.is_owner()
    async def alert_lose(self, ctx, role: discord.Role, channel: discord.TextChannel, *, message: str):
        arID = await db.add_role_alert(ctx.guild.id,
                                       role.id,
                                       'lose_role',
                                       channel.id,
                                       message)
        await ctx.channel.send(f"When a user loses \"{role.name}\", an alert will "
                               f"be sent to \"{channel.name}\" with the message: "
                               f"{message}.\nID = {arID}")


    # Command to delete a role alert
    @role_alert.command(
        name='Delete',
        description="Removes a role alert by its ID.",
        brief="Remove a role alert",
        aliases=['delete', 'del', 'd'])
    @commands.guild_only()
    @commands.is_owner()
    async def delete_alert(self, ctx, uuID):
        exists = await db.del_role_alert(uuID)
        if exists:
            await ctx.channel.send(f"Removed reaction role entry {uuID}.")
        else:
            await ctx.channel.send("No reaction role found for that ID!")


    # Do stuff to members upon joining guild
    @commands.Cog.listener()
    async def on_member_join(self, member):
        autorole = await db.get_cfg(member.guild.id, 'auto_role')
        if autorole:
            role = member.guild.get_role(autorole)
            await member.add_roles(role, reason="AutoRole")
        joinalert = await db.get_cfg(member.guild.id, 'join_channel')
        if joinalert:
            message = await db.get_cfg(member.guild.id, 'join_message')
            channel = self.bot.get_channel(joinalert)
            await channel.send(message.format(member=member))


    # Do stuff to members upon leaving guild
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        leavealert = await db.get_cfg(member.guild.id, 'leave_channel')
        if leavealert is not None:
            message = await db.get_cfg(member.guild.id, 'leave_message')
            channel = self.bot.get_channel(leavealert)
            await channel.send(message.format(member=member))


    # Do stuff when members are updated
    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if before.roles == after.roles:
            return
        if len(before.roles) < len(after.roles):
            s = set(before.roles)
            roles = [i for i in after.roles if i not in s]
            alerts = []
            for role in roles:
                alert = await db.get_role_alert(role.id, 'gain_role')
                if alert:
                    alerts.append(alert)
        else:
            s = set(after.roles)
            roles = [i for i in before.roles if i not in s]
            alerts = []
            for role in roles:
                alert = await db.get_role_alert(role.id, 'lose_role')
                if alert:
                    alerts.append(alert)
        for alert in alerts:
            channel = after.guild.get_channel(alert['channel_id'])
            await channel.send(alert['message'].format(member=after))


    # Voice Role hook function
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        roles = await db.get_voice_roles(member.guild.id)
        if not roles:
            return
        if before.channel:
            for i in roles:
                if i['hook_id'] == before.channel.id:
                    role = member.guild.get_role(i['role_id'])
                    await member.remove_roles(role, reason="VoiceRoleDisconnect")
        if after.channel:
            for i in roles:
                if i['hook_id'] == after.channel.id:
                    role = member.guild.get_role(i['role_id'])
                    await member.add_roles(role, reason="VoiceRoleConnect")


    # Event hook for reactions being added to messages
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.user_id == self.bot.user.id:
            return
        elif payload.guild_id:
            await self.rr_check(payload, 'add')


    # Event hook for reactions being removed from messages
    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        if payload.user_id == self.bot.user.id:
            return
        elif payload.guild_id:
            await self.rr_check(payload, 'rem')


    # Handler for guild reaction events
    async def rr_check(self, payload, event):
        reactionroles = await db.get_react_roles(payload.guild_id)
        if reactionroles:
            hookID = f"{payload.channel_id}-{payload.message_id}"
            if payload.emoji.is_custom_emoji():
                emoji = payload.emoji.id
            else:
                emoji = payload.emoji.name
            for item in reactionroles:
                if hookID == item['hook_id'] and str(emoji) == item['emoji']:
                    guild = self.bot.get_guild(payload.guild_id)
                    member = guild.get_member(payload.user_id)
                    role = guild.get_role(item['role_id'])
                    if event == 'add':
                        await member.add_roles(role, reason="ReactionRole")
                    else:
                        await member.remove_roles(role, reason="ReactionRole")

