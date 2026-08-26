"""
Alert engine.

Generates alerts when statistically meaningful thresholds are crossed. Every
alert carries: condition, time, coordinates, source, evidence, confidence,
recommended investigation, and the affected downstream catchment. Alert wording
is conservative and always includes "requires verification" for anything that
cannot be directly confirmed (e.g. possible river blockage).
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Optional


def _alert(condition: str, severity: str, glacier: dict, evidence: List[str],
           confidence: str, recommend: str, downstream: List[dict]) -> dict:
    return {
        "condition": condition,
        "severity": severity,  # WATCH | ELEVATED | HIGH | CRITICAL INVESTIGATION
        "time": datetime.now(timezone.utc).isoformat(),
        "glacier_id": glacier.get("id"),
        "coordinates": {"lat": glacier.get("latitude"), "lon": glacier.get("longitude")},
        "evidence": evidence,
        "confidence": confidence,
        "recommended_investigation": recommend,
        "affected_downstream": [d.get("name") for d in downstream],
        "disclaimer": "Experimental indicator; not an official warning.",
    }


def generate(report: dict) -> List[dict]:
    alerts: List[dict] = []
    glacier = report.get("glacier", {})
    downstream = report.get("downstream", [])

    temp = report.get("temperature", {})
    anomaly = temp.get("anomaly_c")
    if anomaly is not None and anomaly >= 3.0:
        alerts.append(_alert(
            "TEMPERATURE ANOMALY", "ELEVATED", glacier,
            [f"Air-temperature anomaly {anomaly:+.1f} degC vs climatology "
             f"(elevation-adjusted estimate)"],
            temp.get("freshness", {}).get("status", "UNKNOWN"),
            "Verify with additional model runs and any station/AWS data.",
            downstream))

    pdd = report.get("pdd", {})
    if pdd.get("anomaly_30d_pct") is not None and pdd["anomaly_30d_pct"] >= 40:
        alerts.append(_alert(
            "EXTREME MELT CONDITIONS", "ELEVATED", glacier,
            [f"30-day PDD {pdd['anomaly_30d_pct']:+.0f}% above seasonal normal"],
            "MEDIUM",
            "Melt pressure elevated; check lake levels and downstream gauges. "
            "PDD is an indicator, not proof of flooding.",
            downstream))

    lake = report.get("lake", {})
    if lake.get("change_30d_pct") is not None and lake["change_30d_pct"] >= 10:
        alerts.append(_alert(
            "GLACIAL LAKE GROWTH", "HIGH", glacier,
            [f"Lake area +{lake['change_30d_pct']:.1f}% in 30 days"],
            lake.get("confidence", "UNKNOWN"),
            "Confirm with cloud-free optical imagery; assess moraine-dam state.",
            downstream))

    eq = report.get("earthquakes", {})
    latest = eq.get("latest")
    if latest and (latest.get("magnitude") or 0) >= 4.0 and (latest.get("distance_km") or 999) <= 100:
        alerts.append(_alert(
            "EARTHQUAKE NEAR GLACIER", "WATCH", glacier,
            [f"M{latest['magnitude']} at {latest['distance_km']} km "
             f"({eq.get('association')})"],
            eq.get("confidence", "MEDIUM"),
            "Inspect slopes and SAR change after the event. Association only -- "
            "no causal claim.",
            downstream))

    # Possible river blockage requires hydrology/imagery; only flagged when a
    # dedicated detector (worker) sets report['river_blockage']. We never
    # fabricate this from thin air.
    rb = report.get("river_blockage")
    if rb and rb.get("possible"):
        alerts.append(_alert(
            "POSSIBLE RIVER BLOCKAGE -- REQUIRES VERIFICATION", "HIGH", glacier,
            rb.get("evidence", []), rb.get("confidence", "LOW"),
            "Verify with SAR/optical imagery and downstream gauges before any "
            "action. Never treated as a confirmed dam.",
            downstream))

    return alerts
