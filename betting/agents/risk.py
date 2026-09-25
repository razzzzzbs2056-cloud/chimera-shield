"""RiskManager: turns opportunities into sized, bankroll-safe bets."""
from __future__ import annotations

from collections import defaultdict

from ..odds import arb_stakes, kelly_fraction
from .base import Agent, Desk


class RiskManager(Agent):
    """Fractional Kelly with hard caps.

    * ``kelly_multiplier`` — 0.25 = quarter Kelly (full Kelly is far too volatile
      when fair probabilities are only estimates).
    * ``max_bet_pct`` — never risk more than this share of bankroll on one bet.
    * ``max_game_pct`` — total open exposure per game.
    * ``daily_stop_pct`` — stop betting after losing this share of bankroll today.
    * One value bet per game+market (avoids stacking correlated lines).
    """
    name = "RiskManager"
    role = "Sizes stakes with fractional Kelly and enforces exposure limits."

    def __init__(self, kelly_multiplier: float = 0.25, max_bet_pct: float = 0.02,
                 max_game_pct: float = 0.05, arb_pct: float = 0.05, min_stake: float = 1.0,
                 daily_stop_pct: float = 0.10, max_bets: int = 25):
        self.kelly_multiplier = kelly_multiplier
        self.max_bet_pct = max_bet_pct
        self.max_game_pct = max_game_pct
        self.arb_pct = arb_pct
        self.min_stake = min_stake
        self.daily_stop_pct = daily_stop_pct
        self.max_bets = max_bets

    def run(self, desk: Desk) -> None:
        ledger = desk.ledger
        bankroll = ledger.bankroll()
        if ledger.pnl_today() <= -self.daily_stop_pct * ledger.starting_bankroll:
            self.say(desk, "daily stop-loss hit; no new bets today")
            return
        if bankroll <= 0:
            self.say(desk, "bankroll exhausted; no new bets")
            return

        game_exposure: dict[str, float] = defaultdict(float)
        # Already bet? Don't bet it again. Arb groups drop out if any leg is logged.
        logged_groups = {o.group for o in desk.opportunities if o.group and ledger.has_bet(o)}
        fresh = [o for o in desk.opportunities
                 if not ledger.has_bet(o) and (o.group is None or o.group not in logged_groups)]

        def room(game_id: str) -> float:
            used = ledger.exposure(game_id) + game_exposure[game_id]
            return self.max_game_pct * bankroll - used

        approved = []

        # Arbs first: guaranteed margin, all legs or nothing.
        arb_groups: dict[str, list] = defaultdict(list)
        for o in fresh:
            if o.kind == "arb":
                arb_groups[o.group].append(o)
        for legs in sorted(arb_groups.values(), key=lambda ls: -ls[0].edge):
            total = min(self.arb_pct * bankroll, room(legs[0].game.id))
            stakes = arb_stakes([l.price for l in legs], total)
            if min(stakes) < self.min_stake:
                continue
            for leg, s in zip(legs, stakes):
                leg.stake = round(s, 2)
            game_exposure[legs[0].game.id] += total
            approved.extend(legs)

        # Value bets, best edge first, one per game+market.
        taken = set()
        values = sorted((o for o in fresh if o.kind == "value"), key=lambda o: -o.edge)
        for o in values:
            slot = (o.game.id, o.market)
            if slot in taken:
                continue
            f = kelly_fraction(o.fair_prob, o.price) * self.kelly_multiplier
            stake = min(f, self.max_bet_pct) * bankroll
            stake = min(stake, room(o.game.id))
            if stake < self.min_stake:
                continue
            o.stake = round(stake, 2)
            game_exposure[o.game.id] += o.stake
            taken.add(slot)
            approved.append(o)

        # Respect max_bets without splitting arb groups.
        final, count, seen_groups = [], 0, set()
        for o in approved:
            if o.group:
                if o.group in seen_groups:
                    final.append(o)
                    continue
                n = sum(1 for x in approved if x.group == o.group)
                if count + n > self.max_bets:
                    continue
                seen_groups.add(o.group)
                count += n
                final.append(o)
            elif count < self.max_bets:
                count += 1
                final.append(o)

        desk.approved = final
        total = sum(o.stake for o in final)
        self.say(desk, f"approved {len(final)} bets, ${total:,.2f} at risk "
                       f"(bankroll ${bankroll:,.2f})")
