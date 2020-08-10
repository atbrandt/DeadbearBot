CREATE TABLE guildstemp(
    id INTEGER PRIMARY KEY UNIQUE,
    bot_alias TEXT,
    guild_stats TEXT DEFAULT('enabled'),
    auto_role INTEGER,
    star_channel INTEGER,
    star_threshold INTEGER NOT NULL DEFAULT(3),
    join_channel INTEGER,
    join_message TEXT,
    leave_channel INTEGER,
    leave_message TEXT,
    perm_role INTEGER
);

INSERT INTO guildstemp(id,bot_alias,auto_role,join_channel,join_message,leave_channel,leave_message,perm_role)
SELECT id,bot_alias,auto_role,greet_channel,greet_message,bye_channel,bye_message,perm_role
FROM guilds;

DROP TABLE guilds;

ALTER TABLE guildstemp
RENAME TO guilds;

CREATE TABLE memberstemp(
    id INTEGER PRIMARY KEY,
    guild_id INTEGER,
    member_id INTEGER,
    created_at INTEGER,
    joined_at INTEGER UNIQUE,
    lvl INTEGER,
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

INSERT INTO memberstemp(id,guild_id,member_id,created_at,joined_at,lvl,xp,cash,name,nickname,birthday,gender,location,description,likes,dislikes)
SELECT id,guild_id,member_id,created_at,joined_at,level,xp,cash,name,nickname,birthday,gender,location,description,likes,dislikes
FROM members;

DROP TABLE members;

ALTER TABLE memberstemp
RENAME TO members;

CREATE TABLE IF NOT EXISTS starboard(
    guild_id INTEGER,
    original_id INTEGER PRIMARY KEY UNIQUE,
    starred_id INTEGER UNIQUE,
    FOREIGN KEY (guild_id) REFERENCES guilds (id)
);
