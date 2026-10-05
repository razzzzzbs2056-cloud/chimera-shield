"""Agent C: compare two independent calculations and decide PROCEED or INVESTIGATE.

Inputs are JSON objects {name: number}. Tolerances: {"default": {"rel": 0.05}, "name": {"rel": 0.02, "abs": 1e-6}}.
A value passes if |a - b| <= abs  OR  |a - b| <= rel * max(|a|, |b|).
Keys present in only one result are failures (a check one side did not do is not agreement).
Usage: python architecture/tools/verify_compare.py a.json b.json [--tol tol.json]
"""
import json
import sys
from pathlib import Path


def compare(a: dict, b: dict, tol: dict | None = None) -> dict:
    tol = tol or {}
    default = tol.get("default", {"rel": 0.05})
    rows, ok = [], True
    for k in sorted(set(a) | set(b)):
        if k not in a or k not in b:
            rows.append({"key": k, "a": a.get(k), "b": b.get(k), "pass": False, "why": "missing in " + ("A" if k not in a else "B")}); ok = False; continue
        t = {**default, **tol.get(k, {})}
        d = abs(a[k] - b[k]); scale = max(abs(a[k]), abs(b[k]))
        rel = d / scale if scale else 0.0
        p = d <= t.get("abs", 0.0) or rel <= t.get("rel", 0.0)
        rows.append({"key": k, "a": a[k], "b": b[k], "rel_diff": rel, "tol_rel": t.get("rel"), "pass": p})
        ok &= p
    return {"decision": "PROCEED" if ok else "INVESTIGATE", "rows": rows}


if __name__ == "__main__":
    a = json.loads(Path(sys.argv[1]).read_text()); b = json.loads(Path(sys.argv[2]).read_text())
    tol = json.loads(Path(sys.argv[sys.argv.index("--tol") + 1]).read_text()) if "--tol" in sys.argv else None
    r = compare(a, b, tol)
    for row in r["rows"]:
        print(("ok   " if row["pass"] else "FAIL ") + json.dumps(row))
    print(r["decision"]); sys.exit(0 if r["decision"] == "PROCEED" else 2)
