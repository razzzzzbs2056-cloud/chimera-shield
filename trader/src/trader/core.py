"""The decision pipeline, shared unchanged by paper trading, live trading and backtests.

Per closed candle, in this order:
  1. begin_bar      - mark to market, roll the day, read risk, latch the kill switch.
  2. process_exits  - stops, targets, time stops, thesis invalidation, kill flatten. Code only.
  3. decide         - snapshot -> REFLEX (with a deadline) -> gate -> size -> risk check -> order.
Exits never wait on the REFLEX. Entries are the only thing a REFLEX can influence, and
only by passing the gate; code sets every price, size and order.
"""

from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, replace
from typing import Callable

from trader import gate
from trader.alerts import Alerts
from trader.exec.broker import Broker, CostModel, Fill, Ledger, MarketView, reconcile
from trader.journal import Journal
from trader.policy import Policy
from trader.reflex.base import Reflex, timed_decide
from trader.risk.engine import Account, RiskEngine, RiskReading
from trader.risk.sizing import size_position
from trader.state.engine import AccountView, DataFault, Snapshot
from trader.types import Candle, Direction, OrderIntent, Position, Side


@dataclass(frozen=True)
class Setup:
    id: str
    symbol: str  # traded instrument, e.g. "AAVE/USDT" (spot) or "XRP/USDT:USDT" (swap)
    base: str
    bias: Direction
    market: str  # "spot" | "swap"
    invalidation_price: float | None = None
    lot: float = 0.0
    enabled: bool = True

    def __post_init__(self) -> None:
        if self.bias is Direction.NEUTRAL:
            raise ValueError(f"setup {self.id}: bias must be long or short")
        if self.bias is Direction.SHORT and self.market != "swap":
            raise ValueError(f"setup {self.id}: shorts need a swap market")


@dataclass(frozen=True)
class CoreConfig:
    tf_seconds: int = 3600
    latency_budget_s: float = 5.0
    defer_entries: bool = False  # backtest: fill at the next bar's open
    journal_all_decisions: bool = True


