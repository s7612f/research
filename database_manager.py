import sqlite3
import os
import hashlib
from typing import Tuple
from difflib import SequenceMatcher

class DatabaseManager:
    """SQLite manager with exact and near-duplicate detection"""
    def __init__(self, path: str):
        self.path = path
        os.makedirs(os.path.dirname(path), exist_ok=True)
        self.conn = sqlite3.connect(path)
        self._init_db()

    def _init_db(self):
        cur = self.conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS sources (
                id INTEGER PRIMARY KEY,
                content TEXT,
                content_hash TEXT UNIQUE,
                metadata TEXT
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS contradictions (
                id INTEGER PRIMARY KEY,
                source_a INTEGER,
                source_b INTEGER,
                reason TEXT
            )
        """)
        self.conn.commit()

    def add_source(self, content: str, metadata: str = "") -> Tuple[int, bool]:
        """Insert content if not duplicate. Returns (id, added?)."""
        content_hash = hashlib.sha256(content.encode()).hexdigest()
        cur = self.conn.cursor()
        cur.execute("SELECT id, content FROM sources WHERE content_hash=?", (content_hash,))
        row = cur.fetchone()
        if row:
            return row[0], False
        cur.execute("SELECT id, content FROM sources")
        for sid, existing in cur.fetchall():
            if SequenceMatcher(a=content, b=existing).ratio() >= 0.85:
                return sid, False
        cur.execute("INSERT INTO sources(content, content_hash, metadata) VALUES (?, ?, ?)",
                    (content, content_hash, metadata))
        self.conn.commit()
        return cur.lastrowid, True

    def log_contradiction(self, source_a: int, source_b: int, reason: str) -> None:
        cur = self.conn.cursor()
        cur.execute("INSERT INTO contradictions(source_a, source_b, reason) VALUES (?, ?, ?)",
                    (source_a, source_b, reason))
        self.conn.commit()

    def count_sources(self) -> int:
        cur = self.conn.cursor()
        cur.execute("SELECT COUNT(*) FROM sources")
        return cur.fetchone()[0]
