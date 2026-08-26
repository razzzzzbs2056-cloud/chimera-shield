"""
AI Analyst -- evidence-fusion summary.

Generates a plain-language, evidence-grounded assessment after each data update.
This is deliberately *rule-based / templated* rather than a free-generating LLM,
because the platform's core promise is that every analytical conclusion links
back to underlying evidence and never fabricates. Each line the analyst emits is
built directly from a computed value with its source and age; if a value is
UNKNOWN it is stated as unknown, not glossed over.

Language rules (hard-coded):
  * Never "will collapse / will flood". Use "indicators have increased".
  * Never assert an earthquake caused an avalanche -- only association classes.
  * Never call a lake-area decrease a GLOF.
  * Always close with a monitoring recommendation, not a prediction.

(An optional LLM narration layer could sit on top, but must be constrained to
rephrasing these evidence bullets, never adding facts. Left as an extension.)
"""
from __future__ import annotations

from typing import List, Optional


def _fmt_signed(v: Optional[float], unit: str = "") -> str:
    if v is None:
        return "unknown"
    sign = "+" if v >= 0 else ""
    return f"{sign}{v}{unit}"


def build_assessment(report: dict) -> dict:
    """Consume an assembled glacier report dict and produce an evidence list +
    a conservative narrative assessment."""
    name = report.get("glacier", {}).get("name", "This glacier")
    risk = report.get("risk", {})
    score = risk.get("glacier_risk_score_0_100")
    level = risk.get("risk_level", "UNKNOWN")

    evidence: List[dict] = []

    temp = report.get("temperature", {})
    if temp.get("current_glacier_air_temp_c") is not None:
        evidence.append({
            "label": "Estimated glacier air temperature",
            "value": f"{_fmt_signed(temp['current_glacier_air_temp_c'], ' degC')} "
                     f"(elevation-adjusted estimate)",
            "anomaly": _fmt_signed(temp.get("anomaly_c"), " degC vs climatology"),
        })

    st = report.get("surface_temperature", {})
    evidence.append({
        "label": "Latest satellite surface temperature",
        "value": (f"{_fmt_signed(st.get('value'), ' degC')}"
                  if st.get("value") is not None else "UNKNOWN (no cloud-free LST)"),
    })

    pdd = report.get("pdd", {})
    if pdd.get("anomaly_30d_pct") is not None:
        evidence.append({
            "label": "30-day positive-degree-day anomaly",
            "value": f"{_fmt_signed(pdd['anomaly_30d_pct'], '%')} vs seasonal normal",
        })

    lake = report.get("lake", {})
    if lake.get("change_30d_pct") is not None:
        evidence.append({
            "label": "Glacial lake 30-day area change",
            "value": _fmt_signed(lake.get("change_30d_pct"), "%"),
        })

    quakes = report.get("earthquakes", {})
    latest_q = quakes.get("latest")
    if latest_q:
        evidence.append({
            "label": "Nearest recent earthquake",
            "value": (f"M{latest_q.get('magnitude')} at "
                      f"{latest_q.get('distance_km')} km"),
            "association": quakes.get("association", "insufficient evidence"),
        })

    precip = report.get("precipitation", {})
    if precip.get("precip_24h_mm") is not None:
        evidence.append({
            "label": "24 h precipitation",
            "value": f"{precip['precip_24h_mm']} mm"
                     + (" (rain/snow phase uncertain near freezing)"
                        if precip.get("phase_uncertain_near_freezing") else ""),
        })

    sar = report.get("satellite", {}).get("sentinel1", {})
    if sar.get("latest_scene_time"):
        evidence.append({
            "label": "Latest Sentinel-1 SAR",
            "value": f"scene {sar.get('latest_scene_time')} "
                     f"(intensity change requires InSAR validation before "
                     f"interpretation as movement)",
        })

    # --- Conservative narrative -------------------------------------------
    increased: List[str] = []
    if (temp.get("anomaly_c") or 0) >= 2:
        increased.append("air-temperature anomaly")
    if (pdd.get("anomaly_30d_pct") or 0) >= 20:
        increased.append("melt pressure (PDD)")
    if (lake.get("change_30d_pct") or 0) >= 5:
        increased.append("glacial-lake area")
    if latest_q and (latest_q.get("magnitude") or 0) >= 4:
        increased.append("nearby seismic activity")

    if increased:
        body = (
            f"Multiple indicators have increased for {name}: "
            + ", ".join(increased)
            + ". Available evidence is insufficient to predict slope failure, "
              "lake outburst, or downstream flooding. Increased monitoring is "
              "recommended, and findings should be verified against additional "
              "cloud-free imagery and ground information."
        )
    elif score is None:
        body = (
            f"Insufficient current data to assess {name}. Key inputs are UNKNOWN "
            "(see confidence and freshness on each card). No conclusion is drawn."
        )
    else:
        body = (
            f"No individual indicator is currently elevated for {name}. Routine "
            "monitoring continues. This is not a guarantee of stability."
        )

    return {
        "headline": (f"{name}: risk indicator {score}/100 -- {level}"
                     if score is not None else f"{name}: risk indicator UNKNOWN"),
        "evidence": evidence,
        "assessment": body,
        "disclaimer": ("Experimental hazard indicator. Not a prediction and not "
                       "an official warning. Every figure links to its source, "
                       "acquisition time, and confidence on the dashboard."),
    }
