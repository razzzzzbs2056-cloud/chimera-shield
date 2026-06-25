"""MLB Stats API client with caching."""

import requests
import streamlit as st
from datetime import datetime
from functools import lru_cache

MLB_API = "https://statsapi.mlb.com/api/v1"


@st.cache_data(ttl=3600)
def search_player(name: str) -> list:
    """Search for players by name. Returns list of matches."""
    try:
        url = f"{MLB_API}/people/search?names={name}"
        resp = requests.get(url, timeout=10).json()
        results = []
        for p in resp.get("people", []):
            results.append({
                "id": p["id"],
                "name": p["fullName"],
                "team": p.get("currentTeam", {}).get("abbreviation", ""),
                "position": p.get("primaryPosition", {}).get("abbreviation", ""),
                "bat_side": p.get("batSide", {}).get("code", "?"),
            })
        return results
    except Exception as e:
        st.error(f"Search failed: {e}")
        return []


@st.cache_data(ttl=3600)
def get_player_info(player_id: int) -> dict:
    """Get detailed player info."""
    try:
        url = f"{MLB_API}/people/{player_id}"
        resp = requests.get(url, timeout=10).json()
        p = resp["people"][0]
        return {
            "id": p["id"],
            "name": p["fullName"],
            "bat_side": p.get("batSide", {}).get("description", "Right"),
            "throw_side": p.get("pitchHand", {}).get("description", ""),
            "position": p.get("primaryPosition", {}).get("abbreviation", ""),
            "team_id": p.get("currentTeam", {}).get("id"),
            "team_name": p.get("currentTeam", {}).get("name", ""),
            "team_abbr": p.get("currentTeam", {}).get("abbreviation", ""),
            "age": p.get("currentAge", 0),
            "height": p.get("height", ""),
            "weight": p.get("weight", 0),
            "jersey": p.get("primaryNumber", ""),
        }
    except Exception:
        return {}


@st.cache_data(ttl=1800)
def get_batter_season_stats(player_id: int, season: int = None) -> dict:
    """Get season hitting stats."""
    if season is None:
        season = datetime.now().year
    try:
        url = (f"{MLB_API}/people/{player_id}/stats"
               f"?stats=season&group=hitting&season={season}")
        resp = requests.get(url, timeout=10).json()
        s = resp["stats"][0]["splits"][0]["stat"]
        ab = max(int(s.get("atBats", 1)), 1)
        pa = max(int(s.get("plateAppearances", 1)), 1)
        return {
            "games": int(s.get("gamesPlayed", 0)),
            "ab": ab,
            "pa": pa,
            "hits": int(s.get("hits", 0)),
            "avg": float(s.get("avg", 0)),
            "obp": float(s.get("obp", 0)),
            "slg": float(s.get("slg", 0)),
            "ops": float(s.get("ops", 0)),
            "hr": int(s.get("homeRuns", 0)),
            "rbi": int(s.get("rbi", 0)),
            "runs": int(s.get("runs", 0)),
            "sb": int(s.get("stolenBases", 0)),
            "bb": int(s.get("baseOnBalls", 0)),
            "so": int(s.get("strikeOuts", 0)),
            "iso": float(s.get("slg", 0)) - float(s.get("avg", 0)),
            "k_pct": int(s.get("strikeOuts", 0)) / pa,
            "bb_pct": int(s.get("baseOnBalls", 0)) / pa,
            "babip": float(s.get("babip", 0)),
        }
    except Exception:
        return {}


