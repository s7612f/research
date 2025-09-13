import os
import json
import hashlib
import sqlite3
from datetime import datetime
from typing import Any, Dict, Iterable, Optional, Tuple
from difflib import SequenceMatcher


class DatabaseManager:
    """SQLite manager with extended schema and duplicate detection."""

    def __init__(self, path: str):
        self.path = path
        os.makedirs(os.path.dirname(path), exist_ok=True)
        self.conn = sqlite3.connect(path)
        self._init_db()

    # ------------------------------------------------------------------
    def _init_db(self) -> None:
        cur = self.conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS research_sessions (
                id INTEGER PRIMARY KEY,
                topic TEXT,
                focus TEXT,
                started_at TIMESTAMP,
                completed_at TIMESTAMP,
                status TEXT,
                config TEXT
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS sources (
                id INTEGER PRIMARY KEY,
                url TEXT,
                archived_url TEXT,
                content TEXT,
                content_hash TEXT UNIQUE,
                credibility_score REAL,
                fetched_at TIMESTAMP,
                headers TEXT,
                metadata TEXT
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS findings (
                id INTEGER PRIMARY KEY,
                session_id INTEGER,
                content TEXT,
                confidence REAL,
                source_id INTEGER,
                timestamp TIMESTAMP,
                embedding BLOB,
                metadata TEXT
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS queries (
                id INTEGER PRIMARY KEY,
                session_id INTEGER,
                query TEXT,
                response TEXT,
                model TEXT,
                timestamp TIMESTAMP,
                tokens_used INTEGER
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS contradictions (
                id INTEGER PRIMARY KEY,
                finding_a INTEGER,
                finding_b INTEGER,
                explanation TEXT,
                resolved BOOLEAN,
                resolution TEXT
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS knowledge_graph (
                id INTEGER PRIMARY KEY,
                session_id INTEGER,
                entity_a TEXT,
                relation TEXT,
                entity_b TEXT,
                confidence REAL,
                source_ids TEXT
            )
            """
        )
        self.conn.commit()

    # ------------------------------------------------------------------
    def start_session(self, topic: str, focus: str, config: Dict[str, Any]) -> int:
        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO research_sessions(topic, focus, started_at, status, config) VALUES (?, ?, ?, ?, ?)",
            (topic, focus, datetime.utcnow(), "running", json.dumps(config)),
        )
        self.conn.commit()
        return cur.lastrowid

    def complete_session(self, session_id: int, status: str) -> None:
        cur = self.conn.cursor()
        cur.execute(
            "UPDATE research_sessions SET completed_at=?, status=? WHERE id=?",
            (datetime.utcnow(), status, session_id),
        )
        self.conn.commit()

    # ------------------------------------------------------------------
    def add_source(self, url: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> Tuple[int, bool]:
        """Insert content if not duplicate. Returns (id, added?)."""
        metadata = metadata or {}
        content_hash = hashlib.sha256(content.encode()).hexdigest()
        cur = self.conn.cursor()
        cur.execute("SELECT id, content FROM sources WHERE content_hash=?", (content_hash,))
        row = cur.fetchone()
        if row:
            return row[0], False
        # near-duplicate check
        cur.execute("SELECT id, content FROM sources")
        for sid, existing in cur.fetchall():
            if SequenceMatcher(a=content, b=existing).ratio() >= 0.85:
                return sid, False
        cur.execute(
            "INSERT INTO sources(url, content, content_hash, metadata, fetched_at) VALUES (?, ?, ?, ?, ?)",
            (url, content, content_hash, json.dumps(metadata), datetime.utcnow()),
        )
        self.conn.commit()
        return cur.lastrowid, True

    def add_finding(
        self,
        session_id: int,
        content: str,
        confidence: float,
        source_id: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> int:
        cur = self.conn.cursor()
        cur.execute(
            """
            INSERT INTO findings(session_id, content, confidence, source_id, timestamp, metadata)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (session_id, content, confidence, source_id, datetime.utcnow(), json.dumps(metadata or {})),
        )
        self.conn.commit()
        return cur.lastrowid

    def add_query(
        self,
        session_id: int,
        query: str,
        response: str,
        model: str,
        tokens_used: int,
    ) -> int:
        cur = self.conn.cursor()
        cur.execute(
            """
            INSERT INTO queries(session_id, query, response, model, timestamp, tokens_used)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (session_id, query, response, model, datetime.utcnow(), tokens_used),
        )
        self.conn.commit()
        return cur.lastrowid

    def log_contradiction(self, finding_a: int, finding_b: int, explanation: str) -> None:
        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO contradictions(finding_a, finding_b, explanation, resolved) VALUES (?, ?, ?, 0)",
            (finding_a, finding_b, explanation),
        )
        self.conn.commit()

    def count_sources(self) -> int:
        cur = self.conn.cursor()
        cur.execute("SELECT COUNT(*) FROM sources")
        return cur.fetchone()[0]

    # ------------------------------------------------------------------
    def close(self) -> None:
        self.conn.close()
