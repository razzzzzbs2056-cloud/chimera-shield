"""Thin client for the public MLB Stats API (statsapi.mlb.com).

No API key required. Results are cached in-process so a Streamlit rerun
doesn't hammer the API.
"""

from __future__ import annotations

import datetime as dt
from functools import lru_cache
from typing import Any, Optional

import requests

BASE = "https://statsapi.mlb.com/api/v1"
TIMEOUT = 15


def _get(path: str, **params: Any) -> dict:
    url = f"{BASE}/{path.lstrip('/')}"
    resp = requests.get(url, params=params, timeout=TIMEOUT)
    resp.raise_for_status()
    return resp.json()


@lru_cache(maxsize=64)
def schedule(date: str) -> list[dict]:
    """Games for a given YYYY-MM-DD date, with probable pitchers."""
    data = _get(
        "schedule",
        sportId=1,
        date=date,
        hydrate="probablePitcher,team",
    )
    dates = data.get("dates", [])
    return dates[0]["games"] if dates else []


@lru_cache(maxsize=256)
def search_player(name: str) -> tuple[dict, ...]:
    """Return candidate people matching a name (exact match floated first)."""
    data = _get("people/search", names=name)
    people = data.get("people", [])
    people.sort(key=lambda p: p.get("fullName", "").lower() != name.lower())
    return tuple(people)


@lru_cache(maxsize=256)
def player_stats(player_id: int, season: int) -> dict:
    """Full person record hydrated with season hitting + pitching splits."""
    data = _get(
        f"people/{player_id}",
        hydrate=(
            f"currentTeam,stats(group=[hitting,pitching],type=[season],"
            f"season={season},sportId=1)"
        ),
    )
    return data["people"][0]


def season_split(person: dict, group: str) -> Optional[dict]:
    """Pull the season stat dict for 'hitting' or 'pitching', or None."""
    for block in person.get("stats", []):
        if (block.get("group") or {}).get("displayName") != group:
            continue
        splits = block.get("splits") or []
        if splits:
            return splits[0].get("stat", {})
    return None


def today() -> str:
    return dt.date.today().isoformat()
