"""
⚾ MLB Player Prop Dashboard
Run: streamlit run app.py
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime

from api_client import (
    search_player, get_player_info, get_batter_season_stats,
    get_batter_splits, get_pitcher_season_stats, get_today_schedule
)
from engine import (
    project_hits, project_hr, project_runs, project_rbi,
    score_all_factors, weather_multiplier, ProjectionResult
)
from parks import get_park, PARK_FACTORS

# ── Page Config ──────────────────────────────
st.set_page_config(
    page_title="⚾ MLB Prop Dashboard",
    page_icon="⚾",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ───────────────────────────────
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(90deg, #1e40af, #dc2626);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0;
    }
    .sub-header {
        color: #6b7280;
        font-size: 1rem;
        margin-top: 0;
    }
    .metric-card {
        background: #111827;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        border: 1px solid #1f2937;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 800;
    }
    .metric-label {
        font-size: 0.85rem;
        color: #9ca3af;
    }
    .over-badge {
        background: #064e3b;
        color: #34d399;
        padding: 4px 16px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 1.1rem;
    }
    .under-badge {
        background: #7f1d1d;
        color: #fca5a5;
        padding: 4px 16px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 1.1rem;
    }
    .factor-row {
        display: flex;
        justify-content: space-between;
        padding: 8px 0;
        border-bottom: 1px solid #1f2937;
    }
    div[data-testid="stMetric"] {
        background: #111827;
        border: 1px solid #1f2937;
        border-radius: 10px;
        padding: 15px;
    }
</style>
""", unsafe_allow_html=True)

# ── Header ───────────────────────────────────
st.markdown('<p class="main-header">⚾ MLB Prop Dashboard</p>',
            unsafe_allow_html=True)
st.markdown('<p class="sub-header">Player prop projections powered by '
            'sabermetrics + matchup data</p>', unsafe_allow_html=True)
st.divider()

# ── Sidebar ──────────────────────────────────
with st.sidebar:
    st.header("🔍 Player Search")
    search_query = st.text_input(
        "Type a player name",
        placeholder="e.g. Aaron Judge",
        key="search"
    )

    st.divider()
    st.header("🌤️ Weather")
    col_w1, col_w2 = st.columns(2)
    with col_w1:
        temp = st.number_input("Temp °F", 40, 110, 75)
        humidity = st.number_input("Humidity %", 0, 100, 50)
    with col_w2:
        wind_speed = st.number_input("Wind mph", 0, 40, 5)
        wind_dir = st.selectbox("Wind Dir",
                                ["Calm", "Out", "In", "Cross"])

    st.divider()
    st.header("⚙️ Settings")
    lineup_pos = st.slider("Lineup Position", 1, 9, 3)
    team_obp = st.slider("Team OBP", 0.280, 0.370, 0.320, 0.005)

    st.divider()
    st.header("📅 Today's Games")
    show_schedule = st.checkbox("Show schedule", value=False)

# ── Schedule View ────────────────────────────
if show_schedule:
    st.subheader("📅 Today's Schedule")
    games = get_today_schedule()
    if games:
        for g in games:
            status_emoji = "🔴" if "Live" in g["status"] else \
                           "✅" if "Final" in g["status"] else "⏰"
            st.markdown(
                f"{status_emoji} **{g['away']['abbr']}** "
                f"({g['away']['probable_pitcher']}) @ "
                f"**{g['home']['abbr']}** "
                f"({g['home']['probable_pitcher']}) "
                f"— _{g['venue']}_"
            )
    else:
        st.info("No games found for today.")
    st.divider()

# ── Player Search Results ────────────────────
selected_player = None

if search_query and len(search_query) >= 2:
    results = search_player(search_query)
    if results:
        # Filter to position players only
        hitters = [r for r in results
                   if r["position"] not in ["P", ""]]
        if not hitters:
            hitters = results

        options = [f"{r['name']} ({r['team']} - {r['position']})"
                   for r in hitters[:10]]
        choice = st.selectbox("Select player", options)

        if choice:
            idx = options.index(choice)
            selected_player = hitters[idx]
    else:
        st.warning("No players found. Try a different name.")

