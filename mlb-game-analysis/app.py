"""MLB Daily Game Analysis (Streamlit + Claude).

Pulls today's slate from the public MLB Stats API and uses Claude Opus 4.8 to
write a grounded preview for the game you pick. Bring your own Anthropic API
key — enter it in the sidebar.

Run with:  streamlit run app.py
"""

from __future__ import annotations

import datetime as dt
import os

import anthropic
import streamlit as st

import analysis
import mlb_api

st.set_page_config(page_title="MLB Daily Game Analysis", page_icon="⚾", layout="centered")

st.title("⚾ MLB Daily Game Analysis")
st.caption(
    "Today's slate from the public MLB Stats API, analyzed by Claude. "
    "Informational only — not betting advice."
)

# --- sidebar: API key + model controls -------------------------------------

with st.sidebar:
    st.header("Anthropic API")
    api_key = st.text_input(
        "API key",
        type="password",
        value=os.environ.get("ANTHROPIC_API_KEY", ""),
        help="Your key is used only for this session's requests and is not stored.",
        placeholder="sk-ant-...",
    )
    st.markdown(
        "Need a key? Create one at "
        "[console.anthropic.com](https://console.anthropic.com/settings/keys)."
    )
    st.divider()
    effort = st.select_slider(
        "Reasoning effort",
        options=["low", "medium", "high"],
        value="medium",
        help="Higher effort means more thorough analysis at higher latency/cost.",
    )
    st.caption(f"Model: `{analysis.MODEL}` · adaptive thinking")

# --- game selection --------------------------------------------------------

col1, col2 = st.columns([2, 1])
with col1:
    game_date = st.date_input("Date", value=dt.date.today())
with col2:
    season = st.number_input(
        "Season", min_value=2000, max_value=dt.date.today().year,
        value=game_date.year, step=1,
    )

date_str = game_date.isoformat()
try:
    games = mlb_api.schedule(date_str)
except Exception as exc:
    st.error(f"Could not load the schedule: {exc}")
    st.stop()

if not games:
    st.info("No games scheduled for that date.")
    st.stop()

idx = st.selectbox(
    f"Game ({len(games)} scheduled)",
    range(len(games)),
    format_func=lambda i: mlb_api.game_label(games[i]),
)
game = games[idx]

# Show the raw data context so the analysis is transparent / auditable.
context = analysis.build_context(game, int(season))
with st.expander("Data the analysis is based on"):
    st.code(context, language="text")

# --- run analysis ----------------------------------------------------------

if st.button("Analyze game", type="primary"):
    if not api_key.strip():
        st.warning("Enter your Anthropic API key in the sidebar to run the analysis.")
        st.stop()

    client = anthropic.Anthropic(api_key=api_key.strip())
    st.subheader("Preview")
    try:
        result = st.write_stream(
            analysis.stream_analysis(client, context, effort=effort)
        )
    except anthropic.AuthenticationError:
        st.error("Authentication failed — check that your API key is valid.")
        st.stop()
    except anthropic.RateLimitError:
        st.error("Rate limited by the API. Wait a moment and try again.")
        st.stop()
    except anthropic.APIStatusError as exc:
        st.error(f"API error ({exc.status_code}): {exc.message}")
        st.stop()
    except anthropic.APIConnectionError:
        st.error("Network error reaching the Anthropic API. Check your connection.")
        st.stop()

    st.download_button(
        "Download analysis",
        data=result,
        file_name=f"analysis-{date_str}-game{idx + 1}.md",
        mime="text/markdown",
    )
