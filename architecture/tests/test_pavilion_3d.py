"""The 3D page's finance model is checked against an independent Python calculation, and its geometry against make_ifc.py."""
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
PAGE = (ROOT / "art" / "pavilion-3d.html").read_text()
sys.path.insert(0, str(ROOT / "bim"))

BASE = dict(area=3456, costPerM2=4000, softPct=25, cr003=1, cr003Cost=600000, land=0, grant=0,
            hallDays=150, hallRate=2500, cafeSales=450000, cafeMargin=12, members=120, memberFee=600,
            classSeats=2400, classPrice=25, visitors=30000, ticket=6, terraceEvents=40, terraceRate=3000,
            pvKwp=150, pvYield=1000, elecPrice=0.2, staff=6, staffCost=55000, energyPerM2=15,
            maintPct=1.2, insurPct=0.4, discount=5, escal=2, years=30)


def js_finance(p: dict) -> dict:
    if not shutil.which("node"):
        pytest.skip("node not installed")
    src = PAGE.split("/* ---------- FINANCE-START")[1].split("/* ---------- FINANCE-END")[0]
    src = src.split("*/", 1)[1]
    code = src + f"\nconsole.log(JSON.stringify(financeModel({json.dumps(p)})));"
    out = subprocess.run(["node", "-e", code], capture_output=True, text=True, check=True).stdout
    return json.loads(out)


def py_finance(p: dict) -> dict:
    capex = p["area"] * p["costPerM2"] * (1 + p["softPct"] / 100) + (p["cr003Cost"] if p["cr003"] else 0) + p["land"]
    revenue = (p["hallDays"] * p["hallRate"] + p["cafeSales"] * p["cafeMargin"] / 100 + p["members"] * p["memberFee"]
               + p["classSeats"] * p["classPrice"] + p["visitors"] * p["ticket"] + p["terraceEvents"] * p["terraceRate"]
               + p["pvKwp"] * p["pvYield"] * p["elecPrice"])
    opex = p["staff"] * p["staffCost"] + p["area"] * p["energyPerM2"] + capex * (p["maintPct"] + p["insurPct"]) / 100
    noi = revenue - opex
    g, r = p["escal"] / 100, p["discount"] / 100
    npv = -(capex - p["grant"]) + sum(noi * (1 + g) ** (t - 1) / (1 + r) ** t for t in range(1, p["years"] + 1))
    return {"capex": capex, "revenue": revenue, "opex": opex, "noi": noi, "npv": npv}


@pytest.mark.parametrize("override", [{}, {"cr003": 0}, {"grant": 5_000_000}, {"hallDays": 300, "hallRate": 6000}])
def test_js_finance_matches_python(override):
    p = dict(BASE, **override)
    js, py = js_finance(p), py_finance(p)
    for k in ("capex", "revenue", "opex", "noi", "npv"):
        assert js[k] == pytest.approx(py[k], rel=1e-9), k


def test_break_even_grant_zeroes_npv_and_irr_consistent():
    p = dict(BASE, hallDays=300, hallRate=6000, visitors=80000)
    r = js_finance(p)
    if r["noi"] > 0:
        r2 = js_finance(dict(p, grant=r["grantToBreakEven"]))
        assert r2["npv"] == pytest.approx(0, abs=1.0) or r["grantToBreakEven"] in (0, r["capex"])
    if r["irr"] is not None:
        assert js_finance(dict(p, discount=r["irr"] * 100))["npv"] == pytest.approx(0, abs=50.0)


def test_geometry_constants_match_ifc_script():
    import make_ifc
    geo = re.search(r"var GEO = (\{.*?\});", PAGE, re.S).group(1)
    nums = lambda key: [float(x) for x in re.findall(r"-?\d+\.?\d*", re.search(key + r":\s*(\[\[.*?\]\]|\[[^\]]*\]|[\d.]+)", geo).group(1))]
    assert nums("levels") == list(make_ifc.LEVELS.values())
    assert nums("hall") == list(make_ifc.HALL)
    assert nums("cores") == [v for c in make_ifc.CORES for v in c]
    assert nums("grid") == [make_ifc.GRID] and nums("clt") == [make_ifc.CLT_T] and nums("col") == [make_ifc.COL[0]]
    assert nums("joist") == list(make_ifc.JOIST)
