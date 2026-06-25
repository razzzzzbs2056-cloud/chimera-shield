"""
⚾ MLB Daily Game Analysis Dashboard
====================================

A live Streamlit app that fetches the day's MLB slate from the public MLB Stats
API and generates on-demand sabermetric matchup breakdowns with Claude.

Run:  streamlit run app.py
"""

from __future__ import annotations

import datetime as dt
from zoneinfo import ZoneInfo

import pandas as pd
import requests
import streamlit as st

import anthropic

# ─────────────────────────────────────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────────────────────────────────────
MLB_API = "https://statsapi.mlb.com/api/v1"
EASTERN = ZoneInfo("America/New_York")
REQUEST_TIMEOUT = 15  # seconds, MLB Stats API
LLM_TIMEOUT = 90.0    # seconds, Anthropic API

MODELS = {
    "Claude Opus 4.8 (most capable)": "claude-opus-4-8",
    "Claude Sonnet 4.6 (balanced)": "claude-sonnet-4-6",
    "Claude Haiku 4.5 (fastest)": "claude-haiku-4-5",
}

SYSTEM_PROMPT = """\
You are a veteran MLB betting analyst and sabermetrician. You produce concise,
decision-oriented matchup breakdowns for a single game.

You will be given the matchup, the venue, the scheduled start time, the probable
starting pitchers, and the teams' season records. Using your baseball knowledge
of these teams, pitchers, and ballpark, write an analysis in **GitHub-flavored
Markdown** with EXACTLY these four sections, in this order:

### 1. Pitching Edge
Compare the two probable starters (stuff, command, recent form, durability,
platoon tendencies). State which side has the edge and why.

### 2. Lineup Splits
Assess each offense against the opposing starter's handedness — vs-LHP / vs-RHP
tendencies, power vs. contact profiles, and any obvious exploitable matchups.

### 3. Bullpen Factor
Evaluate relief depth, late-inning leverage arms, and recent bullpen workload
for both sides. Note who you trust more to protect or flip a lead.

### 4. Final Verdict & Run Lean
Give a clear lean: which side and/or whether the total leans OVER or UNDER,
with a one-line rationale. Add a short confidence note (Low / Medium / High).

Rules:
- If a probable pitcher is listed as "TBD", say so explicitly and reason from
  the bullpen/rotation context instead of inventing a name.
- Be specific and analytical; avoid filler. Keep the whole response tight.
- Do not fabricate exact stat lines you are unsure of — speak in well-calibrated
  ranges and tendencies.
- End with this exact italic line:
  *Model-generated analysis for entertainment purposes only — not financial advice.*
"""


# ─────────────────────────────────────────────────────────────────────────────
# Data pipeline (MLB Stats API)
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data(ttl=900, show_spinner=False)
def fetch_schedule(date_str: str) -> list[dict]:
    """Fetch the MLB schedule for a date (YYYY-MM-DD).

    Returns a list of normalized game dicts. Cached so UI interactions don't
    refetch. Raises requests exceptions on network failure (handled by caller).
    """
    url = (
        f"{MLB_API}/schedule"
        f"?sportId=1&date={date_str}"
        f"&hydrate=probablePitcher,venue,team,linescore"
    )
    resp = requests.get(url, timeout=REQUEST_TIMEOUT)
    resp.raise_for_status()
    payload = resp.json()

    dates = payload.get("dates", [])
    if not dates:
        return []

    games: list[dict] = []
    for game in dates[0].get("games", []):
        away = game["teams"]["away"]
        home = game["teams"]["home"]

        def _record(side: dict) -> str:
            rec = side.get("leagueRecord", {})
            w, l = rec.get("wins"), rec.get("losses")
            return f"{w}-{l}" if w is not None and l is not None else "—"

        def _pitcher(side: dict) -> str:
            return side.get("probablePitcher", {}).get("fullName", "TBD")

        games.append(
            {
                "gamePk": game["gamePk"],
                "status": game.get("status", {}).get("detailedState", ""),
                "game_time_utc": game.get("gameDate", ""),
                "venue": game.get("venue", {}).get("name", "Unknown venue"),
                "away_team": away["team"]["name"],
                "away_abbr": away["team"].get("abbreviation", ""),
                "away_record": _record(away),
                "away_pitcher": _pitcher(away),
                "home_team": home["team"]["name"],
                "home_abbr": home["team"].get("abbreviation", ""),
                "home_record": _record(home),
                "home_pitcher": _pitcher(home),
            }
        )
    return games


