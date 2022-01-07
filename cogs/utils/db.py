import aiosqlite
from uuid import uuid4
from pathlib import Path


DBPATH = ""
for path in Path(__file__).parents[2].rglob('bot.db'):
    DBPATH = path
if not DBPATH:
    DBPATH = Path(__file__).parents[1] / 'bot.db'


# Function for creating a connection to db
async def db_connect():
    conn = await aiosqlite.connect(str(DBPATH))
    conn.row_factory = aiosqlite.Row
    return conn


# Adds a guild to the guilds table
async def add_guild(guildID):
    conn = await db_connect()
    c = await conn.cursor()
    sql = """
    INSERT OR IGNORE INTO guilds (
        id
    )
    VALUES
        (?);"""
    await c.execute(sql, (guildID,))
    await conn.commit()
    await conn.close()


# Returns all guilds that the bot has logged
async def get_all_guilds():
    conn = await db_connect()
    c = await conn.cursor()
    sql = """
    SELECT id
    FROM guilds;"""
    await c.execute(sql)
    fetched = await c.fetchall()
    await conn.close()
    guilds = []
    for item in fetched:
        guilds.append(item['id'])
    return guilds


# Returns a guild's config option from the guilds table
async def get_cfg(guildID, option=None):
    conn = await db_connect()
    c = await conn.cursor()
    sql = """
    SELECT *
    FROM guilds
    WHERE id = ?;"""
    await c.execute(sql, (guildID,))
    fetched = await c.fetchone()
    await conn.close()
    if option:
        return fetched[option]
    else:
        return dict(fetched)


# Sets a config option for a guild in the guilds table
async def set_cfg(guildID, option, value):
    conn = await db_connect()
    c = await conn.cursor()
    sql = """
    SELECT *
    FROM guilds;"""
    await c.execute(sql)
    row = await c.fetchone()
    names = row.keys()
    # To avoid the risk of injection attacks, this fstring is only performed
    # if the option passed in exactly matches an existing column name.
    for header in names:
        if option == header:
            sql = f"""
            UPDATE guilds
            SET {option} = ?
            WHERE id = ?;"""
            await c.execute(sql, (value, guildID,))
            await conn.commit()
            await conn.close()
            return
    await conn.close()
    raise Exception(f"No column found for {option}.")


# Resets a guild's config values to default
async def clear_cfg(guildID):
    conn = await db_connect()
    c = await conn.cursor()
    sql = """
    UPDATE guilds
    SET bot_alias = NULL,
        star_channel = NULL,
        auto_role = NULL,
        join_channel = NULL,
        join_message = NULL,
        leave_channel = NULL,
        leave_message = NULL,
        perm_role = NULL
    WHERE id = ?;"""
    await c.execute(sql, (guildID,))
    await conn.commit()
    await conn.close()


# Adds a member to the members table
async def add_member(guildID, memberID, created, joined):
    conn = await db_connect()
    c = await conn.cursor()
    sql = """
    INSERT OR IGNORE INTO members (
        guild_id,
        member_id,
        created_at,
        joined_at,
        lvl,
        xp,
        cash
    )
    VALUES
        (?, ?, ?, ?, ?, ?, ?);"""
    await c.execute(sql, (guildID, memberID, created, joined, 0, 0, 0,))
    await conn.commit()
    await conn.close()


# Removes a member from the members table
async def del_member(guildID, memberID):
    conn = await db_connect()
    c = await conn.cursor()
    sql = """
    DELETE FROM members
    WHERE guild_id = ?
    AND member_id = ?;"""
    await c.execute(sql, (guildID, memberID,))
    await conn.commit()
    await conn.close()


# Returns all members of a given guild
async def get_all_members(guildID):
    conn = await db_connect()
    c = await conn.cursor()
    sql = """
    SELECT *
    FROM members
    WHERE guild_id = ?;"""
    await c.execute(sql, (guildID,))
    fetched = await c.fetchall()
    await conn.close()
    return fetched