# ── Main Analysis ────────────────────────────
if selected_player:
    pid = selected_player["id"]

    with st.spinner("Loading player data..."):
        info = get_player_info(pid)
        stats = get_batter_season_stats(pid)
        splits = get_batter_splits(pid)

    if not stats:
        st.error("Could not load stats. Player may be a pitcher or inactive.")
        st.stop()

    # ── Determine Park ───────────────────────
    # Find today's game to get venue
    games = get_today_schedule()
    park_name = "Busch Stadium"  # default neutral
    park_data = {"hr": 100, "run": 100, "hit": 100}
    opp_pitcher_id = None
    opp_pitcher_name = "League Average"

    team_abbr = info.get("team_abbr", "")
    for g in games:
        if g["away"]["abbr"] == team_abbr:
            park_name = g["venue"]
            opp_pitcher_id = g["home"]["probable_pitcher_id"]
            opp_pitcher_name = g["home"]["probable_pitcher"]
            park_data = PARK_FACTORS.get(park_name,
                                         {"hr": 100, "run": 100, "hit": 100})
            break
        elif g["home"]["abbr"] == team_abbr:
            park_name = g["venue"]
            opp_pitcher_id = g["away"]["probable_pitcher_id"]
            opp_pitcher_name = g["away"]["probable_pitcher"]
            park_data = PARK_FACTORS.get(park_name,
                                         {"hr": 100, "run": 100, "hit": 100})
            break

    # ── Get Pitcher Stats ────────────────────
    pitcher_stats = {
        "era": 4.00, "whip": 1.30, "k_pct": 0.22,
        "bb_pct": 0.08, "hr_9": 1.2, "fb_pct": 0.35,
        "throws": "Right",
    }
    if opp_pitcher_id:
        with st.spinner("Loading pitcher data..."):
            p_info = get_player_info(opp_pitcher_id)
            p_stats = get_pitcher_season_stats(opp_pitcher_id)
            if p_stats:
                pitcher_stats.update(p_stats)
                pitcher_stats["throws"] = p_info.get(
                    "throw_side", "Right")
                opp_pitcher_name = p_info.get("name", opp_pitcher_name)

    # ── Weather Calc ─────────────────────────
    w_mult = weather_multiplier(temp, wind_speed, wind_dir, humidity)

    # ── Run Projections ──────────────────────
    proj_hits = project_hits(
        stats, splits, pitcher_stats, park_data["hit"], lineup_pos)
    proj_hr = project_hr(
        stats, splits, pitcher_stats, park_data["hr"],
        w_mult, lineup_pos)
    proj_runs = project_runs(
        stats, pitcher_stats, park_data["run"], lineup_pos, team_obp)
    proj_rbi = project_rbi(
        stats, pitcher_stats, park_data["run"], lineup_pos, team_obp)

    all_projs = [proj_hits, proj_runs, proj_rbi, proj_hr]

    # ── Player Header ────────────────────────
    st.markdown(f"""
    ### {info.get('name', selected_player['name'])}
    **#{info.get('jersey', '')}** | {info.get('position', '')} |
    {info.get('bat_side', '')} | {info.get('team_name', '')} |
    Age {info.get('age', '')}
    """)

    st.info(f"🏟️ **{park_name}** | vs **{opp_pitcher_name}** "
            f"({pitcher_stats.get('throws', 'R')}) | "
            f"Lineup Spot: **#{lineup_pos}** | "
            f"Weather Mult: **{w_mult:.3f}x**")

    # ── Projection Cards ─────────────────────
    st.subheader("📈 Projections")

    cols = st.columns(4)
    for i, proj in enumerate(all_projs):
        with cols[i]:
            badge_class = "over-badge" if proj.lean == "OVER" \
                else "under-badge"
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">{proj.stat}</div>
                <div class="metric-value"
                     style="color: {proj.color}">
                    {proj.projected:.2f}
                </div>
                <div style="margin: 8px 0;">
                    <span class="{badge_class}">
                        {proj.lean} {proj.line}
                    </span>
                </div>
                <div class="metric-label">
                    Confidence: {proj.confidence:.0f}%
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.divider()

    # ── Tabs ─────────────────────────────────
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Factor Radar",
        "⚾ Matchup Details",
        "📋 Season Stats",
        "🔀 Splits"
    ])

    # ── Tab 1: Factor Radar ──────────────────
    with tab1:
        factors = score_all_factors(
            stats, pitcher_stats, park_data["hr"],
            park_data["run"], w_mult, lineup_pos,
            info.get("bat_side", "Right")
        )

        col_r1, col_r2 = st.columns([3, 2])

        with col_r1:
            # Radar chart
            categories = [f[0] for f in factors]
            scores = [f[1] for f in factors]
            # Close the radar
            categories += [categories[0]]
            scores += [scores[0]]

            fig = go.Figure()
            fig.add_trace(go.Scatterpolar(
                r=scores,
                theta=categories,
                fill='toself',
                fillcolor='rgba(59, 130, 246, 0.3)',
                line=dict(color='#3b82f6', width=3),
                name='Factor Score'
            ))
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True, range=[0, 5],
                        tickvals=[1, 2, 3, 4, 5]
                    ),
                    bgcolor='#111827',
                ),
                paper_bgcolor='#0f172a',
                font=dict(color='white'),
                showlegend=False,
                height=450,
                margin=dict(t=30, b=30, l=60, r=60),
            )
            st.plotly_chart(fig, use_container_width=True)

        with col_r2:
            st.markdown("#### Factor Breakdown")
            total_weighted = 0
            weights = [0.15, 0.15, 0.15, 0.15, 0.10,
                       0.10, 0.10, 0.10]
            for i, (name, score, direction) in enumerate(factors):
                w = weights[i] if i < len(weights) else 0.1
                weighted = score * w
                total_weighted += weighted
                emoji = "🟢" if score >= 4 else \
                        "🟡" if score >= 3 else "🔴"
                st.markdown(
                    f"{emoji} **{name}**: {score}/5 "
                    f"({direction})"
                )

            st.divider()
            if total_weighted > 3.5:
                verdict = "🟢 STRONG OVER"
            elif total_weighted > 3.0:
                verdict = "🟡 LEAN OVER"
            elif total_weighted > 2.5:
                verdict = "⚪ NEUTRAL"
            elif total_weighted > 2.0:
                verdict = "🟡 LEAN UNDER"
            else:
                verdict = "🔴 STRONG UNDER"

            st.markdown(f"### {verdict}")
            st.markdown(f"Weighted Score: **{total_weighted:.2f}** / 5.00")

    # ── Tab 2: Matchup ───────────────────────
    with tab2:
        col_m1, col_m2 = st.columns(2)

        with col_m1:
            st.markdown("#### 🏟️ Park Factors")
            park_df = pd.DataFrame([
                {"Metric": "Home Runs", "Factor": park_data["hr"],
                 "League Avg": 100},
                {"Metric": "Runs", "Factor": park_data["run"],
                 "League Avg": 100},
                {"Metric": "Hits", "Factor": park_data["hit"],
                 "League Avg": 100},
            ])
            fig_park = px.bar(
                park_df, x="Metric", y=["Factor", "League Avg"],
                barmode="group",
                color_discrete_sequence=["#3b82f6", "#4b5563"],
                template="plotly_dark"
            )
            fig_park.update_layout(height=300)
            st.plotly_chart(fig_park, use_container_width=True)

        with col_m2:
            st.markdown("#### ⚾ Opposing Pitcher")
            st.metric("ERA", f"{pitcher_stats.get('era', 0):.2f}")
            st.metric("WHIP", f"{pitcher_stats.get('whip', 0):.2f}")
            st.metric("K%", f"{pitcher_stats.get('k_pct', 0):.1%}")
            st.metric("HR/9", f"{pitcher_stats.get('hr_9', 0):.2f}")
            st.metric("GB%", f"{pitcher_stats.get('gb_pct', 0):.1%}")

    # ── Tab 3: Season Stats ──────────────────
    with tab3:
        st.markdown("#### Season Batting Stats")
        stat_cols = st.columns(6)
        stat_items = [
            ("AVG", f"{stats.get('avg', 0):.3f}"),
            ("OBP", f"{stats.get('obp', 0):.3f}"),
            ("SLG", f"{stats.get('slg', 0):.3f}"),
            ("OPS", f"{stats.get('ops', 0):.3f}"),
            ("ISO", f"{stats.get('iso', 0):.3f}"),
            ("BABIP", f"{stats.get('babip', 0):.3f}"),
        ]
        for col, (label, val) in zip(stat_cols, stat_items):
            col.metric(label, val)

        stat_cols2 = st.columns(6)
        stat_items2 = [
            ("HR", str(stats.get("hr", 0))),
            ("RBI", str(stats.get("rbi", 0))),
            ("Runs", str(stats.get("runs", 0))),
            ("SB", str(stats.get("sb", 0))),
            ("K%", f"{stats.get('k_pct', 0):.1%}"),
            ("BB%", f"{stats.get('bb_pct', 0):.1%}"),
        ]
        for col, (label, val) in zip(stat_cols2, stat_items2):
            col.metric(label, val)

    # ── Tab 4: Splits ────────────────────────
    with tab4:
        st.markdown("#### Platoon Splits")
        if splits.get("vs_lhp") or splits.get("vs_rhp"):
            split_data = []
            for key, label in [("vs_lhp", "vs LHP"),
                               ("vs_rhp", "vs RHP")]:
                s = splits.get(key, {})
                if s:
                    split_data.append({
                        "Split": label,
                        "AVG": s.get("avg", 0),
                        "OBP": s.get("obp", 0),
                        "SLG": s.get("slg", 0),
                        "OPS": s.get("ops", 0),
                        "HR": s.get("hr", 0),
                        "AB": s.get("ab", 0),
                    })
            if split_data:
                split_df = pd.DataFrame(split_data)
                st.dataframe(split_df, use_container_width=True,
                             hide_index=True)

                # Visual split comparison
                fig_split = px.bar(
                    split_df, x="Split", y=["AVG", "OBP", "SLG"],
                    barmode="group",
                    color_discrete_sequence=[
                        "#22c55e", "#3b82f6", "#f59e0b"],
                    template="plotly_dark"
                )
                fig_split.update_layout(height=350)
                st.plotly_chart(fig_split, use_container_width=True)
        else:
            st.info("Split data not available.")

    # ── Disclaimer ───────────────────────────
    st.divider()
    st.caption(
        "⚠️ Projections are model estimates, not guarantees. "
        "Always verify lineups, weather, and injury reports "
        "before game time. Not financial advice."
    )

else:
    # ── Landing State ────────────────────────
    st.markdown("""
    ### 👋 Welcome

    Search for any MLB player in the sidebar to get:

    - 📈 **Hit / Run / RBI / HR projections**
    - 🎯 **Factor radar chart** with 8 key drivers
    - ⚾ **Pitcher matchup** breakdown
    - 🏟️ **Park factor** analysis
    - 🌤️ **Weather-adjusted** HR projections
    - 🔀 **Platoon split** visualization

    ---

    **How it works:**

    1. Type a player name in the sidebar
    2. Adjust weather + lineup position
    3. Review projections and factor scores
    4. Check the radar chart for edge identification

    > Data sourced from MLB Stats API. Park factors
    > are static approximations.
    """)
