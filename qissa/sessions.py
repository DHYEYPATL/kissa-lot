"""Session storage for Qissa Studio.

Thread-safe SQLite + memory caching with automatic serialization of SeriesState.
Persists across server restarts, worker reloads, and multi-threaded requests.
"""

from __future__ import annotations

import json
import sqlite3
import threading
import time
from pathlib import Path
from typing import Optional

from qissa.state import SeriesState

DB_PATH = Path(__file__).resolve().parent.parent / ".qissa_sessions.db"
_LOCK = threading.Lock()
_MEM_CACHE: dict[str, tuple[float, SeriesState]] = {}
CACHE_TTL = 3600  # 1 hour memory TTL


def _get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False, timeout=10.0)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT PRIMARY KEY,
            data_json TEXT NOT NULL,
            updated_at REAL NOT NULL
        )
        """
    )
    conn.commit()
    return conn


def save_session(session_id: str, state: SeriesState) -> None:
    """Save a SeriesState instance to both memory cache and SQLite."""
    if not session_id:
        return
    now = time.time()
    data_str = state.model_dump_json()
    with _LOCK:
        _MEM_CACHE[session_id] = (now, state)
        try:
            conn = _get_conn()
            conn.execute(
                """
                INSERT INTO sessions (session_id, data_json, updated_at)
                VALUES (?, ?, ?)
                ON CONFLICT(session_id) DO UPDATE SET
                    data_json = excluded.data_json,
                    updated_at = excluded.updated_at
                """,
                (session_id, data_str, now),
            )
            conn.commit()
            conn.close()
        except Exception:
            pass


def get_session(session_id: str) -> Optional[SeriesState]:
    """Retrieve a SeriesState by ID from cache or SQLite."""
    if not session_id:
        return None
    with _LOCK:
        if session_id in _MEM_CACHE:
            _, state = _MEM_CACHE[session_id]
            return state

        try:
            conn = _get_conn()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT data_json FROM sessions WHERE session_id = ?",
                (session_id,),
            )
            row = cursor.fetchone()
            conn.close()
            if row:
                data = json.loads(row[0])
                state = SeriesState.model_validate(data)
                _MEM_CACHE[session_id] = (time.time(), state)
                return state
        except Exception:
            return None
    return None


def delete_session(session_id: str) -> bool:
    """Delete a session from cache and database."""
    with _LOCK:
        _MEM_CACHE.pop(session_id, None)
        try:
            conn = _get_conn()
            conn.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
            conn.commit()
            conn.close()
            return True
        except Exception:
            return False


def list_sessions(limit: int = 20) -> list[dict[str, str]]:
    """List recent sessions for diagnostics and UI recovery."""
    out = []
    try:
        conn = _get_conn()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT session_id, data_json, updated_at FROM sessions ORDER BY updated_at DESC LIMIT ?",
            (limit,),
        )
        rows = cursor.fetchall()
        conn.close()
        for sid, d_json, u_at in rows:
            try:
                d = json.loads(d_json)
                out.append({
                    "session_id": sid,
                    "title": d.get("title", "Untitled"),
                    "genre": d.get("genre", ""),
                    "status": d.get("status", "draft"),
                    "updated_at": str(u_at),
                })
            except Exception:
                continue
    except Exception:
        pass
    return out