# Returns a specific member of a given guild
async def get_member(guildID, memberID):
    conn = await db_connect()
    c = await conn.cursor()
    sql = """
    SELECT *
    FROM members
    WHERE guild_id = ?
    AND member_id = ?;"""
    await c.execute(sql, (guildID, memberID,))
    fetched = await c.fetchone()
    await conn.close()
    return fetched


# Updates a specific member of a given guild
async def set_member(guildID, memberID, option, value):
    conn = await db_connect()
    c = await conn.cursor()
    sql = """
    SELECT *
    FROM members;"""
    await c.execute(sql)
    row = await c.fetchone()
    names = row.keys()
    # To avoid the risk of injection attacks, this fstring is only performed
    # if the option passed in exactly matches an existing column name.
    for header in names:
        if option == header:
            sql = f"""
            UPDATE members
            SET {option} = ?
            WHERE guild_id = ?
            AND member_id = ?;"""
            await c.execute(sql, (value, guildID, memberID,))
            await conn.commit()
            await conn.close()
            return
    await conn.close()
    raise Exception(f"No column found for {option}.")


# Returns members who have birthday on a given date
async def get_members_by_bday(date):
    conn = await db_connect()
    c = await conn.cursor()
    date_format = f"%{date.month}-{date.day}"
    sql = """
    SELECT *
    FROM members
    WHERE birthday LIKE ?
    GROUP BY member_id;"""
    await c.execute(sql, (date_format,))
    fetched = await c.fetchall()
    await conn.close()
    return fetched


# Adds currency to a members balance
async def add_currency(guild_id, member_id, amount):
    conn = await db_connect()
    c = await conn.cursor()
    sql = """
    UPDATE members
    SET cash = cash + ?
    WHERE guild_id = ?
    AND member_id = ?;"""
    await c.execute(sql, (amount, guild_id, member_id,))
    await conn.commit()
    await conn.close()


# Removes currency from a members balance
async def remove_currency(guild_id, member_id, amount):
    conn = await db_connect()
    c = await conn.cursor()
    sql = """
    UPDATE members
    SET cash = cash - ?
    WHERE guild_id = ?
    AND member_id = ?;"""
    await c.execute(sql, (amount, guild_id, member_id,))
    await conn.commit()
    await conn.close()


# Transfers currency from one member to another
async def transfer_currency(guild_id, author_id, member_id, amount):
    conn = await db_connect()
    c = await conn.cursor()
    sql = """
    UPDATE members
    SET cash = cash - ?
    WHERE guild_id = ?
    AND member_id = ?;"""
    await c.execute(sql, (amount, guild_id, author_id,))
    sql = """
    UPDATE members
    SET cash = cash + ?
    WHERE guild_id = ?
    AND member_id = ?;"""
    await c.execute(sql, (amount, guild_id, member_id,))
    await conn.commit()
    await conn.close()


# Returns all reaction roles of a given guild
async def get_react_roles(guildID):
    conn = await db_connect()
    c = await conn.cursor()
    sql = """
    SELECT uuid, hook_id, emoji, role_id
    FROM reaction_roles
    WHERE guild_id = ?;"""
    await c.execute(sql, (guildID,))
    fetched = await c.fetchall()
    await conn.close()
    converted = {}
    for row in fetched:
        converted.append(dict(row))
    return converted


# Adds a reaction role to database, excepting on exact duplicates
async def add_react_role(guildID, hookID, emoji, roleID):
    conn = await db_connect()
    c = await conn.cursor()
    sql = """
    SELECT uuid, hook_id, emoji, role_id
    FROM reaction_roles
    WHERE hook_id = ?
    AND emoji = ?
    AND role_id = ?;"""
    await c.execute(sql, (hookID, emoji, roleID,))
    exists = await c.fetchone()
    if not exists:
        UUID = str(uuid4())
        sql = """
        INSERT INTO reaction_roles (
            uuid,
            guild_id,
            hook_id,
            emoji,
            role_id
        )
        VALUES
            (?, ?, ?, ?, ?);"""
        await c.execute(sql, (UUID, guildID, hookID, emoji, roleID,))
        await conn.commit()
        await conn.close()
        return (False, UUID)
    else:
        await conn.close()
        return (True, exists['uuid'])


