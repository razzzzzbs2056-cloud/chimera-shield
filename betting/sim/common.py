"""Shared helpers for the Monte Carlo simulators: scenario patches and result checks."""
from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

GAMES_DIR = Path(__file__).parent / "games"


def load_game(path_or_name: str) -> dict:
    p = Path(path_or_name)
    if not p.exists():
        p = GAMES_DIR / (path_or_name if path_or_name.endswith(".json") else path_or_name + ".json")
    return json.loads(p.read_text())


def _resolve(obj: Any, key: str) -> Any:
    """Step into a dict key, list index, or list element whose 'name' matches."""
    if isinstance(obj, list):
        if key.isdigit():
            return obj[int(key)]
        for item in obj:
            if isinstance(item, dict) and item.get("name") == key:
                return item
        raise KeyError(f"no list element named {key!r}")
    return obj[key]


def _parent(root: dict, path: str) -> tuple[Any, str]:
    parts = path.split(".")
    obj = root
    for part in parts[:-1]:
        obj = _resolve(obj, part)
    return obj, parts[-1]


def apply_ops(game: dict, ops: list[dict]) -> dict:
    """Return a copy of ``game`` with scenario ops applied.

    ops:
      {"op": "set", "path": "home.starter.bf_mean", "value": 18}
      {"op": "mul", "path": "away.attack", "value": 0.9}
      {"op": "replace", "path": "home.lineup", "out": "Aaron Judge", "in": {...player...}}
      {"op": "remove", "path": "home.players", "name": "Lamine Yamal"}
      {"op": "state", "value": {...in-game start state...}}
    Paths walk dicts by key and lists by index or by an element's "name".
    """
    g = copy.deepcopy(game)
    for op in ops:
        kind = op["op"]
        if kind == "state":
            g["state"] = op["value"]
            continue
        parent, last = _parent(g, op["path"])
        if kind == "set":
            if isinstance(parent, list):
                parent[parent.index(_resolve(parent, last))] = op["value"]
            else:
                parent[last] = op["value"]
        elif kind == "mul":
            target = _resolve(parent, last) if isinstance(parent, list) else parent[last]
            if isinstance(target, dict):  # multiply every numeric rate in a dict
                for k, v in target.items():
                    if isinstance(v, (int, float)) and not isinstance(v, bool):
                        target[k] = v * op["value"]
            else:
                parent[last] = target * op["value"]
        elif kind in ("replace", "remove"):
            lst = _resolve(parent, last) if isinstance(parent, list) else parent[last]
            name = op.get("out") or op.get("name")
            idx = next(i for i, p in enumerate(lst) if p.get("name") == name)
            if kind == "replace":
                lst[idx] = op["in"]
            else:
                lst.pop(idx)
        else:
            raise ValueError(f"unknown op {kind!r}")
    return g


def scenario(game: dict, name: str) -> dict:
    for s in game.get("scenarios", []):
        if s["name"].lower() == name.lower():
            return apply_ops(game, s["ops"])
    raise KeyError(f"scenario {name!r} not found; have {[s['name'] for s in game.get('scenarios', [])]}")


def devig2(prices: list[float]) -> list[float]:
    raw = [1 / p for p in prices]
    s = sum(raw)
    return [r / s for r in raw]


def american(p: float) -> str:
    """Fair American price for probability p."""
    if p <= 0 or p >= 1:
        return "n/a"
    return f"{-round(100 * p / (1 - p)):+d}" if p >= 0.5 else f"+{round(100 * (1 - p) / p)}"


def pct(x: float) -> str:
    return f"{x * 100:5.1f}%"
