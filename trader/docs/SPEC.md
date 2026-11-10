# Spec

## Purpose
A crypto trading system that runs unattended, starts in paper trading, and goes live only
after the owner approves. It should survive first and make money second.

## Fixed by the owner (2026-11-10)
| Item | Value |
|---|---|
| Exchange | OKX, through ccxt (chosen by the agent: Bybit geo-blocks the build host; OKX has spot, perps and demo trading on one API) |
| Markets | Spot for longs, USDT perpetual swaps for shorts |
| Paper balance | $1,000 |
| Off-limits | Tokenised stocks, memecoins, privacy coins, low-caps (outside the top 50) |
| REFLEX model | Claude Haiku 5.5 at low effort. No Jev key is available |
| Code location | `trader/` in this repository |

## Requirements
1. **Two layers.** The BRAIN (Claude Code sessions) researches, writes code and reviews.
   The REFLEX judges each candle and returns a typed verdict. Code owns every threshold,
   size, order and side effect.
2. **One snapshot.** The REFLEX sees a single numeric snapshot under 400 tokens, built in
   code from closed bars and a live book, with no future data.
3. **Hard risk layer**, checked before every order, that no model can relax: 2% of equity
   at risk per trade, 5% maximum daily loss, 3 open positions, 2x leverage, kill switch
   at 15% drawdown.
4. **Gate in code:** `setup_quality >= 2`, `direction_confidence > 0.88`,
   `risk_state == safe`. Size at no more than quarter Kelly on a calibrated probability.
5. **Escalation:** confidence below 0.60 or a `crisis` regime pauses new risk and alerts.
   Stopping an unsafe order never waits on a model call.
6. **Latency:** every REFLEX call is timed; a late decision is discarded and the candle
   skipped.
7. **Data safety:** missing data, stale feeds, exchange errors and clock skew block
   orders.
8. **Backtests:** walk-forward only, with fees and slippage, compared with holding BTC.
   A model-driven REFLEX may be tested only on data after its training cutoff.
9. **Nightly review:** score calibration (Brier), list misses, propose versioned changes,
   test them, never promote silently.
10. **Runtime:** Docker Compose with restart policies, health check, Telegram alerts when
    a token is supplied.
11. **Approvals:** live orders, moving funds, trading-enabled keys and production deploys
    need the owner's explicit go-ahead.

## Non-goals
Withdrawals or transfers of any kind. Leverage above 2x. Adding to a losing position.
Market making. Trading any coin that is not a configured, researched setup.

## Stated hypotheses (not evidence)
The gate thresholds, the Kelly multiplier, the confidence-to-probability shrink, the
stop and target distances, and the rule REFLEX's scoring are starting assumptions. The
walk-forward result in `docs/results/` says the rule baseline has no edge.
