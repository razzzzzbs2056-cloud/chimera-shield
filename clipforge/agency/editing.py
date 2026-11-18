"""Edit decision list helpers.

A clip's `edit_map` is the list of [start, end] spans (seconds, relative to the
raw cut) that survived editing, in order. Everything timed against the original
footage (transcript words, sentence starts) is mapped onto the edited timeline
through it, so captions and zooms stay in sync after jump cuts."""


def identity(duration: float) -> list[list[float]]:
    return [[0.0, duration]]


def remap(t: float, keeps: list[list[float]]) -> float | None:
    """Original clip time -> edited time, or None if `t` was cut out."""
    offset = 0.0
    for a, b in keeps:
        if t < a:
            return None
        if t <= b:
            return offset + (t - a)
        offset += b - a
    return None


def remap_span(a: float, b: float, keeps: list[list[float]]) -> list[tuple[float, float]]:
    """Map an original [a, b] span onto the edited timeline (may split or vanish)."""
    out, offset = [], 0.0
    for ka, kb in keeps:
        lo, hi = max(a, ka), min(b, kb)
        if hi > lo:
            out.append((offset + lo - ka, offset + hi - ka))
        offset += kb - ka
    return out


def remap_words(words: list[dict], keeps: list[list[float]]) -> list[dict]:
    out = []
    for w in words:
        spans = remap_span(w["start"], w["end"], keeps)
        if spans and sum(b - a for a, b in spans) >= 0.4 * (w["end"] - w["start"]):
            out.append({**w, "start": spans[0][0], "end": spans[-1][1]})
    return out


def keeps_from_silences(duration: float, silences: list[tuple[float, float]],
                        pad: float = 0.12, min_cut: float = 0.35) -> list[list[float]]:
    """Turn detected silences into kept spans, leaving a short breath (`pad`) on each side."""
    keeps, cursor = [], 0.0
    for s, e in silences:
        cut_a = 0.0 if s <= 0.05 else s + pad      # leading silence goes entirely
        cut_b = duration if e >= duration - 0.05 else e - pad
        if cut_b - cut_a < min_cut:
            continue
        if cut_a > cursor:
            keeps.append([cursor, cut_a])
        cursor = max(cursor, cut_b)
    if cursor < duration:
        keeps.append([cursor, duration])
    return [k for k in keeps if k[1] - k[0] > 0.05] or identity(duration)


def kept_duration(keeps: list[list[float]]) -> float:
    return sum(b - a for a, b in keeps)
