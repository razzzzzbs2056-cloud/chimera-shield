"""Builds a data context for one game and streams a Claude-written analysis.

Uses the official Anthropic SDK with Claude Opus 4.8 and adaptive thinking.
Streaming keeps the (potentially long) generation under HTTP timeouts.
"""

from __future__ import annotations

from typing import Iterator, Optional

import anthropic

import mlb_api

MODEL = "claude-opus-4-8"

SYSTEM_PROMPT = (
    "You are a sharp, even-handed baseball analyst writing a concise daily "
    "preview for a single MLB game. Ground every claim in the data you are "
    "given — do not invent statistics, injuries, or records that aren't in the "
    "context. If a piece of data is missing (e.g. a lineup or a pitcher's "
    "stats), say so rather than guessing.\n\n"
    "Structure the preview with these short sections:\n"
    "1. **Matchup** — the storyline in 2-3 sentences (records, stakes, venue).\n"
    "2. **Pitching** — compare the probable starters using their season lines.\n"
    "3. **Key factors** — 2-4 bullets that could swing the game.\n"
    "4. **Lean** — which side looks better and why, stated with appropriate "
    "uncertainty (this is analysis, not a lock).\n\n"
    "Keep it tight and readable. End with a one-line note that this is "
    "informational analysis, not betting advice."
)


def _pitcher_block(side_label: str, pitcher: dict, stat: Optional[dict]) -> str:
    name = pitcher.get("fullName", "TBD")
    if not stat:
        return f"  {side_label} probable: {name} (no season pitching stats available)"
    parts = [
        f"ERA {stat.get('era', '—')}",
        f"{stat.get('wins', 0)}-{stat.get('losses', 0)}",
        f"WHIP {stat.get('whip', '—')}",
        f"{stat.get('inningsPitched', '—')} IP",
        f"{stat.get('strikeOuts', '—')} K",
        f"{stat.get('baseOnBalls', '—')} BB",
    ]
    return f"  {side_label} probable: {name} — " + ", ".join(parts)


def build_context(game: dict, season: int) -> str:
    """Assemble a plain-text data block describing the game for the model."""
    away = game["teams"]["away"]
    home = game["teams"]["home"]
    away_name = away["team"]["name"]
    home_name = home["team"]["name"]

    def record(side: dict) -> str:
        rec = side.get("leagueRecord") or {}
        w, l = rec.get("wins"), rec.get("losses")
        return f"{w}-{l}" if w is not None else "record n/a"

    venue = (game.get("venue") or {}).get("name", "venue n/a")
    status = (game.get("status") or {}).get("detailedState", "")
    date = game.get("officialDate", "")

    lines = [
        f"Game: {away_name} ({record(away)}) at {home_name} ({record(home)})",
        f"Date: {date}    Status: {status}    Venue: {venue}",
        f"Season: {season}",
        "",
        "Probable starting pitchers:",
    ]

    for side, label in ((away, f"Away ({away_name})"), (home, f"Home ({home_name})")):
        pp = side.get("probablePitcher") or {}
        stat = None
        if pp.get("id"):
            try:
                stat = mlb_api.pitcher_line(pp["id"], season)
            except Exception:
                stat = None
        lines.append(_pitcher_block(label, pp, stat))

    return "\n".join(lines)


def stream_analysis(
    client: anthropic.Anthropic,
    context: str,
    effort: str = "medium",
) -> Iterator[str]:
    """Yield the analysis text incrementally for st.write_stream()."""
    user = (
        "Write the daily preview for this game using only the data below.\n\n"
        + context
    )
    with client.messages.stream(
        model=MODEL,
        max_tokens=4000,
        thinking={"type": "adaptive"},
        output_config={"effort": effort},
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user}],
    ) as stream:
        for text in stream.text_stream:
            yield text
