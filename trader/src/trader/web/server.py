"""Read-only web dashboard.

It only READS the runtime's files (state.json, the journal, nightly reports). It has no
endpoint that changes anything: no orders, no resume, no kill-switch reset, no policy
promotion. Those stay on the command line, on purpose. Every request method other than
GET is refused. It binds to 127.0.0.1 unless told otherwise, and never serves a secret
(it does not read .env, and config is reduced to non-secret fields).
"""

from __future__ import annotations

import json
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from importlib import resources
from pathlib import Path

from trader.config import Config

TAIL_BYTES = 2_000_000


def tail_jsonl(path: Path, n: int) -> list[dict]:
    """Last n records of a JSONL file, reading only the end of large files."""
    if not path.exists():
        return []
    with path.open("rb") as f:
        f.seek(0, 2)
        size = f.tell()
        f.seek(max(0, size - TAIL_BYTES))
        chunk = f.read().decode("utf-8", "replace")
    lines = chunk.splitlines()
    if size > TAIL_BYTES:
        lines = lines[1:]  # the first line may be cut in half
    out = []
    for line in lines[-n:]:
        try:
            out.append(json.loads(line))
        except ValueError:
            continue  # a line being written right now; skip it
    return out


def build_payload(cfg: Config, root: Path, policies: Path, now: float | None = None) -> dict:
    now = time.time() if now is None else now
    root, policies = Path(root), Path(policies)
    state = {}
    if (root / "state.json").exists():
        try:
            state = json.loads((root / "state.json").read_text())
        except ValueError:
            state = {}
    hb = root / "heartbeat"
    hb_age = None
    if hb.exists():
        try:
            hb_age = now - int(hb.read_text().strip())
        except ValueError:
            hb_age = None
    acct = state.get("account", {})
    marks = state.get("marks", {})
    mark_ts = state.get("mark_ts", {})
    L = cfg.limits

    positions, unreal, gross = [], 0.0, 0.0
    for sym, p in acct.get("positions", {}).items():
        mark = marks.get(sym, p["entry_price"])
        u = p["qty"] * (mark - p["entry_price"])
        unreal += u
        gross += abs(p["qty"]) * mark
        risk = abs(p["qty"]) * abs(p["entry_price"] - p["stop_price"])
        positions.append({
            "symbol": sym, "side": "long" if p["qty"] > 0 else "short", "qty": p["qty"],
            "entry": p["entry_price"], "mark": mark, "stop": p["stop_price"], "target": p["target_price"],
            "notional": abs(p["qty"]) * mark, "unrealized": u, "risk_at_stop": risk,
            "opened_ts": p["opened_ts"], "setup": p["setup_id"],
            "mark_age_s": None if sym not in mark_ts else now - mark_ts[sym],
        })
    started = bool(acct)
    balance = acct.get("balance", cfg.paper_balance)
    equity = balance + unreal
    peak = max(acct.get("peak_equity", equity), equity) if started else equity
    day_start = acct.get("day_start_equity", equity) or equity
    drawdown = max(0.0, 1 - equity / peak) if peak > 0 else 0.0

    journal = root / "journal"
    decisions = tail_jsonl(journal / "decisions.jsonl", 400)
    latest: dict[str, dict] = {}
    for d in decisions:
        latest[d["symbol"]] = d
    setups = []
    for s in cfg.setups:
        d = latest.get(s.symbol, {})
        dec = d.get("decision") or {}
        setups.append({
            "id": s.id, "symbol": s.symbol, "base": s.base, "bias": s.bias.value, "market": s.market,
            "enabled": s.enabled, "research": s.research, "ts": d.get("ts"), "status": d.get("status"),
            "action": d.get("action"), "reasons": d.get("reasons", []), "px": d.get("px"),
            "regime": dec.get("regime"), "direction": dec.get("direction"),
            "confidence": dec.get("direction_confidence"), "quality": dec.get("setup_quality"),
            "toxic_flow": dec.get("toxic_flow"), "latency_ms": d.get("latency_ms"),
            "paused_until": state.get("paused_until", {}).get(s.symbol),
        })
    recent = [{k: d.get(k) for k in ("ts", "symbol", "status", "action", "reasons", "latency_ms", "px")}
              | {"decision": d.get("decision")} for d in decisions[-60:]][::-1]

    trades = tail_jsonl(journal / "trades.jsonl", 200)
    wins = [t for t in trades if t.get("pnl", 0) > 0]
    equity_curve = [{"ts": e["ts"], "equity": e["equity"]} for e in tail_jsonl(journal / "equity.jsonl", 2000)]

    reports = sorted((root / "reports").glob("nightly-*.json")) if (root / "reports").exists() else []
    nightly = None
    if reports:
        try:
            r = json.loads(reports[-1].read_text())
            c = r.get("calibration", {})
            nightly = {
                "generated_utc": r.get("generated_utc"), "resolved": c.get("resolved", 0),
                "brier": c.get("brier_calibrated"), "brier_base_rate": c.get("brier_base_rate"),
                "win_rate": c.get("win_rate"), "tests_passed": r.get("regression_tests", {}).get("passed"),
                "proposals": [{"version": p["version"], "note": p.get("note", ""),
                               "recommended": p.get("recommended", False)} for p in r.get("proposals", [])],
                "notes": r.get("notes", []), "misses": r.get("misses", {}),
            }
        except ValueError:
            nightly = None
    active = {}
    if (policies / "ACTIVE.json").exists():
        try:
            active = json.loads((policies / "ACTIVE.json").read_text())
        except ValueError:
            active = {}

    stale_after = 180.0
    if not started and hb_age is None:
        health = "not_started"
    elif hb_age is None or hb_age > stale_after:
        health = "stale"
    else:
        health = "ok"
    pauses = []
    if acct.get("kill_latched"):
        pauses.append({"level": "critical", "text": f"Kill switch latched: {acct.get('kill_reason', '')}. "
                       "No new orders until a human clears it."})
    if state.get("halt_reason"):
        pauses.append({"level": "critical", "text": f"Halted: {state['halt_reason']}"})
    if state.get("global_pause"):
        pauses.append({"level": "warning", "text": "All new risk paused until a human resumes."})
    if state.get("global_pause_until", 0) > now:
        pauses.append({"level": "warning", "text": "All new risk paused: crisis cooldown.",
                       "until": state["global_pause_until"]})
    if state.get("exit_pending"):
        pauses.append({"level": "warning", "text": "Exit orders waiting to fill: "
                       + ", ".join(f"{k} ({v})" for k, v in state["exit_pending"].items())})

    return {
        "now": now,
        "status": {"health": health, "heartbeat_age_s": hb_age, "mode": state.get("mode", cfg.mode),
                   "exchange": cfg.exchange, "timeframe": cfg.timeframe, "reflex": state.get("reflex"),
                   "policy": state.get("policy"), "active_policies": active,
                   "last_candle_ts": state.get("last_asof") or None, "stats": state.get("stats", {})},
        "account": {"started": started, "start_balance": cfg.paper_balance, "balance": balance,
                    "equity": equity, "peak": peak, "drawdown": drawdown,
                    "day_pnl": equity - day_start, "day_pnl_frac": equity / day_start - 1 if day_start else 0.0,
                    "leverage": gross / equity if equity > 0 else 0.0, "open_positions": len(positions)},
        "limits": {"risk_per_trade": L.risk_per_trade, "max_daily_loss": L.max_daily_loss,
                   "max_open_positions": L.max_open_positions, "max_leverage": L.max_leverage,
                   "kill_drawdown": L.kill_drawdown},
        "notices": pauses, "positions": positions, "setups": setups, "decisions": recent,
        "trades": trades[::-1][:50],
        "trade_stats": {"count": len(trades), "wins": len(wins),
                        "net_pnl": sum(t.get("pnl", 0.0) for t in trades)},
        "equity_curve": equity_curve,
        "events": tail_jsonl(journal / "events.jsonl", 40)[::-1], "nightly": nightly,
    }


