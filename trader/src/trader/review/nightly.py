"""Nightly review: read every decision, fill and miss; score calibration; propose changes.

It never changes what trades. It writes a report and CANDIDATE policies. A candidate is
marked `recommended` only if it passes every gate: out-of-sample calibration no worse,
replayed result no worse, drawdown not materially worse, and the regression tests green.
Promotion is a separate, human-approved command (trader policy promote).
"""

from __future__ import annotations

import datetime as dt
import json
import subprocess
import sys
from dataclasses import replace
from pathlib import Path
from typing import Callable

from trader.backtest.engine import Series, metrics, run_backtest
from trader.core import Setup
from trader.exec.broker import CostModel
from trader.policy import Policy, PolicyStore
from trader.reflex.replay import ReplayReflex
from trader.risk.calibration import brier_score, fit_isotonic, reliability_table
from trader.risk.engine import RiskLimits


def resolve_outcome(d: dict, S: Series, policy: Policy, tf_seconds: int) -> int | None:
    """1 if price reached the target before the stop, 0 if the stop came first or time ran out,
    None if the future bars needed to know are not in yet. Uses only bars AFTER the decision."""
    k0 = S.index.get(d["ts"])  # the bar that opens at the decision time
    if k0 is None or not d.get("px") or not d.get("atr"):
        return None
    long = d["decision"]["direction"] == "long"
    px = float(S.o[k0])
    dist = policy.stop_atr_mult * d["atr"] / 100 * d["px"]
    stop, target = (px - dist, px + policy.rr * dist) if long else (px + dist, px - policy.rr * dist)
    end = k0 + policy.time_stop_bars
    for k in range(k0, min(end, len(S.ts))):
        hi, lo = float(S.h[k]), float(S.lo[k])
        if (long and lo <= stop) or (not long and hi >= stop):
            return 0  # stop is checked first: conservative when both are touched in one bar
        if (long and hi >= target) or (not long and lo <= target):
            return 1
    return 0 if end <= len(S.ts) else None


def run_regression_tests(project_root: Path) -> tuple[bool, str]:
    p = subprocess.run([sys.executable, "-m", "pytest", "-q", "-x", "--no-header"], cwd=project_root,
                       capture_output=True, text=True, timeout=900)
    tail = (p.stdout or p.stderr).strip().splitlines()[-1:] or [""]
    return p.returncode == 0, tail[0]


