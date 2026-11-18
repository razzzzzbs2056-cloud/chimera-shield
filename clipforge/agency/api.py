"""HTTP API + CEO dashboard."""
import csv
import io
import json
import logging
import shutil
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from . import config, db, llm
from .agents.business import price_for
from .agents.research import discover_youtube
from .orchestrator import Orchestrator

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
STATIC = Path(__file__).parent / "static"
orch: Orchestrator | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global orch
    orch = Orchestrator()
    orch.start()
    yield
    await orch.stop()


app = FastAPI(title="ClipForge", description="AI-run video clipping agency", lifespan=lifespan)
app.mount("/files", StaticFiles(directory=config.OUTPUT), name="files")
app.mount("/static", StaticFiles(directory=STATIC), name="static")


def _file_url(path: str | None) -> str | None:
    return f"/files/{Path(path).name}" if path else None


def _clip_view(c: dict) -> dict:
    c = dict(c)
    for k in ("qc_report", "publish", "fix_notes"):
        c[k] = json.loads(c[k]) if c.get(k) else None
    c["video_url"] = _file_url(c.get("final_path"))
    c["thumb_url"] = _file_url(c.get("thumb_path"))
    c["srt_url"] = _file_url(c.get("srt_path"))
    for k in ("raw_path", "final_path", "thumb_path", "srt_path"):
        c.pop(k, None)
    return c


@app.get("/")
def index():
    return FileResponse(STATIC / "index.html")


@app.get("/api/dashboard")
def dashboard():
    paid = db.row("SELECT COALESCE(SUM(amount_cents),0) v FROM invoices WHERE status = 'paid'")["v"]
    outstanding = db.row("SELECT COALESCE(SUM(amount_cents),0) v FROM invoices WHERE status IN ('sent','overdue')")["v"]
    month_start = db.now() - 30 * 86400
    last30 = db.row("SELECT COALESCE(SUM(amount_cents),0) v FROM invoices WHERE created_at > ?", (month_start,))["v"]
    qc = db.row("SELECT COUNT(*) n, SUM(CASE WHEN attempts = 1 AND status NOT IN ('qc_failed') THEN 1 ELSE 0 END) first "
                "FROM clips WHERE qc_score IS NOT NULL")
    clip_counts = {r["status"]: r["n"] for r in db.rows("SELECT status, COUNT(*) n FROM clips GROUP BY status")}
    order_counts = {r["status"]: r["n"] for r in db.rows("SELECT status, COUNT(*) n FROM orders GROUP BY status")}
    lead_counts = {r["stage"]: r["n"] for r in db.rows("SELECT stage, COUNT(*) n FROM leads GROUP BY stage")}
    return {
        "ai_mode": "claude" if llm.enabled() else "heuristic",
        "model": config.ANTHROPIC_MODEL,
        "kpis": {
            "revenue_paid": paid / 100, "revenue_outstanding": outstanding / 100, "billed_30d": last30 / 100,
            "clients": db.row("SELECT COUNT(*) n FROM clients WHERE status = 'active'")["n"],
            "orders_active": sum(v for k, v in order_counts.items() if k not in ("delivered", "failed")),
            "awaiting_approval": clip_counts.get("awaiting_approval", 0),
            "clips_delivered": clip_counts.get("scheduled", 0),
            "qc_first_pass_rate": round(100 * (qc["first"] or 0) / qc["n"]) if qc["n"] else None,
            "leads_pipeline": sum(v for k, v in lead_counts.items() if k not in ("won", "lost", "disqualified")),
        },
        "clip_counts": clip_counts, "order_counts": order_counts, "lead_counts": lead_counts,
        "agents": db.rows("SELECT * FROM agents"),
        "events": db.rows("SELECT * FROM events ORDER BY id DESC LIMIT 80"),
        "approval_queue": [_clip_view(c) for c in db.rows(
            "SELECT c.*, o.title order_title, cl.name client_name FROM clips c JOIN orders o ON o.id = c.order_id "
            "LEFT JOIN clients cl ON cl.id = o.client_id WHERE c.status = 'awaiting_approval' ORDER BY c.id")],
        "clips": [_clip_view(c) for c in db.rows(
            "SELECT c.*, o.title order_title FROM clips c JOIN orders o ON o.id = c.order_id ORDER BY c.id DESC LIMIT 100")],
        "orders": db.rows("SELECT o.*, c.name client_name, (SELECT COUNT(*) FROM clips WHERE order_id = o.id) clip_total, "
                          "(SELECT COUNT(*) FROM clips WHERE order_id = o.id AND status = 'scheduled') clip_done "
                          "FROM orders o LEFT JOIN clients c ON c.id = o.client_id ORDER BY o.id DESC LIMIT 50"),
        "leads": db.rows("SELECT * FROM leads ORDER BY CASE stage WHEN 'outreach_drafted' THEN 0 WHEN 'contacted' THEN 1 "
                         "WHEN 'qualified' THEN 2 WHEN 'new' THEN 3 ELSE 4 END, fit_score DESC LIMIT 100"),
        "outreach": db.rows("SELECT o.*, l.name lead_name, l.email lead_email FROM outreach o JOIN leads l ON l.id = o.lead_id "
                            "WHERE o.status = 'draft' ORDER BY o.id"),
        "clients": db.rows("SELECT c.*, (SELECT COUNT(*) FROM orders WHERE client_id = c.id) orders, "
                           "(SELECT COALESCE(SUM(amount_cents),0) FROM invoices WHERE client_id = c.id AND status='paid') paid_cents "
                           "FROM clients c ORDER BY c.id DESC"),
        "invoices": db.rows("SELECT i.*, c.name client_name FROM invoices i LEFT JOIN clients c ON c.id = i.client_id "
                            "ORDER BY i.id DESC LIMIT 50"),
        "packages": {k: {"clips": v[0], "price": v[1] / 100} for k, v in config.PACKAGES.items()},
    }


