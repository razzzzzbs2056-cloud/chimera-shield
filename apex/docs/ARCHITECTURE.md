# Apex architecture

Apex is a Top 1% Life OS. It's one app made of independent trackers that all feed a
single **Life Score**. Each tracker was built as a separate part, by a separate agent,
against one shared contract. The core connects them together at the end.

```
                        ┌──────────────────────────────┐
                        │   app.js (shell)             │
                        │   router · header · nav      │
                        │   Dashboard · Settings       │
                        └──────────────┬───────────────┘
                                       │ Apex.lifeScore(date)
                        ┌──────────────┴───────────────┐
                        │   registry.js                 │
                        │   registerModule · weights    │
                        │   tiers · streaks             │
                        └──────────────┬───────────────┘
      ┌────────────┬───────────┬───────┴─────┬────────────┬────────────┐
   DISCIPLINE: bootcamp (orders ← auto-links to other trackers) · pt · character
   BODY          MIND        WORK          WEALTH        LIFE
   sleep         mindset     focus         finance       habits
   fitness       learning    goals                       social
   nutrition     digital                                 review ← reads every module's score
      └────────────┴───────────┴──────┬──────┴────────────┴────────────┘
                                      │ Apex.store (get/set/range/config)
                        ┌─────────────┴────────────────┐
                        │  store.js → localStorage     │
                        │  apex:v1:<module>:<date>     │
                        │  apex:v1:<module>:config     │
                        └──────────────────────────────┘
```

## How the parts connect

1. **The contract** (`docs/MODULE_CONTRACT.md`) is the only thing a module depends on:
   `Apex.registerModule({ id, category, render, score, summary })`.
2. **The registry** collects the modules. `Apex.lifeScore(date)` takes a weighted average of each
   enabled module's `score(date)`, both overall and per category. Areas with no data count as 0,
   so skipping a day never inflates your score.
3. **The tiers** map the score to a rank: 90+ Top 1%, 80+ Top 5%, 70+ Top 10%, 50+ Above average.
4. **The shell** renders the dashboard: a Life Score ring, a 14-day trend, balance by area, your
   weakest areas, and one tile per module. Each module also gets its own page at `#/m/<id>`.
5. **Ranks** (`Apex.rank`) turn a rolling year of Life Scores into military rank. Life Scores are memoised and the cache is cleared on every write.
6. **Boot Camp orders** can link to any tracker ("Deep work block" is done when Deep Work scores ≥ 50), so discipline is measured across the whole system.
7. **Daily Review** is the loop-closer. It reads every other module's score, so each evening you
   see your whole day in one place.

## Around the core

```
 Library (knowledge.js) ── principle of the day · per-tracker tips · #/library
          │
 Browser app ⇄ Export/Import JSON ⇄ ~/.apex/data.json ⇄ MCP server (mcp/server.mjs) ⇄ Claude
                                                              ▲
                                             skills: apex-coach, apex-new-tracker
```

The MCP server loads `store.js`, `registry.js`, `knowledge.js` and every tracker listed in `index.html` into a
Node sandbox with a file-backed `localStorage`. So scoring logic exists in one place only, and a new
tracker shows up in the AI tools automatically.

## Build split (who built what)

| Agent | Parts |
|-------|-------|
| Orchestrator | core store, registry and Life Score, UI kit, app shell, dashboard, settings, PWA, library, MCP server, skills, tests, CI, integration |
| Agent 1 · Body | sleep, fitness, nutrition |
| Agent 2 · Mind | mindset, learning, digital discipline |
| Agent 3 · Work | deep work (focus timer), goals, habits |
| Agent 4 · Wealth & Life | finance, relationships, daily review |
| Agent 5 · Boot Camp | Boot Camp HQ: orders, drill sergeant, Iron 75, Big Four, AAR |
| Agent 6 · PT & Character | PT test and drills, Code & Ownership |

## Adding a new tracker

1. Copy the example in `MODULE_CONTRACT.md` into `js/modules/<id>.js`.
2. Add a `<script>` tag in `index.html` (before `app.js`) and add the file path to `ASSETS` in `sw.js`.
3. Run `node tests/smoke.mjs <id>`.

## Privacy

All data stays on the device (localStorage). Nothing is sent over the network.
Use Settings → Export JSON to back up, and Import JSON to restore or move to another device.
