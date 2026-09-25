import json
import unittest

from betting import odds
from betting.agents import DeskConfig, HeadTrader
from betting.agents.tracker import grade
from betting.feeds import DATA_DIR, SampleFeed
from betting.ledger import Ledger


class OddsMath(unittest.TestCase):
    def test_conversions(self):
        self.assertAlmostEqual(odds.american_to_decimal(-110), 1.9091, places=4)
        self.assertAlmostEqual(odds.american_to_decimal(150), 2.5)
        self.assertEqual(odds.decimal_to_american(2.5), 150)
        self.assertEqual(odds.decimal_to_american(1.9091), -110)

    def test_devig_sums_to_one(self):
        for method in ("multiplicative", "power"):
            probs = odds.devig([1.91, 1.91, 12.0], method)
            self.assertAlmostEqual(sum(probs), 1.0, places=9)

    def test_power_devig_shades_longshot(self):
        mult = odds.devig([1.25, 4.5], "multiplicative")
        power = odds.devig([1.25, 4.5], "power")
        self.assertLess(power[1], mult[1])

    def test_ev_and_kelly(self):
        self.assertAlmostEqual(odds.expected_value(0.5, 2.1), 0.05)
        self.assertAlmostEqual(odds.kelly_fraction(0.5, 2.1), 0.05 / 1.1)
        self.assertEqual(odds.kelly_fraction(0.4, 2.0), 0.0)

    def test_arbitrage(self):
        self.assertIsNone(odds.arbitrage([1.91, 1.91]))
        margin = odds.arbitrage([2.1, 2.1])
        self.assertAlmostEqual(margin, 0.05)
        stakes = odds.arb_stakes([1.7, 2.56], 100)
        self.assertAlmostEqual(stakes[0] * 1.7, stakes[1] * 2.56)


class Grading(unittest.TestCase):
    def bet(self, **kw):
        base = {"selection": "Home", "market": "h2h", "point": None, "line_key": "h2h",
                "sport": "basketball_nba"}
        base.update(kw)
        return base

    def test_grades(self):
        s = {"Home": 100, "Away": 97}
        self.assertEqual(grade(self.bet(), "Home", "Away", s), "won")
        self.assertEqual(grade(self.bet(selection="Away", market="spreads", point=3.0),
                               "Home", "Away", s), "push")
        self.assertEqual(grade(self.bet(selection="Away", market="spreads", point=3.5),
                               "Home", "Away", s), "won")
        self.assertEqual(grade(self.bet(selection="Over", market="totals", point=196.5),
                               "Home", "Away", s), "won")
        tie = {"Home": 1, "Away": 1}
        self.assertEqual(grade(self.bet(selection="Draw", sport="soccer_epl"), "Home", "Away", tie), "won")
        self.assertEqual(grade(self.bet(sport="soccer_epl"), "Home", "Away", tie), "lost")


class DeskEndToEnd(unittest.TestCase):
    def test_scan_settle_cycle(self):
        ledger = Ledger(":memory:")
        trader = HeadTrader(SampleFeed(), ledger, DeskConfig(sports=[], analyst=False))
        trader.train(json.loads((DATA_DIR / "sample_history.json").read_text()))

        desk = trader.scan()
        self.assertTrue(desk.approved)
        kinds = {o.kind for o in desk.approved}
        self.assertIn("arb", kinds)
        self.assertIn("value", kinds)
        for o in desk.approved:
            self.assertGreater(o.edge, 0)
            self.assertLessEqual(o.stake, 0.05 * 1000 + 1e-6)

        # Arb legs return the same payout whichever side wins.
        legs = [o for o in desk.approved if o.group == desk.approved[0].group]
        payouts = [o.stake * o.price for o in legs]
        self.assertAlmostEqual(min(payouts), max(payouts), delta=0.05)

        # Re-scanning does not double up.
        self.assertEqual(trader.scan().approved, [])

        trader.settle()
        report = ledger.report()
        self.assertEqual(report["open_bets"], 0)
        self.assertEqual(report["settled_bets"], len(desk.approved))


if __name__ == "__main__":
    unittest.main()