# ---------------------------------------------------------------- clients & orders
class ClientIn(BaseModel):
    name: str
    email: str | None = None
    package: str = "starter"


@app.post("/api/clients")
def create_client(c: ClientIn):
    if c.package not in config.PACKAGES:
        raise HTTPException(400, f"package must be one of {list(config.PACKAGES)}")
    cid = db.insert("clients", name=c.name, email=c.email, package=c.package, status="active")
    db.log("business", f"Client added: {c.name}", entity_type="client", entity_id=cid)
    return {"id": cid}


@app.post("/api/orders")
async def create_order(client_id: int = Form(...), title: str = Form(...), brief: str = Form(""),
                       clips_requested: int | None = Form(None), video: UploadFile = File(...),
                       transcript: UploadFile | None = File(None)):
    client = db.row("SELECT * FROM clients WHERE id = ?", (client_id,))
    if not client:
        raise HTTPException(404, "client not found")
    n, price = price_for(client["package"])
    if clips_requested:
        n = max(1, min(20, clips_requested))
    oid = db.insert("orders", client_id=client_id, title=title, brief=brief, clips_requested=n,
                    price_cents=price, status="uploading")
    vpath = config.UPLOADS / f"order_{oid}{Path(video.filename or 'v.mp4').suffix or '.mp4'}"
    with vpath.open("wb") as f:
        shutil.copyfileobj(video.file, f)
    tpath = None
    if transcript and transcript.filename:
        tpath = config.UPLOADS / f"order_{oid}_transcript{Path(transcript.filename).suffix}"
        with tpath.open("wb") as f:
            shutil.copyfileobj(transcript.file, f)
    db.update("orders", oid, source_path=str(vpath), transcript_path=str(tpath) if tpath else None, status="received")
    db.log("intake", f"Order #{oid} received from {client['name']}: {title}", entity_type="order", entity_id=oid)
    return {"id": oid}


# ---------------------------------------------------------------- approvals
class Review(BaseModel):
    action: str  # approve | reject | revise
    note: str = ""


@app.post("/api/clips/{cid}/review")
def review_clip(cid: int, r: Review):
    clip = db.row("SELECT * FROM clips WHERE id = ?", (cid,))
    if not clip:
        raise HTTPException(404, "clip not found")
    if clip["status"] not in ("awaiting_approval", "qc_failed"):
        raise HTTPException(409, f"clip is {clip['status']}, not awaiting review")
    if r.action == "approve":
        db.update("clips", cid, status="approved", review_note=r.note)
        msg = f"CEO approved clip #{cid}"
    elif r.action == "reject":
        db.update("clips", cid, status="rejected", review_note=r.note)
        msg = f"CEO rejected clip #{cid}" + (f": {r.note}" if r.note else "")
    elif r.action == "revise":
        db.update("clips", cid, status="needs_recaption", review_note=r.note, fix_notes=["weak_hook"], attempts=0)
        msg = f"CEO asked for a new hook on clip #{cid}" + (f": {r.note}" if r.note else "")
    else:
        raise HTTPException(400, "action must be approve, reject or revise")
    db.log("ceo", msg, entity_type="clip", entity_id=cid)
    return {"ok": True}


