---
name: betting-desk
description: Run the multi-agent sports betting desk in this repo — scan every game and book for +EV and arbitrage bets, size them, log them to the ledger, settle results, and report P&L/ROI/CLV. Use when the user asks for today's bets, edges, arbs, line shopping, bankroll, or betting results.
---

# Betting desk

The desk lives in `betting/`. Everything runs from the CLI with the standard library only.

## Daily loop

1. `python -m betting scan` — every agent runs in order (OddsScout → LineShopper →
   FairValue → EloModel → ValueHunter + ArbHunter → RiskManager → Tracker → Analyst).
   Uses live odds when `ODDS_API_KEY` is set, otherwise the bundled sample.
   Useful flags: `--sports basketball_nba americanfootball_nfl`, `--min-edge 0.03`,
   `--dry-run` (don't log), `--json`.
2. Show the user the card: game, selection, book, price, fair %, edge, stake.
   Remind them the stakes are paper bets: they place real ones themselves at the named book,
   after checking the price is still there.
3. After games finish: `python -m betting settle` (grades bets, teaches the Elo model).
4. `python -m betting report` — bankroll, ROI, win rate, CLV, breakdown by sport/book/market/type.

## Other commands

- `python -m betting bets --status open` — the open book
- `python -m betting bankroll --set 500` — starting bankroll
- `python -m betting train --file results.json` — warm up Elo on past results
- `python -m betting convert -110` — odds converter
- `python -m betting books | sports | agents`

## How to read results

- **CLV (closing line value)** is the best early signal: consistently beating the close means
  the edges are real, even before the P&L catches up.
- Small samples are noise. Judge the process over hundreds of bets, not a weekend.
- Arbs are near risk-free only if every leg is placed at the logged price; books limit
  accounts that arb or bet sharp.

## Guardrails when helping the user

- Never present an edge as guaranteed profit, and don't raise Kelly/caps to "win faster".
- If the user is chasing losses or betting money they can't afford to lose, say so plainly and
  point them to a responsible-gambling resource (US: 1-800-GAMBLER).
- Betting is legal only in some jurisdictions and for adults; the user is responsible for
  complying with local law and each book's terms.
