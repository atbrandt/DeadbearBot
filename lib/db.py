import sqlite3
from uuid import uuid4
from pathlib import Path


# Set platform-independent path to db file
DBPATH = Path(__file__).parent / "bot.db"

# Set platform-independent path to migrations folder
MIGPATH = Path(__file__).parent / "migration"

# Create DB connection
conn = sqlite3.connect(str(DBPATH))

# Set the DB to return row objects for name-based access to values
conn.row_factory = sqlite3.Row


# Initialize DB and create default tables
def setup_db():
    c = conn.cursor()

    # Get the current DB version
    dbver = c.execute("PRAGMA user_version").fetchone()[0]

    if dbver == 0:
        # Set DB to use Write Ahead Log for concurrency
        c.execute("PRAGMA journal_mode=WAL;")

    # Get list of migrations available
    migrations = []
    for child in sorted(MIGPATH.iterdir()):
        if child.suffix == ".sql":
            migrations.append(child)

    # Check if db matches latest version available, then update if not
    latest = sorted(migrations, reverse = True)
    latestver = int(latest[0].stem)
    if dbver < latestver:
        print("Database is out of date! Migrating...\n")
        for item in migrations:
            print(f"Checking DB migration file {item.stem}")
            scriptver = int(item.stem)
            if scriptver > dbver:
                print(f"Migrating DB to version {scriptver}")
                sqlfile = open(item, 'r').read()
                try:
                    c.executescript(sqlfile)
                except Exception as e:
                    print(e)
                else:
                    c.execute(f"PRAGMA user_version={scriptver};")
                    print(f"Done! DB at version {scriptver}\n")
            else:
                print(f"Migration {item.stem} already applied, skipping...\n")


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
    if option == "bot_alias":
        c = conn.cursor()
        c.execute("""
        UPDATE guilds
        SET bot_alias = ?
        WHERE id = ?;""", (value,guildID,))
        conn.commit()

    if option == "guild_stats":
        c = conn.cursor()
        c.execute("""
        UPDATE guilds
        SET guild_stats = ?
        WHERE id = ?;""", (value,guildID,))
        conn.commit()

    if option == "star_channel":
        c = conn.cursor()
        c.execute("""
        UPDATE guilds
        SET star_channel = ?
        WHERE id = ?;""", (value,guildID,))
        conn.commit()

    if option == "star_threshold":
        c = conn.cursor()
        c.execute("""
        UPDATE guilds
        SET star_threshold = ?
        WHERE id = ?;""", (value,guildID,))
        conn.commit()

    if option == "auto_role":
        c = conn.cursor()
        c.execute("""
        UPDATE guilds
        SET auto_role = ?
        WHERE id = ?;""", (value,guildID,))
        conn.commit()

    if option == "join_channel":
        c = conn.cursor()
        c.execute("""
        UPDATE guilds
        SET join_channel = ?
        WHERE id = ?;""", (value,guildID,))
        conn.commit()

    if option == "join_message":
        c = conn.cursor()
        c.execute("""
        UPDATE guilds
        SET join_message = ?
        WHERE id = ?;""", (value,guildID,))
        conn.commit()

    if option == "leave_channel":
        c = conn.cursor()
        c.execute("""
        UPDATE guilds
        SET leave_channel = ?
        WHERE id = ?;""", (value,guildID,))
        conn.commit()

    if option == "leave_message":
        c = conn.cursor()
        c.execute("""
        UPDATE guilds
        SET leave_message = ?
        WHERE id = ?;""", (value,guildID,))
        conn.commit()

    if option == "perm_role":
        c = conn.cursor()
        c.execute("""
        UPDATE guilds
        SET bperm_role = ?
        WHERE id = ?;""", (value,guildID,))
        conn.commit()


