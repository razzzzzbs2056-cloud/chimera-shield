# ⚾ MLB Starting Lineups & Player Stats

A small command-line script that pulls the daily schedule, **starting lineups**,
and **season player stats** from the free **MLB Stats API**.

## Which package?

This uses **[`MLB-StatsAPI`](https://pypi.org/project/MLB-StatsAPI/)**
(`import statsapi`) — an actively maintained wrapper around the official
`statsapi.mlb.com` endpoints.

> ℹ️ **Not `mlbgame`.** The older `mlbgame` package is unmaintained and breaks
> against the current MLB API, so it's intentionally avoided here.

The MLB Stats API is free and requires no key.

## Install

```bash
# From the mlb-lineups/ directory:
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Usage

```bash
# Today's slate (games + probable pitchers)
python fetch_lineups.py

# A specific date
python fetch_lineups.py --date 06/25/2026

# Full lineups + per-batter season stats + probable pitcher stats for one game
python fetch_lineups.py --game 776543

# Every game's lineups for the date (verbose)
python fetch_lineups.py --all

# Look up a single player's season hitting/pitching stats
python fetch_lineups.py --player "Aaron Judge"
```

## What it pulls

| Function | Source |
|----------|--------|
| Daily schedule + probable pitchers | `statsapi.schedule()` |
| Starting lineups (batting order, position) | `statsapi.boxscore_data()` → `battingOrder` |
| Per-batter season stats (AVG/OPS/HR/RBI) | boxscore `seasonStats` |
| Player / pitcher season stats | `statsapi.lookup_player()` + `statsapi.player_stat_data()` |

## Notes

- **Lineups post a few hours before first pitch.** Earlier than that, the script
  shows the matchup and probable pitchers and notes that lineups aren't posted.
- Game times are rendered in US/Eastern (best effort via stdlib `zoneinfo`).
- Pure standard library otherwise — the only dependency is `MLB-StatsAPI`.
