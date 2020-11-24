import sqlite3
from pathlib import Path


# Set platform-independent path to db file and migrations folder
for path in Path(__file__).parents[2].rglob('bot.db'):
    DBPATH = path
if not DBPATH:
    DBPATH = Path(__file__).parents[1] / 'bot.db'

MIGPATH = Path(__file__).parent / "migration"


def migrate():
    conn = sqlite3.connect(str(DBPATH))
    c = conn.cursor()
    c.execute("PRAGMA user_version")
    dbver = c.fetchone()

    # Get list of migrations available
    migrations = []
    for child in sorted(MIGPATH.iterdir()):
        if child.suffix == ".sql":
            migrations.append(child)

    # Check if db matches latest version available, then update if not
    latest = sorted(migrations, reverse=True)
    latestver = int(latest[0].stem)
    if dbver[0] < latestver:
        print("Database is out of date! Migrating...\n")
        for item in migrations:
            print(f"Checking DB migration file {item.stem}")
            scriptver = int(item.stem)
            if scriptver > dbver[0]:
                print(f"Migrating DB to version {scriptver}")
                sqlfile = open(item, 'r').read()
                try:
                    conn.executescript(sqlfile)
                except Exception as e:
                    print(e)
                else:
                    conn.execute(f"PRAGMA user_version={scriptver};")
                    print(f"Done! DB at version {scriptver}\n")
            else:
                print(f"Migration {item.stem} already applied, skipping...\n")
    conn.commit()
    conn.close()
