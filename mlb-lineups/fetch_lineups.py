#!/usr/bin/env python3
"""Lineups + player stats CLI backed by the public MLB Stats API.

Examples
--------
    python fetch_lineups.py                      # today's slate
    python fetch_lineups.py --date 2026-06-25    # a specific day
    python fetch_lineups.py --player "Aaron Judge"
    python fetch_lineups.py --player "Seth Lugo" --season 2025

No API key is required; statsapi.mlb.com is a free, public endpoint.
"""

from __future__ import annotations

import argparse
import datetime as dt
import sys
from typing import Any, Optional

import requests

try:  # stdlib on Python 3.9+, used only for prettier game times
    from zoneinfo import ZoneInfo

    _ET = ZoneInfo("America/New_York")
except Exception:  # pragma: no cover - zoneinfo always present on 3.9+
    _ET = None

BASE = "https://statsapi.mlb.com/api/v1"
TIMEOUT = 15

# ---------------------------------------------------------------------------
# HTTP helper
# ---------------------------------------------------------------------------


def get_json(path: str, **params: Any) -> dict:
    """GET a Stats API path and return parsed JSON, or exit with a message."""
    url = f"{BASE}/{path.lstrip('/')}"
    try:
        resp = requests.get(url, params=params, timeout=TIMEOUT)
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as exc:
        sys.exit(f"error: request to MLB Stats API failed: {exc}")
    except ValueError:
        sys.exit("error: MLB Stats API returned a non-JSON response")


# ---------------------------------------------------------------------------
# Today's slate / lineups
# ---------------------------------------------------------------------------


def _fmt_game_time(iso: Optional[str]) -> str:
    if not iso:
        return "TBD"
    try:
        utc = dt.datetime.fromisoformat(iso.replace("Z", "+00:00"))
    except ValueError:
        return iso
    if _ET is not None:
        return utc.astimezone(_ET).strftime("%-I:%M %p ET")
    return utc.strftime("%H:%M UTC")


def _probable(side: dict) -> str:
    pp = side.get("probablePitcher") or {}
    return pp.get("fullName") or "TBD"


def _print_lineup(label: str, players: list[dict]) -> None:
    if not players:
        return
    print(f"    {label}:")
    for i, p in enumerate(players, start=1):
        pos = (p.get("primaryPosition") or {}).get("abbreviation", "")
        name = p.get("fullName", "?")
        print(f"      {i}. {name:<22} {pos}")


def show_slate(date: str) -> None:
    data = get_json(
        "schedule",
        sportId=1,
        date=date,
        hydrate="probablePitcher,lineups,team",
    )

    dates = data.get("dates", [])
    games = dates[0]["games"] if dates else []

    pretty = date
    try:
        pretty = dt.date.fromisoformat(date).strftime("%A, %B %-d, %Y")
    except ValueError:
        pass

    header = f"  MLB — {pretty}  ({len(games)} game{'s' if len(games) != 1 else ''})  "
    print("\n" + "=" * len(header))
    print(header)
    print("=" * len(header))

    if not games:
        print("\n  No games scheduled.\n")
        return

    for g in games:
        away = g["teams"]["away"]
        home = g["teams"]["home"]
        status = (g.get("status") or {}).get("detailedState", "")
        line = g.get("linescore") or {}

        away_name = away["team"]["name"]
        home_name = home["team"]["name"]

        print(f"\n  {away_name} @ {home_name}")
        venue = (g.get("venue") or {}).get("name")
        meta = f"    {_fmt_game_time(g.get('gameDate'))} · {status}"
        if venue:
            meta += f" · {venue}"
        print(meta)
        print(f"    Probable: {_probable(away)}  vs  {_probable(home)}")

        lineups = g.get("lineups") or {}
        away_lu = lineups.get("awayPlayers") or []
        home_lu = lineups.get("homePlayers") or []
        if away_lu or home_lu:
            _print_lineup(f"{away_name} lineup", away_lu)
            _print_lineup(f"{home_name} lineup", home_lu)
        else:
            print("    Lineups not yet posted.")
    print()


# ---------------------------------------------------------------------------
# Player stats
# ---------------------------------------------------------------------------


