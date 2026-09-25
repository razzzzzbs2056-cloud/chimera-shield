"""Sportsbook registry.

Keys match The Odds API bookmaker keys. "Sharp" books take big limits and move
fast, so their de-vigged prices are the best available estimate of true odds.
"""

SHARP_BOOKS = {
    "pinnacle": "Pinnacle",
    "circasports": "Circa Sports",
    "betfair_ex_uk": "Betfair Exchange (UK)",
    "betfair_ex_eu": "Betfair Exchange (EU)",
    "matchbook": "Matchbook",
    "lowvig": "LowVig.ag",
    "betonlineag": "BetOnline.ag",
}

RETAIL_BOOKS = {
    "draftkings": "DraftKings",
    "fanduel": "FanDuel",
    "betmgm": "BetMGM",
    "williamhill_us": "Caesars",
    "espnbet": "ESPN BET",
    "betrivers": "BetRivers",
    "fanatics": "Fanatics",
    "hardrockbet": "Hard Rock Bet",
    "bovada": "Bovada",
    "mybookieag": "MyBookie.ag",
    "betus": "BetUS",
    "bet365": "bet365",
    "williamhill": "William Hill",
    "unibet_eu": "Unibet",
    "betway": "Betway",
    "sport888": "888sport",
    "paddypower": "Paddy Power",
    "skybet": "Sky Bet",
}

ALL_BOOKS = {**SHARP_BOOKS, **RETAIL_BOOKS}

# Popular sport keys (The Odds API naming).
SPORTS = {
    "americanfootball_nfl": "NFL",
    "americanfootball_ncaaf": "NCAAF",
    "basketball_nba": "NBA",
    "basketball_wnba": "WNBA",
    "basketball_ncaab": "NCAAB",
    "baseball_mlb": "MLB",
    "icehockey_nhl": "NHL",
    "soccer_epl": "EPL",
    "soccer_uefa_champs_league": "Champions League",
    "soccer_spain_la_liga": "La Liga",
    "soccer_usa_mls": "MLS",
    "mma_mixed_martial_arts": "MMA",
    "tennis_atp_us_open": "ATP US Open",
}


def is_sharp(book: str) -> bool:
    return book in SHARP_BOOKS


def book_name(book: str) -> str:
    return ALL_BOOKS.get(book, book)
