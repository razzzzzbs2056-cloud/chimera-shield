"""Projection engine — the math behind the magic."""

import numpy as np
from dataclasses import dataclass


@dataclass
class ProjectionResult:
    stat: str
    projected: float
    line: float
    lean: str
    confidence: float
    color: str  # for UI


def weather_multiplier(temp: float, wind: float,
                       wind_dir: str, humidity: float) -> float:
    """Physics-based HR distance multiplier."""
    m = 1.0
    m *= 1.0 + ((temp - 70) / 10) * 0.015       # temp
    if wind_dir == "Out":
        m *= 1.0 + (wind * 0.02)
    elif wind_dir == "In":
        m *= 1.0 - (wind * 0.02)
    m *= 1.0 + ((50 - humidity) / 100) * 0.01    # humidity
    return round(m, 4)


def estimate_ab(lineup_pos: int) -> float:
    """Expected at-bats by lineup slot."""
    table = {1: 5.0, 2: 4.8, 3: 4.6, 4: 4.5, 5: 4.3,
             6: 4.0, 7: 3.8, 8: 3.5, 9: 3.2}
    return table.get(lineup_pos, 4.0)


def project_hits(batter_stats: dict, splits: dict,
                 pitcher_stats: dict, park_hit: float,
                 lineup_pos: int) -> ProjectionResult:
    """Project hits."""
    ab = estimate_ab(lineup_pos)
    avg = batter_stats.get("avg", 0.250)

    # Platoon adjustment
    pitcher_throws = pitcher_stats.get("throws", "R")
    if pitcher_throws == "Left" and splits.get("vs_lhp", {}).get("avg"):
        adj_avg = splits["vs_lhp"]["avg"]
    elif pitcher_throws == "Right" and splits.get("vs_rhp", {}).get("avg"):
        adj_avg = splits["vs_rhp"]["avg"]
    else:
        adj_avg = avg

    # Pitcher K% suppression
    k_pct = pitcher_stats.get("k_pct", 0.22)
    k_suppress = 1.0 - ((k_pct - 0.22) * 0.8)
    k_suppress = np.clip(k_suppress, 0.70, 1.30)

    # BABIP regression
    babip = batter_stats.get("babip", 0.300)
    if babip > 0:
        babip_adj = np.clip(0.300 / babip, 0.85, 1.15)
    else:
        babip_adj = 1.0

    park_mult = park_hit / 100.0

    prob = adj_avg * k_suppress * babip_adj * park_mult
    prob = np.clip(prob, 0.10, 0.50)

    projected = round(ab * prob, 2)
    line = 0.5 if projected < 0.9 else 1.5

    if projected > line:
        lean, color = "OVER", "#22c55e"
    else:
        lean, color = "UNDER", "#ef4444"

    conf = min(90, max(35, abs(projected - line) * 180))

    return ProjectionResult("Hits", projected, line, lean, conf, color)


def project_hr(batter_stats: dict, splits: dict,
               pitcher_stats: dict, park_hr: float,
               weather_mult: float, lineup_pos: int) -> ProjectionResult:
    """Project home runs."""
    ab = estimate_ab(lineup_pos)
    iso = batter_stats.get("iso", 0.150)

    # Base HR rate from ISO
    base_rate = max(0, iso - 0.08) * 0.18

    # Platoon power
    pitcher_throws = pitcher_stats.get("throws", "R")
    if pitcher_throws == "Left" and splits.get("vs_lhp", {}).get("slg"):
        platoon_slg = splits["vs_lhp"]["slg"]
        season_slg = batter_stats.get("slg", 0.400)
        platoon_mult = platoon_slg / max(season_slg, 0.001)
    elif pitcher_throws == "Right" and splits.get("vs_rhp", {}).get("slg"):
        platoon_slg = splits["vs_rhp"]["slg"]
        season_slg = batter_stats.get("slg", 0.400)
        platoon_mult = platoon_slg / max(season_slg, 0.001)
    else:
        platoon_mult = 1.0

    # Pitcher HR susceptibility
    hr_9 = pitcher_stats.get("hr_9", 1.2)
    pitcher_hr_mult = np.clip(hr_9 / 1.2, 0.5, 2.0)

    # Pitcher FB%
    fb_pct = pitcher_stats.get("fb_pct", 0.35)
    fb_mult = np.clip(fb_pct / 0.35, 0.7, 1.5)

    park_mult = park_hr / 100.0

    hr_prob = base_rate * platoon_mult * pitcher_hr_mult * \
              fb_mult * park_mult * weather_mult
    hr_prob = np.clip(hr_prob, 0.01, 0.40)

    projected = round(ab * hr_prob, 3)
    line = 0.5

    lean = "OVER" if projected > 0.32 else "UNDER"
    color = "#22c55e" if lean == "OVER" else "#ef4444"
    conf = min(85, max(20, projected * 200))

    return ProjectionResult("Home Runs", projected, line, lean, conf, color)


