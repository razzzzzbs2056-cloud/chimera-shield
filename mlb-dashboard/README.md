# ⚾ MLB Prop Projection Dashboard

A Streamlit dashboard that projects MLB player props from season per-game rates
and reports over/under probabilities and fair odds. Data comes from the public
[MLB Stats API](https://statsapi.mlb.com) — no API key required.

> The model is a transparent baseline for learning the mechanics, **not betting
> advice**.

## Run

```bash
cd mlb-dashboard
pip install -r requirements.txt
streamlit run app.py
```

Then open the URL Streamlit prints (default <http://localhost:8501>).

## What it does

**🎯 Player Prop tab**
- Search any player by name.
- Pick a prop and a line:
  - *Hitting* — Hits, Total Bases, Home Runs, RBIs, Runs, Stolen Bases, Walks, Strikeouts
  - *Pitching* — Strikeouts, Hits Allowed, Walks, Earned Runs
- Get the projected mean, **Over / Under probability**, **fair American odds**,
  and a chart of the projected outcome distribution.
- A *Projected plate appearances* slider lets you scale a hitter's rate up or
  down to model batting-order spot or matchup.

**📅 Today's Slate tab**
- Every game on the selected date with each probable starter's **projected
  strikeouts** and the chance of clearing the default K line.

## How the projection works

Each prop is modeled as a **Poisson** count whose mean λ is the player's season
rate:

- Hitters: `λ = season total / games played` (optionally scaled by projected PA).
- Pitchers: `λ = season total / games started` (per start; falls back to per
  appearance for relievers).

Over/under probabilities come from the Poisson CDF, and fair (no-vig) American
odds are derived from those probabilities. The math lives in `props.py` and is
covered by sanity checks; the API client is in `mlb_api.py`.

## Files

| File | Purpose |
|---|---|
| `app.py` | Streamlit UI |
| `props.py` | Projection + probability/odds math |
| `mlb_api.py` | Cached MLB Stats API client |
| `requirements.txt` | streamlit, requests, pandas |
