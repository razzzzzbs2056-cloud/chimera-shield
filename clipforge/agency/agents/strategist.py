"""Content strategist: finds the moments most likely to perform as short-form clips."""
import re

from pydantic import BaseModel

from .. import config, db, llm, transcript
from .base import Agent

HOOK_WORDS = {"why", "how", "secret", "mistake", "never", "always", "nobody", "everyone", "truth", "stop",
              "biggest", "worst", "best", "wrong", "actually", "crazy", "insane", "million", "money",
              "here's", "imagine", "most", "people", "realized", "changed", "lesson", "you"}
EMOTION_WORDS = {"love", "hate", "scared", "afraid", "angry", "shocked", "amazing", "incredible", "broke",
                 "fired", "quit", "failed", "died", "cried", "laughed", "terrified", "obsessed", "regret"}


class Moment(BaseModel):
    start: float
    end: float
    title: str
    hook: str
    reason: str
    score: int


class MomentList(BaseModel):
    moments: list[Moment]


def _words(t: str) -> list[str]:
    return re.findall(r"[a-z0-9']+", t.lower())


def score_window(segs: list[dict], brief_terms: set[str]) -> tuple[int, str]:
    text = " ".join(s["text"] for s in segs)
    first = segs[0]["text"]
    dur = segs[-1]["end"] - segs[0]["start"]
    words = _words(text)
    fw = _words(first)
    pts, why = 0.0, []
    hook_hits = sum(w in HOOK_WORDS for w in fw)
    if "?" in first:
        pts += 15; why.append("opens with a question")
    if hook_hits:
        pts += min(20, 7 * hook_hits); why.append("strong opening words")
    if re.search(r"\d", first):
        pts += 8; why.append("specific number up front")
    emo = sum(w in EMOTION_WORDS for w in words)
    if emo:
        pts += min(15, 5 * emo); why.append("emotional language")
    pts += min(10, 5 * text.count("!"))
    wps = len(words) / max(dur, 1)
    if 2.0 <= wps <= 3.8:
        pts += 12; why.append("good pacing")
    if re.search(r"[.!?]$", segs[-1]["text"].strip()):
        pts += 10; why.append("ends on a complete thought")
    if 25 <= dur <= 45:
        pts += 10
    if brief_terms and (hits := brief_terms & set(words)):
        pts += min(15, 5 * len(hits)); why.append(f"matches brief ({', '.join(sorted(hits)[:3])})")
    return int(min(100, pts)), ", ".join(why) or "steady talking segment"


TRAILING = {"the", "a", "an", "and", "or", "but", "to", "of", "in", "on", "for", "with", "your", "my", "that", "is"}


def make_hook(text: str, max_words: int = 9) -> str:
    """Pick the punchiest early sentence that fits on screen; never end mid-phrase."""
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()][:5] or [text]

    def strength(s: str) -> int:
        return sum(w in HOOK_WORDS | EMOTION_WORDS for w in _words(s)) + 2 * ("?" in s) + bool(re.search(r"\d", s))

    def shorten(s: str) -> str:
        words = s.split()
        if len(words) <= max_words:
            return s
        clause = re.split(r"[,;:\u2014]", s)[0].split()  # first clause often stands alone
        words = clause if 3 <= len(clause) <= max_words else words[:max_words]
        while len(words) > 3 and words[-1].lower().strip(".,!?") in TRAILING:
            words.pop()
        return " ".join(words).rstrip(",;:")

    # Earlier sentences win ties: the hook should match what the viewer hears first.
    ranked = sorted(enumerate(sentences), key=lambda p: (-(strength(p[1]) - 0.5 * p[0]), p[0]))
    return shorten(ranked[0][1])