# Removes a reaction role from database by its unique ID, if it exists
async def del_react_role(UUID):
    conn = await db_connect()
    c = await conn.cursor()
    sql = """
    SELECT uuid
    FROM reaction_roles
    WHERE uuid = ?;"""
    await c.execute(sql, (UUID,))
    exists = await c.fetchone()
    if exists:
        sql = """
        DELETE FROM reaction_roles
        WHERE uuid = ?;"""
        await c.execute(sql, (UUID,))
        await conn.commit()
        await conn.close()
        return True
    else:
        await conn.close()
        return False


# Returns all voice roles for a given guild
async def get_voice_roles(guildID):
    conn = await db_connect()
    c = await conn.cursor()
    sql = """
    SELECT uuid, hook_id, role_id
    FROM voice_roles
    WHERE guild_id = ?;"""
    await c.execute(sql, (guildID,))
    fetched = await c.fetchall()
    await conn.close()
    return fetched


# Adds a voice role to database, excepting on exact duplicates
async def add_voice_role(guildID, hookID, roleID):
    conn = await db_connect()
    c = await conn.cursor()
    sql = """
    SELECT uuid, hook_id, role_id
    FROM voice_roles
    WHERE hook_id = ?
    AND role_id = ?;"""
    await c.execute(sql, (hookID, roleID,))
    exists = await c.fetchone()
    if not exists:
        UUID = str(uuid4())
        sql = """
        INSERT INTO voice_roles (
            uuid,
            guild_id,
            hook_id,
            role_id
        )
        VALUES
            (?, ?, ?, ?);"""
        await c.execute(sql, (UUID, guildID, hookID, roleID,))
        await conn.commit()
        await conn.close()
        return (False, UUID)
    else:
        await conn.close()
        return (True, exists['uuid'])


# Removes a voice role from database by its unique ID, if it exists
async def del_voice_role(UUID):
    conn = await db_connect()
    c = await conn.cursor()
    sql = """
    SELECT uuid
    FROM voice_roles
    WHERE uuid = ?;"""
    await c.execute(sql, (UUID,))
    check = await c.fetchone()
    if check:
        sql = """
        DELETE FROM voice_roles
        WHERE uuid = ?;"""
        await c.execute(sql, (UUID,))
        await conn.commit()
        await conn.close()
        return True
    else:
        await conn.close()
        return False


# Creates a starred message for a given guild
async def add_starred(guildID, originalID, starredID):
    conn = await db_connect()
    c = await conn.cursor()
    sql = """
    INSERT INTO starboard (
        guild_id,
        original_id,
        starred_id
    )
    VALUES
        (?,?,?);"""
    await c.execute(sql, (guildID, originalID, starredID,))
    await conn.commit()
    await conn.close()


# Returns a starred message of a given guild
async def get_starred(messageID):
    conn = await db_connect()
    c = await conn.cursor()
    sql = """
    SELECT *
    FROM starboard
    WHERE original_id = ?;"""
    await c.execute(sql, (messageID,))
    fetched = await c.fetchone()
    await conn.close()
    return fetched


# Deletes a starred message of a given guild
async def del_starred(messageID):
    conn = await db_connect()
    c = await conn.cursor()
    sql = """
    DELETE FROM starboard
    WHERE original_id = ?;"""
    await c.execute(sql, (messageID,))
    await conn.commit()
    await conn.close()