def _page() -> bytes:
    return resources.files("trader.web").joinpath("dashboard.html").read_bytes()


def make_handler(cfg: Config, root: Path, policies: Path):
    class Handler(BaseHTTPRequestHandler):
        server_version = "trader-dashboard"

        def _send(self, code: int, body: bytes, ctype: str) -> None:
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("X-Frame-Options", "DENY")
            self.send_header("Referrer-Policy", "no-referrer")
            self.send_header("Content-Security-Policy",
                             "default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; "
                             "connect-src 'self'; img-src data:; base-uri 'none'; form-action 'none'")
            self.end_headers()
            if self.command != "HEAD":
                self.wfile.write(body)

        def do_GET(self) -> None:  # noqa: N802
            path = self.path.split("?", 1)[0]
            if path in ("/", "/index.html"):
                self._send(200, _page(), "text/html; charset=utf-8")
            elif path == "/api/state":
                try:
                    body = json.dumps(build_payload(cfg, root, policies), default=str).encode()
                except Exception as e:  # never leak a traceback to the browser
                    self._send(500, json.dumps({"error": type(e).__name__}).encode(), "application/json")
                    return
                self._send(200, body, "application/json")
            elif path == "/healthz":
                self._send(200, b"ok", "text/plain")
            else:
                self._send(404, b"not found", "text/plain")

        do_HEAD = do_GET  # noqa: N815

        def _refuse(self) -> None:
            self._send(405, b"read-only dashboard", "text/plain")

        do_POST = do_PUT = do_DELETE = do_PATCH = _refuse  # noqa: N815

        def log_message(self, fmt: str, *args) -> None:  # keep the trading logs clean
            return

    return Handler


def serve(cfg: Config, root: Path, policies: Path, host: str = "127.0.0.1", port: int = 8080) -> None:
    httpd = ThreadingHTTPServer((host, port), make_handler(cfg, root, policies))
    print(f"dashboard on http://{host}:{port}  (read-only)")
    try:
        httpd.serve_forever()
    finally:
        httpd.server_close()
