from fastapi import APIRouter
from pydantic import BaseModel
import os

from betting.agents import DeskConfig, HeadTrader
from betting.feeds import OddsAPIFeed, SampleFeed
from betting.ledger import DEFAULT_DB, Ledger

router = APIRouter(prefix="/api/betting", tags=["betting"])


def _trader(sample: bool, config: DeskConfig) -> HeadTrader:
    feed = SampleFeed() if sample or not os.getenv("ODDS_API_KEY") else OddsAPIFeed()
    if isinstance(feed, SampleFeed) and config.sports == DeskConfig().sports:
        config.sports = []
    return HeadTrader(feed, Ledger(os.getenv("BETTING_DB", str(DEFAULT_DB))), config)


class ScanRequest(BaseModel):
    sports: list[str] | None = None
    sample: bool = False
    min_edge: float = 0.02
    record: bool = True
    analyst: bool = False


@router.get("/agents")
def agents():
    return _trader(True, DeskConfig()).roster()


@router.post("/scan")
def scan(req: ScanRequest):
    cfg = DeskConfig(min_edge=req.min_edge, place=req.record, analyst=req.analyst)
    if req.sports:
        cfg.sports = req.sports
    desk = _trader(req.sample, cfg).scan()
    return {"log": desk.log, "bets": [o.to_dict() for o in desk.approved], "briefing": desk.briefing}


@router.post("/settle")
def settle(sample: bool = False):
    desk = _trader(sample, DeskConfig()).settle()
    return {"log": desk.log, "report": desk.ledger.report()}


@router.get("/bets")
def bets(status: str | None = None):
    ledger = Ledger(os.getenv("BETTING_DB", str(DEFAULT_DB)))
    return [dict(r) for r in ledger.bets(status=status)]


@router.get("/report")
def report():
    return Ledger(os.getenv("BETTING_DB", str(DEFAULT_DB))).report()
