"""Real-exchange broker through ccxt (OKX). Sandbox (demo trading) unless live is approved.

STATUS: written against the ccxt unified API and unit-tested with a fake exchange only.
It has NOT been run against OKX demo or live: this session has no exchange keys.
Run the testnet checklist in docs/RUNBOOK.md before trusting it.

Keys come from the environment, are passed straight to ccxt, and are never logged.
Use keys with trading permission only: withdrawals off, IP-whitelisted.
"""

from __future__ import annotations

import logging

from trader.exec.broker import Fill, MarketView
from trader.types import OrderIntent, Side

log = logging.getLogger("trader.exec")


class CcxtBroker:
    def __init__(self, exchange, *, sandbox: bool, live_allowed: bool):
        if not sandbox and not live_allowed:
            raise PermissionError("live trading is not approved; refusing to build a live broker")
        self.ex = exchange
        self.sandbox = sandbox
        self._seen: dict[str, Fill] = {}

    def _amount(self, symbol: str, qty: float) -> float:
        market = self.ex.market(symbol)
        if market.get("contract"):
            qty = qty / float(market.get("contractSize") or 1.0)  # swaps are ordered in contracts
        return float(self.ex.amount_to_precision(symbol, qty))

    def place(self, intent: OrderIntent, view: MarketView) -> Fill:
        if intent.client_id in self._seen:
            return self._seen[intent.client_id]

        def no(status: str, reason: str) -> Fill:
            return Fill(intent.client_id, intent.symbol, intent.side, 0.0, 0.0, 0.0, view.ts, status, reason)

        is_swap = ":" in intent.symbol
        cid = "".join(ch for ch in intent.client_id if ch.isalnum())[:32]  # OKX: alphanumeric, <= 32
        params: dict = {"clOrdId": cid, "tdMode": "cross" if is_swap else "cash"}
        if is_swap and intent.reduce_only:
            params["reduceOnly"] = True
        if not is_swap and intent.side is Side.BUY:
            params["tgtCcy"] = "base_ccy"  # size spot market buys in the base coin, like every other order
        if intent.stop_price and not intent.reduce_only:
            params["stopLoss"] = {"triggerPrice": float(self.ex.price_to_precision(intent.symbol, intent.stop_price))}
        try:
            amount = self._amount(intent.symbol, intent.qty)
            if amount <= 0:
                return no("rejected", "amount_rounds_to_zero")
            o = self.ex.create_order(intent.symbol, "market", intent.side.value, amount, None, params)
            if o.get("status") not in ("closed", "filled") or not o.get("average"):
                o = self.ex.fetch_order(o["id"], intent.symbol)
        except Exception as e:  # network, rejection, insufficient funds: all are a failed order
            log.error("order failed for %s: %s", intent.symbol, type(e).__name__)
            return no("failed", type(e).__name__)
        filled = float(o.get("filled") or 0.0)
        market = self.ex.market(intent.symbol)
        if market.get("contract"):
            filled *= float(market.get("contractSize") or 1.0)
        price = float(o.get("average") or 0.0)
        if filled <= 0 or price <= 0:
            return no("failed", f"no_fill_status_{o.get('status')}")
        fee = float((o.get("fee") or {}).get("cost") or 0.0)
        status = "filled" if filled >= intent.qty * 0.999 else "partial"
        fill = Fill(intent.client_id, intent.symbol, intent.side, filled, price, abs(fee), view.ts, status)
        self._seen[intent.client_id] = fill
        return fill

    def positions(self) -> dict[str, float]:
        """Signed base quantities per symbol: swaps from positions, spot from balances."""
        out: dict[str, float] = {}
        for p in self.ex.fetch_positions():
            size = float(p.get("contracts") or 0.0) * float(p.get("contractSize") or 1.0)
            if size:
                out[p["symbol"]] = size if p.get("side") == "long" else -size
        bal = self.ex.fetch_balance().get("total", {})
        for ccy, amt in bal.items():
            if ccy not in ("USDT", "USD", "USDC") and float(amt or 0.0) > 0:
                out[f"{ccy}/USDT"] = float(amt)
        return out
