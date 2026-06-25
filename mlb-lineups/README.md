# ⚾ MLB Lineups + Player Stats CLI

A tiny, dependency-light CLI over the public [MLB Stats API](https://statsapi.mlb.com)
(`statsapi.mlb.com`). No API key required.

## Install

```bash
cd mlb-lineups
pip install -r requirements.txt
```

## Usage

```bash
python fetch_lineups.py                      # today's slate (times in ET)
python fetch_lineups.py --date 2026-06-25    # a specific day's slate
python fetch_lineups.py --player "Aaron Judge"
python fetch_lineups.py --player "Seth Lugo" --season 2025
```

### Slate output

For each game on the day it prints the matchup, start time, status, venue,
probable starting pitchers, and the batting-order lineups **once they're posted**
(lineups typically appear an hour or two before first pitch — until then you'll
see `Lineups not yet posted.`).

### Player output

Looks the player up by name and prints their season line:

- **Hitters** — G, AVG, OBP, SLG, OPS, HR, RBI, H, R, SB, BB, SO
- **Pitchers** — G, GS, W-L, ERA, WHIP, IP, SO, BB, SV, HR

Two-way players (e.g. Shohei Ohtani) show whichever groups have stats for the
requested season.

## Options

| Flag | Default | Description |
|---|---|---|
| `--player NAME` | — | Show a player's season stats instead of the slate |
| `--date YYYY-MM-DD` | today | Slate date |
| `--season YEAR` | current year | Season for `--player` stats |
