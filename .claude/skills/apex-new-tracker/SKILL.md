---
name: apex-new-tracker
description: Add a new life-area tracker module to the Apex app (apex/). Use when the user wants to track something new in Apex, such as skincare, prayer, language practice, water, posture, or a side project.
---

# Add an Apex tracker

Apex trackers are independent plain-JS modules that plug into the core through one contract.

1. **Read first:** `apex/docs/MODULE_CONTRACT.md` (the contract and rules), `apex/js/core/ui.js`
   (the UI helpers), and one existing module of similar shape as a model. For example, read
   `apex/js/modules/nutrition.js` for counters and goals, `habits.js` for configurable lists, or
   `finance.js` for logged entries.
2. **Choose:** a unique lowercase `id`, a `category` (body | mind | work | wealth | life), an emoji `icon`,
   and an `order` (existing modules use 10–120 in steps of 10).
3. **Create `apex/js/modules/<id>.js`** following the contract:
   - `render(el, ctx)`: today's inputs, progress vs target, a settings card (config via
     `Apex.store.getConfig/setConfig`), a 14- or 30-day history chart, and a `.tip` insight.
   - `score(date)`: 0–100, and `null` when nothing is logged. It must be pure. 100 means a top-1% day.
   - `summary(date)`: a one-line status.
   - Only use `Apex.store`; never use `localStorage` directly. Never use `innerHTML` with user data.
     Save on `change` and call `ctx.refresh()`.
4. **Register the file in both places:**
   - add `<script src="js/modules/<id>.js"></script>` to `apex/index.html` before `js/core/app.js`
   - add `'js/modules/<id>.js'` to `ASSETS` in `apex/sw.js` and bump `CACHE` (e.g. `apex-v2` → `apex-v3`)
5. **Optional:** add book principles for the new tracker to `RAW` in `apex/js/core/knowledge.js`.
   Paraphrase them in your own words and never quote at length.
6. **Verify:**
   - `node --check apex/js/modules/<id>.js`
   - `node apex/tests/smoke.mjs <id>` must print PASS
   - `node apex/tests/mcp.test.mjs` (the MCP server loads every module)
   - `SHOTS=1 node apex/tests/smoke.mjs <id>`, then look at `apex/tests/shots/*-<id>.png` at mobile width
7. **Update docs:** add the tracker to the tables in `apex/README.md` and `apex/docs/ARCHITECTURE.md`.
