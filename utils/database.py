import os
import sqlite3
from contextlib import contextmanager


class Database:
    """Small SQLite persistence layer for Forge configuration and saved data."""
    def __init__(self, path: str):
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        self.path = path
        with self._connect() as con:
            con.execute("CREATE TABLE IF NOT EXISTS guild_config (guild_id INTEGER PRIMARY KEY, prefix TEXT DEFAULT '!', log_channel INTEGER, welcome_channel INTEGER, ai_enabled INTEGER DEFAULT 1, ai_model TEXT)")
            con.execute("CREATE TABLE IF NOT EXISTS usage (guild_id INTEGER, user_id INTEGER, command TEXT, uses INTEGER DEFAULT 0, PRIMARY KEY (guild_id, user_id, command))")
            con.execute("CREATE TABLE IF NOT EXISTS ai_sessions (guild_id INTEGER, user_id INTEGER, session TEXT, role TEXT, content TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP)")
            con.execute("CREATE TABLE IF NOT EXISTS saved_projects (guild_id INTEGER, user_id INTEGER, name TEXT, language TEXT, payload TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP, updated_at TEXT DEFAULT CURRENT_TIMESTAMP, PRIMARY KEY (guild_id, user_id, name))")
            con.execute("CREATE TABLE IF NOT EXISTS saved_embeds (guild_id INTEGER, user_id INTEGER, name TEXT, payload TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP, updated_at TEXT DEFAULT CURRENT_TIMESTAMP, PRIMARY KEY (guild_id, user_id, name))")
            columns = {row[1] for row in con.execute("PRAGMA table_info(guild_config)")}
            if "ai_enabled" not in columns: con.execute("ALTER TABLE guild_config ADD COLUMN ai_enabled INTEGER DEFAULT 1")
            if "ai_model" not in columns: con.execute("ALTER TABLE guild_config ADD COLUMN ai_model TEXT")

    @contextmanager
    def _connect(self):
        con = sqlite3.connect(self.path)
        try:
            yield con
            con.commit()
        finally: con.close()

    def set_config(self, guild_id, **values):
        allowed = {"prefix", "log_channel", "welcome_channel", "ai_enabled", "ai_model"}
        values = {k: v for k, v in values.items() if k in allowed}
        if not values: return
        with self._connect() as con:
            con.execute("INSERT OR IGNORE INTO guild_config (guild_id) VALUES (?)", (guild_id,))
            for key, value in values.items(): con.execute(f"UPDATE guild_config SET {key}=? WHERE guild_id=?", (value, guild_id))

    def get_config(self, guild_id):
        with self._connect() as con:
            row = con.execute("SELECT prefix, log_channel, welcome_channel, ai_enabled, ai_model FROM guild_config WHERE guild_id=?", (guild_id,)).fetchone()
        if not row: return {"prefix":"!", "log_channel":None, "welcome_channel":None, "ai_enabled":True, "ai_model":None}
        return {"prefix":row[0], "log_channel":row[1], "welcome_channel":row[2], "ai_enabled":bool(row[3]), "ai_model":row[4]}

    def record_usage(self, guild_id, user_id, command):
        with self._connect() as con:
            con.execute("INSERT INTO usage(guild_id,user_id,command,uses) VALUES(?,?,?,1) ON CONFLICT(guild_id,user_id,command) DO UPDATE SET uses=uses+1", (int(guild_id or 0), int(user_id), command))

    def get_usage(self, guild_id, user_id=None):
        with self._connect() as con:
            if user_id is None: return con.execute("SELECT command, SUM(uses) FROM usage WHERE guild_id=? GROUP BY command ORDER BY SUM(uses) DESC", (guild_id,)).fetchall()
            return con.execute("SELECT command, uses FROM usage WHERE guild_id=? AND user_id=? ORDER BY uses DESC", (guild_id, user_id)).fetchall()

    def save_session_message(self, guild_id, user_id, session, role, content):
        with self._connect() as con:
            con.execute("INSERT INTO ai_sessions(guild_id,user_id,session,role,content) VALUES(?,?,?,?,?)", (guild_id, user_id, session, role, content))

    def get_session(self, guild_id, user_id, session, limit=12):
        with self._connect() as con:
            rows = con.execute("SELECT role, content FROM ai_sessions WHERE guild_id=? AND user_id=? AND session=? ORDER BY rowid DESC LIMIT ?", (guild_id, user_id, session, limit)).fetchall()
        return list(reversed(rows))

    def clear_session(self, guild_id, user_id, session):
        with self._connect() as con: con.execute("DELETE FROM ai_sessions WHERE guild_id=? AND user_id=? AND session=?", (guild_id, user_id, session))

    def save_item(self, table, guild_id, user_id, name, payload, language=None):
        if table == "saved_projects":
            sql = "INSERT INTO saved_projects(guild_id,user_id,name,language,payload) VALUES(?,?,?,?,?) ON CONFLICT(guild_id,user_id,name) DO UPDATE SET language=excluded.language,payload=excluded.payload,updated_at=CURRENT_TIMESTAMP"
            args = (guild_id, user_id, name, language or "unknown", payload)
        elif table == "saved_embeds":
            sql = "INSERT INTO saved_embeds(guild_id,user_id,name,payload) VALUES(?,?,?,?) ON CONFLICT(guild_id,user_id,name) DO UPDATE SET payload=excluded.payload,updated_at=CURRENT_TIMESTAMP"
            args = (guild_id, user_id, name, payload)
        else: raise ValueError("Unsupported saved-data table")
        with self._connect() as con: con.execute(sql, args)

    def get_items(self, table, guild_id, user_id):
        if table not in {"saved_projects", "saved_embeds"}: raise ValueError("Unsupported saved-data table")
        with self._connect() as con: return con.execute(f"SELECT name,payload FROM {table} WHERE guild_id=? AND user_id=? ORDER BY updated_at DESC", (guild_id, user_id)).fetchall()
