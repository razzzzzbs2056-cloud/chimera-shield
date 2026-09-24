# Contributing to Apex

Thanks for helping people build better days. Apex is small on purpose: plain JavaScript,
no build step, no dependencies, and everything works offline.

## Ways to help

- **New tracker:** follow [`docs/MODULE_CONTRACT.md`](docs/MODULE_CONTRACT.md). If you use Claude Code,
  the repo includes an `apex-new-tracker` skill that does this for you.
- **Book principles:** add them to `RAW` in `js/core/knowledge.js`. **Summarise ideas in your own words.**
  Do not paste quotations or passages from books. Always credit the book and author.
- **Better scoring:** each tracker's `score()` should reflect what a top-1% day really looks like.
  Explain your reasoning in the PR, and cite research where you can.
- **MCP tools:** `mcp/server.mjs`. Keep it dependency-free.
- **Translations, accessibility, and design polish** are all very welcome.

## Before you open a PR

```bash
node apex/tests/smoke.mjs        # every tracker, desktop + mobile, no console errors
node apex/tests/mcp.test.mjs     # MCP server loads every tracker and its tools work
```

The smoke test needs Playwright with Chromium (`npm i -g playwright && npx playwright install chromium`).

## Ground rules

- Never send user data anywhere. Apex is local-first, and that is a core promise.
- No `innerHTML` with user input. Use `Apex.ui.h`.
- Keep modules independent: a tracker should only depend on `Apex.store`, `Apex.date`, and `Apex.ui`.
- Health, money, and mental-health features give general information only, never diagnosis or advice.
- Be kind in issues and reviews.

By contributing, you agree that your contributions are licensed under the MIT License.
