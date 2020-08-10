CREATE TABLE IF NOT EXISTS guilds(
    id INTEGER PRIMARY KEY UNIQUE,
    bot_alias TEXT,
    auto_role INTEGER,
    greet_channel INTEGER,
    greet_message TEXT,
    bye_channel INTEGER,
    bye_message TEXT,
    perm_role INTEGER
);

CREATE TABLE IF NOT EXISTS members(
    id INTEGER PRIMARY KEY,
    guild_id INTEGER,
    member_id INTEGER,
    created_at INTEGER,
    joined_at INTEGER UNIQUE,
    level INTEGER,
    xp INTEGER,
    cash INTEGER,
    name TEXT,
    nickname TEXT,
    birthday INTEGER,
    gender TEXT,
    location TEXT,
    description TEXT,
    likes TEXT,
    dislikes TEXT,
    FOREIGN KEY (guild_id) REFERENCES guilds (id)
);

CREATE TABLE IF NOT EXISTS reaction_roles(
    uuid TEXT PRIMARY KEY UNIQUE,
    guild_id INTEGER,
    hook_id TEXT,
    emoji TEXT,
    role_id INTEGER,
    FOREIGN KEY (guild_id) REFERENCES guilds (id)
);

CREATE TABLE IF NOT EXISTS voice_roles(
    uuid TEXT PRIMARY KEY UNIQUE,
    guild_id INTEGER,
    hook_id INTEGER,
    role_id INTEGER,
    FOREIGN KEY (guild_id) REFERENCES guilds (id)
);

CREATE TABLE IF NOT EXISTS blurbs(
    uuid TEXT PRIMARY KEY UNIQUE,
    guild_id INTEGER,
    command TEXT UNIQUE,
    message TEXT,
    FOREIGN KEY (guild_id) REFERENCES guilds (id)
);

CREATE TABLE IF NOT EXISTS temp(
    id INTEGER PRIMARY KEY,
    guild_id INTEGER,
    member_id INTEGER UNIQUE,
    menu TEXT,
    selected TEXT,
    FOREIGN KEY (guild_id) REFERENCES guilds (id)
);
