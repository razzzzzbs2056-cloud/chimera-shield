"""Concept-stage calculators for the architecture data pack.

Feasibility numbers only. Not a substitute for a licensed engineer's analysis.
Usage:  python architecture/tools/quickcheck.py
"""
import csv
import math
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"


def load_materials() -> dict[str, dict]:
    with open(DATA / "materials.csv", newline="") as f:
        return {r["material"]: r for r in csv.DictReader(f)}


def factored_load_ec(dead_kpa: float, live_kpa: float) -> float:
    """EN 1990 eq 6.10: 1.35 G + 1.5 Q (kPa)."""
    return 1.35 * dead_kpa + 1.5 * live_kpa


def rect_section_modulus_mm3(b_mm: float, h_mm: float) -> float:
    return b_mm * h_mm ** 2 / 6


def simply_supported(w_kn_m: float, span_m: float) -> tuple[float, float]:
    """Return (max moment kNm, max shear kN) for a UDL."""
    return w_kn_m * span_m ** 2 / 8, w_kn_m * span_m / 2


def deflection_mm(w_kn_m: float, span_m: float, e_mpa: float, i_mm4: float) -> float:
    """Midspan deflection of a simply supported beam under a UDL, mm."""
    w = w_kn_m  # kN/m == N/mm
    return 5 * w * (span_m * 1000) ** 4 / (384 * e_mpa * i_mm4)


def size_timber_beam(span_m: float, trib_width_m: float, dead_kpa: float, live_kpa: float,
                     b_mm: float = 240, fm_k: float = 24.0, e0_mean_mpa: float = 11500.0,
                     kmod: float = 0.8, gamma_m: float = 1.25, lamella_mm: float = 40,
                     limit_ratio: float = 300) -> dict:
    """Smallest rectangular glulam depth passing bending (ULS) and L/limit deflection (SLS).

    Ignores shear, lateral-torsional stability, creep, bearing and fire; see notes in the brief.
    """
    w_uls = factored_load_ec(dead_kpa, live_kpa) * trib_width_m
    w_sls = (dead_kpa + live_kpa) * trib_width_m
    m_knm, v_kn = simply_supported(w_uls, span_m)
    fm_d = kmod * fm_k / gamma_m
    h_req = math.sqrt(6 * m_knm * 1e6 / (fm_d * b_mm))
    h = math.ceil(h_req / lamella_mm) * lamella_mm
    while True:
        i = b_mm * h ** 3 / 12
        d = deflection_mm(w_sls, span_m, e0_mean_mpa, i)
        if d <= span_m * 1000 / limit_ratio:
            break
        h += lamella_mm
    return {
        "w_uls_kN_m": w_uls, "w_sls_kN_m": w_sls, "M_kNm": m_knm, "V_kN": v_kn,
        "fm_d_MPa": fm_d, "h_req_bending_mm": h_req, "h_selected_mm": h,
        "deflection_mm": d, "span_over_deflection": span_m * 1000 / d,
    }


def embodied_carbon(takeoff_csv: Path | None = None) -> dict:
    """A1-A3 carbon (low/high) and biogenic storage from the quantity take-off."""
    mats = load_materials()
    rows, lo, hi, bio = [], 0.0, 0.0, 0.0
    with open(takeoff_csv or DATA / "quantity_takeoff.csv", newline="") as f:
        for r in csv.DictReader(f):
            m = mats[r["material"]]
            q = float(r["quantity"])
            kg = q * float(m["density_kg_m3"]) if r["unit"] == "m3" else q
            if r["unit"] not in ("m3", "kg"):
                raise ValueError(f"unknown unit {r['unit']}")
            l, h = kg * float(m["embodied_kgCO2e_per_kg_low"]), kg * float(m["embodied_kgCO2e_per_kg_high"])
            b = kg * float(m["biogenic_kgCO2e_per_kg"])
            rows.append({"element": r["element"], "mass_t": kg / 1000, "low_tCO2e": l / 1000,
                         "high_tCO2e": h / 1000, "biogenic_tCO2e": b / 1000})
            lo, hi, bio = lo + l, hi + h, bio + b
    return {"rows": rows, "low_t": lo / 1000, "high_t": hi / 1000, "biogenic_t": bio / 1000}


def per_m2(total_t: float, gfa_m2: float) -> float:
    return total_t * 1000 / gfa_m2


if __name__ == "__main__":
    print("Glulam primary beam, 8 m span, 4 m tributary, G=1.7 kPa, Q=4.0 kPa")
    for k, v in size_timber_beam(8, 4, 1.7, 4.0).items():
        print(f"  {k}: {v:.2f}")
    ec = embodied_carbon()
    gfa = 4188
    print(f"\nEmbodied carbon A1-A3 (structure+envelope subset): {ec['low_t']:.0f}-{ec['high_t']:.0f} tCO2e"
          f" = {per_m2(ec['low_t'], gfa):.0f}-{per_m2(ec['high_t'], gfa):.0f} kgCO2e/m2 GFA")
    print(f"Biogenic carbon stored in timber: {ec['biogenic_t']:.0f} tCO2e (report separately, not netted)")
