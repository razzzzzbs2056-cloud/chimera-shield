"""Odds and score feeds.

* ``OddsAPIFeed`` pulls live odds/scores from https://the-odds-api.com (v4).
  Set ``ODDS_API_KEY`` in your environment.
* ``SampleFeed`` serves bundled JSON in the same format so everything works offline.
"""
from __future__ import annotations

import json
import os
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Iterable, Protocol

from .models import Game, Quote

DATA_DIR = Path(__file__).parent / "data"


class Feed(Protocol):
    def games(self, sports: Iterable[str]) -> list[Game]: ...
    def scores(self, sports: Iterable[str]) -> list[dict]: ...


def parse_events(events: list[dict]) -> list[Game]:
    """Parse The Odds API v4 ``/odds`` payload into Games."""
    games = []
    for ev in events:
        game = Game(
            id=ev["id"],
            sport=ev["sport_key"],
            commence_time=ev["commence_time"],
            home=ev["home_team"],
            away=ev["away_team"],
        )
        for bm in ev.get("bookmakers", []):
            for mk in bm.get("markets", []):
                for oc in mk.get("outcomes", []):
                    game.quotes.append(Quote(
                        book=bm["key"],
                        market=mk["key"],
                        outcome=oc["name"],
                        price=float(oc["price"]),
                        point=oc.get("point"),
                    ))
        games.append(game)
    return games


class SampleFeed:
    """Offline feed backed by ``betting/data/*.json``."""

    def __init__(self, odds_file: Path = DATA_DIR / "sample_odds.json",
                 scores_file: Path = DATA_DIR / "sample_scores.json"):
        self.odds_file = Path(odds_file)
        self.scores_file = Path(scores_file)

    def games(self, sports: Iterable[str] = ()) -> list[Game]:
        events = json.loads(self.odds_file.read_text())
        wanted = set(sports)
        return [g for g in parse_events(events) if not wanted or g.sport in wanted]

    def scores(self, sports: Iterable[str] = ()) -> list[dict]:
        rows = json.loads(self.scores_file.read_text())
        wanted = set(sports)
        return [r for r in rows if not wanted or r["sport_key"] in wanted]


class OddsAPIFeed:
    BASE = "https://api.the-odds-api.com/v4"

    def __init__(self, api_key: str | None = None, regions: str = "us,us2,eu,uk",
                 markets: str = "h2h,spreads,totals", timeout: float = 20.0):
        self.api_key = api_key or os.getenv("ODDS_API_KEY")
        if not self.api_key:
            raise RuntimeError("ODDS_API_KEY is not set (get one at https://the-odds-api.com)")
        self.regions = regions
        self.markets = markets
        self.timeout = timeout
        self.requests_remaining: str | None = None

    def _get(self, path: str, **params) -> list[dict]:
        params["apiKey"] = self.api_key
        url = f"{self.BASE}{path}?{urllib.parse.urlencode(params)}"
        with urllib.request.urlopen(url, timeout=self.timeout) as resp:
            self.requests_remaining = resp.headers.get("x-requests-remaining")
            return json.loads(resp.read())

    def active_sports(self) -> list[dict]:
        return self._get("/sports")

    def games(self, sports: Iterable[str]) -> list[Game]:
        games: list[Game] = []
        for sport in sports:
            events = self._get(f"/sports/{sport}/odds", regions=self.regions,
                               markets=self.markets, oddsFormat="decimal")
            games.extend(parse_events(events))
        return games

    def scores(self, sports: Iterable[str], days_from: int = 3) -> list[dict]:
        rows: list[dict] = []
        for sport in sports:
            rows.extend(self._get(f"/sports/{sport}/scores", daysFrom=days_from))
        return rows
