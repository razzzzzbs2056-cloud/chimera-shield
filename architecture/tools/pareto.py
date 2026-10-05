"""Non-dominated (Pareto) comparison of design options.

options: {"Option A": {"cost": 10, "carbon": 300, "daylight": 0.4}, ...}
senses:  {"cost": "min", "carbon": "min", "daylight": "max"}
Options that fail a hard constraint must be removed BEFORE calling this (constraints are not objectives).
Usage: python architecture/tools/pareto.py options.json senses.json
"""
import json
import sys
from pathlib import Path


def dominates(x: dict, y: dict, senses: dict) -> bool:
    better = False
    for k, s in senses.items():
        a, b = (x[k], y[k]) if s == "min" else (-x[k], -y[k])
        if a > b:
            return False
        if a < b:
            better = True
    return better


def pareto(options: dict, senses: dict) -> dict:
    names = list(options)
    front = [n for n in names if not any(dominates(options[m], options[n], senses) for m in names if m != n)]
    best = {k: (min if s == "min" else max)(names, key=lambda n: options[n][k]) for k, s in senses.items()}
    return {"front": front, "dominated": [n for n in names if n not in front], "best_per_objective": best}


if __name__ == "__main__":
    print(json.dumps(pareto(json.loads(Path(sys.argv[1]).read_text()), json.loads(Path(sys.argv[2]).read_text())), indent=1))