# Resets a guild's config values to default
def clear_cfg(guildID):
    c = conn.cursor()
    c.execute("""
    UPDATE guilds
    SET bot_alias = NULL,
        star_channel = NULL,
        auto_role = NULL,
        join_channel = NULL,
        join_message = NULL,
        leave_channel = NULL,
        leave_message = NULL,
        perm_role = NULL
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
        lvl,
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
def get_mem_prof(guildID, memberID):
    c = conn.cursor()
    c.execute("""
    SELECT *
    FROM members
    WHERE guild_id = ?
    AND member_id = ?;""", (guildID,memberID,))
    return c.fetchone()


# Updates a specific member of a given guild
def set_mem_prof(guildID, memberID, option, value):
    if option == "lvl":    
        c = conn.cursor()
        c.execute("""
        UPDATE members
        SET lvl = ?
        WHERE guild_id = ?
        AND member_id = ?;""", (value,guildID,memberID,))
        conn.commit()

    if option == "xp":
        c = conn.cursor()
        c.execute("""
        UPDATE members
        SET xp = ?
        WHERE guild_id = ?
        AND member_id = ?;""", (value,guildID,memberID,))
        conn.commit()

    if option == "name":
        c = conn.cursor()
        c.execute("""
        UPDATE members
        SET name = ?
        WHERE guild_id = ?
        AND member_id = ?;""", (value,guildID,memberID,))
        conn.commit()

    if option == "nickname":
        c = conn.cursor()
        c.execute("""
        UPDATE members
        SET nickname = ?
        WHERE guild_id = ?
        AND member_id = ?;""", (value,guildID,memberID,))
        conn.commit()

    if option == "birthday":
        c = conn.cursor()
        c.execute("""
        UPDATE members
        SET birthday = ?
        WHERE guild_id = ?
        AND member_id = ?;""", (value,guildID,memberID,))
        conn.commit()

    if option == "gender":
        c = conn.cursor()
        c.execute("""
        UPDATE members
        SET gender = ?
        WHERE guild_id = ?
        AND member_id = ?;""", (value,guildID,memberID,))
        conn.commit()

    if option == "location":
        c = conn.cursor()
        c.execute("""
        UPDATE members
        SET location = ?
        WHERE guild_id = ?
        AND member_id = ?;""", (value,guildID,memberID,))
        conn.commit()

    if option == "description":
        c = conn.cursor()
        c.execute("""
        UPDATE members
        SET description = ?
        WHERE guild_id = ?
        AND member_id = ?;""", (value,guildID,memberID,))
        conn.commit()

    if option == "likes":
        c = conn.cursor()
        c.execute("""
        UPDATE members
        SET likes = ?
        WHERE guild_id = ?
        AND member_id = ?;""", (value,guildID,memberID,))
        conn.commit()

    if option == "dislikes":
        c = conn.cursor()
        c.execute("""
        UPDATE members
        SET dislikes = ?
        WHERE guild_id = ?
        AND member_id = ?;""", (value,guildID,memberID,))
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


# Creates a starred message for a given guild
def add_starred(guildID, originalID, starredID):
    c = conn.cursor()
    c.execute("""
    INSERT INTO starboard (
        guild_id,
        original_id,
        starred_id
    )
    VALUES
        (?,?,?);""", (guildID,originalID,starredID,))
    conn.commit()


# Returns a starred message of a given guild
def get_starred(messageID):
    c = conn.cursor()
    c.execute("""
    SELECT *
    FROM starboard
    WHERE original_id = ?;""", (messageID,))
    return c.fetchone()


# Deletes a starred message of a given guild
def delete_starred(messageID):
    c = conn.cursor()
    c.execute("""
    DELETE FROM starboard
    WHERE original_id = ?;""", (messageID,))
    conn.commit()


# Set temp data in case the bot goes down mid-process
def set_temp(guildID, memberID, menu):
    c = conn.cursor()
    c.execute("""
    INSERT OR REPLACE INTO temp (
        guild_id,
        member_id,
        menu
    )
    VALUES
        (?, ?, ?);""", (guildID,memberID,menu,))
    conn.commit()


# Update the menu layer a user is currently on
def update_temp(memberID, selected):
    c = conn.cursor()
    c.execute("""
    UPDATE temp
    SET selected = ?
    WHERE member_id = ?;""", (selected,memberID,))


# Get temp data
def get_temp(memberID):
    c = conn.cursor()
    c.execute("""
    SELECT *
    FROM temp
    WHERE member_id = ?;""", (memberID,))
    return c.fetchone()


# Delete temp data when finished
def del_temp(memberID):
    c = conn.cursor()
    c.execute("""
    DELETE FROM temp
    WHERE member_id = ?;""", (memberID,))
    conn.commit()

