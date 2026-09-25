"""SQLite ledger: every bet, every result, bankroll, and team ratings."""
from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from .odds import closing_line_value

DEFAULT_DB = Path(__file__).parent / "data" / "ledger.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS bets (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    placed_at     TEXT NOT NULL,
    mode          TEXT NOT NULL DEFAULT 'paper',
    kind          TEXT NOT NULL,
    arb_group     TEXT,
    game_id       TEXT NOT NULL,
    sport         TEXT NOT NULL,
    event         TEXT NOT NULL,
    commence_time TEXT NOT NULL,
    market        TEXT NOT NULL,
    line_key      TEXT NOT NULL,
    selection     TEXT NOT NULL,
    point         REAL,
    book          TEXT NOT NULL,
    price         REAL NOT NULL,
    stake         REAL NOT NULL,
    fair_prob     REAL NOT NULL,
    edge          REAL NOT NULL,
    closing_price REAL,
    status        TEXT NOT NULL DEFAULT 'open',
    payout        REAL,
    settled_at    TEXT,
    notes         TEXT
);
CREATE UNIQUE INDEX IF NOT EXISTS uniq_bet
    ON bets (game_id, line_key, selection, book, kind);
CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS ratings (
    sport TEXT NOT NULL, team TEXT NOT NULL, rating REAL NOT NULL, games INTEGER NOT NULL,
    PRIMARY KEY (sport, team)
);
CREATE TABLE IF NOT EXISTS processed_results (game_id TEXT PRIMARY KEY);
"""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class Ledger:
    def __init__(self, path: str | Path = DEFAULT_DB):
        self.path = str(path)
        if self.path != ":memory:":
            Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(self.path)
        self.db.row_factory = sqlite3.Row
        self.db.executescript(SCHEMA)

    # ------------------------------------------------------------ bankroll
    def get_setting(self, key: str, default: Optional[str] = None) -> Optional[str]:
        row = self.db.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
        return row["value"] if row else default

    def set_setting(self, key: str, value) -> None:
        self.db.execute("INSERT INTO settings(key,value) VALUES(?,?) "
                        "ON CONFLICT(key) DO UPDATE SET value=excluded.value", (key, str(value)))
        self.db.commit()

    @property
    def starting_bankroll(self) -> float:
        return float(self.get_setting("bankroll", "1000"))

    def bankroll(self) -> float:
        """Starting bankroll + realised P&L - money tied up in open bets."""
        row = self.db.execute(
            "SELECT COALESCE(SUM(CASE WHEN status='open' THEN -stake ELSE payout - stake END),0) AS d "
            "FROM bets").fetchone()
        return self.starting_bankroll + row["d"]

    def pnl_today(self) -> float:
        today = datetime.now(timezone.utc).date().isoformat()
        row = self.db.execute(
            "SELECT COALESCE(SUM(payout - stake),0) AS p FROM bets "
            "WHERE status!='open' AND substr(settled_at,1,10)=?", (today,)).fetchone()
        return row["p"]

    # ------------------------------------------------------------ bets
    def record(self, opp, mode: str = "paper") -> Optional[int]:
        """Insert a bet; returns row id, or None if an identical bet already exists."""
        cur = self.db.execute(
            """INSERT OR IGNORE INTO bets (placed_at, mode, kind, arb_group, game_id, sport, event,
               commence_time, market, line_key, selection, point, book, price, stake, fair_prob,
               edge, notes) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (_now(), mode, opp.kind, opp.group, opp.game.id, opp.game.sport, opp.game.label,
             opp.game.commence_time, opp.market, opp.line_key, opp.selection, opp.point,
             opp.book, opp.price, round(opp.stake, 2), opp.fair_prob, opp.edge, opp.notes))
        self.db.commit()
        return cur.lastrowid if cur.rowcount else None

    def has_bet(self, opp) -> bool:
        return self.db.execute(
            "SELECT 1 FROM bets WHERE game_id=? AND line_key=? AND selection=? AND book=? AND kind=?",
            (opp.game.id, opp.line_key, opp.selection, opp.book, opp.kind)).fetchone() is not None

    def open_bets(self) -> list[sqlite3.Row]:
        return self.db.execute("SELECT * FROM bets WHERE status='open' ORDER BY commence_time").fetchall()

    def bets(self, status: Optional[str] = None, limit: int = 200) -> list[sqlite3.Row]:
        if status:
            return self.db.execute("SELECT * FROM bets WHERE status=? ORDER BY id DESC LIMIT ?",
                                   (status, limit)).fetchall()
        return self.db.execute("SELECT * FROM bets ORDER BY id DESC LIMIT ?", (limit,)).fetchall()

    def exposure(self, game_id: str) -> float:
        row = self.db.execute("SELECT COALESCE(SUM(stake),0) AS s FROM bets "
                              "WHERE status='open' AND game_id=?", (game_id,)).fetchone()
        return row["s"]

    def update_closing(self, bet_id: int, price: float) -> None:
        self.db.execute("UPDATE bets SET closing_price=? WHERE id=?", (price, bet_id))
        self.db.commit()

    def settle(self, bet_id: int, status: str) -> None:
        row = self.db.execute("SELECT stake, price FROM bets WHERE id=?", (bet_id,)).fetchone()
        payout = {"won": row["stake"] * row["price"], "lost": 0.0,
                  "push": row["stake"], "void": row["stake"]}[status]
        self.db.execute("UPDATE bets SET status=?, payout=?, settled_at=? WHERE id=?",
                        (status, round(payout, 2), _now(), bet_id))
        self.db.commit()

    # ------------------------------------------------------------ ratings
    def ratings(self, sport: str) -> dict[str, float]:
        rows = self.db.execute("SELECT team, rating FROM ratings WHERE sport=?", (sport,)).fetchall()
        return {r["team"]: r["rating"] for r in rows}

    def rating_games(self, sport: str, team: str) -> int:
        row = self.db.execute("SELECT games FROM ratings WHERE sport=? AND team=?",
                              (sport, team)).fetchone()
        return row["games"] if row else 0

    def set_rating(self, sport: str, team: str, rating: float) -> None:
        self.db.execute("INSERT INTO ratings(sport,team,rating,games) VALUES(?,?,?,1) "
                        "ON CONFLICT(sport,team) DO UPDATE SET rating=excluded.rating, games=games+1",
                        (sport, team, rating))
        self.db.commit()

    def result_processed(self, game_id: str) -> bool:
        return self.db.execute("SELECT 1 FROM processed_results WHERE game_id=?",
                               (game_id,)).fetchone() is not None

    def mark_result_processed(self, game_id: str) -> None:
        self.db.execute("INSERT OR IGNORE INTO processed_results(game_id) VALUES(?)", (game_id,))
        self.db.commit()

    # ------------------------------------------------------------ reporting
    def report(self) -> dict:
        settled = self.db.execute("SELECT * FROM bets WHERE status IN ('won','lost','push')").fetchall()
        open_ = self.open_bets()
        staked = sum(b["stake"] for b in settled)
        profit = sum(b["payout"] - b["stake"] for b in settled)
        wins = sum(1 for b in settled if b["status"] == "won")
        decided = sum(1 for b in settled if b["status"] in ("won", "lost"))
        clvs = [closing_line_value(b["price"], b["closing_price"])
                for b in self.db.execute("SELECT price, closing_price FROM bets "
                                         "WHERE closing_price IS NOT NULL").fetchall()]

        def breakdown(col: str) -> dict:
            out: dict = {}
            for b in settled:
                d = out.setdefault(b[col], {"bets": 0, "staked": 0.0, "profit": 0.0})
                d["bets"] += 1
                d["staked"] += b["stake"]
                d["profit"] += b["payout"] - b["stake"]
            for d in out.values():
                d["roi"] = d["profit"] / d["staked"] if d["staked"] else 0.0
            return out

        return {
            "starting_bankroll": self.starting_bankroll,
            "bankroll": round(self.bankroll(), 2),
            "open_bets": len(open_),
            "open_stake": round(sum(b["stake"] for b in open_), 2),
            "expected_profit_open": round(sum(b["stake"] * b["edge"] for b in open_), 2),
            "settled_bets": len(settled),
            "staked": round(staked, 2),
            "profit": round(profit, 2),
            "roi": profit / staked if staked else 0.0,
            "win_rate": wins / decided if decided else 0.0,
            "avg_clv": sum(clvs) / len(clvs) if clvs else None,
            "by_sport": breakdown("sport"),
            "by_book": breakdown("book"),
            "by_kind": breakdown("kind"),
            "by_market": breakdown("market"),
        }
