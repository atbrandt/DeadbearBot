import sqlite3
from pathlib import Path

db = sqlite3.connect(Path(__file__).parent / "bot.db")

def setupDatabase():
    # Makes the database return rows as dictionaries instead of tuples
    # See: https://stackoverflow.com/questions/3300464/how-can-i-get-dict-from-sqlite-query
    db.row_factory = dict_factory

    c = db.cursor()

    # Create tables if they don't exist
    c.execute('''
    CREATE TABLE IF NOT EXISTS reaction_roles (
        id INTEGER PRIMARY KEY,
        roleID INTEGER UNIQUE,
        emoji TEXT UNIQUE
    )
    ''')

    c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        experience INTEGER
    )
    ''')

    c.execute('''
    CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY,
        name TEXT UNIQUE,
        description TEXT
    )
    ''')

    c.execute('''
    CREATE TABLE IF NOT EXISTS user_items (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        item_id INTEGER,
        FOREIGN KEY(user_id) REFERENCES users(id),
        FOREIGN KEY(item_id) REFERENCES items(id)
    )
    ''')
    db.commit()

    # If there are no items, add some
    if(len(getAllItems()) == 0):
        createItem("Diamond", "A pretty rock.")
        createItem("Shoe", "Goes on your foot.")
        createItem("Knife", "For poking.")


# Create an item
def createItem(name, description=""):
    db.cursor().execute(
        "INSERT INTO items (name, description) VALUES (?, ?)",
        (name, description,)
    )
    db.commit()

# Returns all items
def getAllItems():
    c = db.cursor()
    c.execute("SELECT * FROM items")
    return c.fetchall()

# Finds an item by its name and returns it
def getItemByName(name):
    c = db.cursor()
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
    db.cursor().execute(
        "INSERT INTO user_items (user_id, item_id) VALUES (?, ?)",
        (userId, itemId,)
    )
    db.commit()

# Returns all reaction roles
def getAllRRs():
    c = db.cursor()
    c.execute("SELECT * FROM reaction_roles")
    return c.fetchall()

# Adds a reaction role to database
def addRR(roleID, emoji):
    db.cursor().execute(
        "INSERT INTO reaction_roles (roleID, emoji) VALUES (?, ?)",
        (roleID, emoji,)
    )
    db.commit()

# Removes a reaction role from database
def removeRR(id):
    db.cursor().execute(
        "DELETE FROM reaction_roles WHERE id=?",
        (id,)
    )
    db.commit()

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d
