"""Maps the REFLEX's raw confidence to a calibrated win probability, and scores it.

Until enough resolved decisions exist, the calibrator SHRINKS confidence toward 0.5
(a stated hypothesis, not evidence). The nightly review can fit a monotone (isotonic)
map from resolved outcomes; a fitted map only goes live through the policy promotion gate.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Sequence


def brier_score(probs: Sequence[float], outcomes: Sequence[int]) -> float:
    if len(probs) != len(outcomes) or not probs:
        raise ValueError("need equal, non-empty probs and outcomes")
    return sum((p - o) ** 2 for p, o in zip(probs, outcomes)) / len(probs)


def reliability_table(probs: Sequence[float], outcomes: Sequence[int], n_bins: int = 5) -> list[dict]:
    rows = []
    for i in range(n_bins):
        lo, hi = i / n_bins, (i + 1) / n_bins
        idx = [j for j, p in enumerate(probs) if (lo <= p < hi) or (i == n_bins - 1 and p == 1.0)]
        if idx:
            rows.append({
                "bin": f"{lo:.1f}-{hi:.1f}", "n": len(idx),
                "mean_pred": sum(probs[j] for j in idx) / len(idx),
                "win_rate": sum(outcomes[j] for j in idx) / len(idx),
            })
    return rows


def _pav(values: list[float], weights: list[float]) -> list[float]:
    """Pool-adjacent-violators: the monotone non-decreasing fit to values."""
    blocks: list[list[float]] = []  # [mean, weight, count]
    for v, w in zip(values, weights):
        blocks.append([v, w, 1])
        while len(blocks) > 1 and blocks[-2][0] > blocks[-1][0]:
            v2, w2, c2 = blocks.pop()
            v1, w1, c1 = blocks.pop()
            blocks.append([(v1 * w1 + v2 * w2) / (w1 + w2), w1 + w2, c1 + c2])
    out: list[float] = []
    for v, _, c in blocks:
        out.extend([v] * int(c))
    return out


@dataclass(frozen=True)
class Calibrator:
    shrink: float = 0.5  # used when knots is empty: p = 0.5 + shrink * (conf - 0.5)
    knots: tuple[tuple[float, float], ...] = field(default_factory=tuple)  # (confidence, p), sorted
    max_p: float = 0.80  # never believe a win probability above this

    def p_win(self, confidence: float) -> float:
        c = min(1.0, max(0.0, confidence))
        if not self.knots:
            p = 0.5 + self.shrink * (c - 0.5)
        elif c <= self.knots[0][0]:
            p = self.knots[0][1]
        elif c >= self.knots[-1][0]:
            p = self.knots[-1][1]
        else:
            p = self.knots[-1][1]
            for (c0, p0), (c1, p1) in zip(self.knots, self.knots[1:]):
                if c0 <= c <= c1:
                    p = p0 if c1 == c0 else p0 + (p1 - p0) * (c - c0) / (c1 - c0)
                    break
        return min(self.max_p, max(0.0, p))

    def to_dict(self) -> dict:
        return {"shrink": self.shrink, "knots": [list(k) for k in self.knots], "max_p": self.max_p}

    @classmethod
    def from_dict(cls, d: dict) -> "Calibrator":
        return cls(shrink=d.get("shrink", 0.5), knots=tuple(tuple(k) for k in d.get("knots", [])),
                   max_p=d.get("max_p", 0.80))


def fit_isotonic(confidences: Sequence[float], outcomes: Sequence[int], n_bins: int = 6,
                 min_samples: int = 100, min_per_bin: int = 10, max_p: float = 0.80) -> Calibrator | None:
    """Binned isotonic fit. Returns None when there is not enough data to trust a fit."""
    if len(confidences) != len(outcomes) or len(confidences) < min_samples:
        return None
    pairs = sorted(zip(confidences, outcomes))
    size = max(min_per_bin, len(pairs) // n_bins)
    xs, ys, ws = [], [], []
    for i in range(0, len(pairs), size):
        chunk = pairs[i : i + size]
        if len(chunk) < min_per_bin and xs:
            # fold a short tail into the previous bin
            n_prev = ws[-1]
            xs[-1] = (xs[-1] * n_prev + sum(c for c, _ in chunk)) / (n_prev + len(chunk))
            ys[-1] = (ys[-1] * n_prev + sum(o for _, o in chunk)) / (n_prev + len(chunk))
            ws[-1] = n_prev + len(chunk)
            continue
        xs.append(sum(c for c, _ in chunk) / len(chunk))
        ys.append(sum(o for _, o in chunk) / len(chunk))
        ws.append(float(len(chunk)))
    if len(xs) < 2:
        return None
    fitted = _pav(ys, ws)
    return Calibrator(knots=tuple((round(x, 4), round(y, 4)) for x, y in zip(xs, fitted)), max_p=max_p)
