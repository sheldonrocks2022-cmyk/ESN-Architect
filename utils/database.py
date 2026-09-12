import os
import sqlite3
from contextlib import contextmanager


class Database:
    def __init__(self, path: str):
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        self.path = path
        with self._connect() as con:
            con.execute("""
                CREATE TABLE IF NOT EXISTS guild_config (
                    guild_id INTEGER PRIMARY KEY,
                    prefix TEXT DEFAULT '!',
                    log_channel INTEGER,
                    welcome_channel INTEGER,
                    ai_enabled INTEGER DEFAULT 1,
                    ai_model TEXT
                )
            """)
            con.execute("""
                CREATE TABLE IF NOT EXISTS usage (
                    guild_id INTEGER,
                    user_id INTEGER,
                    command TEXT,
                    uses INTEGER DEFAULT 0,
                    PRIMARY KEY (guild_id, user_id, command)
                )
            """)
            columns = {row[1] for row in con.execute("PRAGMA table_info(guild_config)")}
            if "ai_enabled" not in columns:
                con.execute("ALTER TABLE guild_config ADD COLUMN ai_enabled INTEGER DEFAULT 1")
            if "ai_model" not in columns:
                con.execute("ALTER TABLE guild_config ADD COLUMN ai_model TEXT")

    @contextmanager
    def _connect(self):
        con = sqlite3.connect(self.path)
        try:
            yield con
            con.commit()
        finally:
            con.close()

    def set_config(self, guild_id, **values):
        allowed = {"prefix", "log_channel", "welcome_channel", "ai_enabled", "ai_model"}
        values = {k: v for k, v in values.items() if k in allowed}
        if not values:
            return
        with self._connect() as con:
            con.execute("INSERT OR IGNORE INTO guild_config (guild_id) VALUES (?)", (guild_id,))
            for key, value in values.items():
                con.execute(f"UPDATE guild_config SET {key}=? WHERE guild_id=?", (value, guild_id))

    def get_config(self, guild_id):
        with self._connect() as con:
            row = con.execute(
                "SELECT prefix, log_channel, welcome_channel, ai_enabled, ai_model FROM guild_config WHERE guild_id=?",
                (guild_id,),
            ).fetchone()
        if not row:
            return {"prefix": "!", "log_channel": None, "welcome_channel": None, "ai_enabled": True, "ai_model": None}
        return {
            "prefix": row[0],
            "log_channel": row[1],
            "welcome_channel": row[2],
            "ai_enabled": bool(row[3]),
            "ai_model": row[4],
        }

    def record_usage(self, guild_id, user_id, command):
        guild_id = int(guild_id or 0)
        user_id = int(user_id)
        with self._connect() as con:
            con.execute(
                "INSERT INTO usage(guild_id,user_id,command,uses) VALUES(?,?,?,1) "
                "ON CONFLICT(guild_id,user_id,command) DO UPDATE SET uses=uses+1",
                (guild_id, user_id, command),
            )

    def get_usage(self, guild_id, user_id=None):
        with self._connect() as con:
            if user_id is None:
                return con.execute(
                    "SELECT command, SUM(uses) FROM usage WHERE guild_id=? GROUP BY command ORDER BY SUM(uses) DESC",
                    (guild_id,),
                ).fetchall()
            return con.execute(
                "SELECT command, uses FROM usage WHERE guild_id=? AND user_id=? ORDER BY uses DESC",
                (guild_id, user_id),
            ).fetchall()
