"""SQLite persistence. One short-lived connection per call keeps threads safe."""
import json
import sqlite3
import threading
import time
from contextlib import contextmanager

from . import config

_lock = threading.Lock()

SCHEMA = """
CREATE TABLE IF NOT EXISTS clients (
  id INTEGER PRIMARY KEY, name TEXT NOT NULL, email TEXT, package TEXT DEFAULT 'starter',
  status TEXT DEFAULT 'active', lead_id INTEGER, created_at REAL
);
CREATE TABLE IF NOT EXISTS leads (
  id INTEGER PRIMARY KEY, name TEXT NOT NULL, email TEXT, channel_url TEXT, platform TEXT,
  niche TEXT, followers INTEGER DEFAULT 0, avg_views INTEGER DEFAULT 0, uploads_per_week REAL DEFAULT 0,
  has_shorts INTEGER DEFAULT 0, fit_score INTEGER, fit_reasons TEXT, stage TEXT DEFAULT 'new',
  last_contact_at REAL, followups_sent INTEGER DEFAULT 0, notes TEXT, created_at REAL, updated_at REAL
);
CREATE TABLE IF NOT EXISTS outreach (
  id INTEGER PRIMARY KEY, lead_id INTEGER, kind TEXT, subject TEXT, body TEXT,
  status TEXT DEFAULT 'draft', created_at REAL, sent_at REAL
);
CREATE TABLE IF NOT EXISTS orders (
  id INTEGER PRIMARY KEY, client_id INTEGER, title TEXT, brief TEXT, source_path TEXT,
  transcript_path TEXT, duration REAL, width INTEGER, height INTEGER, clips_requested INTEGER,
  price_cents INTEGER, status TEXT DEFAULT 'received', error TEXT, created_at REAL, delivered_at REAL
);
CREATE TABLE IF NOT EXISTS clips (
  id INTEGER PRIMARY KEY, order_id INTEGER, start REAL, end REAL, title TEXT, hook TEXT,
  reason TEXT, score INTEGER, status TEXT DEFAULT 'planned', raw_path TEXT, final_path TEXT,
  srt_path TEXT, thumb_path TEXT, qc_report TEXT, qc_score INTEGER, attempts INTEGER DEFAULT 0,
  fix_notes TEXT, publish TEXT, review_note TEXT, created_at REAL, updated_at REAL
);
CREATE TABLE IF NOT EXISTS invoices (
  id INTEGER PRIMARY KEY, client_id INTEGER, order_id INTEGER, amount_cents INTEGER,
  status TEXT DEFAULT 'sent', created_at REAL, paid_at REAL
);
CREATE TABLE IF NOT EXISTS agents (
  name TEXT PRIMARY KEY, role TEXT, status TEXT DEFAULT 'idle', current_task TEXT,
  processed INTEGER DEFAULT 0, errors INTEGER DEFAULT 0, enabled INTEGER DEFAULT 1, updated_at REAL
);
CREATE TABLE IF NOT EXISTS events (
  id INTEGER PRIMARY KEY, ts REAL, agent TEXT, level TEXT, message TEXT,
  entity_type TEXT, entity_id INTEGER
);
"""


@contextmanager
def conn():
    with _lock:
        c = sqlite3.connect(config.DB_PATH, timeout=30)
        c.row_factory = sqlite3.Row
        try:
            yield c
            c.commit()
        finally:
            c.close()


def init():
    with conn() as c:
        c.executescript(SCHEMA)
        c.execute("PRAGMA journal_mode=WAL")


def now() -> float:
    return time.time()


def rows(sql: str, params=()) -> list[dict]:
    with conn() as c:
        return [dict(r) for r in c.execute(sql, params).fetchall()]


def row(sql: str, params=()) -> dict | None:
    r = rows(sql, params)
    return r[0] if r else None


def execute(sql: str, params=()) -> int:
    with conn() as c:
        cur = c.execute(sql, params)
        return cur.lastrowid


def insert(table: str, **fields) -> int:
    fields.setdefault("created_at", now())
    cols = ", ".join(fields)
    qs = ", ".join("?" for _ in fields)
    return execute(f"INSERT INTO {table} ({cols}) VALUES ({qs})", tuple(_enc(v) for v in fields.values()))


def update(table: str, id_: int, key: str = "id", **fields) -> None:
    if table in ("clips", "leads"):
        fields.setdefault("updated_at", now())
    sets = ", ".join(f"{k} = ?" for k in fields)
    execute(f"UPDATE {table} SET {sets} WHERE {key} = ?", (*(_enc(v) for v in fields.values()), id_))


def claim(table: str, from_status: str, to_status: str, extra_where: str = "", params=()) -> dict | None:
    """Atomically move the oldest row in `from_status` to `to_status` and return it."""
    with conn() as c:
        r = c.execute(
            f"SELECT * FROM {table} WHERE status = ? {extra_where} ORDER BY id LIMIT 1",
            (from_status, *params),
        ).fetchone()
        if not r:
            return None
        c.execute(f"UPDATE {table} SET status = ? WHERE id = ?", (to_status, r["id"]))
        d = dict(r)
        d["status"] = to_status
        return d


def _enc(v):
    return json.dumps(v) if isinstance(v, (dict, list)) else v


def log(agent: str, message: str, level: str = "info", entity_type: str | None = None, entity_id: int | None = None):
    execute(
        "INSERT INTO events (ts, agent, level, message, entity_type, entity_id) VALUES (?, ?, ?, ?, ?, ?)",
        (now(), agent, level, message, entity_type, entity_id),
    )
