import sqlite3
from sqlite3 import Error
from pathlib import Path


# Set platform-independent path to db file
DATABASE = str(Path(__file__).parent / "bot.db")


# Create a database connection
try:
    conn = sqlite3.connect(DATABASE)
except Error as e:
    print(e)
else:
    # Set the database to return dictionaries instead of tuples
    conn.row_factory = sqlite3.Row


# Initialize database and create default tables
def setup_database():
    c = conn.cursor()

    # Set database to use Write Ahead Log for concurrency
    c.execute("PRAGMA journal_mode=WAL")

    c.execute("""
    CREATE TABLE IF NOT EXISTS reaction_role_hooks (
        id INTEGER PRIMARY KEY,
        channel_id INTEGER,
        message_id INTEGER UNIQUE
    );""")

    c.execute("""
    CREATE TABLE IF NOT EXISTS reaction_roles (
        id INTEGER PRIMARY KEY,
        emoji text,
        role_id INTEGER,
        hook_id INTEGER NOT NULL,
        FOREIGN KEY (hook_id) REFERENCES reaction_role_hooks (id)
    );""")

    c.execute("""
    CREATE TABLE IF NOT EXISTS voice_roles (
        id INTEGER PRIMARY KEY,
        vchannel_id INTEGER UNIQUE,
        role_id INTEGER
    );""")

    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        experience INTEGER
    );""")

    c.execute("""
    CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY,
        name TEXT UNIQUE,
        description TEXT
    );""")

    c.execute("""
    CREATE TABLE IF NOT EXISTS user_items (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        item_id INTEGER,
        FOREIGN KEY (user_id) REFERENCES users (id),
        FOREIGN KEY (item_id) REFERENCES items (id)
    );""")

    conn.commit()

    # If there are no items, add some
    if(len(get_all_items()) == 0):
        print(get_all_items())
        create_item("Diamond", "A pretty rock.")
        create_item("Shoe", "Goes on your foot.")
        create_item("Knife", "For poking.")


# Returns all items in Item table
def get_all_items():
    c = conn.cursor()
    c.execute("""
    SELECT *
    FROM items;""")
    return c.fetchall()


# Finds an item in Item table by its name and returns it
def get_item(name):
    c = conn.cursor()
    c.execute("""
    SELECT id, name, description
    FROM items
    WHERE name = ? COLLATE NOCASE LIMIT 1;""", (name,))
    return c.fetchall()


# Create an item
def create_item(name, description):
    c = conn.cursor()
    c.execute("""
    INSERT INTO items (
        name,
        description
    )
    VALUES (
        ?,
        ?
    );""", (name, description,))
    conn.commit()


# Gives an item to a user
def give_item(userId, itemId):
    c = conn.cursor()
    c.execute("""
    INSERT INTO user_items (
        user_id,
        item_id
    )
    VALUES (
        ?,
        ?
    );""", (userId, itemId,))
    conn.commit()


# Returns all reaction role hooks
def get_all_hooks():
    c = conn.cursor()
    c.execute("""
    SELECT id, channel_id, message_id
    FROM reaction_role_hooks;""")
    return c.fetchall()


# Returns a reaction role hook by message_id
def get_hook_by_message(messageID):
    c = conn.cursor()
    c.execute("""
    SELECT *
    FROM reaction_role_hooks
    WHERE message_id = ?;""", (messageID,))
    return c.fetchone()


# Returns a reaction role hook by message_id
def get_hook_by_id(hookID):
    c = conn.cursor()
    c.execute("""
    SELECT *
    FROM reaction_role_hooks
    WHERE id = ?;""", (hookID,))
    return c.fetchone()


# Adds a reaction role hook to database
def add_reaction_role_hook(channelID, messageID):
    c = conn.cursor()
    c.execute("""
    INSERT INTO reaction_role_hooks (
        channel_id,
        message_id
    )
    VALUES (
        ?,
        ?
    );""", (channelID, messageID,))
    conn.commit()
    return c.lastrowid


# Deletes a reaction role hook and all associated reaction roles
def delete_reaction_role_hook(rrID):
    c = conn.cursor()
    c.execute("""
    DELETE FROM reaction_role_hooks
    WHERE id = ?;""", (rrID,))
    c.execute("""
    DELETE FROM reaction_roles
    WHERE hook_id = ?;""", (rrID,))
    conn.commit()


# Returns all reaction roles
def get_all_reaction_roles():
    c = conn.cursor()
    c.execute("""
    SELECT *
    FROM reaction_roles;""")
    return c.fetchall()


# Get reaction role entry by emoji and hook_id
def get_reaction_role(hookID, emoji):
    c = conn.cursor()
    c.execute("""
    SELECT *
    FROM reaction_roles
    WHERE hook_id = ? AND emoji = ?;""", (hookID, emoji,))
    return c.fetchone()


# Adds a reaction role to database
def add_reaction_role(emoji, roleID, hookID):
    c = conn.cursor()
    c.execute("""
    INSERT INTO reaction_roles (
        emoji,
        role_id,
        hook_id
    )
    VALUES (
        ?,
        ?,
        ?
    );""", (emoji, roleID, hookID,))
    conn.commit()
    return c.lastrowid


# Removes a reaction role from database
def delete_reaction_role(rrID):
    c = conn.cursor()
    c.execute("""
    DELETE FROM reaction_roles
    WHERE id = ?;""", (rrID,))
    conn.commit()


# Returns all voice chat roles
def get_all_voice_channel_roles():
    c = conn.cursor()
    c.execute("""
    SELECT *
    FROM voice_roles;""")
    return c.fetchall()


# Returns a voice chat role by vchannel_id
def get_voice_channel_role(vchannelID):
    c = conn.cursor()
    c.execute("""
    SELECT *
    FROM voice_roles
    WHERE vchannel_id = ?;""", (vchannelID,))
    return c.fetchall()


# Adds a voice chat role to database
def add_voice_channel_role(vchannelID, roleID):
    c = conn.cursor()
    c.execute("""
    INSERT INTO voice_roles (
        vchannel_id,
        role_id
    )
    VALUES (
        ?,
        ?
    );""", (vchannelID, roleID,))
    conn.commit()


# Removes a voice chat role from database
def delete_voice_channel_role(vcrID):
    c = conn.cursor()
    c.execute("""
    DELETE FROM voice_roles
    WHERE id = ?;""", (vcrID,))
    conn.commit()
