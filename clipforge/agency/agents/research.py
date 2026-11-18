"""Research agent: discovers and qualifies creators who would pay for clipping."""
import os

from pydantic import BaseModel

from .. import db, llm
from .base import Agent

GOOD_NICHES = {"podcast", "business", "finance", "education", "fitness", "health", "tech",
               "marketing", "coaching", "interviews", "comedy", "sports", "real estate", "self-improvement"}


class FitAssessment(BaseModel):
    fit_score: int
    reasons: list[str]


def heuristic_fit(lead: dict) -> tuple[int, list[str]]:
    score, why = 30, []
    f, v, upw = lead.get("followers") or 0, lead.get("avg_views") or 0, lead.get("uploads_per_week") or 0
    if 10_000 <= f <= 2_000_000:
        score += 20; why.append(f"{f:,} followers: big enough to pay, small enough to lack an in-house editor")
    elif f > 2_000_000:
        score += 5; why.append("Very large audience; likely has an existing team")
    elif f:
        why.append("Small audience; budget may be limited")
    if upw >= 1:
        score += 20; why.append(f"Publishes ~{upw:g} long-form videos/week: steady source material")
    if v and f and v / f >= 0.05:
        score += 10; why.append("Healthy views-to-followers ratio")
    if not lead.get("has_shorts"):
        score += 15; why.append("Not posting short-form yet: clear opportunity")
    else:
        why.append("Already posts shorts; pitch quality and volume")
    if (lead.get("niche") or "").lower() in GOOD_NICHES:
        score += 5; why.append(f"'{lead['niche']}' content clips well")
    return max(0, min(100, score)), why


class ResearchAgent(Agent):
    name = "research"
    role = "Finds creators and qualifies leads"
    QUALIFY_AT = 60

    def step(self) -> bool:
        lead = db.row("SELECT * FROM leads WHERE stage = 'new' ORDER BY id LIMIT 1")
        if not lead:
            return False
        self.working(f"Qualifying lead: {lead['name']}")
        score, reasons = heuristic_fit(lead)
        ai = llm.structured(
            "You qualify leads for a short-form video clipping agency. Score 0-100 how likely this "
            "creator is to pay for clips of their long-form content. Be concise and factual; only use the data given.",
            f"Lead data: {({k: lead[k] for k in ('name', 'platform', 'niche', 'followers', 'avg_views', 'uploads_per_week', 'has_shorts', 'notes')})}\n"
            f"Heuristic score: {score}. Heuristic reasons: {reasons}",
            FitAssessment, effort="low",
        )
        if ai:
            score, reasons = max(0, min(100, ai.fit_score)), ai.reasons
        stage = "qualified" if score >= self.QUALIFY_AT else "disqualified"
        db.update("leads", lead["id"], fit_score=score, fit_reasons=reasons, stage=stage)
        self.log(f"{lead['name']} scored {score} -> {stage}", entity=("lead", lead["id"]))
        self.done()
        return True


def discover_youtube(query: str, max_results: int = 10) -> list[int]:
    """Create leads from a YouTube channel search. Needs YOUTUBE_API_KEY."""
    import httpx

    key = os.getenv("YOUTUBE_API_KEY")
    if not key:
        raise RuntimeError("Set YOUTUBE_API_KEY to discover channels automatically, or add leads manually/CSV.")
    base = "https://www.googleapis.com/youtube/v3"
    with httpx.Client(timeout=20) as h:
        s = h.get(f"{base}/search", params={"part": "snippet", "type": "channel", "q": query,
                                             "maxResults": max_results, "key": key}).raise_for_status().json()
        ids = [i["snippet"]["channelId"] for i in s.get("items", [])]
        if not ids:
            return []
        c = h.get(f"{base}/channels", params={"part": "snippet,statistics", "id": ",".join(ids),
                                               "key": key}).raise_for_status().json()
    created = []
    for ch in c.get("items", []):
        url = f"https://www.youtube.com/channel/{ch['id']}"
        if db.row("SELECT id FROM leads WHERE channel_url = ?", (url,)):
            continue
        st = ch.get("statistics", {})
        subs, views, vids = int(st.get("subscriberCount", 0)), int(st.get("viewCount", 0)), int(st.get("videoCount", 0)) or 1
        created.append(db.insert(
            "leads", name=ch["snippet"]["title"], channel_url=url, platform="youtube", niche=query,
            followers=subs, avg_views=views // vids, notes=ch["snippet"].get("description", "")[:500],
            stage="new", updated_at=db.now(),
        ))
    db.log("research", f"Discovered {len(created)} new channels for '{query}'")
    return created
