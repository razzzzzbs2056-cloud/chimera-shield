"""24/7 runtime: one pass per closed candle, state saved after every pass.

Survives restarts: the account, pauses, kill latch and last processed candle are loaded
from var/state.json. A heartbeat file feeds the container health check. Any error
fetching data becomes a DataFault for that symbol (no new orders); exits still run
whenever a price is available.
"""

from __future__ import annotations

import logging
import math
import time
from pathlib import Path

from trader.alerts import Alerts
from trader.config import Config
from trader.core import CoreConfig, TraderCore
from trader.data.market import TF_SECONDS, view_from_book
from trader.exec.broker import MarketView, PaperBroker
from trader.journal import Journal, load_state, save_state
from trader.policy import Policy
from trader.reflex.base import Reflex
from trader.risk.engine import Account, RiskEngine
from trader.state.engine import DataFault, EngineConfig, build_snapshot
from trader.types import Candle

log = logging.getLogger("trader.runtime")


class Runner:
    def __init__(self, cfg: Config, policy: Policy, data, broker, reflex: Reflex, alerts: Alerts,
                 root: Path, clock=time.time, max_start_delay_s: float = 120.0):
        self.cfg, self.data, self.alerts, self.clock = cfg, data, alerts, clock
        self.tf_s = TF_SECONDS[cfg.timeframe]
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.state_path = self.root / "state.json"
        self.max_start_delay_s = max_start_delay_s
        self.ecfg = EngineConfig(tf=cfg.timeframe, tf_seconds=self.tf_s, max_book_age_s=cfg.max_book_age_s,
                                 max_clock_skew_s=cfg.max_clock_skew_s, require_book=True)
        loaded = load_state(self.state_path)
        if loaded:
            account, extra = loaded
        else:
            account = Account(balance=cfg.paper_balance, peak_equity=cfg.paper_balance, day="",
                              day_start_equity=cfg.paper_balance)
            extra = {}
        if isinstance(broker, PaperBroker):  # the paper "exchange" restarts with us: reseed it
            broker._pos = {s: p.qty for s, p in account.positions.items()}
        self.core = TraderCore(
            setups=cfg.enabled_setups(), policy=policy, reflex=reflex, broker=broker,
            risk=RiskEngine(cfg.limits.build()), account=account, journal=Journal(self.root / "journal"),
            alerts=alerts, cfg=CoreConfig(tf_seconds=self.tf_s, latency_budget_s=cfg.reflex.latency_budget_s),
            cost_of=cfg.cost_of)
        self.core.global_pause = extra.get("global_pause", False)
        self.core.global_pause_until = int(extra.get("global_pause_until", 0))
        self.core.paused_until = {k: int(v) for k, v in extra.get("paused_until", {}).items()}
        self.core.exit_pending = dict(extra.get("exit_pending", {}))
        self.core.halt_reason = extra.get("halt_reason", "")
        self.last_asof = int(extra.get("last_asof", 0))
        self.marks: dict[str, float] = dict(extra.get("marks", {}))
        self.mark_ts: dict[str, int] = {k: int(v) for k, v in extra.get("mark_ts", {}).items()}
        self.last_funding = int(extra.get("last_funding", 0))

    def save(self) -> None:
        c = self.core
        save_state(self.state_path, c.account, {
            "global_pause": c.global_pause, "global_pause_until": c.global_pause_until,
            "paused_until": c.paused_until, "exit_pending": c.exit_pending,
            "halt_reason": c.halt_reason, "last_asof": self.last_asof, "marks": self.marks,
            "mark_ts": self.mark_ts, "last_funding": self.last_funding,
            "policy": c.policy.version, "reflex": c.reflex.name, "mode": self.cfg.mode, "stats": c.stats,
        })
        (self.root / "heartbeat").write_text(str(int(self.clock())))

    def _fetch(self, symbol: str) -> tuple:
        """Returns (candles, book, funding, fault). Each feed is fetched on its own so that losing
        one (say the order book) still leaves the others usable for pricing and exits. Never raises."""
        out: list = [None, None, None, None]
        for i, call in enumerate((lambda: self.data.candles(symbol, 300), lambda: self.data.book(symbol),
                                  lambda: self.data.funding_pct(symbol))):
            try:
                out[i] = call()
            except DataFault as e:
                out[3] = out[3] or e
            except Exception as e:
                out[3] = out[3] or DataFault("exchange_error", f"{symbol}: {type(e).__name__}")
        return tuple(out)

    def run_once(self) -> list[dict]:
        """Process the most recent closed candle once. Returns the decision records.

        Order matters: price everything we hold (falling back to the last candle, then to the
        last known price), run the risk read and kill check, manage EVERY open position, and
        only then consider entries. Missing data for one symbol never stops the others, and
        any position priced from stale data blocks all new entries for the pass.
        """
        try:
            ex_now = self.data.exchange_time()
        except Exception as e:
            self.alerts.notify("error", f"exchange time unavailable: {type(e).__name__}", key="extime")
            self.save()
            return []
        local_now = self.clock()
        asof = int(ex_now // self.tf_s) * self.tf_s
        if asof <= self.last_asof:
            self.save()
            return []
        late = ex_now - asof > self.max_start_delay_s  # e.g. we were down at the close: exits only
        core = self.core
        try:
            ctx = self.data.candles(self.cfg.context_symbol, 300)
        except Exception as e:
            ctx = DataFault("exchange_error", f"context: {type(e).__name__}")

        symbols = list(core.setups) + [s for s in core.account.positions if s not in core.setups]
        fetched = {s: self._fetch(s) for s in symbols}
        views: dict[str, object] = {}
        closed_bars: dict[str, list] = {}
        for s, (candles, book, _, _fault) in fetched.items():
            closed_bars[s] = [c for c in candles or [] if c.ts_close <= asof]
            try:
                views[s] = view_from_book(s, book, contract_size=self.data.contract_size(s) if ":" in s else 1.0)
                self.marks[s], self.mark_ts[s] = views[s].mid, int(ex_now)
            except Exception:
                if closed_bars[s]:  # no usable book: the last closed bar is the next best price
                    self.marks[s], self.mark_ts[s] = closed_bars[s][-1].close, closed_bars[s][-1].ts_close

        # Every open position needs a price. Unknown or stale prices make the account "not valued".
        unvalued = []
        for s, pos in core.account.positions.items():
            if s not in self.marks:
                self.marks[s], self.mark_ts[s] = pos.entry_price, 0
            if ex_now - self.mark_ts.get(s, 0) > 2 * self.tf_s:
                unvalued.append(s)
        if unvalued:
            self.alerts.notify("critical", f"STALE PRICES for open positions {unvalued}: equity and the kill "
                               "switch are computed from old prices. No new entries. Check the exchange and "
                               "close by hand if this persists.", key="stale_marks")
        marks = {s: self.marks[s] for s in symbols if s in self.marks}
        if not marks:
            self.alerts.notify("error", "no market data for any symbol; skipping candle", key="nodata")
            self.save()
            return []
        self._apply_funding(asof, fetched, marks)
        reading = core.begin_bar(asof, marks)
        core.journal.write("equity", {"ts": asof, "equity": round(reading.equity, 4),
                                      "drawdown": round(reading.drawdown, 5)})  # for the dashboard chart

        # Exits first, for everything held (including positions whose setup was removed).
        for s in list(core.account.positions):
            pos = core.account.positions[s]
            bars = [c for c in closed_bars.get(s, []) if c.ts_close > max(self.last_asof, pos.opened_ts)]
            view = views.get(s)
            if view is None and s in closed_bars and closed_bars[s]:
                px = closed_bars[s][-1].close  # degraded: quote around the last close, with a wide spread
                view = MarketView(s, px * 0.999, px * 1.001, 0.0, closed_bars[s][-1].ts_close)
            if view is None:
                self.alerts.notify("critical", f"cannot manage open position {s}: no market data at all",
                                   key=f"noexit:{s}")
                continue
            if not bars:
                bars = closed_bars.get(s, [])[-1:]
            # One bar covering everything since the last check, widened by the live price, so a stop
            # touched in a skipped candle or since the last close is not missed.
            lo = min([c.low for c in bars] + [view.bid])
            hi = max([c.high for c in bars] + [view.ask])
            span = Candle(bars[0].ts_open, bars[-1].ts_close, bars[0].open, hi, lo, view.mid, 0.0) if bars \
                else Candle(asof - self.tf_s, asof, view.mid, hi, lo, view.mid, 0.0)
            core.process_exits(s, asof, span, lambda ref, v=view: v, marks)

        records = []
        for s in core.setups:
            f = fetched[s]
            view = views.get(s)
            if f[3] is not None:
                snap: object = f[3]
            elif isinstance(ctx, DataFault):
                snap = ctx
            elif late:
                snap = DataFault("late_start", f"{ex_now - asof:.0f}s after the close")
            elif unvalued:
                snap = DataFault("stale_marks", f"positions without a fresh price: {unvalued}")
            else:
                try:
                    # Decision time is "now" on the exchange clock: the book is live, bars must be closed.
                    decision_ts = math.ceil(ex_now + (self.clock() - local_now))
                    snap = build_snapshot(
                        asof=decision_ts, symbol=s, cfg=self.ecfg, bias=core.setups[s].bias,
                        candles=closed_bars[s], btc_candles=[c for c in ctx if c.ts_close <= asof], book=f[1],
                        funding_pct=f[2], invalidation_price=core.setups[s].invalidation_price,
                        account=core.account_view(s, marks, reading), local_ts=local_now, exchange_ts=ex_now)
                except DataFault as e:
                    snap = e
            reading = core.risk.read(core.account, marks)  # re-read: an earlier symbol may have traded
            records.append(core.decide(s, asof, snap, view, marks, reading))
        self.last_asof = asof
        self.save()
        return records

    def _apply_funding(self, asof: int, fetched: dict, marks: dict[str, float]) -> None:
        """Paper approximation of perp funding: charge the current rate on 8-hour boundaries
        (00:00, 08:00, 16:00 UTC). On a real exchange the venue settles funding itself."""
        if asof % 28800 != 0 or asof <= self.last_funding or not isinstance(self.core.broker, PaperBroker):
            return
        self.last_funding = asof  # recorded first, so a retried pass can never charge twice
        for s, pos in list(self.core.account.positions.items()):
            f = fetched.get(s)
            if ":" not in s or f is None or f[2] is None:
                continue
            paid = self.core.ledger.apply_funding(s, f[2] / 100, marks[s])
            self.core.journal.write("events", {"ts": asof, "type": "funding", "symbol": s, "paid": paid,
                                               "rate_pct": f[2], "qty": pos.qty})

    def run_forever(self, poll_s: float = 5.0) -> None:
        log.info("runner started: mode=%s policy=%s reflex=%s setups=%d", self.cfg.mode,
                 self.core.policy.version, self.core.reflex.name, len(self.core.setups))
        while True:
            try:
                recs = self.run_once()
                for r in recs:
                    log.info("%s %s %s %s", r["symbol"], r["status"], r["action"], ",".join(r["reasons"]))
            except Exception as e:  # never die on one bad pass; the next candle gets a fresh try
                log.exception("pass failed")
                self.alerts.notify("error", f"runtime pass failed: {type(e).__name__}", key="passfail")
            time.sleep(poll_s)


def heartbeat_ok(root: Path, max_age_s: float, now: float | None = None) -> tuple[bool, str]:
    p = Path(root) / "heartbeat"
    if not p.exists():
        return False, "no heartbeat file"
    age = (now or time.time()) - int(p.read_text().strip() or 0)
    return age <= max_age_s, f"heartbeat age {age:.0f}s (limit {max_age_s:.0f}s)"
