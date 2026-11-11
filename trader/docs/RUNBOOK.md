# Runbook

All commands run from `trader/`. Inside Docker, prefix with
`docker compose exec trader` (for example `docker compose exec trader trader status`).

## First start (paper trading)
```bash
cp .env.example .env
```
```bash
mkdir -p var data_cache && echo "TRADER_UID=$(id -u)" >> .env && echo "TRADER_GID=$(id -g)" >> .env
```
```bash
docker compose up -d --build
```
```bash
docker compose ps
```
`trader` should show `healthy` within about two minutes. Paper mode needs no keys: it
reads public OKX data and simulates fills. To survive host reboots, enable the Docker
service at boot (`sudo systemctl enable docker`); `restart: unless-stopped` does the rest.

To use the Haiku REFLEX, put `ANTHROPIC_API_KEY` in `.env`, set `reflex.kind: haiku` in
`config/default.yaml`, and restart: `docker compose up -d`.

For Telegram alerts, put `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` in `.env` and restart.

## Dashboard (website)
`docker compose up -d` also starts a read-only web page on the server at
`http://localhost:8080`. It shows whether the bot is running, account value, drawdown
against the kill switch, open positions, each coin's latest verdict, closed trades,
alerts and the last nightly review. It refreshes every 30 seconds and works on a phone.

To view it from your own computer, open a tunnel and then browse to
`http://localhost:8080`:
```bash
ssh -L 8080:localhost:8080 <user>@<server>
```
Without Docker: `trader dashboard`.

The page cannot place, change or cancel anything; resuming, clearing the kill switch and
promoting policies stay on the command line. It has **no login**, so the port is bound to
the server's loopback address. Do not expose it to the internet as it is; put it behind a
VPN or a reverse proxy with authentication if you want remote access without SSH.

## Daily checks
| Question | Command |
|---|---|
| Is it alive? | The dashboard, `docker compose ps` (health) or `trader health` |
| What does it hold? | `trader status` |
| What did it decide? | `tail var/journal/decisions.jsonl` |
| What traded? | `cat var/journal/trades.jsonl` |
| Last night's review | newest file in `var/reports/` |

## Alerts and what to do
| Alert | Meaning | Action |
|---|---|---|
| `KILL SWITCH` | Drawdown reached 15%. Positions are being closed, new orders blocked | Find the cause in the journal. Only then: `trader clear-kill --i-have-reviewed-the-drawdown`, restart |
| `HALT: reconciliation mismatch` | Our ledger and the exchange disagree | Compare `trader status` with the exchange. Fix by hand, then `trader resume`, restart |
| `ESCALATION ... regime_crisis` | REFLEX read a crisis. New risk pauses 72 candles after the last such reading | Review the market. `trader resume` lifts it early |
| `ESCALATION ... confidence_below_pause_floor` | REFLEX unsure. That symbol pauses 12 candles | Usually none |
| `EXIT ORDER FAILED` | A closing order failed; it retries every candle | If it repeats, close the position by hand on the exchange |
| `cannot price exit` / `no price for open positions` | No market data while holding a position | Check exchange status and network; exchange-side stops (live only) still stand |
| `data fault` / `REFLEX late` / `REFLEX error` | Candle skipped, no order | None unless it persists |

Pauses, the kill latch and halts are stored in `var/state.json` and survive restarts.

## Stop everything now
```bash
docker compose stop trader
```
This stops new decisions. It does not close positions. In paper mode nothing is at risk.
In live mode, close positions on the exchange yourself; entries carry an exchange-side
stop-loss, which stays active.

## Backtest
```bash
trader backtest --download --out docs/results/walkforward-$(date -u +%F).json
```
Prints first whether the strategy beat holding BTC after costs.

## Policies
```bash
trader policy list
```
```bash
trader policy promote <version> --stage paper --approved-by "<your name>"
```
```bash
trader policy rollback --stage paper --approved-by "<your name>"
```
The nightly review only writes candidates to `policies/candidates/`. Read its report,
then promote by hand if you agree. Restart the trader service to load a new policy.

## Exchange keys
Create OKX API keys with **Trade** permission only, **withdrawals off**, and an **IP
allowlist** containing the server's address. Put them in `.env` (git-ignored), never in
the repository or in chat. The code never logs them.

## Testnet checklist (before any live order)
`exec/ccxt_broker.py` has only been tested against a fake exchange. With OKX
demo-trading keys in `.env` and `mode: testnet`:
1. `trader once` places no order on a quiet candle and exits cleanly.
2. Force one entry (temporarily lower `min_confidence` in a test policy). Check on OKX
   demo: size is right in coin terms for spot and in contracts for swaps, and a stop-loss
   order is attached.
3. Force the exit. Check the position is flat and `trader status` agrees.
4. Restart mid-position. Reconciliation must pass with no `HALT`.
5. Revoke the key mid-run. The order must fail, alert, and leave the ledger unchanged.

## Going live (needs the owner's explicit approval)
All of these, in order:
1. Plan steps A to C passed (`docs/PLAN.md`).
2. `trader policy promote <version> --stage live --approved-by "<owner>"` (only works if
   that version is already active in paper and the interlock below is set).
3. `mode: live` in the config.
4. `TRADER_LIVE_APPROVED=I-APPROVE-LIVE-TRADING` in `.env`.
5. Start with a balance you can afford to lose entirely.
Without every item, the process refuses to start in live mode.

## Roll back code
```bash
git log --oneline -- trader
```
```bash
git checkout <good-commit> -- trader && docker compose up -d --build
```
