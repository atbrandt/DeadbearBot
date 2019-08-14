import sqlite3
from pathlib import Path

# Set platform-independent path to db file
DATABASE = str(Path(__file__).parent / "bot.db")

# Create a database connection 
try:
    conn = sqlite3.connect(DATABASE)
except Error as e:
    print(e)

# Set the database to return dictionaries instead of tuples
conn.row_factory = sqlite3.Row

# Set global cursor
c = conn.cursor()

# Create an item
def createItem(name, description):
    c.execute("""INSERT INTO items (
        name,
        description
    )
    VALUES (
        ?,
        ?
    );""", (
        name,
        description,)
    )


# Returns all items
def getAllItems():
    c.execute("SELECT * FROM items")
    return c.fetchall()


# Finds an item by its name and returns it
def getItemByName(name):
    c.execute(
        "SELECT * FROM items WHERE name = ? COLLATE NOCASE LIMIT 1",
        (name,)
    )
    row = c.fetchone()
    if(row is None):
        return None
    return row


# Gives an item to a user
def giveUserItem(userId, itemId):
    c.execute(
        "INSERT INTO user_items (user_id, item_id) VALUES (?, ?)",
        (userId, itemId,)
    )


# Returns all reaction roles
def getAllRR():
    c.execute("SELECT * FROM reaction_roles")
    return c.fetchall()


# Adds a reaction role to database
def addRR(emoji, roleID):
    c.execute(
        "INSERT INTO reaction_roles (emoji, roleID) VALUES (?, ?)",
        (emoji, roleID,)
    )


# Removes a reaction role from database
def removeRR(id):
    c.execute(
        "DELETE FROM reaction_roles WHERE id=?",
        (id,)
    )


def findRRbyEmoji(emoji):
    c.execute(
        "SELECT * FROM reaction_roles WHERE emoji=?", (emoji)
    )
    return


# Returns all voice chat roles
def getAllVCR():
    c.execute("SELECT * FROM voice_roles")
    return c.fetchall()


# Adds a voice chat role to database
def addVCR(vcID, roleID):
    c.execute(
        "INSERT INTO voice_roles (vcID, roleID) VALUES (?, ?)",
        (vcID, roleID,)
    )


# Removes a voice chat role from database
def removeVCR(id):
    c.execute(
        "DELETE FROM voice_roles WHERE id=?",
        (id,)
    )


# Adds a reaction role hook to database
def addRRHook(channelID, messageID):
    c.execute("""
        INSERT INTO reaction_role_hooks (
            channelID,
            messageID)
        VALUES (
            ?,
            ?);""", (
        channelID,
        messageID,)
    )


# Returns all reaction role hooks
def getAllRRHooks():
    c.execute("SELECT * FROM reaction_role_hooks")
    return c.fetchall()


# Initialize database and create default tables
def setup_database():
    c.execute("""CREATE TABLE IF NOT EXISTS reaction_role_hooks (
        id int PRIMARY KEY,
        channel_id int,
        message_id int UNIQUE
    );""")

    c.execute("""CREATE TABLE IF NOT EXISTS reaction_roles (
        id int PRIMARY KEY,
        emoji varchar(255),
        role_id int,
        hook_id int NOT NULL,
        FOREIGN KEY (hook_id) REFERENCES reaction_role_hooks (id)
    );""")

    c.execute("""CREATE TABLE IF NOT EXISTS voice_roles (
        id int PRIMARY KEY,
        vchannel_id int UNIQUE,
        role_id int
    );""")

    c.execute("""CREATE TABLE IF NOT EXISTS users (
        id int PRIMARY KEY,
        experience int
    );""")

    c.execute("""CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY,
        name TEXT UNIQUE,
        description TEXT
    );""")

    c.execute("""CREATE TABLE IF NOT EXISTS user_items (
        id int PRIMARY KEY,
        user_id int,
        item_id int,
        FOREIGN KEY (user_id) REFERENCES users (id),
        FOREIGN KEY (item_id) REFERENCES items (id)
    );""")

    # If there are no items, add some
    if(len(getAllItems()) == 0):
        createItem("Diamond", "A pretty rock.")
        createItem("Shoe", "Goes on your foot.")
        createItem("Knife", "For poking.")

