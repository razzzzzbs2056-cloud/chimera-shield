"""Publishing agent: packages approved clips per platform and books schedule slots.

It writes a ready-to-post package (video, caption, hashtags, SRT, time slot) for
TikTok, Instagram Reels and YouTube Shorts. Direct uploading needs each platform's
API approval and OAuth tokens; plug those in at `upload()` when you have them."""
import datetime as dt
import json
import os
import re
from pathlib import Path

from pydantic import BaseModel

from .. import config, db, llm
from .base import Agent

PLATFORMS = {
    "tiktok": {"max_caption": 2200, "max_tags": 5},
    "instagram_reels": {"max_caption": 2200, "max_tags": 8},
    "youtube_shorts": {"max_caption": 100, "max_tags": 3},  # caption = Shorts title
}
SLOTS = [int(h) for h in os.getenv("CLIPFORGE_SLOTS", "9,13,19").split(",")]
STOP = {"the", "and", "that", "this", "with", "have", "from", "your", "you", "what", "they", "just", "about",
        "there", "their", "were", "been", "when", "will", "into", "than", "then", "them", "because", "really"}


class Copy(BaseModel):
    caption: str
    hashtags: list[str]


def next_slot(platform: str, client_id: int) -> float:
    """Next free posting slot (local time) for this client's account on this platform."""
    taken = set()
    for r in db.rows("SELECT c.publish FROM clips c JOIN orders o ON o.id = c.order_id "
                     "WHERE o.client_id = ? AND c.publish IS NOT NULL", (client_id,)):
        taken.add(round(json.loads(r["publish"]).get(platform, {}).get("scheduled_for", 0)))
    day = dt.datetime.now().replace(minute=0, second=0, microsecond=0)
    for d in range(60):
        for h in SLOTS:
            t = (day + dt.timedelta(days=d)).replace(hour=h)
            if t > dt.datetime.now() + dt.timedelta(minutes=30) and round(t.timestamp()) not in taken:
                return t.timestamp()
    return (day + dt.timedelta(days=61)).timestamp()


def fallback_copy(clip: dict, niche: str) -> Copy:
    words = [w for w in re.findall(r"[a-z]{4,}", (clip["title"] + " " + clip["hook"]).lower()) if w not in STOP]
    tags = list(dict.fromkeys([niche.replace(" ", "")] if niche else []) | dict.fromkeys(words[:4]))
    return Copy(caption=f"{clip['hook']}\n\n{clip['title']}", hashtags=[t for t in tags if t] + ["shorts"])


class PublishingAgent(Agent):
    name = "publisher"
    role = "Schedules approved clips"

    def step(self) -> bool:
        clip = db.claim("clips", "approved", "publishing")
        if not clip:
            return False
        cid = clip["id"]
        order = db.row("SELECT * FROM orders WHERE id = ?", (clip["order_id"],))
        client = db.row("SELECT * FROM clients WHERE id = ?", (order["client_id"],)) or {}
        self.working(f"Packaging clip #{cid} for TikTok, Reels and Shorts")
        copy = llm.structured(
            "Write a social caption and hashtags for a short vertical video. Caption: 1-2 short lines, "
            "conversational, ends with a question or call to comment. Hashtags without '#', lowercase, specific.",
            f"Hook: {clip['hook']}\nTitle: {clip['title']}\nCreator: {client.get('name')}\nBrief: {order.get('brief')}",
            Copy, effort="low") or fallback_copy(clip, "")
        tags = [t.strip("#").replace(" ", "").lower() for t in copy.hashtags if t.strip("#")]
        package = {}
        for p, rules in PLATFORMS.items():
            tagstr = " ".join(f"#{t}" for t in tags[:rules["max_tags"]])
            text = (clip["title"] if p == "youtube_shorts" else copy.caption)
            text = f"{text} {tagstr}".strip()[:rules["max_caption"]]
            package[p] = {"caption": text, "scheduled_for": next_slot(p, order["client_id"]), "status": "ready"}
        out = Path(config.OUTPUT) / f"clip_{cid}_publish.json"
        out.write_text(json.dumps({"clip_id": cid, "video": clip["final_path"], "srt": clip["srt_path"],
                                   "platforms": package}, indent=2))
        db.update("clips", cid, status="scheduled", publish=package)
        when = dt.datetime.fromtimestamp(min(v["scheduled_for"] for v in package.values()))
        self.log(f"Clip #{cid} packaged for 3 platforms, first slot {when:%a %d %b %H:%M}", entity=("clip", cid))
        self.done()
        return True
