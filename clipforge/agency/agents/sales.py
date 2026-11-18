"""Sales agent: drafts personalised outreach and follow-ups.

Nothing is sent automatically. Drafts land in the CEO's queue; once you approve
and send one, mark it sent and the agent tracks follow-up timing."""
import os

from pydantic import BaseModel

from .. import config, db, llm
from .base import Agent

FOLLOWUP_DAYS = float(os.getenv("CLIPFORGE_FOLLOWUP_DAYS", "3"))
MAX_FOLLOWUPS = 2
SENDER = os.getenv("CLIPFORGE_SENDER_NAME", "The ClipForge team")


class Email(BaseModel):
    subject: str
    body: str


def template(lead: dict, kind: str) -> Email:
    first = lead["name"].split()[0]
    price = config.PACKAGES["starter"][1] // 100
    if kind == "initial":
        return Email(
            subject=f"{config.PACKAGES['starter'][0]} free clips from your latest video?",
            body=(f"Hi {first},\n\nI watch a lot of {lead.get('niche') or 'long-form'} content and yours stands out. "
                  "Your long videos have moments that would do well as TikToks, Reels and Shorts, "
                  "and right now most of them stay inside the full episode.\n\n"
                  "We turn one long video into ready-to-post vertical clips with captions and hooks, "
                  f"usually within 24 hours. Plans start at ${price} per video.\n\n"
                  "Want me to clip your latest upload for free so you can judge the quality?\n\n"
                  f"Best,\n{SENDER}"),
        )
    n = lead.get("followups_sent", 0) + 1
    return Email(
        subject=f"Re: free clips from your latest video",
        body=(f"Hi {first},\n\n" + (
            "Bumping this in case it got buried. Happy to send 3 sample clips, no strings attached."
            if n == 1 else
            "Last note from me: if short-form isn't a priority right now, no problem. "
            "If it becomes one, reply and I'll send samples the same day."
        ) + f"\n\nBest,\n{SENDER}"),
    )


class SalesAgent(Agent):
    name = "sales"
    role = "Outreach and follow-ups"

    def step(self) -> bool:
        lead = db.row("SELECT * FROM leads WHERE stage = 'qualified' ORDER BY fit_score DESC, id LIMIT 1")
        if lead:
            return self._draft(lead, "initial", "outreach_drafted")
        due = db.now() - FOLLOWUP_DAYS * 86400
        lead = db.row(
            "SELECT * FROM leads WHERE stage = 'contacted' AND last_contact_at < ? AND followups_sent < ? "
            "AND NOT EXISTS (SELECT 1 FROM outreach o WHERE o.lead_id = leads.id AND o.status = 'draft') "
            "ORDER BY last_contact_at LIMIT 1", (due, MAX_FOLLOWUPS))
        if lead:
            return self._draft(lead, f"followup{lead['followups_sent'] + 1}", "contacted")
        return False

    def _draft(self, lead: dict, kind: str, stage: str) -> bool:
        self.working(f"Writing {kind} email for {lead['name']}")
        email = llm.structured(
            "You write short, specific cold emails for a video clipping agency that turns long-form videos "
            "into TikToks, Reels and Shorts. Under 120 words, plain text, one clear ask, no hype, no invented facts. "
            f"Sign off as: {SENDER}",
            f"Email type: {kind}. Lead: name={lead['name']}, platform={lead.get('platform')}, niche={lead.get('niche')}, "
            f"followers={lead.get('followers')}, why they fit={lead.get('fit_reasons')}, notes={lead.get('notes')}. "
            f"Starter plan: {config.PACKAGES['starter'][0]} clips for ${config.PACKAGES['starter'][1] // 100}. "
            "Offer free sample clips.",
            Email, effort="low",
        ) or template(lead, kind)
        oid = db.insert("outreach", lead_id=lead["id"], kind=kind, subject=email.subject, body=email.body, status="draft")
        db.update("leads", lead["id"], stage=stage)
        self.log(f"Drafted {kind} email to {lead['name']} (awaiting your approval)", entity=("outreach", oid))
        self.done()
        return True
