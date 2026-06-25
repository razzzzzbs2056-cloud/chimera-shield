"""MLB Stats API client for the daily game analysis app.

Public, key-free endpoints on statsapi.mlb.com. Cached in-process so Streamlit
reruns don't re-hit the API.
"""

from __future__ import annotations

import datetime as dt
from functools import lru_cache
from typing import Any, Optional

import requests

BASE = "https://statsapi.mlb.com/api/v1"
TIMEOUT = 15


def _get(path: str, **params: Any) -> dict:
    resp = requests.get(f"{BASE}/{path.lstrip('/')}", params=params, timeout=TIMEOUT)
    resp.raise_for_status()
    return resp.json()


def today() -> str:
    return dt.date.today().isoformat()


@lru_cache(maxsize=32)
def schedule(date: str) -> list[dict]:
    """Games for a date with probable pitchers, team records, and linescore."""
    data = _get(
        "schedule",
        sportId=1,
        date=date,
        hydrate="probablePitcher,team,linescore",
    )
    dates = data.get("dates", [])
    return dates[0]["games"] if dates else []


@lru_cache(maxsize=256)
def pitcher_line(player_id: int, season: int) -> Optional[dict]:
    """Season pitching stat line for a probable starter, or None."""
    if not player_id:
        return None
    data = _get(
        f"people/{player_id}",
        hydrate=f"stats(group=[pitching],type=[season],season={season},sportId=1)",
    )
    person = data["people"][0]
    for block in person.get("stats", []):
        splits = block.get("splits") or []
        if splits:
            return splits[0].get("stat", {})
    return None


def game_label(game: dict) -> str:
    away = game["teams"]["away"]["team"]["name"]
    home = game["teams"]["home"]["team"]["name"]
    status = (game.get("status") or {}).get("detailedState", "")
    return f"{away} @ {home}  ({status})"
