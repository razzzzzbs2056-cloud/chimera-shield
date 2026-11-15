# trader-freqtrade

The rule strategy from `../trader`, rebuilt on [freqtrade](https://github.com/freqtrade/freqtrade),
the open-source crypto trading bot. Paper trading (dry run) only until the owner approves live.

**It does not beat holding BTC.** See Results.

## What comes from where

| Part | Source |
|---|---|
| Exchange connection, orders, dry-run wallet, trade database | freqtrade (uses ccxt) |
| Backtester, data download | freqtrade |
| Web UI (FreqUI), Telegram bot, REST API | freqtrade |
| Entry rule, gate, sizing, exits, account limits | `user_data/strategies/ChimeraRule.py` (this repo) |

Freqtrade is GPL-3.0. Nothing from it is copied here; the strategy file imports it. If you
distribute this folder together with freqtrade, treat it as GPL-3.0.

## What changed from `../trader`

| Topic | `../trader` | Here |
|---|---|---|
| Markets | Longs on spot, shorts on perps | All eight coins on OKX USDT perps at 1x leverage. Freqtrade runs one market type per bot, and one bot keeps the account limits global |
| Decision maker | Rule baseline, or Claude Haiku behind the same interface | Rule only. The model layer is not ported |
| Kill switch and daily loss | On marked equity, every candle | On **realised** equity (closed trades). An open loss counts only when the trade closes; each open trade is still bounded by its stop |
| Order-book check | Every decision | Live and dry run only, at order time |
| Spread and depth impact | Modelled per coin | Folded into a flat fee of 0.07% per side in backtests |
| Policy versions, nightly review | Yes | Not ported. Numbers are constants at the top of the strategy file |
| Dashboard | Custom read-only page | FreqUI, which has start/stop and force-exit buttons, behind a password |

Same as before: the scoring rule (a test checks it bar by bar against the original),
quality >= 2 and confidence > 0.88 gate, crisis cooldown, quarter-Kelly sizing capped at 2% of
equity at risk, ATR stop, 2:1 target, 96-hour time stop, invalidation prices, 3 open
positions, 5% daily loss stop, 15% drawdown kill switch that only a human can clear.

## Set up

Needs Python 3.11 or newer. Freqtrade's own install guide covers Windows:
https://www.freqtrade.io/en/stable/installation/

```bash
python3 -m venv .venv && .venv/bin/pip install freqtrade pytest
```

## Test

```bash
.venv/bin/python -m pytest tests
```

## Backtest

```bash
.venv/bin/freqtrade download-data -c config.json --userdir user_data --timeframes 1h --timerange 20230101- --pairs BTC/USDT:USDT HYPE/USDT:USDT AAVE/USDT:USDT SKY/USDT:USDT UNI/USDT:USDT TRX/USDT:USDT LINK/USDT:USDT XRP/USDT:USDT ADA/USDT:USDT
```

```bash
.venv/bin/freqtrade backtesting -c config.json --userdir user_data --strategy ChimeraRule --timerange 20240101-20261110 --fee 0.0007
```

## Paper trade

No keys needed. Trades are simulated against live OKX prices with a 1,000 USDT wallet.

```bash
.venv/bin/freqtrade trade -c config.json --userdir user_data --strategy ChimeraRule
```

To get the web UI, copy `config-private.example.json` to `config-private.json`, replace every
`REPLACE` value, set `listen_ip_address` to `127.0.0.1`, then:

```bash
.venv/bin/freqtrade install-ui --userdir user_data
```

```bash
.venv/bin/freqtrade trade -c config.json -c config-private.json --userdir user_data --strategy ChimeraRule
```

Open http://localhost:8080 and log in with the username and password you set.

With Docker instead (after creating `config-private.json`, leaving `listen_ip_address` at `0.0.0.0`;
the port is published to this computer only):

```bash
docker compose up -d
```

## Kill switch

When realised equity falls 15% from its peak, the bot closes open trades and takes no new
ones. It stays that way across restarts. To clear it after you have looked at what happened,
add the current UTC time to `config-private.json` and restart:

```json
{"chimera_kill_cleared_at": "2026-11-15T14:00:00+00:00"}
```

## Results

One pass, 2024-01-01 to 2026-11-10, 1,000 USDT, fixed numbers (nothing fitted on this data),
0.07% per side. Full numbers: `docs/results/backtest-2026-11-15.json`.

| | Return | Max drawdown | Trades |
|---|---|---|---|
| ChimeraRule on freqtrade | +18.8% | -15.2% (kill switch tripped 2025-05-23, idle for the 17 months after) | 521, 38% winners, profit factor 1.06 |
| Hold BTC (OKX perp) | +76.7% | -53.8% | 1 |

- All of the profit came from the two shorts (+212 USDT). The six longs lost 24 USDT.
- A profit factor of 1.06 over 521 trades is too thin to call an edge.
- The custom engine in `../trader` gave -10.3% over the same period. The two differ in
  market type, cost model and walk-forward parameter choice, so neither number confirms the other.
- Limits held: worst single trade lost 1.95% of equity, worst day 4.14%.

Not modelled: funding before 2026-08-10 (OKX serves about three months of history), order-book
spread and depth, and the hindsight in choosing these coins in November 2026.

## Not verified

- Docker Compose file: syntax checked only. The Docker daemon was not available in the build session.
- FreqUI and Telegram: not started in the build session.
- Websocket price feed: blocked in the build session; the bot was run on REST polling only.
- Any real or testnet order. Going live needs the owner's explicit approval, trade-only keys
  in `config-private.json`, and `dry_run` set to false by the owner.
