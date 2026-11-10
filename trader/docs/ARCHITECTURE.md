# Architecture

```
            BRAIN (Claude Code, not in the runtime)
   research -> setups/config   code + tests   nightly report -> candidate policy
                                   |                         (human promotes)
  ---------------------------------+----------------------------------------------
   RUNTIME (Docker: `trader run`), once per closed candle, per setup
                                   |
   OKX public data (ccxt) --> State engine --> Snapshot (< 400 tokens, numbers only)
     candles, book, funding,    validates:          |
     exchange clock             missing, stale,     v
                                lookahead, skew   REFLEX  (deadline; late = skip candle)
                                    |             rule | Haiku 5.5 | replay
                                    | DataFault      |
                                    v                v  ReflexDecision (typed)
   Hard risk layer  <------------  Gate (code) -- size (quarter Kelly, capped) --+
   kill 15% | daily 5% | 3 pos | 2x | 2%/trade | reduce-only always allowed      |
        |                                                                         v
        +--> exits: stop, target, time, thesis price, kill flatten  --------> Broker
             (code only, never wait on the REFLEX)                     paper | OKX demo | OKX live
                                                                              |
   Ledger (balance, positions) <-- fills --- reconcile vs broker --- journal (JSONL) + state.json
```

## Modules (`src/trader/`)
| File | Role |
|---|---|
| `types.py` | `ReflexDecision`, candles, book, positions, order intents |
| `state/features.py` | Causal indicators; the same function serves live and backtest |
| `state/engine.py` | Data checks and the `Snapshot` |
| `reflex/base.py` | Interface and the latency deadline |
| `reflex/rule.py` | Deterministic baseline (no model) |
| `reflex/haiku.py` | Claude Haiku 5.5, structured output, low effort, no retries |
| `reflex/replay.py` | Replays logged decisions to test candidate policies |
| `gate.py` | The entry rules and escalation |
| `risk/engine.py` | Hard limits, kill switch, drawdown-based size reduction |
| `risk/sizing.py` | Fractional Kelly, capped |
| `risk/calibration.py` | Confidence to probability, Brier score, isotonic fit |
| `policy.py` | Versioned thresholds; promote and roll back with a named approver |
| `core.py` | The pipeline, shared by paper, live and backtest |
| `exec/broker.py` | Paper broker (fees, spread, slippage, impact, failures), ledger, reconciliation |
| `exec/ccxt_broker.py` | OKX orders through ccxt. Not yet run against the exchange |
| `data/market.py` | ccxt market data and the history cache |
| `backtest/engine.py`, `backtest/walkforward.py` | Event-driven backtest and walk-forward versus BTC |
| `review/nightly.py` | Calibration, misses, candidate policies |
| `runtime/loop.py` | The 24/7 loop, saved state, heartbeat |
| `config.py`, `cli.py`, `alerts.py`, `journal.py` | Config validation, commands, Telegram, records |

## Design rules
- **The model cannot size, price or order.** `ReflexDecision` forbids extra fields, and
  the gate takes the worse of the model's risk state and the risk layer's.
- **Same code path everywhere.** Backtests drive `TraderCore`, the gate, the sizer, the
  risk engine and the paper broker exactly as the live loop does.
- **No look-ahead.** Features at bar k use bars up to k; a test recomputes on truncated
  data to prove it. Backtest entries fill at the next bar's open. Stops are checked
  before targets inside a bar.
- **Fail closed.** Any data fault, REFLEX error or timeout means no new order. Exits use
  reduce-only orders, which the risk layer always allows. A failed exit is retried every
  candle and alerts.
- **Every held position is managed every pass.** The live loop prices each position from the
  order book, else the last closed candle, else the last known price. Stops are checked
  against every bar since the last check plus the live quote. A price older than two
  candles blocks all new entries and raises a critical alert.
- **Latched stops need a human.** The kill switch and a reconciliation mismatch stay set
  across restarts until cleared from the CLI.
- **Idempotent orders.** Client order ids are derived from setup and candle time, so a
  retry or restart cannot double-fill.

## Decisions that differ from a literal reading of the brief
1. *Crisis pause is a 72-candle cooldown that renews while crisis readings continue*, not
   a pause until a human acts. With a permanent pause the first crisis reading switched
   the system off for good (found in the first walk-forward run). Set
   `crisis_cooldown_bars: 0` in a policy to require a human.
2. *Drawdown does not make the risk state "near limit".* Drawdown only recovers by
   trading, so gating on it froze the system at 10.5% drawdown. Instead trade size
   shrinks linearly to a quarter as drawdown approaches 15%, where the kill switch
   latches.
3. *Two extra hard limits:* one position may not exceed 1x equity, and spot buys may not
   exceed cash. Both are stricter than the brief.