def find_player(name: str) -> Optional[dict]:
    data = get_json("people/search", names=name)
    people = data.get("people", [])
    if not people:
        return None
    # Prefer an exact (case-insensitive) full-name match, else first result.
    for p in people:
        if p.get("fullName", "").lower() == name.lower():
            return p
    return people[0]


def _hitting_table(stat: dict) -> list[tuple[str, Any]]:
    return [
        ("G", stat.get("gamesPlayed")),
        ("AVG", stat.get("avg")),
        ("OBP", stat.get("obp")),
        ("SLG", stat.get("slg")),
        ("OPS", stat.get("ops")),
        ("HR", stat.get("homeRuns")),
        ("RBI", stat.get("rbi")),
        ("H", stat.get("hits")),
        ("R", stat.get("runs")),
        ("SB", stat.get("stolenBases")),
        ("BB", stat.get("baseOnBalls")),
        ("SO", stat.get("strikeOuts")),
    ]


def _pitching_table(stat: dict) -> list[tuple[str, Any]]:
    return [
        ("G", stat.get("gamesPlayed")),
        ("GS", stat.get("gamesStarted")),
        ("W-L", f"{stat.get('wins', 0)}-{stat.get('losses', 0)}"),
        ("ERA", stat.get("era")),
        ("WHIP", stat.get("whip")),
        ("IP", stat.get("inningsPitched")),
        ("SO", stat.get("strikeOuts")),
        ("BB", stat.get("baseOnBalls")),
        ("SV", stat.get("saves")),
        ("HR", stat.get("homeRuns")),
    ]


def _print_stat_block(title: str, rows: list[tuple[str, Any]]) -> None:
    cells = [(k, "—" if v is None else str(v)) for k, v in rows]
    widths = [max(len(k), len(v)) for k, v in cells]
    keys = "  ".join(k.ljust(w) for (k, _), w in zip(cells, widths))
    vals = "  ".join(v.ljust(w) for (_, v), w in zip(cells, widths))
    print(f"    {title}")
    print(f"      {keys}")
    print(f"      {vals}")


def show_player(name: str, season: int) -> None:
    player = find_player(name)
    if not player:
        sys.exit(f"error: no player found matching {name!r}")

    pid = player["id"]
    full = get_json(
        f"people/{pid}",
        hydrate=(
            f"currentTeam,stats(group=[hitting,pitching],type=[season],"
            f"season={season},sportId=1)"
        ),
    )
    p = full["people"][0]

    pos = (p.get("primaryPosition") or {}).get("abbreviation", "")
    team = (p.get("currentTeam") or {}).get("name", "Free agent")
    num = p.get("primaryNumber")
    bats = (p.get("batSide") or {}).get("code", "?")
    throws = (p.get("pitchHand") or {}).get("code", "?")
    age = p.get("currentAge")

    header = f"  {p['fullName']}"
    if num:
        header += f"  #{num}"
    print("\n" + "=" * max(40, len(header) + 2))
    print(header)
    print("=" * max(40, len(header) + 2))
    print(f"  {pos} · {team}")
    print(f"  Bats: {bats}  Throws: {throws}  Age: {age}")
    print(f"  {season} season stats:")

    printed = False
    for block in p.get("stats", []):
        splits = block.get("splits") or []
        if not splits:
            continue
        stat = splits[0].get("stat", {})
        group = (block.get("group") or {}).get("displayName", "")
        if group == "hitting":
            _print_stat_block("Hitting", _hitting_table(stat))
            printed = True
        elif group == "pitching":
            _print_stat_block("Pitching", _pitching_table(stat))
            printed = True

    if not printed:
        print(f"    No {season} regular-season stats available.")
    print()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main(argv: Optional[list[str]] = None) -> None:
    parser = argparse.ArgumentParser(
        description="MLB lineups for the day + player season stats.",
    )
    parser.add_argument(
        "--player",
        metavar="NAME",
        help="show season stats for a player instead of the day's slate",
    )
    parser.add_argument(
        "--date",
        default=dt.date.today().isoformat(),
        help="slate date as YYYY-MM-DD (default: today)",
    )
    parser.add_argument(
        "--season",
        type=int,
        default=dt.date.today().year,
        help="season year for --player stats (default: current year)",
    )
    args = parser.parse_args(argv)

    if args.player:
        show_player(args.player, args.season)
    else:
        show_slate(args.date)


if __name__ == "__main__":
    main()