# ---------------------------------------------------------------- leads & outreach
class LeadIn(BaseModel):
    name: str
    email: str | None = None
    channel_url: str | None = None
    platform: str | None = "youtube"
    niche: str | None = None
    followers: int = 0
    avg_views: int = 0
    uploads_per_week: float = 0
    has_shorts: bool = False
    notes: str | None = None


def _add_lead(l: LeadIn) -> int:
    d = l.model_dump()
    d["has_shorts"] = int(d["has_shorts"])
    return db.insert("leads", **d, stage="new", updated_at=db.now())


@app.post("/api/leads")
def create_lead(l: LeadIn):
    return {"id": _add_lead(l)}


@app.post("/api/leads/import")
async def import_leads(file: UploadFile = File(...)):
    text = (await file.read()).decode("utf-8-sig", errors="replace")
    ids = []
    for rowd in csv.DictReader(io.StringIO(text)):
        rowd = {k.strip().lower(): (v or "").strip() for k, v in rowd.items() if k}
        if not rowd.get("name"):
            continue
        ids.append(_add_lead(LeadIn(
            name=rowd["name"], email=rowd.get("email") or None, channel_url=rowd.get("channel_url") or None,
            platform=rowd.get("platform") or "youtube", niche=rowd.get("niche") or None,
            followers=int(float(rowd.get("followers") or 0)), avg_views=int(float(rowd.get("avg_views") or 0)),
            uploads_per_week=float(rowd.get("uploads_per_week") or 0),
            has_shorts=rowd.get("has_shorts", "").lower() in ("1", "true", "yes"), notes=rowd.get("notes") or None)))
    db.log("research", f"Imported {len(ids)} leads from CSV")
    return {"imported": len(ids)}


class Discover(BaseModel):
    query: str
    max_results: int = 10


@app.post("/api/leads/discover")
def discover(d: Discover):
    try:
        return {"created": len(discover_youtube(d.query, d.max_results))}
    except RuntimeError as e:
        raise HTTPException(400, str(e))


class Stage(BaseModel):
    stage: str


@app.post("/api/leads/{lid}/stage")
def set_stage(lid: int, s: Stage):
    if s.stage not in ("new", "qualified", "contacted", "won", "lost", "disqualified"):
        raise HTTPException(400, "invalid stage")
    db.update("leads", lid, stage=s.stage)
    db.log("ceo", f"Lead #{lid} moved to {s.stage}", entity_type="lead", entity_id=lid)
    return {"ok": True}


class OutreachEdit(BaseModel):
    action: str  # sent | discard | save
    subject: str | None = None
    body: str | None = None


@app.post("/api/outreach/{oid}")
def outreach_action(oid: int, e: OutreachEdit):
    o = db.row("SELECT * FROM outreach WHERE id = ?", (oid,))
    if not o:
        raise HTTPException(404, "not found")
    if e.subject is not None or e.body is not None:
        db.update("outreach", oid, subject=e.subject or o["subject"], body=e.body or o["body"])
    if e.action == "sent":
        db.update("outreach", oid, status="sent", sent_at=db.now())
        inc = 0 if o["kind"] == "initial" else 1
        db.execute("UPDATE leads SET stage = 'contacted', last_contact_at = ?, followups_sent = followups_sent + ?, "
                   "updated_at = ? WHERE id = ?", (db.now(), inc, db.now(), o["lead_id"]))
        db.log("ceo", f"Outreach #{oid} ({o['kind']}) marked sent", entity_type="lead", entity_id=o["lead_id"])
    elif e.action == "discard":
        db.update("outreach", oid, status="discarded")
        lead = db.row("SELECT stage FROM leads WHERE id = ?", (o["lead_id"],))
        if lead and lead["stage"] == "outreach_drafted":
            db.update("leads", o["lead_id"], stage="lost")
    return {"ok": True}


# ---------------------------------------------------------------- money & control
@app.post("/api/invoices/{iid}/paid")
def invoice_paid(iid: int):
    db.update("invoices", iid, status="paid", paid_at=db.now())
    db.log("business", f"Invoice #{iid} marked paid", entity_type="invoice", entity_id=iid)
    return {"ok": True}


@app.post("/api/agents/{name}/toggle")
def toggle_agent(name: str):
    a = db.row("SELECT * FROM agents WHERE name = ?", (name,))
    if not a:
        raise HTTPException(404, "agent not found")
    en = 0 if a["enabled"] else 1
    db.update("agents", name, key="name", enabled=en, status="idle" if en else "paused")
    db.log("ceo", f"{'Resumed' if en else 'Paused'} {name} agent")
    return {"enabled": bool(en)}
