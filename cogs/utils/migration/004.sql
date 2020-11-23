CREATE TABLE IF NOT EXISTS custom_roles(
    id INTEGER PRIMARY KEY UNIQUE,
    guild_id INTEGER,
    member_id INTEGER,
    role_id INTEGER,
    FOREIGN KEY (guild_id) REFERENCES guilds (id)
);

CREATE TABLE guildstemp(
    id INTEGER PRIMARY KEY UNIQUE,
    bot_role INTEGER,
    bot_alias TEXT,
    guild_stats TEXT NOT NULL DEFAULT('enabled'),
    min_cash INTEGER NOT NULL DEFAULT(1),
    max_cash INTEGER NOT NULL DEFAULT(25),
    auto_role INTEGER,
    star_channel INTEGER,
    star_threshold INTEGER NOT NULL DEFAULT(3),
    join_channel INTEGER,
    join_message TEXT,
    leave_channel INTEGER,
    leave_message TEXT,
    perm_role INTEGER
);

INSERT INTO guildstemp(id,bot_alias,guild_stats,auto_role,star_channel,star_threshold,join_channel,join_message,leave_channel,leave_message,perm_role)
SELECT id,bot_alias,guild_stats,auto_role,star_channel,star_threshold,join_channel,join_message,leave_channel,leave_message,perm_role
FROM guilds;

DROP TABLE guilds;

ALTER TABLE guildstemp
RENAME TO guilds;

ALTER TABLE members
ADD COLUMN daily_timestamp TEXT;

ALTER TABLE temp
ADD COLUMN storage TEXT;