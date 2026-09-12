import os
import sqlite3

class Database:
    def __init__(self, path: str):
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        self.path = path
        with sqlite3.connect(self.path) as con:
            con.execute("CREATE TABLE IF NOT EXISTS guild_config (guild_id INTEGER PRIMARY KEY, prefix TEXT DEFAULT '!', log_channel INTEGER, welcome_channel INTEGER)")
            con.execute("CREATE TABLE IF NOT EXISTS usage (guild_id INTEGER, user_id INTEGER, command TEXT, uses INTEGER DEFAULT 0, PRIMARY KEY (guild_id, user_id, command))")

    def set_config(self, guild_id, **values):
        allowed = {"prefix", "log_channel", "welcome_channel"}
        values = {k: v for k, v in values.items() if k in allowed}
        if not values: return
        with sqlite3.connect(self.path) as con:
            con.execute("INSERT OR IGNORE INTO guild_config (guild_id) VALUES (?)", (guild_id,))
            for key, value in values.items():
                con.execute(f"UPDATE guild_config SET {key}=? WHERE guild_id=?", (value, guild_id))

    def get_config(self, guild_id):
        with sqlite3.connect(self.path) as con:
            row = con.execute("SELECT prefix, log_channel, welcome_channel FROM guild_config WHERE guild_id=?", (guild_id,)).fetchone()
        return {"prefix": row[0], "log_channel": row[1], "welcome_channel": row[2]} if row else {"prefix": "!", "log_channel": None, "welcome_channel": None}

    def record_usage(self, guild_id, user_id, command):
        with sqlite3.connect(self.path) as con:
            con.execute("INSERT INTO usage(guild_id,user_id,command,uses) VALUES(?,?,?,1) ON CONFLICT(guild_id,user_id,command) DO UPDATE SET uses=uses+1", (guild_id,user_id,command))