def review(*, decisions: list[dict], trades: list[dict], fills: list[dict], events: list[dict],
           series: dict[str, Series], setups: list[Setup], store: PolicyStore, stage: str,
           limits: RiskLimits, cost_of: Callable[[str], CostModel], spread: dict[str, float],
           depth: dict[str, float], tf: str, tf_seconds: int, balance: float, now: int,
           out_dir: Path, run_tests: Callable[[], tuple[bool, str]], min_samples: int = 100) -> dict:
    active = store.active(stage)
    day0 = now - 86400
    today = [d for d in decisions if d["ts"] > day0]
    by_status: dict[str, int] = {}
    for d in today:
        by_status[d["status"]] = by_status.get(d["status"], 0) + 1
    lat = sorted(d["latency_ms"] for d in today if "latency_ms" in d)

    def pct(q: float) -> float | None:
        return lat[min(len(lat) - 1, int(q * len(lat)))] if lat else None

    # ---- outcomes and calibration over all logged directional decisions --------------
    rows = []
    for d in decisions:
        dec = d.get("decision")
        if not dec or dec["direction"] == "neutral" or d["symbol"] not in series:
            continue
        o = resolve_outcome(d, series[d["symbol"]], active, tf_seconds)
        if o is not None:
            rows.append({"ts": d["ts"], "conf": dec["direction_confidence"], "outcome": o,
                         "p": active.calibrator.p_win(dec["direction_confidence"]),
                         "action": d["action"], "symbol": d["symbol"]})
    rows.sort(key=lambda r: r["ts"])
    calib: dict = {"resolved": len(rows)}
    if rows:
        outs = [r["outcome"] for r in rows]
        base_rate = sum(outs) / len(outs)
        calib.update(
            win_rate=base_rate,
            brier_calibrated=brier_score([r["p"] for r in rows], outs),
            brier_raw_confidence=brier_score([r["conf"] for r in rows], outs),
            brier_base_rate=brier_score([base_rate] * len(outs), outs),
            reliability=reliability_table([r["p"] for r in rows], outs),
        )
    taken = [r for r in rows if r["action"].startswith("enter")]
    blocked = [r for r in rows if not r["action"].startswith("enter")]
    misses = {
        "skipped_candles_24h": {k: v for k, v in by_status.items() if k != "ok"},
        "blocked_that_would_have_won": sum(r["outcome"] for r in blocked),
        "blocked_that_would_have_lost": sum(1 - r["outcome"] for r in blocked),
        "taken_won": sum(r["outcome"] for r in taken), "taken_lost": sum(1 - r["outcome"] for r in taken),
    }

    # ---- proposals -------------------------------------------------------------------
    stamp = dt.datetime.fromtimestamp(now, dt.timezone.utc).strftime("%Y%m%d")
    candidates: list[Policy] = []
    notes: list[str] = []
    split = int(len(rows) * 0.7)
    fit_rows, test_rows = rows[:split], rows[split:]
    cal = fit_isotonic([r["conf"] for r in fit_rows], [r["outcome"] for r in fit_rows],
                       min_samples=min_samples) if fit_rows else None
    if cal is None:
        notes.append(f"calibration refit skipped: {len(fit_rows)} resolved decisions in the fit window, "
                     f"need {min_samples}")
    else:
        candidates.append(replace(active, version=f"{active.version}-cal{stamp}", calibrator=cal,
                                  parent=active.version, note="isotonic calibration refit"))
    for delta in (-0.03, 0.03):
        mc = round(active.min_confidence + delta, 3)
        if 0.6 < mc < 0.99:
            candidates.append(replace(active, version=f"{active.version}-mc{int(mc * 100)}-{stamp}",
                                      min_confidence=mc, parent=active.version,
                                      note=f"min_confidence {active.min_confidence} -> {mc}"))

    tests_ok, tests_tail = run_tests()
    replayable = [d for d in decisions if d.get("decision")]
    proposals = []
    if replayable and test_rows:
        t0, t1 = test_rows[0]["ts"], max(d["ts"] for d in replayable) + tf_seconds
        reflex = ReplayReflex(replayable)

        def replay(p: Policy) -> dict:
            r = run_backtest(series, setups, policy_at=lambda t: p, limits=limits, cost_of=cost_of,
                             spread_bps=spread, depth_usd=depth, t_start=t0, t_end=t1, tf=tf,
                             tf_seconds=tf_seconds, start_balance=balance, reflex_for=lambda _p: reflex)
            return metrics(r.equity, r.trades, tf_seconds, balance)

        cur = replay(active)
        outs = [r["outcome"] for r in test_rows]
        cur_brier = brier_score([active.calibrator.p_win(r["conf"]) for r in test_rows], outs)
        for c in candidates:
            m = replay(c)
            b = brier_score([c.calibrator.p_win(r["conf"]) for r in test_rows], outs)
            gates = {
                "oos_brier_not_worse": b <= cur_brier + 1e-9,
                "oos_return_not_worse": m["total_return"] >= cur["total_return"] - 1e-9,
                "oos_drawdown_not_worse_by_2pts": m["max_drawdown"] >= cur["max_drawdown"] - 0.02,
                "enough_oos_decisions": len(test_rows) >= 30,
                "regression_tests_pass": tests_ok,
            }
            rec = all(gates.values()) and (b < cur_brier - 1e-6 or m["total_return"] > cur["total_return"] + 1e-6)
            try:
                store.save(c, candidate=True)
            except FileExistsError:
                pass
            proposals.append({"version": c.version, "note": c.note, "oos_brier": b, "oos_return": m["total_return"],
                              "oos_max_drawdown": m["max_drawdown"], "oos_trades": m["trades"], "gates": gates,
                              "recommended": rec})
        current = {"oos_brier": cur_brier, "oos_return": cur["total_return"],
                   "oos_max_drawdown": cur["max_drawdown"], "oos_trades": cur["trades"],
                   "oos_window": [t0, t1]}
    else:
        current = {}
        notes.append("no proposals evaluated: not enough resolved decisions for an out-of-sample window")

    report = {
        "generated_utc": dt.datetime.fromtimestamp(now, dt.timezone.utc).isoformat(),
        "stage": stage, "active_policy": active.version,
        "last_24h": {"decisions": len(today), "by_status": by_status,
                     "fills": sum(1 for f in fills if f.get("ts", 0) > day0),
                     "trades_closed": sum(1 for t in trades if t["closed_ts"] > day0),
                     "pnl": sum(t["pnl"] for t in trades if t["closed_ts"] > day0),
                     "events": [e for e in events if e["ts"] > day0],
                     "latency_ms": {"p50": pct(0.5), "p95": pct(0.95), "max": lat[-1] if lat else None}},
        "calibration": calib, "misses": misses, "current_policy_oos": current, "proposals": proposals,
        "regression_tests": {"passed": tests_ok, "summary": tests_tail}, "notes": notes,
        "promotion": "manual only: `trader policy promote <version> --stage paper --approved-by <name>`",
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / f"nightly-{stamp}.json").write_text(json.dumps(report, indent=2, default=str))
    return report
