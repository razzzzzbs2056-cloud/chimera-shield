# ▲ Apex: Top 1% Life OS

Apex is a website and installable phone/desktop app that tracks every part of your day.
Each life area has its own tracker, and together they roll up into one **Life Score**
that ranks your day from *Just starting* up to **Top 1%**.

| Area | Trackers |
|------|----------|
| 💪 Body | 😴 Sleep · 🏋️ Fitness · 🥗 Nutrition |
| 🧠 Mind | 🧘 Mindset · 📚 Learning · 📵 Digital Discipline |
| 🎯 Work | 🎯 Deep Work (focus timer) · 🏔️ Goals |
| 💰 Wealth | 💰 Finance |
| ❤️ Life | ✅ Habits · 🤝 Relationships · 📝 Daily Review |

## Run it

No install and no build step are needed, just a static file server:

```bash
make apex            # from the repo root, then open http://localhost:5173
# or
cd apex && python3 -m http.server 5173
```

**Install as an app:** open the site on your phone and choose *Add to Home Screen* (iOS) or
*Install app* (Android/Chrome). It works fully offline.

## 📖 Library (book knowledge)

42 principles from 25 books, including *Atomic Habits*, *Deep Work*, *Why We Sleep*, *Outlive*,
*The Psychology of Money* and *How to Win Friends*. They are summarised in our own words and
linked to the trackers they apply to. You'll find:
- a **principle of the day** on the dashboard, aimed at your weakest area
- a related principle on every tracker page
- a searchable **Library** page

Add more in `js/core/knowledge.js`.

## 🤖 AI coach: MCP server + Claude skills

`mcp/server.mjs` is a zero-dependency [MCP](https://modelcontextprotocol.io) server. It runs the app's own
tracker code, so Claude (or any MCP client) sees the same scores the app does.

| Tool | What it does |
|------|--------------|
| `get_life_score` | a day's Life Score, tier, and per-area and per-tracker scores |
| `weekly_report` | 7-day averages, streak, weakest and strongest areas, and book principles for the weak spots |
| `get_trend` | daily Life Scores for the last N days |
| `get_day` / `log_day` | read or write one tracker's entry ("log 7.5h sleep") |
| `list_trackers`, `get_principles` | discovery and library search |

The repo's `.mcp.json` registers it for Claude Code automatically. Elsewhere, run
`claude mcp add apex -- node apex/mcp/server.mjs`. Data is read from `APEX_DATA` (default `~/.apex/data.json`).
That file is the same format as the app's **Settings → Export JSON**, so move data between the app and
the AI with Export and Import.

Two Claude Code skills are included in `.claude/skills/`:
- **apex-coach**: a daily or weekly review, a plan for tomorrow, and logging by chat ("I ran 5k today")
- **apex-new-tracker**: adds a new life area to the app end to end

## Test

```bash
node apex/tests/smoke.mjs          # every tracker, desktop + mobile, fails on any console error
node apex/tests/smoke.mjs sleep    # one tracker
node apex/tests/mcp.test.mjs       # MCP server
```

CI runs all of these on every push (`.github/workflows/apex.yml`).

## Open source

MIT licensed ([`LICENSE`](LICENSE)). Contributions are welcome: see [`CONTRIBUTING.md`](CONTRIBUTING.md).

## Docs

- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md): how the parts connect, and which agent built each part
- [`docs/MODULE_CONTRACT.md`](docs/MODULE_CONTRACT.md): how to write a new tracker

All data stays on your device. Back up with Settings → Export JSON.
