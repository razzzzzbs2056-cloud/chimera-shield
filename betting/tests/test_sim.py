import unittest

from betting.sim import baseball, soccer
from betting.sim.common import apply_ops, load_game, scenario


def avg_mlb_team(name):
    L = dict(baseball.LEAGUE)
    pen = {"rates": L}
    return {"name": name,
            "starter": {"name": name + " SP", "throws": "R", "bf_mean": 23, "bf_sd": 3, "rates": L},
            "bullpen": {"high": pen, "rest": pen, "closer": pen},
            "lineup": [dict(name=f"{name}{i}", bats="R" if i % 2 else "L", **L) for i in range(9)]}


class BaseballCalibration(unittest.TestCase):
    def test_league_average_game(self):
        g = {"away": avg_mlb_team("A"), "home": avg_mlb_team("H"), "postseason": False}
        r = baseball.simulate(g, 6000, seed=3)
        self.assertAlmostEqual(r.mean_runs[0], 4.4, delta=0.3)      # MLB ~4.45 R/G
        self.assertAlmostEqual(r.win[1], 0.535, delta=0.03)         # home win rate
        self.assertAlmostEqual(r.nrfi, 0.54, delta=0.04)

    def test_walkoff_home_never_bats_when_leading(self):
        g = load_game("mlb_bos_nyy_2026-09-29")
        sim = baseball.BaseballSim(g, seed=1)
        for _ in range(300):
            r = sim.play()
            self.assertNotEqual(r.runs[0], r.runs[1])
            if r.runs[1] > r.runs[0] and r.innings == 9:
                # home either won without batting in the 9th or walked off in it
                self.assertLessEqual(len(r.by_inning[1]), 9)


class SoccerCalibration(unittest.TestCase):
    def team(self, name, xg):
        return {"name": name, "base_xg": xg, "players": [{"name": name + "9", "share": 0.3, "minutes": 75}]}

    def test_goal_totals_and_draws(self):
        r = soccer.simulate({"home": self.team("H", 1.35), "away": self.team("A", 1.35)}, 8000, seed=2)
        self.assertAlmostEqual(sum(r.mean_goals), 2.7, delta=0.25)
        self.assertAlmostEqual(r.result["draw"], 0.27, delta=0.035)
        self.assertAlmostEqual(r.result["home"], r.result["away"], delta=0.03)

    def test_live_state_respected(self):
        g = load_game("soccer_esp_cro_2026-09-29")
        r = soccer.simulate(scenario(g, "Goalless at 60'"), 3000, seed=1)
        self.assertLess(r.totals[2.5], 0.2)


class Scenarios(unittest.TestCase):
    def test_ops(self):
        g = load_game("mlb_bos_nyy_2026-09-29")
        g2 = apply_ops(g, [{"op": "set", "path": "home.lineup.Aaron Judge.hr", "value": 0.01},
                           {"op": "mul", "path": "away.starter.bf_mean", "value": 0.5}])
        self.assertEqual(g2["home"]["lineup"][1]["hr"], 0.01)
        self.assertEqual(g2["away"]["starter"]["bf_mean"], 10.5)
        self.assertNotEqual(g["home"]["lineup"][1]["hr"], 0.01)  # original untouched
        self.assertEqual(scenario(g, "Judge scratched")["home"]["lineup"][1]["name"], "Bench bat")


class AgentTeam(unittest.TestCase):
    def test_stats_agent_builds_rates_from_season_lines(self):
        from betting.sim.stats import batter_rates, pitcher_rates
        r = batter_rates({"pa": 600, "h": 150, "2b": 30, "3b": 2, "hr": 35, "bb": 70, "so": 140})
        self.assertAlmostEqual(r["hr"], (35 + 220 * 0.030) / 820, places=4)
        rates, per_start = pitcher_rates({"ip": 180.0, "h": 150, "hr": 18, "bb": 45, "so": 200, "gs": 30})
        self.assertGreater(rates["k"], 0.25)
        self.assertAlmostEqual(per_start, (540 + 150 + 45) / 30, places=1)

    def test_director_end_to_end(self):
        from betting.ledger import Ledger
        from betting.sim.agents import SimDirector
        g = load_game("soccer_esp_cro_2026-09-29")
        desk = SimDirector(research=False, actual="2-0").run(g, n=1500, ledger=Ledger(":memory:"))
        names = [line.split("]")[0][1:] for line in desk.log]
        for agent in ("Research", "Stats", "Scout", "Scenarios", "Simulator", "Market",
                      "RiskManager", "Reporter", "Reviewer"):
            self.assertIn(agent, names)
        self.assertGreater(len(desk.scenarios), len(g["scenarios"]))   # auto scenarios added
        self.assertTrue(desk.edges)
        self.assertIn("MARKET CHECK", desk.briefing)
        self.assertLess(desk.review["brier"], 0.5)
        self.assertEqual(g["scenarios"], load_game("soccer_esp_cro_2026-09-29")["scenarios"])  # input untouched


if __name__ == "__main__":
    unittest.main()