def heuristic_moments(segs: list[dict], n: int, brief: str = "") -> list[Moment]:
    brief_terms = {w for w in _words(brief) if len(w) > 3}
    cands = []
    for i in range(len(segs)):
        for j in range(i, len(segs)):
            dur = segs[j]["end"] - segs[i]["start"]
            if dur > config.MAX_CLIP_S:
                break
            if dur >= config.MIN_CLIP_S + 5:
                sc, why = score_window(segs[i:j + 1], brief_terms)
                cands.append((sc, segs[i]["start"], segs[j]["end"], why, segs[i:j + 1]))
    cands.sort(key=lambda c: (-c[0], c[1]))
    chosen = []
    for sc, a, b, why, window in cands:
        if any(a < cb and b > ca for _, ca, cb, *_ in chosen):
            continue
        chosen.append((sc, a, b, why, window))
        if len(chosen) == n:
            break
    out = []
    for sc, a, b, why, window in sorted(chosen, key=lambda c: c[1]):
        text = " ".join(s["text"] for s in window)
        title = window[0]["text"].split(".")[0][:70]
        out.append(Moment(start=a, end=b, title=title, hook=make_hook(text), reason=why, score=sc))
    return out


def snap(m: Moment, segs: list[dict]) -> Moment | None:
    """Align AI-chosen times to transcript segment boundaries and length limits."""
    starts = [s["start"] for s in segs]
    ends = [s["end"] for s in segs]
    a = min(starts, key=lambda t: abs(t - m.start))
    b = min((e for e in ends if e > a), key=lambda t: abs(t - m.end), default=None)
    if b is None:
        return None
    if b - a > config.MAX_CLIP_S:
        b = max((e for e in ends if a < e <= a + config.MAX_CLIP_S), default=a + config.MAX_CLIP_S)
    if b - a < config.MIN_CLIP_S:
        return None
    return m.model_copy(update={"start": a, "end": b, "score": max(0, min(100, m.score))})


class StrategistAgent(Agent):
    name = "strategist"
    role = "Finds viral moments"

    def step(self) -> bool:
        order = db.claim("orders", "transcribed", "planning")
        if not order:
            return False
        oid, n = order["id"], order["clips_requested"] or 3
        self.working(f"Finding the best {n} moments in order #{oid}")
        segs = transcript.load(order["transcript_path"])
        moments = None
        if llm.enabled():
            lines = "\n".join(f"[{s['start']:.1f}-{s['end']:.1f}] {s['text']}" for s in segs)
            res = llm.structured(
                "You are a short-form content strategist. From a timestamped transcript, pick the moments most "
                "likely to perform on TikTok, Reels and Shorts: a strong hook in the first 3 seconds, a single "
                "self-contained idea, payoff by the end, no dependence on earlier context. "
                f"Each clip must be {config.MIN_CLIP_S:.0f}-{config.MAX_CLIP_S:.0f} seconds and must not overlap others. "
                "The hook is on-screen text of at most 9 words. Score each 0-100.",
                f"Client brief: {order.get('brief') or 'none'}\nReturn exactly {n} moments.\n\nTranscript:\n{lines}",
                MomentList, effort="medium",
            )
            if res:
                moments = [m for m in (snap(m, segs) for m in res.moments) if m]
                moments = [m for i, m in enumerate(moments)
                           if not any(m.start < o.end and m.end > o.start for o in moments[:i])][:n]
                self.log(f"Claude proposed {len(moments)} moments for order #{oid}", entity=("order", oid))
        if not moments:
            moments = heuristic_moments(segs, n, order.get("brief") or "")
        if not moments:
            db.update("orders", oid, status="failed", error="No clip-worthy moments found")
            self.log(f"Order #{oid}: no usable moments", "error", ("order", oid))
            return True
        for m in moments:
            cid = db.insert("clips", order_id=oid, start=m.start, end=m.end, title=m.title, hook=m.hook,
                            reason=m.reason, score=m.score, status="planned", updated_at=db.now())
            self.log(f"Clip #{cid} planned {m.start:.0f}s-{m.end:.0f}s (score {m.score}): {m.hook}", entity=("clip", cid))
        db.update("orders", oid, status="in_production")
        self.done()
        return True
