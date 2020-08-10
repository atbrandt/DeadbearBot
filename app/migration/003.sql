CREATE TABLE IF NOT EXISTS role_alerts(
    uuid TEXT PRIMARY KEY UNIQUE,
    guild_id INTEGER,
    role_id INTEGER,
    event TEXT,
    channel_id INTEGER,
    message TEXT,
    FOREIGN KEY (guild_id) REFERENCES guilds (id)
);