# Creates a role alert for a given guild
async def add_role_alert(guildID, roleID, event, channelID, message):
    conn = await db_connect()
    c = await conn.cursor()
    sql = """
    INSERT INTO role_alerts (
        uuid,
        guild_id,
        role_id,
        event,
        channel_id,
        message
    )
    VALUES
        (?, ?, ?, ?, ?, ?);"""
    UUID = str(uuid4())
    await c.execute(sql, (UUID, guildID, roleID, event, channelID, message,))
    await conn.commit()
    await conn.close()
    return UUID


# Returns a role alert for a given guild
async def get_role_alert(roleID, event):
    conn = await db_connect()
    c = await conn.cursor()
    sql = """
    SELECT *
    FROM role_alerts
    WHERE role_id = ?
    AND event = ?;"""
    await c.execute(sql, (roleID, event,))
    fetched = await c.fetchone()
    await conn.close()
    return fetched


# Deletes a role alert for a given guild
async def del_role_alert(UUID):
    conn = await db_connect()
    c = await conn.cursor()
    sql = """
    SELECT uuid
    FROM role_alerts
    WHERE uuid = ?;"""
    await c.execute(sql, (UUID,))
    check = await c.fetchone()
    if check:
        sql = """
        DELETE FROM role_alerts
        WHERE uuid = ?;"""
        await c.execute(sql, (UUID,))
        await conn.commit()
        await conn.close()
        return True
    else:
        await conn.close()
        return False


# Add custom role when purchased
async def add_custom_role(guildID, memberID, roleID):
    conn = await db_connect()
    c = await conn.cursor()
    sql = """
    INSERT INTO custom_roles (
        guild_id,
        member_id,
        role_id
    )
    VALUES
        (?, ?, ?);"""
    await c.execute(sql, (guildID, memberID, roleID,))
    await conn.commit()
    await conn.close()


# Get custom role
async def get_custom_role(guildID, memberID):
    conn = await db_connect()
    c = await conn.cursor()
    sql = """
    SELECT *
    FROM custom_roles
    WHERE guild_id = ?
    AND member_id = ?;"""
    await c.execute(sql, (guildID, memberID,))
    fetched = await c.fetchone()
    await conn.close()
    return fetched


# Delete custom role entry when the role itself is deleted
async def del_custom_role(guildID, roleID):
    conn = await db_connect()
    c = await conn.cursor()
    sql = """
    DELETE FROM custom_roles
    WHERE guild_id = ?
    AND role_id = ?;"""
    await c.execute(sql, (guildID, roleID,))
    await conn.commit()
    await conn.close()


# Set temp data in case the bot goes down mid-process
async def add_temp(guildID, memberID, menu, selected):
    conn = await db_connect()
    c = await conn.cursor()
    sql = """
    INSERT OR REPLACE INTO temp (
        guild_id,
        member_id,
        menu,
        selected
    )
    VALUES
        (?, ?, ?, ?);"""
    await c.execute(sql, (guildID, memberID, menu, selected,))
    await conn.commit()
    await conn.close()


# Updates temp data
async def update_temp(temp, value):
    conn = await db_connect()
    c = await conn.cursor()
    sql = """
    UPDATE temp
    SET storage = ?
    WHERE guild_id = ?
    AND member_id = ?;"""
    await c.execute(sql, (value, temp['guild_id'], temp['member_id'],))
    await conn.commit()
    await conn.close()


# Get temp data
async def get_temp(memberID):
    conn = await db_connect()
    c = await conn.cursor()
    sql = """
    SELECT *
    FROM temp
    WHERE member_id = ?;"""
    await c.execute(sql, (memberID,))
    fetched = await c.fetchone()
    await conn.close()
    return fetched


# Delete temp data when finished
async def del_temp(memberID):
    conn = await db_connect()
    c = await conn.cursor()
    sql = """
    DELETE FROM temp
    WHERE member_id = ?;"""
    await c.execute(sql, (memberID,))
    await conn.commit()
    await conn.close()
