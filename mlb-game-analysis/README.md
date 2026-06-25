# ⚾ MLB Daily Game Analysis

A Streamlit app that pulls the day's MLB slate from the public
[MLB Stats API](https://statsapi.mlb.com) and uses **Claude** to write a
grounded preview for the game you pick.

> Informational analysis, **not betting advice**.

## Run

```bash
cd mlb-game-analysis
pip install -r requirements.txt
streamlit run app.py
```

Then enter your **Anthropic API key** in the sidebar (or set `ANTHROPIC_API_KEY`
before launching and it'll be pre-filled). Get a key at
[console.anthropic.com](https://console.anthropic.com/settings/keys).

## What it does

1. Loads the schedule for the chosen date — matchups, team records, venue, and
   probable starting pitchers.
2. For the game you select, builds a plain-text **data context** (shown in an
   expander so you can see exactly what the model is given) including each
   probable starter's season line (ERA, W-L, WHIP, IP, K, BB).
3. Streams a Claude-written preview with four sections — **Matchup**,
   **Pitching**, **Key factors**, and a **Lean** — grounded only in that data.

## Model details

- Model: **`claude-opus-4-8`** via the official `anthropic` Python SDK.
- **Adaptive thinking** (`thinking={"type": "adaptive"}`) with a selectable
  effort level (low / medium / high).
- **Streaming** (`client.messages.stream`) so long generations render live and
  don't hit HTTP timeouts.
- The system prompt instructs the model to ground every claim in the supplied
  data and to flag missing data rather than inventing stats.

Your API key is used only for the current session's requests; it is not stored.

## Files

| File | Purpose |
|---|---|
| `app.py` | Streamlit UI (sidebar key, game picker, streamed output) |
| `analysis.py` | Data-context builder + Claude streaming call |
| `mlb_api.py` | Cached MLB Stats API client |
| `requirements.txt` | streamlit, requests, anthropic |