@st.cache_data(ttl=1800)
def get_batter_splits(player_id: int, season: int = None) -> dict:
    """Get vs LHP / vs RHP splits."""
    if season is None:
        season = datetime.now().year
    try:
        url = (f"{MLB_API}/people/{player_id}/stats"
               f"?stats=split&group=hitting&season={season}"
               f"&splits=vs_lhp,vs_rhp")
        resp = requests.get(url, timeout=10).json()
        splits = {"vs_lhp": {}, "vs_rhp": {}}
        for split in resp.get("stats", [{}])[0].get("splits", []):
            split_type = split.get("split", {}).get("code", "")
            stat = split.get("stat", {})
            key = "vs_lhp" if "lhp" in split_type else "vs_rhp"
            splits[key] = {
                "avg": float(stat.get("avg", 0)),
                "obp": float(stat.get("obp", 0)),
                "slg": float(stat.get("slg", 0)),
                "ops": float(stat.get("ops", 0)),
                "hr": int(stat.get("homeRuns", 0)),
                "ab": int(stat.get("atBats", 0)),
            }
        return splits
    except Exception:
        return {"vs_lhp": {}, "vs_rhp": {}}


@st.cache_data(ttl=1800)
def get_pitcher_season_stats(player_id: int, season: int = None) -> dict:
    """Get season pitching stats."""
    if season is None:
        season = datetime.now().year
    try:
        url = (f"{MLB_API}/people/{player_id}/stats"
               f"?stats=season&group=pitching&season={season}")
        resp = requests.get(url, timeout=10).json()
        s = resp["stats"][0]["splits"][0]["stat"]
        ip = max(float(s.get("inningsPitched", 1)), 1)
        bf = max(int(s.get("battersFaced", 1)), 1)
        go = int(s.get("groundOuts", 0))
        ao = int(s.get("airOuts", 0))
        total_outs = max(go + ao, 1)
        return {
            "era": float(s.get("era", 4.00)),
            "whip": float(s.get("whip", 1.30)),
            "ip": ip,
            "k": int(s.get("strikeOuts", 0)),
            "bb": int(s.get("baseOnBalls", 0)),
            "hr": int(s.get("homeRuns", 0)),
            "k_pct": int(s.get("strikeOuts", 0)) / bf,
            "bb_pct": int(s.get("baseOnBalls", 0)) / bf,
            "hr_9": (int(s.get("homeRuns", 0)) / ip) * 9,
            "k_9": (int(s.get("strikeOuts", 0)) / ip) * 9,
            "gb_pct": go / total_outs,
            "fb_pct": ao / total_outs,
            "games_started": int(s.get("gamesStarted", 0)),
        }
    except Exception:
        return {}


@st.cache_data(ttl=1800)
def get_today_schedule(date_str: str = None) -> list:
    """Get today's MLB schedule."""
    if date_str is None:
        date_str = datetime.now().strftime("%Y-%m-%d")
    try:
        url = (f"{MLB_API}/schedule?sportId=1&date={date_str}"
               f"&hydrate=probablePitcher,venue,team")
        resp = requests.get(url, timeout=10).json()
        games = []
        for game in resp.get("dates", [{}])[0].get("games", []):
            g = {
                "gamePk": game["gamePk"],
                "status": game.get("status", {}).get("detailedState", ""),
                "gameTime": game.get("gameDate", ""),
                "venue": game.get("venue", {}).get("name", ""),
                "away": {
                    "name": game["teams"]["away"]["team"]["name"],
                    "abbr": game["teams"]["away"]["team"].get("abbreviation", ""),
                    "probable_pitcher": game["teams"]["away"].get(
                        "probablePitcher", {}).get("fullName", "TBD"),
                    "probable_pitcher_id": game["teams"]["away"].get(
                        "probablePitcher", {}).get("id"),
                },
                "home": {
                    "name": game["teams"]["home"]["team"]["name"],
                    "abbr": game["teams"]["home"]["team"].get("abbreviation", ""),
                    "probable_pitcher": game["teams"]["home"].get(
                        "probablePitcher", {}).get("fullName", "TBD"),
                    "probable_pitcher_id": game["teams"]["home"].get(
                        "probablePitcher", {}).get("id"),
                },
            }
            games.append(g)
        return games
    except Exception:
        return []
