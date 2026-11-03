"""Philadelphia game days from ESPN's public scoreboards (no key).

For each team the banner knows, it reads today's scoreboard to light the stadium on a game
day, and yesterday's to set off victory fireworks the morning after a win. Each league is
fetched on its own; one that fails is simply skipped.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta

from .clock import PHILLY
from .model import Game
from .net import Get, get_json

LEAGUES = {"eagles": "football/nfl", "phillies": "baseball/mlb", "sixers": "basketball/nba"}
SCOREBOARD = "https://site.api.espn.com/apis/site/v2/sports/{league}/scoreboard?dates={day}"
HOME = "PHI"


def _philly_game(data: dict) -> tuple[dict, dict, dict] | None:
    """The event Philadelphia plays in, with its own and the other side's competitor."""
    for event in data.get("events", []):
        sides = event["competitions"][0]["competitors"]
        ours = [s for s in sides if s["team"]["abbreviation"] == HOME]
        if ours:
            theirs = next(s for s in sides if s is not ours[0])
            return event, ours[0], theirs
    return None


def parse_game(team: str, data: dict) -> Game | None:
    """Today's game for one team, if it plays today."""
    found = _philly_game(data)
    if not found:
        return None
    event, ours, theirs = found
    start = datetime.fromisoformat(event["date"]).astimezone(PHILLY)
    state = event["status"]["type"]["state"]
    result = None
    if state == "post":
        result = (f"{'W' if ours.get('winner') else 'L'} "
                  f"{ours.get('score', '?')}-{theirs.get('score', '?')}")
    elif state == "in":
        result = f"LIVE {ours.get('score', '0')}-{theirs.get('score', '0')}"
    return Game(team, theirs["team"]["abbreviation"], start, ours["homeAway"] == "home", result)


def won(data: dict) -> bool:
    """Whether Philadelphia won a finished game on this scoreboard."""
    found = _philly_game(data)
    if not found:
        return False
    event, ours, _ = found
    return event["status"]["type"]["state"] == "post" and bool(ours.get("winner"))


def _board(get: Get, league: str, day: date) -> dict:
    return get(SCOREBOARD.format(league=league, day=day.strftime("%Y%m%d")))


def fetch_games(today: date, get: Get = get_json) -> tuple[tuple[Game, ...], tuple[str, ...]]:
    """Today's Philadelphia games and the teams that won yesterday."""
    games, wins = [], []
    for team, league in LEAGUES.items():
        try:
            game = parse_game(team, _board(get, league, today))
            if game:
                games.append(game)
            if won(_board(get, league, today - timedelta(days=1))):
                wins.append(team)
        except Exception as err:  # noqa: BLE001 - one league failing never stops the redraw
            print(f"{team} scores unavailable ({type(err).__name__})")
    return tuple(games), tuple(wins)
