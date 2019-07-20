import sqlite3
db = sqlite3.connect('bot.db')

def setupDatabase():
    c = db.cursor()

    # Create tables if they don't exist
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
    return list(map(parseItemRow, c.fetchall()))

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
    return parseItemRow(row)

# Gives an item to a user
def giveUserItem(userId, itemId):
    db.cursor().execute(
        "INSERT INTO user_items (user_id, item_id) VALUES (?, ?)",
        (userId, itemId,)
    )
    db.commit()

# Converts an item tuple into a dictionary (so you don't have to remember the indexes)
def parseItemRow(row):
    if row is None:
        return None
    return {
        'id': row[0],
        'name': row[1],
        'description': row[2]
    }
