"""Baza SQLite: konta graczy, sesje i zapis rozegranych partii.

Plik bazy wskazuje zmienna ORLOG_DB (domyślnie orlog.db obok serwera).
Serwer działa jako jeden proces z wątkami, więc wystarcza jedno połączenie
chronione blokadą. Zmiany schematu idą kolejno przez MIGRATIONS
(numer ostatniej zastosowanej siedzi w PRAGMA user_version).
"""
from __future__ import annotations

import os
import sqlite3
import threading
from contextlib import contextmanager
from typing import Iterator, List

DEFAULT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "orlog.db")

MIGRATIONS: List[str] = [
    # 1: konta, sesje, kody do resetu hasła, partie
    """
    CREATE TABLE users (
        id INTEGER PRIMARY KEY,
        login TEXT NOT NULL,
        login_key TEXT NOT NULL UNIQUE,     -- login bez rozróżniania wielkości liter
        email TEXT NOT NULL,
        email_key TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        rating INTEGER NOT NULL DEFAULT 1000,
        created_at REAL NOT NULL
    );
    CREATE TABLE sessions (
        token_hash TEXT PRIMARY KEY,        -- sam token zna tylko aplikacja gracza
        user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        created_at REAL NOT NULL,
        last_used REAL NOT NULL
    );
    CREATE INDEX sessions_user ON sessions(user_id);
    CREATE TABLE reset_codes (
        user_id INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
        code_hash TEXT NOT NULL,
        expires_at REAL NOT NULL,
        attempts INTEGER NOT NULL DEFAULT 0
    );
    CREATE TABLE matches (
        id INTEGER PRIMARY KEY,
        ranked INTEGER NOT NULL,
        rounds INTEGER NOT NULL,
        forfeit INTEGER NOT NULL DEFAULT 0, -- przegrany wyszedł albo nie wrócił do partii
        finished_at REAL NOT NULL
    );
    CREATE TABLE match_players (
        match_id INTEGER NOT NULL REFERENCES matches(id) ON DELETE CASCADE,
        seat INTEGER NOT NULL,              -- 0 albo 1
        user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,   -- NULL: gość
        name TEXT NOT NULL,
        won INTEGER NOT NULL,
        hp INTEGER NOT NULL,
        gods TEXT NOT NULL,                 -- lista JSON
        rating_before INTEGER,              -- tylko w partiach rankingowych
        rating_after INTEGER,
        PRIMARY KEY (match_id, seat)
    );
    CREATE INDEX match_players_user ON match_players(user_id, match_id);
    """,
]


class Database:
    def __init__(self, path: str | None = None) -> None:
        self.path = path or os.environ.get("ORLOG_DB") or DEFAULT_PATH
        if self.path != ":memory:":
            folder = os.path.dirname(os.path.abspath(self.path))
            os.makedirs(folder, exist_ok=True)
        self.conn = sqlite3.connect(self.path, check_same_thread=False, isolation_level=None)
        self.conn.row_factory = sqlite3.Row
        self.lock = threading.RLock()
        with self.lock:
            self.conn.execute("PRAGMA foreign_keys = ON")
            if self.path != ":memory:":
                self.conn.execute("PRAGMA journal_mode = WAL")
            self.conn.execute("PRAGMA busy_timeout = 5000")
            self._migrate()

    def _migrate(self) -> None:
        version = self.conn.execute("PRAGMA user_version").fetchone()[0]
        for number, script in enumerate(MIGRATIONS[version:], start=version + 1):
            with self.transaction() as conn:
                for statement in script.split(";"):
                    if statement.strip():
                        conn.execute(statement)
                conn.execute(f"PRAGMA user_version = {number}")

    @contextmanager
    def transaction(self) -> Iterator[sqlite3.Connection]:
        """Wszystko albo nic; zagnieżdżenia (np. przy migracji) dołączają do trwającej transakcji."""
        with self.lock:
            if self.conn.in_transaction:
                yield self.conn
                return
            self.conn.execute("BEGIN IMMEDIATE")
            try:
                yield self.conn
            except BaseException:
                self.conn.execute("ROLLBACK")
                raise
            self.conn.execute("COMMIT")

    def query(self, sql: str, params=()) -> List[sqlite3.Row]:
        with self.lock:
            return self.conn.execute(sql, params).fetchall()

    def one(self, sql: str, params=()):
        with self.lock:
            return self.conn.execute(sql, params).fetchone()

    def close(self) -> None:
        with self.lock:
            self.conn.close()
