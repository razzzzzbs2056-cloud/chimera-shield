"""MLB Prop Projection Dashboard (Streamlit).

Run with:  streamlit run app.py

Projects player props from season per-game rates using a Poisson model, and
shows over/under probabilities, fair odds, and the projected distribution.
"""

from __future__ import annotations

import datetime as dt

import pandas as pd
import streamlit as st

import mlb_api
import props

st.set_page_config(page_title="MLB Prop Projections", page_icon="⚾", layout="wide")

st.title("⚾ MLB Prop Projection Dashboard")
st.caption(
    "Poisson projections from season per-game rates · data: public MLB Stats API · "
    "model is a transparent baseline, not betting advice."
)

# --- sidebar ---------------------------------------------------------------

with st.sidebar:
    st.header("Settings")
    season = st.number_input(
        "Season", min_value=2000, max_value=dt.date.today().year,
        value=dt.date.today().year, step=1,
    )
    slate_date = st.date_input("Slate date", value=dt.date.today())

player_tab, slate_tab = st.tabs(["🎯 Player Prop", "📅 Today's Slate"])


# --- helpers ---------------------------------------------------------------


def render_projection(proj: props.Projection) -> None:
    c1, c2, c3 = st.columns(3)
    c1.metric("Projected (mean)", f"{proj.lam:.2f}")
    c1.caption(f"{proj.season_total} in {proj.games} G ({proj.lam:.2f}/G)")
    c2.metric(f"Over {proj.line:g}", f"{proj.p_over*100:.1f}%", proj.odds_over)
    c3.metric(f"Under {proj.line:g}", f"{proj.p_under*100:.1f}%", proj.odds_under)

    dist = proj.distribution()
    df = pd.DataFrame(dist, columns=["outcome", "probability"]).set_index("outcome")
    st.bar_chart(df, height=240)


# --- Player Prop tab -------------------------------------------------------

with player_tab:
    name = st.text_input("Player name", value="Aaron Judge", key="player_name")
    if name.strip():
        try:
            candidates = mlb_api.search_player(name.strip())
        except Exception as exc:  # network / API error
            st.error(f"Lookup failed: {exc}")
            candidates = ()

        if not candidates:
            st.warning(f"No player found matching “{name}”.")
        else:
            if len(candidates) > 1:
                labels = [
                    f"{p['fullName']} — {(p.get('primaryPosition') or {}).get('abbreviation','?')}"
                    for p in candidates
                ]
                idx = st.selectbox(
                    "Multiple matches", range(len(candidates)),
                    format_func=lambda i: labels[i],
                )
                person_lite = candidates[idx]
            else:
                person_lite = candidates[0]

            try:
                person = mlb_api.player_stats(person_lite["id"], int(season))
            except Exception as exc:
                st.error(f"Stats fetch failed: {exc}")
                st.stop()

            pos = (person.get("primaryPosition") or {}).get("abbreviation", "")
            team = (person.get("currentTeam") or {}).get("name", "Free agent")
            num = person.get("primaryNumber")
            title = person["fullName"] + (f"  ·  #{num}" if num else "")
            st.subheader(title)
            st.write(f"**{pos}** · {team} · {season} season")

            hitting = mlb_api.season_split(person, "hitting")
            pitching = mlb_api.season_split(person, "pitching")

            is_pitcher = pos in {"P", "TWP"} and pitching is not None
            mode = "Pitching" if is_pitcher else "Hitting"
            if hitting and pitching:
                mode = st.radio("Prop group", ["Hitting", "Pitching"],
                                horizontal=True,
                                index=1 if is_pitcher else 0)

            if mode == "Hitting":
                if not hitting:
                    st.info(f"No {season} hitting stats available.")
                else:
                    prop = st.selectbox("Prop", list(props.HITTING_PROPS),
                                        key="hit_prop")
                    default_line = props.HITTING_PROPS[prop]["line"]
                    line = st.number_input("Line", value=float(default_line),
                                           step=0.5, key="hit_line")
                    pa_pg = props.season_pa_per_game(hitting)
                    projected_pa = None
                    if pa_pg:
                        projected_pa = st.slider(
                            "Projected plate appearances",
                            min_value=1.0, max_value=6.0,
                            value=round(pa_pg, 1), step=0.5,
                            help=f"Season average is {pa_pg:.2f} PA/G. "
                                 "Raise/lower to model batting order or matchup.",
                        )
                    proj = props.project_hitting(hitting, prop, line, projected_pa)
                    if proj:
                        render_projection(proj)
            else:
                if not pitching:
                    st.info(f"No {season} pitching stats available.")
                else:
                    prop = st.selectbox("Prop", list(props.PITCHING_PROPS),
                                        key="pit_prop")
                    default_line = props.PITCHING_PROPS[prop]["line"]
                    line = st.number_input("Line", value=float(default_line),
                                           step=0.5, key="pit_line")
                    proj = props.project_pitching(pitching, prop, line)
                    if proj:
                        st.caption("Projected per start (falls back to per "
                                   "appearance for relievers).")
                        render_projection(proj)


# --- Slate tab -------------------------------------------------------------

with slate_tab:
    date_str = slate_date.isoformat()
    try:
        games = mlb_api.schedule(date_str)
    except Exception as exc:
        st.error(f"Schedule fetch failed: {exc}")
        games = []

    st.subheader(f"{date_str} — {len(games)} game(s)")
    if not games:
        st.info("No games scheduled.")

    pit_prop = "Strikeouts"
    pit_line = props.PITCHING_PROPS[pit_prop]["line"]

    rows = []
    for g in games:
        away = g["teams"]["away"]
        home = g["teams"]["home"]
        matchup = f"{away['team']['name']} @ {home['team']['name']}"
        for side, label in ((away, "away"), (home, "home")):
            pp = side.get("probablePitcher") or {}
            if not pp.get("id"):
                continue
            try:
                person = mlb_api.player_stats(pp["id"], int(season))
                stat = mlb_api.season_split(person, "pitching")
            except Exception:
                stat = None
            k_proj = "—"
            p_over = "—"
            if stat:
                proj = props.project_pitching(stat, pit_prop, pit_line)
                if proj:
                    k_proj = f"{proj.lam:.1f}"
                    p_over = f"{proj.p_over*100:.0f}%"
            rows.append({
                "Game": matchup,
                "Probable Pitcher": pp.get("fullName", "TBD"),
                "Proj K": k_proj,
                f"K Over {pit_line:g}": p_over,
            })

    if rows:
        st.caption(f"Projected strikeouts for probable starters (line {pit_line:g}).")
        st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)
