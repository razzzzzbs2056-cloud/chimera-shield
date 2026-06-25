"""Park factor data for all 30 MLB stadiums."""

PARK_FACTORS = {
    "Coors Field":               {"hr": 135, "run": 130, "hit": 115, "city": "Denver",         "alt": 5280},
    "Great American Ball Park":  {"hr": 118, "run": 110, "hit": 104, "city": "Cincinnati",     "alt": 482},
    "Yankee Stadium":            {"hr": 114, "run": 108, "hit": 103, "city": "New York",       "alt": 16},
    "Guaranteed Rate Field":     {"hr": 113, "run": 107, "hit": 102, "city": "Chicago",        "alt": 597},
    "Globe Life Field":          {"hr": 112, "run": 106, "hit": 103, "city": "Arlington",      "alt": 587},
    "Progressive Field":         {"hr": 110, "run": 105, "hit": 102, "city": "Cleveland",      "alt": 653},
    "Citizens Bank Park":        {"hr": 109, "run": 106, "hit": 103, "city": "Philadelphia",   "alt": 39},
    "Chase Field":               {"hr": 108, "run": 105, "hit": 104, "city": "Phoenix",        "alt": 1086},
    "Fenway Park":               {"hr": 107, "run": 112, "hit": 108, "city": "Boston",         "alt": 20},
    "Wrigley Field":             {"hr": 106, "run": 104, "hit": 103, "city": "Chicago",        "alt": 597},
    "Oriole Park at Camden Yards":{"hr": 105,"run": 103, "hit": 102, "city": "Baltimore",      "alt": 33},
    "Target Field":              {"hr": 104, "run": 102, "hit": 101, "city": "Minneapolis",    "alt": 840},
    "Dodger Stadium":            {"hr": 103, "run": 105, "hit": 102, "city": "Los Angeles",    "alt": 340},
    "Citi Field":                {"hr": 102, "run": 101, "hit": 100, "city": "New York",       "alt": 16},
    "Rogers Centre":             {"hr": 102, "run": 103, "hit": 101, "city": "Toronto",        "alt": 250},
    "Busch Stadium":             {"hr": 100, "run": 100, "hit": 100, "city": "St. Louis",      "alt": 465},
    "PNC Park":                  {"hr": 99,  "run": 99,  "hit": 100, "city": "Pittsburgh",     "alt": 730},
    "Comerica Park":             {"hr": 99,  "run": 100, "hit": 101, "city": "Detroit",        "alt": 603},
    "Minute Maid Park":          {"hr": 98,  "run": 101, "hit": 102, "city": "Houston",        "alt": 43},
    "Truist Park":               {"hr": 97,  "run": 100, "hit": 101, "city": "Atlanta",        "alt": 1050},
    "Nationals Park":            {"hr": 97,  "run": 100, "hit": 101, "city": "Washington",     "alt": 26},
    "loanDepot Park":            {"hr": 96,  "run": 97,  "hit": 99,  "city": "Miami",          "alt": 6},
    "T-Mobile Park":             {"hr": 94,  "run": 95,  "hit": 97,  "city": "Seattle",        "alt": 175},
    "Petco Park":                {"hr": 92,  "run": 95,  "hit": 97,  "city": "San Diego",      "alt": 26},
    "Oakland Coliseum":          {"hr": 90,  "run": 94,  "hit": 96,  "city": "Oakland",        "alt": 12},
    "Oracle Park":               {"hr": 85,  "run": 92,  "hit": 95,  "city": "San Francisco",  "alt": 13},
    "George M. Steinbrenner Field":{"hr": 100,"run": 100,"hit": 100, "city": "Tampa",          "alt": 15},
    "Sutter Health Park":        {"hr": 100, "run": 100, "hit": 100, "city": "Sacramento",     "alt": 30},
}

# Map team abbreviations to home parks
TEAM_PARK_MAP = {
    "COL": "Coors Field", "CIN": "Great American Ball Park",
    "NYY": "Yankee Stadium", "CWS": "Guaranteed Rate Field",
    "TEX": "Globe Life Field", "CLE": "Progressive Field",
    "PHI": "Citizens Bank Park", "ARI": "Chase Field",
    "BOS": "Fenway Park", "CHC": "Wrigley Field",
    "BAL": "Oriole Park at Camden Yards", "MIN": "Target Field",
    "LAD": "Dodger Stadium", "NYM": "Citi Field",
    "TOR": "Rogers Centre", "STL": "Busch Stadium",
    "PIT": "PNC Park", "DET": "Comerica Park",
    "HOU": "Minute Maid Park", "ATL": "Truist Park",
    "WSH": "Nationals Park", "MIA": "loanDepot Park",
    "SEA": "T-Mobile Park", "SD": "Petco Park",
    "OAK": "Oakland Coliseum", "SF": "Oracle Park",
    "TB": "George M. Steinbrenner Field",
    "ATH": "Sutter Health Park",
    "LAA": "Angel Stadium", "KC": "Kauffman Stadium",
    "MIL": "American Family Field",
}

def get_park(team_abbr: str) -> dict:
    park_name = TEAM_PARK_MAP.get(team_abbr, "Unknown")
    return {
        "name": park_name,
        **PARK_FACTORS.get(park_name, {"hr": 100, "run": 100, "hit": 100})
    }
