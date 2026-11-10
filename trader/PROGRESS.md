# PROGRESS

Read this first in every new session. Update it before ending one.

## Where things stand (2026-11-10)

- **Mode:** paper only. No exchange keys exist. No live order has ever been placed.
- **Edge:** none demonstrated. The rule baseline loses to holding BTC out of sample.
- **Branch:** `claude/compassionate-gates-mvl606` in `razzzzzbs2056-cloud/chimera-shield`,
  code under `trader/`. The rest of the repository (ChimeraShield) is unrelated and untouched.

## Owner's answers

| Question | Answer |
|---|---|
| Exchange | "Whichever is best": OKX chosen (see decisions) |
| Spot or perps | Both: spot for longs, perps for shorts |
| Paper balance | $1,000 |
| Off-limits coins | "all stocks and all": read as tokenised stocks, memecoins, privacy coins and low-caps. **Unconfirmed reading** |
| Jev API key | Said yes, then declined the key form and said they do not have one. REFLEX is Haiku 5.5 |
| Where to build | New `trader/` folder |
| Reference repo | Asked for a public reference without naming one. `freqtrade/freqtrade` cloned read-only outside the repo; no code copied (GPL) |

## Done

| Item | Evidence |
|---|---|
| State engine, snapshot under 400 tokens | Live OKX snapshot: 380 characters, about 150 tokens by a conservative estimate (not a tokenizer count) |
| No look-ahead | Tests recompute features on truncated data; backtest test alters future bars and the past is unchanged |
| Hard risk layer | 2% per trade, 5% daily loss, 3 positions, 2x leverage, 15% kill switch, all tested |
| Gate, Kelly sizing, calibration, policy versions | Tested |
| Paper broker | Fees, spread, slippage, depth impact, partial fills, failed orders, idempotency, reconciliation tested |
| REFLEX: rule baseline | Tested; runs live |
| REFLEX: Haiku 5.5 | Request shape tested against a fake client only |
| Backtest and walk-forward | Run on real OKX hourly history 2023-01-01 to 2026-11-10 |
| Nightly review | Tested on synthetic logs; run end to end once on the real journal (refreshed history, regression tests passed, nothing to calibrate yet, no proposals); never promotes |
| Runtime | One pass on live OKX data: 8 symbols in 9.1 s. Refuses to trade when started late |
| Docker | Image built; Compose service ran healthy; restarted by Docker after its process was killed, with state reloaded; processed the 09:00 UTC candle on 2026-11-10 11 s after the close (8 decisions, all held; XRP short refused at confidence 0.874). Test container stopped afterwards: **nothing is running now** |
| Tests | 106 passing, lint clean |
| Independent code review | A subagent reviewed the risk-critical paths: no way found around the gate or limits; 10 findings (2 high, in the live loop's handling of missing data), all fixed with regression tests |

## Result versus holding BTC

Out of sample, 2024-01-01 to 2026-11-10, $1,000 start, OKX taker fees, spread, slippage
and depth impact on, 8 parameter variants chosen on the prior 365 days and applied to the
next 91:

| | Return | Max drawdown | Trades |
|---|---|---|---|
| Rule baseline | -10.3% | -15.1% (kill switch tripped mid-2024, then idle) | 109, 33% winners, profit factor 0.79 net of fees |
| Hold BTC | +76.7% | -53.7% | 1 |

Diagnostic, each 91-day window with a fresh account: positive in 4 of 12 windows, mean
-3.3% per window against +8.4% for BTC. Full numbers:
`docs/results/walkforward-2026-11-10.json`.

Limits of this test: no historical order book (spread and depth are today's values
applied to history), perp funding not simulated, HYPE and SKY have about one year of
OKX history, and the setups were chosen with today's knowledge, which flatters them.

## Blocked

| Item | Exact missing piece |
|---|---|
| Haiku REFLEX on real data | An Anthropic API key (`ANTHROPIC_API_KEY`) on the runtime host. None in this session |
| Model-driven backtest after the June 2026 cutoff | Same key; then replay July to November 2026 |
| Measured REFLEX latency and real token count | Same key |
| Jev REFLEX | A TypeSafe key, and network access to `api.typesafe.ai` and `docs.typesafe.ai`. The API shape could not be confirmed from primary docs, so no adapter was written |
| OKX demo (testnet) orders | OKX demo-trading API keys. `exec/ccxt_broker.py` is tested against a fake exchange only |
| Telegram alerts | A bot token and chat id; and `api.telegram.org` is not reachable from this build environment |
| Live trading | Owner approval, trade-only keys, and plan steps A to C |
| Primary-source research | Web page fetching was blocked; web facts in `docs/RESEARCH.md` are from search summaries |

## Next

1. Owner: confirm the off-limits reading; supply an Anthropic key on a host that runs 24/7.
2. Run paper trading with the Haiku REFLEX for 30 days (plan step A).
3. Replay July to November 2026 with Haiku for a first model-driven, post-cutoff test.
4. Review calibration (Brier against the base rate) before changing any threshold.
5. Run the testnet checklist in `docs/RUNBOOK.md` once demo keys exist.
6. Improve the baseline or drop it: it currently has no edge.

## Decisions and reasons

| # | Decision | Reason |
|---|---|---|
| 1 | OKX | Bybit returned a geo-block from the build host; Binance futures were not reachable; OKX serves spot, swaps and demo trading on one host that ccxt supports |
| 2 | Longs on spot, shorts on perps | No liquidation or funding risk on the long side; perps only where a short needs them |
| 3 | Hourly candles | Slow enough that a model call (seconds) never matters, fast enough to manage stops. Configurable |
| 4 | Haiku 5.5 at low effort, no retries | The brief's fallback. A retry would break the latency budget; skipping a candle is always safe |
| 5 | No Jev adapter | The official docs were unreachable and the owner has no key. Writing one would mean inventing an API |
| 6 | Snapshot is the only model input | Setup thesis is compiled into `bias` and `inval` numbers, so nothing else varies per call |
| 7 | Gate takes the worse of model and code risk state | A model must not be able to talk the risk state down |
| 8 | Confidence is shrunk halfway to 0.5 before Kelly, capped at 0.80 | Uncalibrated confidence would oversize. A hypothesis until the nightly fit has 100 resolved decisions |
| 9 | Crisis pause is a renewing 72-candle cooldown | A permanent pause switched the system off for good at the first crisis reading. `crisis_cooldown_bars: 0` restores manual-only |
| 10 | Drawdown shrinks size instead of setting "near limit" | Gating on drawdown froze the system at 10.5%, below the kill level, with no way back |
| 11 | Extra limits: position at most 1x equity, spot buys at most cash | Tight stops otherwise produced positions larger than the account |
| 12 | Kill switch and reconciliation halt need a human | These mean something is wrong that code should not judge |
| 13 | Live needs four separate things | Mode, approval phrase, keys, and a policy promoted to `live` by a named person |
| 14 | Nightly review writes candidates only | "Never silently promote a policy" |
| 15 | Model backtests refused before the training cutoff | The model may remember earlier prices |
| 16 | PUMP excluded | Its revenue is memecoin trading; the owner excluded memecoins |
| 17 | Containers run as the host user | So they can write the mounted `var/` and `policies/` |
| 18 | Live loop prices every held position from book, then last candle, then last known price; stale prices block entries | Review finding: one unpriced position froze all exits and the kill check |
| 19 | Trade records are net of entry and exit fees | Review finding: gross records overstated win rate and profit factor |
| 20 | Environment network allowlist edited | Added OKX, Bybit, Binance public data, CoinGecko and DefiLlama hosts to the owner's "git" cloud environment, with approval, to read market data |

## Session log

- 2026-11-10: first session. Asked setup questions, researched regime and eight
  candidates with five research subagents, built and tested the system, ran the
  walk-forward, verified the Docker runtime, wrote docs.