def format_local_time(iso_utc: str) -> str:
    """Render an ISO-8601 UTC timestamp as Eastern wall-clock time."""
    if not iso_utc:
        return "TBD"
    try:
        utc = dt.datetime.fromisoformat(iso_utc.replace("Z", "+00:00"))
        return utc.astimezone(EASTERN).strftime("%-I:%M %p ET")
    except (ValueError, TypeError):
        return "TBD"


def schedule_dataframe(games: list[dict]) -> pd.DataFrame:
    """Build a clean summary DataFrame for the slate."""
    rows = [
        {
            "Away": f"{g['away_team']} ({g['away_record']})",
            "Home": f"{g['home_team']} ({g['home_record']})",
            "First Pitch": format_local_time(g["game_time_utc"]),
            "Away SP": g["away_pitcher"],
            "Home SP": g["home_pitcher"],
            "Venue": g["venue"],
            "Status": g["status"],
        }
        for g in games
    ]
    return pd.DataFrame(rows)


def build_matchup_context(game: dict, date_str: str) -> str:
    """Render a single game's facts into a prompt for the model."""
    return (
        f"Date: {date_str}\n"
        f"Matchup: {game['away_team']} ({game['away_record']}) "
        f"@ {game['home_team']} ({game['home_record']})\n"
        f"First pitch: {format_local_time(game['game_time_utc'])}\n"
        f"Venue: {game['venue']}\n"
        f"Away probable SP: {game['away_pitcher']}\n"
        f"Home probable SP: {game['home_pitcher']}\n"
        f"Game status: {game['status']}\n\n"
        f"Write the four-section sabermetric breakdown for this matchup."
    )


# ─────────────────────────────────────────────────────────────────────────────
# AI pipeline (Anthropic / Claude)
# ─────────────────────────────────────────────────────────────────────────────
def stream_analysis(api_key: str, model: str, user_content: str):
    """Yield text chunks of Claude's analysis as they stream.

    Streaming is used so large/thinking responses don't hit request timeouts and
    the UI feels live. Adaptive thinking is enabled on models that support it.
    Exceptions propagate to the caller for friendly error handling.
    """
    client = anthropic.Anthropic(api_key=api_key, timeout=LLM_TIMEOUT)

    kwargs = {
        "model": model,
        "max_tokens": 4096,
        "system": SYSTEM_PROMPT,
        "messages": [{"role": "user", "content": user_content}],
    }
    # Adaptive thinking improves matchup reasoning on the Opus/Sonnet tiers.
    if model.startswith(("claude-opus", "claude-sonnet")):
        kwargs["thinking"] = {"type": "adaptive"}

    with client.messages.stream(**kwargs) as stream:
        for text in stream.text_stream:
            yield text


def render_anthropic_error(exc: Exception) -> None:
    """Map common Anthropic/network failures to actionable Streamlit messages."""
    if isinstance(exc, anthropic.AuthenticationError):
        st.error("🔑 Invalid API key. Check the key you entered in the sidebar.")
    elif isinstance(exc, anthropic.PermissionDeniedError):
        st.error("🚫 This API key lacks access to the selected model.")
    elif isinstance(exc, anthropic.RateLimitError):
        st.error("⏳ Rate limited by the API. Wait a moment and try again.")
    elif isinstance(exc, (anthropic.APITimeoutError, anthropic.APIConnectionError)):
        st.error("🌐 Could not reach the Anthropic API (timeout / connection).")
    elif isinstance(exc, anthropic.APIStatusError):
        st.error(f"API error ({exc.status_code}): {exc.message}")
    else:
        st.error(f"Unexpected error generating analysis: {exc}")


