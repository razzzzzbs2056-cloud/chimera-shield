"""Append-only records (decisions, fills, events) and atomically saved runtime state."""

from __future__ import annotations

import json
import os
from dataclasses import asdict
from pathlib import Path

from trader.risk.engine import Account
from trader.types import Position


class Journal:
    def __init__(self, root: Path | None):
        self.root = Path(root) if root else None
        self.mem: dict[str, list[dict]] = {"decisions": [], "fills": [], "trades": [], "events": []}
        if self.root:
            self.root.mkdir(parents=True, exist_ok=True)

    def write(self, stream: str, rec: dict) -> None:
        if self.root is None:
            self.mem[stream].append(rec)
            return
        with (self.root / f"{stream}.jsonl").open("a") as f:
            f.write(json.dumps(rec, separators=(",", ":"), default=str) + "\n")

    def read(self, stream: str) -> list[dict]:
        if self.root is None:
            return list(self.mem[stream])
        p = self.root / f"{stream}.jsonl"
        if not p.exists():
            return []
        return [json.loads(x) for x in p.read_text().splitlines() if x.strip()]


def save_state(path: Path, account: Account, extra: dict) -> None:
    data = {
        "account": {
            "balance": account.balance, "peak_equity": account.peak_equity, "day": account.day,
            "day_start_equity": account.day_start_equity, "kill_latched": account.kill_latched,
            "kill_reason": account.kill_reason,
            "positions": {s: asdict(p) for s, p in account.positions.items()},
        },
        **extra,
    }
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, indent=2))
    os.replace(tmp, path)  # atomic: a crash never leaves a half-written state file


def load_state(path: Path) -> tuple[Account, dict] | None:
    if not path.exists():
        return None
    data = json.loads(path.read_text())
    a = data.pop("account")
    acct = Account(
        balance=a["balance"], peak_equity=a["peak_equity"], day=a["day"],
        day_start_equity=a["day_start_equity"], kill_latched=a["kill_latched"],
        kill_reason=a.get("kill_reason", ""),
        positions={s: Position(**p) for s, p in a["positions"].items()},
    )
    return acct, data
