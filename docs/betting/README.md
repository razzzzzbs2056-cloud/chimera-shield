# Betting desk

A team of small agents that tracks every game across every sportsbook, prices the true odds,
finds bets that pay more than they should, sizes them safely, and keeps a ledger of results.

> **Reality check.** Nothing here guarantees money. Bookmakers build a margin (the "vig") into
> every price, so most bettors lose over time. This desk only bets when a price beats a fair
> line estimated from sharp books, and even then results swing a lot over small samples.
> Everything is logged as **paper** bets: it never wagers real money for you.
> Bet only where legal, only money you can afford to lose. Help: 1-800-GAMBLER.

## Quick start

```bash
python -m betting train              # warm up the Elo model on sample history
python -m betting scan               # run the desk (sample data unless ODDS_API_KEY is set)
python -m betting settle             # grade finished games
python -m betting report             # P&L, ROI, CLV, breakdowns
python -m unittest discover -s betting/tests -t .
```

For live odds, get a key at <https://the-odds-api.com> and `export ODDS_API_KEY=...`.
For the Claude briefing, set `ANTHROPIC_API_KEY` (model: `BETTING_ANALYST_MODEL`, default `claude-opus-5`).

## The agents

| Agent | Job |
|---|---|
| **HeadTrader** | Lead agent. Runs every sub-agent in order on a shared `Desk` blackboard. |
| **OddsScout** | Pulls every upcoming game and every moneyline / spread / total from every book. |
| **LineShopper** | Groups identical lines across books (for example "totals 47.5") so prices compare like for like. |
| **FairValue** | Removes the vig. Uses sharp books (Pinnacle, Circa, exchanges) first, otherwise the median across at least 3 books. Power or multiplicative method. |
| **EloModel** | Rates every team from final scores and blends 25% of its opinion into 2-way moneylines, once both teams have 5 or more games. |
| **ValueHunter** | Finds the best price per outcome at retail books with edge ≥ 2% (edges over 15% are treated as stale or bad data). |
| **ArbHunter** | Finds lines where the best prices across books add up to a guaranteed return (≥ 0.5%). |
| **RiskManager** | Quarter-Kelly sizing, 2% max per bet, 5% max per game, one value bet per game and market, 10% daily stop-loss, never repeats a logged bet. |
| **Tracker** | Writes bets to SQLite, refreshes closing prices for CLV, and grades results (won, lost, push). |
| **Analyst** | Optional. Claude reviews the card for injury or news risk, correlation, and edges that look too good to be true. |

## Where the edge ("margin") comes from

1. **Line shopping.** The same bet is priced differently across 10+ books. Always take the best.
2. **Sharp vs soft.** Retail books lag the sharp market. When DraftKings still offers +175 after
   Pinnacle's no-vig line moved to +160, that gap is the edge.
3. **Arbitrage.** When books disagree enough, backing every outcome locks in a profit.
4. **Your own model.** Elo adds an independent opinion. Keep its weight modest until your
   tracked CLV proves it's adding value.

Key formulas (in `betting/odds.py`): `EV = p × price − 1`, `Kelly = (p·b − q) / b`,
arb exists when `Σ 1/price < 1`, `CLV = bet price / closing price − 1`.

## API

With the backend running (`make backend`):

- `GET  /api/betting/agents`
- `POST /api/betting/scan` `{"sports": [...], "sample": false, "min_edge": 0.02, "record": true, "analyst": false}`
- `POST /api/betting/settle`
- `GET  /api/betting/bets?status=open`
- `GET  /api/betting/report`

## Extending

- **New sports:** pass any The Odds API sport key (`python -m betting sports` lists common ones).
- **New books:** add the key to `betting/books.py`. Mark it sharp if it's a market-maker.
- **New agent:** subclass `betting.agents.base.Agent`, implement `run(desk)`, and insert it into
  `HeadTrader.pipeline`. Examples: player props, weather or injury feeds, a line-move alert agent.
- **Claude Code skill:** `.claude/skills/betting-desk/SKILL.md` teaches Claude Code the daily loop.