class TraderCore:
    def __init__(self, *, setups: list[Setup], policy: Policy, reflex: Reflex, broker: Broker,
                 risk: RiskEngine, account: Account, journal: Journal, alerts: Alerts,
                 cfg: CoreConfig, cost_of: Callable[[str], CostModel]):
        self.setups = {s.symbol: s for s in setups if s.enabled}
        self.policy = policy
        self.reflex = reflex
        self.broker = broker
        self.risk = risk
        self.account = account
        self.ledger = Ledger(account)
        self.journal = journal
        self.alerts = alerts
        self.cfg = cfg
        self.cost_of = cost_of
        self.pending: dict[str, OrderIntent] = {}
        self.exit_pending: dict[str, str] = {}
        self.paused_until: dict[str, int] = {}
        self.global_pause = False  # manual: stays set until a human runs `trader resume`
        self.global_pause_until = 0  # automatic crisis cooldown
        self.halt_reason = ""
        self.stats = {"candles": 0, "late": 0, "error": 0, "fault": 0, "entries": 0, "exits": 0,
                      "order_failures": 0, "escalations": 0}

    # ---- 1. risk -------------------------------------------------------------------
    def begin_bar(self, asof: int, marks: dict[str, float]) -> RiskReading:
        day = dt.datetime.fromtimestamp(asof, dt.timezone.utc).strftime("%Y-%m-%d")
        self.risk.roll_day(self.account, day, marks)
        reading = self.risk.read(self.account, marks)
        if reading.kill:
            for sym in self.account.positions:
                self.exit_pending.setdefault(sym, "kill_switch")
            self.pending.clear()
            if self.alerts.notify("critical", f"KILL SWITCH: {self.account.kill_reason}. Flattening; "
                                  "new orders blocked until a human clears it.", key="kill"):
                self.journal.write("events", {"ts": asof, "type": "kill_switch",
                                              "detail": self.account.kill_reason})
        problems = reconcile(self.account.positions, self.broker.positions())
        if problems and not self.halt_reason:
            self.halt_reason = "reconciliation mismatch: " + "; ".join(problems)
            self.alerts.notify("critical", f"HALT: {self.halt_reason}", key="reconcile")
            self.journal.write("events", {"ts": asof, "type": "halt", "detail": self.halt_reason})
        return reading

    def account_view(self, symbol: str, marks: dict[str, float], reading: RiskReading) -> AccountView:
        pos = self.account.positions.get(symbol)
        eq = reading.equity if reading.equity > 0 else 1.0
        inv = pos.qty * marks[symbol] / eq if pos else 0.0
        dpl = (reading.equity / self.account.day_start_equity - 1) * 100 if self.account.day_start_equity else 0.0
        return AccountView(inv, reading.leverage, reading.drawdown * 100, dpl, reading.open_positions,
                           reading.state)

    # ---- 2. exits ------------------------------------------------------------------
    def _exit_trigger(self, pos: Position, setup: Setup, asof: int, bar: Candle) -> tuple[str, float | None] | None:
        long = pos.qty > 0
        if long:
            if bar.low <= pos.stop_price:
                return "stop", min(pos.stop_price, bar.open)
            if bar.high >= pos.target_price:
                return "target", pos.target_price
        else:
            if bar.high >= pos.stop_price:
                return "stop", max(pos.stop_price, bar.open)
            if bar.low <= pos.target_price:
                return "target", pos.target_price
        inval = setup.invalidation_price
        if inval is not None and ((long and bar.close < inval) or (not long and bar.close > inval)):
            return "thesis_invalidated", None
        if asof - pos.opened_ts >= self.policy.time_stop_bars * self.cfg.tf_seconds:
            return "time_stop", None
        return None

    def process_exits(self, symbol: str, asof: int, bar: Candle,
                      view_at: Callable[[float | None], MarketView], marks: dict[str, float]) -> Fill | None:
        pos = self.account.positions.get(symbol)
        if pos is None:
            self.exit_pending.pop(symbol, None)
            return None
        setup = self.setups.get(symbol)
        ref: float | None = None
        if symbol in self.exit_pending:
            reason = self.exit_pending[symbol]
        else:
            trig = self._exit_trigger(pos, setup, asof, bar) if setup else ("orphan_position", None)
            if trig is None:
                return None
            reason, ref = trig
        view = view_at(ref)
        side = Side.SELL if pos.qty > 0 else Side.BUY
        intent = OrderIntent(symbol, side, abs(pos.qty), ref or view.mid, None, None, True, pos.setup_id,
                             f"{pos.setup_id}-{asof}-x", reason)
        verdict = self.risk.check_order(intent, self.account, marks)
        if not verdict.ok:  # cannot happen for a well-formed reduce-only order; never swallow it
            self.exit_pending[symbol] = reason
            self.alerts.notify("critical", f"exit for {symbol} blocked by risk layer: {verdict.reasons}",
                               key=f"exitblock:{symbol}")
            return None
        fill = self.broker.place(intent, view)
        self.journal.write("fills", {**fill.__dict__, "kind": "exit", "reason": reason})
        if fill.done:
            trade = self.ledger.apply(fill, intent)
            if trade:
                self.journal.write("trades", trade)
            self.stats["exits"] += 1
            if symbol in self.account.positions:
                self.exit_pending[symbol] = reason  # partial: finish next bar
            else:
                self.exit_pending.pop(symbol, None)
        else:
            self.exit_pending[symbol] = reason  # retried on every bar until it fills
            self.stats["order_failures"] += 1
            self.alerts.notify("error", f"EXIT ORDER FAILED for {symbol} ({reason}): {fill.reason}. "
                               "Will retry next candle.", key=f"exitfail:{symbol}")
        return fill

    # ---- 3. entries ----------------------------------------------------------------
    def _notional_cap(self, setup: Setup, equity: float, marks: dict[str, float]) -> float:
        """Largest notional this setup may open now: per-position cap, and for spot, cash on hand
        (spot cannot borrow, so spot holdings plus pending spot buys may not exceed equity)."""
        cap = self.risk.limits.max_position_frac * equity
        if setup.market == "spot":
            spot = sum(p.notional(marks[s]) for s, p in self.account.positions.items()
                       if s in self.setups and self.setups[s].market == "spot")
            spot += sum(i.qty * i.ref_price for s, i in self.pending.items()
                        if s in self.setups and self.setups[s].market == "spot")
            cap = min(cap, equity - spot)
        return max(0.0, cap)

    def _paused(self, symbol: str, asof: int) -> bool:
        return bool(self.global_pause or self.halt_reason or self.global_pause_until > asof
                    or self.paused_until.get(symbol, 0) > asof)

    def decide(self, symbol: str, asof: int, snap: Snapshot | DataFault, view: MarketView | None,
               marks: dict[str, float], reading: RiskReading) -> dict:
        setup = self.setups[symbol]
        self.stats["candles"] += 1
        rec: dict = {"ts": asof, "symbol": symbol, "setup": setup.id, "bias": setup.bias.value,
                     "policy": self.policy.version, "reflex": self.reflex.name, "status": "ok",
                     "action": "hold", "reasons": []}
        if isinstance(snap, DataFault) or view is None:
            fault = snap if isinstance(snap, DataFault) else DataFault("missing_data", "no market view")
            rec.update(status="fault", reasons=[fault.kind], detail=fault.detail)
            self.stats["fault"] += 1
            self.alerts.notify("warning", f"data fault on {symbol}: {fault}", key=f"fault:{symbol}:{fault.kind}")
            self.journal.write("decisions", rec)
            return rec

        out = timed_decide(self.reflex, snap, self.cfg.latency_budget_s)
        rec.update(latency_ms=round(out.latency_ms, 2), px=snap.px, atr=snap.atr)
        if out.decision is None:
            rec.update(status=out.status, reasons=[f"reflex_{out.status}"], detail=out.error)
            self.stats[out.status] += 1
            self.alerts.notify("warning", f"REFLEX {out.status} on {symbol} ({out.latency_ms:.0f} ms); "
                               "candle skipped.", key=f"reflex:{out.status}")
            self.journal.write("decisions", {**rec, "snapshot": snap.model_dump(mode="json")})
            return rec

        d = out.decision
        g = gate.evaluate(d, reading.state, setup.bias, self.policy, self._paused(symbol, asof))
        rec.update(decision=d.model_dump(mode="json"), action=g.action.value, reasons=list(g.reasons))
        if g.action is gate.GateAction.PAUSE:
            self.stats["escalations"] += 1
            cool = self.policy.crisis_cooldown_bars
            if g.global_pause and cool <= 0:
                self.global_pause = True
            elif g.global_pause:
                self.global_pause_until = max(self.global_pause_until, asof + cool * self.cfg.tf_seconds)
            else:
                self.paused_until[symbol] = asof + self.policy.pause_bars * self.cfg.tf_seconds
            scope = (("ALL new risk paused until a human resumes" if cool <= 0 else
                      f"ALL new risk paused for {cool} candles after the last crisis reading")
                     if g.global_pause else f"{symbol} paused for {self.policy.pause_bars} candles")
            if self.alerts.notify("critical" if g.global_pause else "warning",
                                  f"ESCALATION {symbol}: {', '.join(g.reasons)} "
                                  f"(regime={d.regime.value}, conf={d.direction_confidence:.2f}). {scope}.",
                                  key=f"escalate:{'global' if g.global_pause else symbol}"):
                self.journal.write("events", {"ts": asof, "type": "escalation", "symbol": symbol,
                                              "reasons": list(g.reasons), "global": g.global_pause})
        elif g.action is gate.GateAction.ENTER:
            self._try_enter(setup, asof, snap, d.direction_confidence, view, marks, reading, rec)

        if self.cfg.journal_all_decisions or d.direction is not Direction.NEUTRAL:
            self.journal.write("decisions", {**rec, "snapshot": snap.model_dump(mode="json")})
        return rec

    def _try_enter(self, setup: Setup, asof: int, snap: Snapshot, confidence: float, view: MarketView,
                   marks: dict[str, float], reading: RiskReading, rec: dict) -> None:
        sym, L = setup.symbol, self.risk.limits
        if sym in self.account.positions or sym in self.pending:
            rec.update(action="hold", reasons=["already_in_position"])
            return
        if len(self.account.positions) + len(self.pending) >= L.max_open_positions:
            rec.update(action="hold", reasons=["max_open_positions"])
            return
        long = setup.bias is Direction.LONG
        px = view.ask if long else view.bid
        dist = self.policy.stop_atr_mult * snap.atr / 100 * px
        stop = px - dist if long else px + dist
        target = px + self.policy.rr * dist if long else px - self.policy.rr * dist
        p_win = self.policy.calibrator.p_win(confidence)
        cost = self.cost_of(sym)
        spread_bps = (view.ask - view.bid) / view.mid * 1e4
        # Budget for market impact as if the order were as large as the position cap allows.
        cap = self.risk.limits.max_position_frac * reading.equity
        cost_frac = cost.round_trip_frac(spread_bps, cap / view.depth_usd if view.depth_usd > 0 else 1.0)
        pending_gross = sum(i.qty * i.ref_price for i in self.pending.values())
        scale = self.risk.risk_scale(reading.drawdown)  # smaller bets the deeper the drawdown
        rec["risk_scale"] = round(scale, 3)
        size = size_position(
            equity=reading.equity, price=px, stop=stop, p_win=p_win, rr=self.policy.rr,
            risk_per_trade=L.risk_per_trade * scale, kelly_mult=self.policy.kelly_mult, cost_frac=cost_frac,
            gross_exposure=self.account.gross_exposure(marks) + pending_gross, max_leverage=L.max_leverage,
            depth_usd=view.depth_usd or None, lot=setup.lot, min_notional=cost.min_notional,
        )
        rec.update(p_win=round(p_win, 4), kelly=round(size.kelly_full, 4), net_rr=round(size.net_rr, 3),
                   stop=stop, target=target)
        qty = min(size.qty, self._notional_cap(setup, reading.equity, marks) / px)
        if setup.lot > 0:
            qty = int(qty / setup.lot + 1e-9) * setup.lot
        if qty <= 0 or qty * px < cost.min_notional:
            rec.update(action="hold", reasons=[f"size:{size.reason if size.qty <= 0 else 'no_cash_or_cap'}"])
            return
        size = replace(size, qty=qty, risk_frac=qty * (dist + px * cost_frac) / reading.equity)
        intent = OrderIntent(sym, Side.BUY if long else Side.SELL, size.qty, px, stop, target, False,
                             setup.id, f"{setup.id}-{asof}-e", "entry")
        rec.update(qty=size.qty, risk_frac=round(size.risk_frac, 5), cost_frac=round(cost_frac, 6))
        if self.cfg.defer_entries:
            self.pending[sym] = intent
            rec["action"] = "enter_pending"
        else:
            fill = self._execute_entry(intent, view, marks)
            rec.update(action="enter" if fill and fill.done else "enter_failed",
                       fill_price=fill.price if fill else None)

    def execute_pending(self, symbol: str, view: MarketView, marks: dict[str, float]) -> Fill | None:
        intent = self.pending.pop(symbol, None)
        return self._execute_entry(intent, view, marks) if intent else None

    def _execute_entry(self, intent: OrderIntent, view: MarketView, marks: dict[str, float]) -> Fill | None:
        """Re-price at the executable quote, shrink to fit the risk budget, then the final risk check."""
        long = intent.side is Side.BUY
        px = view.ask if long else view.bid
        marks = {**marks, intent.symbol: view.mid}
        cost = self.cost_of(intent.symbol)
        equity = self.account.equity(marks)
        cap = self.risk.limits.max_position_frac * equity
        cost_frac = cost.round_trip_frac((view.ask - view.bid) / view.mid * 1e4,
                                         cap / view.depth_usd if view.depth_usd > 0 else 1.0)
        dist = abs(px - (intent.stop_price or px))
        qty = intent.qty
        if dist > 0:
            qty = min(qty, self.risk.limits.risk_per_trade * equity / (dist + px * cost_frac))
        setup = self.setups.get(intent.symbol)
        if setup is not None:
            qty = min(qty, self._notional_cap(setup, equity, marks) / px)
        if qty <= 0:
            return None
        intent = replace(intent, qty=qty, ref_price=px)
        verdict = self.risk.check_order(intent, self.account, marks, est_cost=qty * px * cost_frac)
        if not verdict.ok:
            self.journal.write("fills", {"client_id": intent.client_id, "symbol": intent.symbol, "kind": "entry",
                                         "status": "blocked_by_risk", "reasons": list(verdict.reasons),
                                         "ts": view.ts})
            return None
        fill = self.broker.place(intent, view)
        self.journal.write("fills", {**fill.__dict__, "kind": "entry", "stop": intent.stop_price,
                                     "target": intent.target_price})
        if fill.done:
            self.ledger.apply(fill, intent)
            pos = self.account.positions[intent.symbol]  # align the open time to the candle grid so the
            tf = self.cfg.tf_seconds                     # time stop counts the same bars live and in backtests
            self.account.positions[intent.symbol] = replace(pos, opened_ts=fill.ts // tf * tf)
            self.stats["entries"] += 1
        else:
            self.stats["order_failures"] += 1
            self.alerts.notify("error", f"ENTRY ORDER {fill.status} for {intent.symbol}: {fill.reason}. "
                               "Not retried this candle.", key=f"entryfail:{intent.symbol}")
        return fill
