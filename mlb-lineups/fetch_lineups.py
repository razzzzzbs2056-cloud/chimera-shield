#!/usr/bin/env python3
"""
⚾ MLB Starting Lineups & Player Stats
======================================

Pulls the daily schedule, starting lineups, and season player stats from the
free MLB Stats API via the `MLB-StatsAPI` package (`import statsapi`).

Examples
--------
    # Today's slate (games + probable pitchers)
    python fetch_lineups.py

    # A specific date (MM/DD/YYYY)
    python fetch_lineups.py --date 06/25/2026

    # Full lineups + per-batter season stats + probable pitcher stats for one game
    python fetch_lineups.py --game 776543

    # Every game's lineups for the date (verbose)
    python fetch_lineups.py --all

    # Look up a single player's season stats
    python fetch_lineups.py --player "Aaron Judge"

Notes
-----
Starting lineups are typically posted by the MLB Stats API a few hours before
first pitch. Before that, this script shows the matchup and probable pitchers and
reports that lineups are not yet available.
"""

from __future__ import annotations

import argparse
import datetime as dt
import sys

try:
    import statsapi
except ImportError:
    sys.exit(
        "The 'MLB-StatsAPI' package is required.\n"
        "Install it with:  pip install -r requirements.txt\n"
        "(or:  pip install MLB-StatsAPI)"
    )


# ─────────────────────────────────────────────────────────────────────────────
# Schedule
# ─────────────────────────────────────────────────────────────────────────────
def get_games(date_str: str) -> list[dict]:
    """Return the list of MLB games for a date (MM/DD/YYYY)."""
    try:
        return statsapi.schedule(date=date_str, sportId=1)
    except Exception as exc:  # network / API failure
        sys.exit(f"Failed to fetch schedule for {date_str}: {exc}")


def print_slate(games: list[dict]) -> None:
    """Print a one-line summary per game."""
    if not games:
        print("No MLB games scheduled for this date.")
        return

    print(f"\n{len(games)} game(s):\n")
    header = f"{'GamePk':>8}  {'Time':<9}  {'Matchup':<33}  Probable pitchers"
    print(header)
    print("-" * len(header))
    for g in games:
        time = _local_time(g.get("game_datetime", ""))
        matchup = f"{g.get('away_name', '?')} @ {g.get('home_name', '?')}"
        sp = (
            f"{g.get('away_probable_pitcher') or 'TBD'} vs "
            f"{g.get('home_probable_pitcher') or 'TBD'}"
        )
        print(f"{g.get('game_id', ''):>8}  {time:<9}  {matchup:<33.33}  {sp}")
    print()


def _local_time(iso_utc: str) -> str:
    """Render the API's ISO time as Eastern wall-clock (best effort)."""
    if not iso_utc:
        return "TBD"
    try:
        from zoneinfo import ZoneInfo

        utc = dt.datetime.fromisoformat(iso_utc.replace("Z", "+00:00"))
        return utc.astimezone(ZoneInfo("America/New_York")).strftime("%-I:%M%p")
    except Exception:
        return "TBD"


# ─────────────────────────────────────────────────────────────────────────────
# Lineups + batter stats
# ─────────────────────────────────────────────────────────────────────────────
def get_lineups(game_id: int) -> dict:
    """Return starting lineups for a game from the boxscore.

    Shape:
        {
          "away": {"team": str, "starters": [ {order, name, pos, stats}, ... ]},
          "home": {...},
        }
    `starters` is empty if lineups are not yet posted.
    """
    box = statsapi.boxscore_data(game_id)
    info = box.get("teamInfo", {})
    result: dict = {}

    for side in ("away", "home"):
        team_name = info.get(side, {}).get("teamName", side.title())
        players = box.get(side, {}).get("players", {})
        batting_order = box.get(side, {}).get("battingOrder", [])  # starter IDs

        starters = []
        for person_id in batting_order:
            p = players.get(f"ID{person_id}", {})
            season = p.get("seasonStats", {}).get("batting", {})
            starters.append(
                {
                    "order": _spot(p.get("battingOrder")),
                    "name": p.get("person", {}).get("fullName", "Unknown"),
                    "pos": p.get("position", {}).get("abbreviation", ""),
                    "avg": season.get("avg", "—"),
                    "ops": season.get("ops", "—"),
                    "hr": season.get("homeRuns", "—"),
                    "rbi": season.get("rbi", "—"),
                }
            )
        result[side] = {"team": team_name, "starters": starters}

    return result


def _spot(batting_order: str | None) -> int:
    """Convert a battingOrder code like '300' to lineup spot 3."""
    try:
        return int(batting_order) // 100
    except (TypeError, ValueError):
        return 0


def print_lineup_side(side: dict) -> None:
    print(f"\n  {side['team']} lineup:")
    if not side["starters"]:
        print("    (lineup not yet posted)")
        return
    print(f"    {'#':<2} {'Pos':<4} {'Player':<24} {'AVG':>5} {'OPS':>5} "
          f"{'HR':>3} {'RBI':>4}")
    for b in side["starters"]:
        print(
            f"    {b['order']:<2} {b['pos']:<4} {b['name']:<24.24} "
            f"{str(b['avg']):>5} {str(b['ops']):>5} "
            f"{str(b['hr']):>3} {str(b['rbi']):>4}"
        )


