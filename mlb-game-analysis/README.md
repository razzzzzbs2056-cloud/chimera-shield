# ⚾ MLB Daily Game Analysis Dashboard

A live, interactive Streamlit app that pulls the day's MLB slate from the public
**MLB Stats API** and generates on-demand **sabermetric matchup breakdowns** with
**Claude** (Anthropic API).

> ⚠️ **Disclaimer:** Analyses are model-generated for entertainment only — not
> financial advice. Always verify lineups, weather, and injuries before game time.

---

## ✨ Features

- **Date picker** (defaults to today) to load any day's schedule.
- **Secure, masked API-key input** — held in session memory only, never stored.
- **Model selector** — Claude Opus 4.8 (default), Sonnet 4.6, or Haiku 4.5.
- **Refresh Daily Slate** button that clears cached data and re-fetches.
- **Clean slate summary** rendered as a pandas DataFrame.
- **Per-game expander cards** with teams, records, and probable starters.
- **"Generate Sabermetric Analysis"** per game → a four-section breakdown:
  1. Pitching Edge
  2. Lineup Splits
  3. Bullpen Factor
  4. Final Verdict & Run Lean
- **Streamed** responses (live token output, no request timeouts).
- **State preserved** — generated analyses survive reruns/other interactions.
- **Robust error handling** — missing key, missing probable pitchers, API
  timeouts, auth/rate-limit/permission errors all surface clearly.

## 🏗️ How it works

| Layer | Detail |
|-------|--------|
| Data | `GET statsapi.mlb.com/api/v1/schedule` (hydrated with probable pitchers, venue, records), cached via `@st.cache_data(ttl=900)`. |
| AI | Official **Anthropic SDK** (`anthropic`). Each game's facts are injected into a fixed system prompt and streamed with `client.messages.stream(...)`. Adaptive thinking is enabled on the Opus/Sonnet tiers. |
| State | Generated analyses are stored in `st.session_state.analyses` keyed by `gamePk`, so clicking one game's button doesn't wipe another's output. |

The default model is `claude-opus-4-8`. No sampling params (`temperature`/`top_p`)
are sent — they're rejected by the current Opus/Sonnet tiers.

## 🚀 Run locally

```bash
# From the mlb-game-analysis/ directory:
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt

streamlit run app.py
```

Opens at http://localhost:8501

You'll need an Anthropic API key (`sk-ant-...`) from
https://console.anthropic.com — paste it into the sidebar. (Tip: a recent
`anthropic` SDK is recommended so newer models/params are recognized; upgrade
with `pip install -U anthropic`.)

## ☁️ Deploy free

1. Push to GitHub.
2. Go to [share.streamlit.io](https://share.streamlit.io), connect the repo, and
   set the app file to `mlb-game-analysis/app.py`.
3. (Optional) Add `ANTHROPIC_API_KEY` as a Streamlit secret and adapt `app.py`
   to read it — or just have each user paste their own key in the sidebar.
