import sqlite3
from uuid import uuid4
from pathlib import Path


# Set platform-independent path to db file
DATABASE = str(Path(__file__).parent / "bot.db")


# Create a database connection
conn = sqlite3.connect(DATABASE)
# Set the database to return dictionaries instead of tuples
conn.row_factory = sqlite3.Row


# Initialize database and create default tables
def setup_database():
    c = conn.cursor()

    # Set database to use Write Ahead Log for concurrency
    c.execute("PRAGMA journal_mode=WAL")

    c.execute("""
    CREATE TABLE IF NOT EXISTS guilds (
        id INTEGER PRIMARY KEY UNIQUE,
        bot_alias TEXT,
        auto_role INTEGER,
        greet_channel INTEGER,
        greet_message TEXT,
        bye_channel INTEGER,
        bye_message TEXT
    );""")

    c.execute("""
    CREATE TABLE IF NOT EXISTS members (
        id INTEGER PRIMARY KEY,
        guild_id INTEGER,
        member_id INTEGER,
        created_at INTEGER,
        joined_at INTEGER,
        level INTEGER,
        xp INTEGER,
        cash INTEGER,
        FOREIGN KEY (guild_id) REFERENCES guilds (id)
    );""")

    c.execute("""
    CREATE TABLE IF NOT EXISTS reaction_roles (
        uuid TEXT PRIMARY KEY UNIQUE,
        guild_id INTEGER,
        hook_id TEXT,
        emoji TEXT,
        role_id INTEGER,
        FOREIGN KEY (guild_id) REFERENCES guilds (id)
    );""")

    c.execute("""
    CREATE TABLE IF NOT EXISTS voice_roles (
        uuid TEXT PRIMARY KEY UNIQUE,
        guild_id INTEGER,
        hook_id INTEGER,
        role_id INTEGER,
        FOREIGN KEY (guild_id) REFERENCES guilds (id)
    );""")

    c.execute("""
    CREATE TABLE IF NOT EXISTS blurbs (
        uuid TEXT PRIMARY KEY UNIQUE,
        command TEXT UNIQUE,
        message TEXT,
        FOREIGN KEY (guild_id) REFERENCES guilds (id)
    );""")

    conn.commit()


# Adds a guild to the guilds table
def add_guild(guildID):
    c = conn.cursor()
    c.execute("""
    INSERT OR IGNORE INTO guilds (
        id
    )
    VALUES
        (?);""", (guildID,))
    conn.commit()


# Returns a guild's config option from the guilds table
def get_cfg(guildID, option):
    c = conn.cursor()
    c.execute("""
    SELECT *
    FROM guilds
    WHERE id = ?;""", (guildID,))
    return c.fetchone()[option]
    

# Sets a config option for a guild in the guilds table
def set_cfg(guildID, option, value):
    c = conn.cursor()
    c.execute(f"""
    UPDATE guilds
    SET {option} = ?
    WHERE id = ?;""", (value,guildID,))
    conn.commit()


# Resets a guild's config values to default
def clear_cfg(guildID):
    c = conn.cursor()
    c.execute("""
    UPDATE guilds
    SET bot_alias = NULL,
        auto_role = NULL,
        greet_channel = NULL,
        greet_message = NULL,
        bye_channel = NULL,
        bye_message = NULL
    WHERE id = ?;""", (guildID,))
    conn.commit()


# Adds a member to the members table
def add_member(guildID, memberID, created, joined):
    c = conn.cursor()
    c.execute("""
    INSERT OR IGNORE INTO members (
        guild_id,
        member_id,
        created_at,
        joined_at,
        level,
        xp,
        cash
    )
    VALUES
        (?, ?, ?, ?, ?, ?, ?);""", (guildID,memberID,created,joined,0,0,0,))
    conn.commit()


# Returns all members of a given guild
def get_all_members(guildID):
    c = conn.cursor()
    c.execute("""
    SELECT member_id
    FROM members
    WHERE guild_id = ?;""", (guildID,))
    return c.fetchall()


# Returns a specific member of a given guild
def get_member(guildID, memberID):
    c = conn.cursor()
    c.execute("""
    SELECT level, xp, cash
    FROM members
    WHERE guild_id = ?
    AND member_id = ?;""", (guildID,memberID,))
    return c.fetchone()


# Updates a specific member of a given guild
def set_member(guildID, memberID, level, xp, cash):
    c = conn.cursor()
    c.execute("""
    UPDATE members
    SET level = ?,
        xp = ?,
        cash = ?
    WHERE guild_id = ?
    AND member_id = ?;""", (level,xp,cash,guildID,memberID,))
    conn.commit()


# Returns all reaction roles of a given guild
def get_reaction_roles(guildID):
    c = conn.cursor()
    c.execute("""
    SELECT uuid, hook_id, emoji, role_id
    FROM reaction_roles
    WHERE guild_id = ?;""", (guildID,))
    return c.fetchall()


# Adds a reaction role to database, excepting on exact duplicates
def add_reaction_role(guildID, hookID, emoji, roleID):
    c = conn.cursor()
    c.execute("""
    SELECT uuid, hook_id, emoji, role_id
    FROM reaction_roles
    WHERE hook_id = ?
    AND emoji = ?
    AND role_id = ?;""", (hookID,emoji,roleID,))
    check = c.fetchone()
    if not check:
        uniqueID = str(uuid4())
        c.execute("""
        INSERT INTO reaction_roles (
            uuid,
            guild_id,
            hook_id,
            emoji,
            role_id
        )
        VALUES
            (?, ?, ?, ?, ?);""", (uniqueID,guildID,hookID,emoji,roleID,))
        conn.commit()
        return (False, uniqueID)
    else:
        return (True, check['uuid'])


# Removes a reaction role from database by its unique ID, if it exists
def delete_reaction_role(rrID):
    c = conn.cursor()
    c.execute("""
    SELECT uuid
    FROM reaction_roles
    WHERE uuid = ?;""", (rrID,))
    check = c.fetchone()
    if check:
        c.execute("""
        DELETE FROM reaction_roles
        WHERE uuid = ?;""", (rrID,))
        conn.commit()
        return True
    else:
        return False


# Returns all voice roles for a given guild
def get_voice_roles(guildID):
    c = conn.cursor()
    c.execute("""
    SELECT uuid, hook_id, role_id
    FROM voice_roles
    WHERE guild_id = ?;""", (guildID,))
    return c.fetchall()


# Adds a voice role to database, excepting on exact duplicates
def add_voice_role(guildID, hookID, roleID):
    c = conn.cursor()
    c.execute("""
    SELECT uuid, hook_id, role_id
    FROM voice_roles
    WHERE hook_id = ?
    AND role_id = ?;""", (hookID,roleID,))
    check = c.fetchone()
    if not check:
        uniqueID = str(uuid4())
        c.execute("""
        INSERT INTO voice_roles (
            uuid,
            guild_id,
            hook_id,
            role_id
        )
        VALUES
            (?, ?, ?, ?);""", (uniqueID,guildID,hookID,roleID,))
        conn.commit()
        return (False, uniqueID)
    else:
        return (True, check['uuid'])


# Removes a voice role from database by its unique ID, if it exists
def delete_voice_role(vrID):
    c = conn.cursor()
    c.execute("""
    SELECT uuid
    FROM voice_roles
    WHERE uuid = ?;""", (rrID,))
    check = c.fetchone()
    if check:
        c.execute("""
        DELETE FROM voice_roles
        WHERE uuid = ?;""", (rrID,))
        conn.commit()
        return True
    else:
        return False