# ─────────────────────────────────────────────────────────────────────────────
# UI
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="⚾ MLB Daily Game Analysis",
    page_icon="⚾",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Dark-theme-friendly accents (Streamlit theme is set via .streamlit/config.toml).
st.markdown(
    """
    <style>
      .stApp { background-color: #0e1117; }
      .matchup-title { font-size: 1.15rem; font-weight: 700; }
      .meta { color: #9ca3af; font-size: 0.9rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

# Persist generated analyses across reruns so they don't disappear on interaction.
if "analyses" not in st.session_state:
    st.session_state.analyses = {}  # {gamePk: markdown_text}

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Controls")

    selected_date = st.date_input("Game date", value=dt.date.today())
    date_str = selected_date.strftime("%Y-%m-%d")

    st.divider()
    st.subheader("🤖 AI Settings")
    api_key = st.text_input(
        "Anthropic API key",
        type="password",
        placeholder="sk-ant-...",
        help="Your key is held in memory for this session only and is never stored.",
    )
    model_label = st.selectbox("Model", list(MODELS.keys()), index=0)
    model_id = MODELS[model_label]

    st.divider()
    if st.button("🔄 Refresh Daily Slate", use_container_width=True):
        fetch_schedule.clear()
        st.session_state.analyses.clear()
        st.rerun()

    st.caption(
        "Schedule data: MLB Stats API. Analysis: Anthropic Claude. "
        "Projections are model estimates — not financial advice."
    )

# ── Header ───────────────────────────────────────────────────────────────────
st.title("⚾ MLB Daily Game Analysis")
st.caption(
    f"Slate for **{selected_date.strftime('%A, %B %-d, %Y')}** · "
    "live matchups + on-demand sabermetric breakdowns"
)

# ── Load slate ───────────────────────────────────────────────────────────────
try:
    games = fetch_schedule(date_str)
except requests.exceptions.RequestException as exc:
    st.error(f"Failed to load the schedule from the MLB Stats API: {exc}")
    st.stop()

if not games:
    st.info("No MLB games scheduled for this date. Try another day.")
    st.stop()

# ── Slate summary table ──────────────────────────────────────────────────────
st.subheader(f"📅 {len(games)} games")
st.dataframe(
    schedule_dataframe(games),
    use_container_width=True,
    hide_index=True,
)
st.divider()

# ── Per-game cards ───────────────────────────────────────────────────────────
if not api_key:
    st.warning(
        "Enter your Anthropic API key in the sidebar to generate matchup analyses.",
        icon="🔑",
    )

for game in games:
    pk = game["gamePk"]
    first_pitch = format_local_time(game["game_time_utc"])
    title = (
        f"{game['away_abbr']} @ {game['home_abbr']}  ·  {first_pitch}  ·  "
        f"{game['venue']}"
    )

    with st.expander(title, expanded=False):
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown(
                f"<span class='matchup-title'>✈️ {game['away_team']}</span><br>"
                f"<span class='meta'>Record: {game['away_record']} · "
                f"SP: {game['away_pitcher']}</span>",
                unsafe_allow_html=True,
            )
        with col_b:
            st.markdown(
                f"<span class='matchup-title'>🏟️ {game['home_team']}</span><br>"
                f"<span class='meta'>Record: {game['home_record']} · "
                f"SP: {game['home_pitcher']}</span>",
                unsafe_allow_html=True,
            )

        st.markdown("")  # spacer
        generate = st.button(
            "🧠 Generate Sabermetric Analysis",
            key=f"gen_{pk}",
            disabled=not api_key,
            use_container_width=True,
        )

        if generate:
            context = build_matchup_context(game, date_str)
            try:
                with st.spinner("Analyzing matchup with Claude…"):
                    full_text = st.write_stream(
                        stream_analysis(api_key, model_id, context)
                    )
                st.session_state.analyses[pk] = full_text
            except Exception as exc:  # noqa: BLE001 - mapped to friendly UI below
                render_anthropic_error(exc)
        elif pk in st.session_state.analyses:
            # Re-render a previously generated analysis so it survives reruns
            # (e.g. when another game's button is clicked).
            st.markdown(st.session_state.analyses[pk])