# ─────────────────────────────────────────────────────────────────────────────
# Player stats lookup
# ─────────────────────────────────────────────────────────────────────────────
def resolve_player_id(name: str) -> int | None:
    """Resolve a player name to an MLBAM person id (None on miss or API error)."""
    try:
        matches = statsapi.lookup_player(name)
    except Exception:
        return None
    return matches[0]["id"] if matches else None


def get_player_season_stats(person_id: int, group: str) -> dict:
    """Return a player's current-season stats for a group ('hitting'/'pitching')."""
    try:
        data = statsapi.player_stat_data(
            person_id, group=f"[{group}]", type="season"
        )
    except Exception:
        return {}
    for entry in data.get("stats", []):
        if entry.get("group") == group:
            return entry.get("stats", {})
    return {}


def print_player(name: str) -> None:
    pid = resolve_player_id(name)
    if not pid:
        print(f"No player found matching '{name}' (or the API was unreachable).")
        return

    try:
        data = statsapi.player_stat_data(
            pid, group="[hitting,pitching]", type="season"
        )
    except Exception as exc:
        print(f"Could not load stats for '{name}': {exc}")
        return
    print(f"\n{data.get('first_name', '')} {data.get('last_name', '')} "
          f"(#{data.get('primary_number', '?')}, "
          f"{data.get('position', '?')}) — {data.get('current_team', '')}")

    hitting = get_player_season_stats(pid, "hitting")
    if hitting:
        print("  Hitting:  "
              f"AVG {hitting.get('avg', '—')} | OBP {hitting.get('obp', '—')} | "
              f"SLG {hitting.get('slg', '—')} | OPS {hitting.get('ops', '—')} | "
              f"HR {hitting.get('homeRuns', '—')} | RBI {hitting.get('rbi', '—')} | "
              f"SB {hitting.get('stolenBases', '—')}")

    pitching = get_player_season_stats(pid, "pitching")
    if pitching:
        print("  Pitching: "
              f"W-L {pitching.get('wins', '—')}-{pitching.get('losses', '—')} | "
              f"ERA {pitching.get('era', '—')} | WHIP {pitching.get('whip', '—')} | "
              f"IP {pitching.get('inningsPitched', '—')} | "
              f"K {pitching.get('strikeOuts', '—')} | "
              f"BB {pitching.get('baseOnBalls', '—')}")

    if not hitting and not pitching:
        print("  No season stats available.")


def print_probable_pitchers(game: dict) -> None:
    print("\n  Probable pitchers:")
    for side in ("away", "home"):
        name = game.get(f"{side}_probable_pitcher")
        team = game.get(f"{side}_name", side)
        if not name:
            print(f"    {team}: TBD")
            continue
        pid = resolve_player_id(name)
        stats = get_player_season_stats(pid, "pitching") if pid else {}
        if stats:
            print(f"    {team}: {name} — "
                  f"{stats.get('wins', '—')}-{stats.get('losses', '—')}, "
                  f"ERA {stats.get('era', '—')}, WHIP {stats.get('whip', '—')}, "
                  f"K {stats.get('strikeOuts', '—')}")
        else:
            print(f"    {team}: {name} (no season pitching stats)")


# ─────────────────────────────────────────────────────────────────────────────
# Game detail
# ─────────────────────────────────────────────────────────────────────────────
def print_game_detail(game: dict) -> None:
    gid = game.get("game_id")
    print("=" * 70)
    print(f"{game.get('away_name')} @ {game.get('home_name')}  "
          f"({_local_time(game.get('game_datetime', ''))}, "
          f"{game.get('venue_name', '')})  [GamePk {gid}]")
    print(f"Status: {game.get('status', '')}")

    print_probable_pitchers(game)

    try:
        lineups = get_lineups(gid)
        for side in ("away", "home"):
            print_lineup_side(lineups[side])
    except Exception as exc:
        print(f"\n  Could not load lineups: {exc}")
    print()


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────
def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Pull MLB starting lineups and player stats "
        "from the free MLB Stats API."
    )
    parser.add_argument(
        "--date",
        default=dt.date.today().strftime("%m/%d/%Y"),
        help="Date in MM/DD/YYYY (default: today)",
    )
    parser.add_argument(
        "--game", type=int, help="GamePk to show full lineups + stats for one game"
    )
    parser.add_argument(
        "--all", action="store_true",
        help="Show full lineups for every game on the date",
    )
    parser.add_argument(
        "--player", help="Look up a single player's season stats by name"
    )
    args = parser.parse_args(argv)

    if args.player:
        print_player(args.player)
        return 0

    games = get_games(args.date)

    if args.game:
        game = next((g for g in games if g.get("game_id") == args.game), None)
        if not game:
            print(f"GamePk {args.game} not found on {args.date}.")
            return 1
        print_game_detail(game)
        return 0

    print(f"\nMLB slate for {args.date}")
    print_slate(games)

    if args.all:
        for game in games:
            print_game_detail(game)
    elif games:
        print("Tip: pass --game <GamePk> for full lineups, or --all for every game.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