def project_runs(batter_stats: dict, pitcher_stats: dict,
                 park_run: float, lineup_pos: int,
                 team_obp: float = 0.320) -> ProjectionResult:
    """Project runs scored."""
    ab = estimate_ab(lineup_pos)
    obp = batter_stats.get("obp", 0.320)

    # Lineup position scoring multiplier
    pos_mult = {1: 1.35, 2: 1.30, 3: 1.20, 4: 1.10, 5: 1.00,
                6: 0.90, 7: 0.80, 8: 0.70, 9: 0.65}
    pm = pos_mult.get(lineup_pos, 1.0)

    # Drive-in factor (hitters behind)
    drive_in = team_obp / 0.320

    park_mult = park_run / 100.0

    era = pitcher_stats.get("era", 4.00)
    pitcher_suppress = np.clip(1.0 - ((era - 4.0) * 0.04), 0.80, 1.20)

    run_prob = obp * pm * drive_in * park_mult * pitcher_suppress
    run_prob = np.clip(run_prob, 0.10, 0.80)

    projected = round(ab * run_prob * 0.32, 2)
    line = 0.5

    lean = "OVER" if projected > 0.55 else "UNDER"
    color = "#22c55e" if lean == "OVER" else "#ef4444"
    conf = min(80, max(25, abs(projected - line) * 160))

    return ProjectionResult("Runs", projected, line, lean, conf, color)


def project_rbi(batter_stats: dict, pitcher_stats: dict,
                park_run: float, lineup_pos: int,
                team_obp: float = 0.320) -> ProjectionResult:
    """Project RBI."""
    ab = estimate_ab(lineup_pos)
    iso = batter_stats.get("iso", 0.150)

    # Lineup position RBI multiplier
    pos_mult = {1: 0.60, 2: 0.70, 3: 1.20, 4: 1.40, 5: 1.30,
                6: 1.00, 7: 0.80, 8: 0.60, 9: 0.50}
    pm = pos_mult.get(lineup_pos, 1.0)

    # Runners on base factor
    runners = team_obp / 0.320

    park_mult = park_run / 100.0

    whip = pitcher_stats.get("whip", 1.30)
    whip_mult = np.clip(whip / 1.30, 0.7, 1.5)

    rbi_prob = iso * pm * runners * park_mult * whip_mult
    rbi_prob = np.clip(rbi_prob, 0.05, 0.50)

    projected = round(ab * rbi_prob * 0.9, 2)
    line = 0.5

    lean = "OVER" if projected > 0.55 else "UNDER"
    color = "#22c55e" if lean == "OVER" else "#ef4444"
    conf = min(80, max(25, abs(projected - line) * 160))

    return ProjectionResult("RBI", projected, line, lean, conf, color)


def score_all_factors(batter_stats: dict, pitcher_stats: dict,
                      park_hr: float, park_run: float,
                      weather_mult: float, lineup_pos: int,
                      bat_side: str) -> list:
    """Score all factors 1-5 for the radar chart."""
    factors = []

    # Platoon
    pitcher_throws = pitcher_stats.get("throws", "R")[0]
    bat = bat_side[0] if bat_side else "R"
    if bat != pitcher_throws:
        factors.append(("Platoon Edge", 4, "+"))
    else:
        factors.append(("Platoon Edge", 2, "-"))

    # Pitcher quality
    era = pitcher_stats.get("era", 4.00)
    if era < 3.50:
        factors.append(("Pitcher Quality", 2, "-"))
    elif era > 4.80:
        factors.append(("Pitcher Quality", 5, "+"))
    elif era > 4.20:
        factors.append(("Pitcher Quality", 4, "+"))
    else:
        factors.append(("Pitcher Quality", 3, "="))

    # Recent form (using season avg as proxy)
    avg = batter_stats.get("avg", 0.250)
    if avg > .300:
        factors.append(("Batting Form", 5, "+"))
    elif avg > .270:
        factors.append(("Batting Form", 4, "+"))
    elif avg < .220:
        factors.append(("Batting Form", 1, "-"))
    else:
        factors.append(("Batting Form", 3, "="))

    # Power
    iso = batter_stats.get("iso", 0.150)
    if iso > .250:
        factors.append(("Power", 5, "+"))
    elif iso > .200:
        factors.append(("Power", 4, "+"))
    elif iso < .120:
        factors.append(("Power", 1, "-"))
    else:
        factors.append(("Power", 3, "="))

    # Park
    if park_hr > 110:
        factors.append(("Park Factor", 5, "+"))
    elif park_hr > 105:
        factors.append(("Park Factor", 4, "+"))
    elif park_hr < 95:
        factors.append(("Park Factor", 1, "-"))
    else:
        factors.append(("Park Factor", 3, "="))

    # Weather
    if weather_mult > 1.05:
        factors.append(("Weather", 5, "+"))
    elif weather_mult > 1.02:
        factors.append(("Weather", 4, "+"))
    elif weather_mult < 0.95:
        factors.append(("Weather", 1, "-"))
    else:
        factors.append(("Weather", 3, "="))

    # Lineup spot
    if lineup_pos <= 3:
        factors.append(("Lineup Spot", 5, "+"))
    elif lineup_pos <= 5:
        factors.append(("Lineup Spot", 4, "+"))
    elif lineup_pos >= 8:
        factors.append(("Lineup Spot", 1, "-"))
    else:
        factors.append(("Lineup Spot", 3, "="))

    # Pitcher HR/9
    hr9 = pitcher_stats.get("hr_9", 1.2)
    if hr9 > 1.5:
        factors.append(("Pitcher HR/9", 5, "+"))
    elif hr9 > 1.2:
        factors.append(("Pitcher HR/9", 4, "+"))
    elif hr9 < 0.8:
        factors.append(("Pitcher HR/9", 1, "-"))
    else:
        factors.append(("Pitcher HR/9", 3, "="))

    return factors
