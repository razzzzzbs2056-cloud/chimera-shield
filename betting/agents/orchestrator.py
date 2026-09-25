"""HeadTrader: the lead agent that runs every sub-agent in order."""
from __future__ import annotations

from dataclasses import dataclass, field

from ..feeds import Feed
from ..ledger import Ledger
from .analyst import Analyst
from .base import Agent, Desk
from .hunters import ArbHunter, ValueHunter
from .market import FairValueAgent, LineShopper, OddsScout
from .model import EloModel
from .risk import RiskManager
from .tracker import Tracker


@dataclass
class DeskConfig:
    sports: list[str] = field(default_factory=lambda: ["americanfootball_nfl", "basketball_nba",
                                                       "soccer_epl"])
    devig_method: str = "power"
    min_edge: float = 0.02
    min_arb: float = 0.005
    model_weight: float = 0.25
    kelly_multiplier: float = 0.25
    max_bet_pct: float = 0.02
    max_game_pct: float = 0.05
    place: bool = True
    mode: str = "paper"
    analyst: bool | None = None       # None = auto (on when ANTHROPIC_API_KEY is set)


class HeadTrader:
    """Coordinates the desk:

    OddsScout -> LineShopper -> FairValue -> EloModel -> ValueHunter + ArbHunter
              -> RiskManager -> Tracker -> Analyst
    """

    def __init__(self, feed: Feed, ledger: Ledger, config: DeskConfig | None = None):
        self.feed = feed
        self.ledger = ledger
        self.config = cfg = config or DeskConfig()
        self.model = EloModel(weight=cfg.model_weight)
        self.tracker = Tracker(mode=cfg.mode, place=cfg.place)
        self.pipeline: list[Agent] = [
            OddsScout(feed),
            LineShopper(),
            FairValueAgent(method=cfg.devig_method),
            self.model,
            ValueHunter(min_edge=cfg.min_edge),
            ArbHunter(min_margin=cfg.min_arb),
            RiskManager(kelly_multiplier=cfg.kelly_multiplier, max_bet_pct=cfg.max_bet_pct,
                        max_game_pct=cfg.max_game_pct),
            self.tracker,
            Analyst(enabled=cfg.analyst),
        ]

    def desk(self) -> Desk:
        return Desk(ledger=self.ledger, sports=list(self.config.sports))

    def scan(self) -> Desk:
        desk = self.desk()
        for agent in self.pipeline:
            agent.run(desk)
        return desk

    def settle(self) -> Desk:
        """Pull final scores, grade open bets, and teach the Elo model."""
        desk = self.desk()
        desk.scores = self.feed.scores(desk.sports)
        self.tracker.settle(desk, desk.scores)
        self.model.learn(desk, desk.scores)
        return desk

    def train(self, results: list[dict]) -> Desk:
        desk = self.desk()
        self.model.learn(desk, results)
        return desk

    def roster(self) -> list[dict]:
        return [{"name": a.name, "role": a.role} for a in self.pipeline]
