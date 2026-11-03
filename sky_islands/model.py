"""The data one drawing of the world is made from."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta

from .clock import PHILLY, approx_sun_times, moon_phase, phase_for


@dataclass(frozen=True)
class Repo:
    """A public repository; each one is a building on the island."""

    name: str
    language: str | None
    commits: int  # on the default branch
    pushed_at: datetime
    stars: int = 0


@dataclass(frozen=True)
class Stats:
    """Public GitHub numbers for one account."""

    login: str
    contributions_total: int  # every contribution since the account was made
    contributions_year: int
    streak_days: int
    repos: tuple[Repo, ...] = ()
    latest_commit: str = ""
    weekly: tuple[int, ...] = ()  # contributions per week, oldest first, ending this week
    merged_prs: int = 0  # pull requests merged this year


@dataclass(frozen=True)
class Game:
    """A Philadelphia team playing today."""

    team: str
    opponent: str
    start: datetime | None = None
    home: bool = True


@dataclass(frozen=True)
class World:
    """Everything that decides how one frame looks."""

    when: datetime  # local Philadelphia time
    phase: str  # dawn, day, golden, dusk or night
    weather: str  # clear, cloudy, rain or snow
    stats: Stats
    temp_f: int | None = None
    games: tuple[Game, ...] = field(default_factory=tuple)
    seed: int = 7

    @property
    def moon(self) -> float:
        return moon_phase(self.when)


_DEMO_NOW = datetime(2026, 11, 2, 12, 0, tzinfo=PHILLY)


def _repo(name: str, lang: str | None, commits: int, days_ago: float, stars: int = 0) -> Repo:
    return Repo(name, lang, commits, _DEMO_NOW - timedelta(days=days_ago), stars)


DEMO_STATS = Stats(
    login="kevfang03",
    contributions_total=300,
    contributions_year=240,
    streak_days=14,
    repos=(
        _repo("ops-suite", "Python", 186, 0.2, 3),
        _repo("desk-scene", "Python", 64, 2),
        _repo("portfolio", "TypeScript", 41, 20, 2),
        _repo("dotfiles", "Shell", 22, 60),
        _repo("notes", "Markdown", 12, 9),
        _repo("hello-world", None, 3, 400),
    ),
    latest_commit="fix dst-safe test times",
    weekly=(3, 0, 5, 8, 2, 0, 0, 4, 9, 12, 6, 3, 0, 7, 11, 15, 9, 4, 6, 13, 18, 10, 8, 14, 21, 16),
    merged_prs=9,
)

# A representative local time for each phase, used by demo drawings.
DEMO_HOURS = {"dawn": (6, 50), "day": (12, 30), "golden": (15, 40), "dusk": (16, 50),
              "night": (23, 40)}


def demo_world(phase: str = "dusk", weather: str = "clear", stats: Stats = DEMO_STATS,
               day: tuple[int, int, int] = (2026, 11, 2), game: str | None = None) -> World:
    hour, minute = DEMO_HOURS[phase]
    when = datetime(*day, hour, minute, tzinfo=PHILLY)
    games = ()
    if game:
        opp, gh, gm, home = {"eagles": ("DAL", 20, 20, True), "phillies": ("NYM", 19, 5, True),
                             "sixers": ("BOS", 19, 30, False)}[game]
        games = (Game(game, opp, datetime(*day, gh, gm, tzinfo=PHILLY), home),)
    return World(when=when, phase=phase, weather=weather, stats=stats, temp_f=48, games=games)


def world_at(stats: Stats, now: datetime) -> World:
    """The world for real stats at a real moment: the light comes from Philadelphia's
    approximate sunrise and sunset that day. Weather and game days are not live yet."""
    now = now.astimezone(PHILLY)
    sunrise, sunset = approx_sun_times(now.date())
    return World(when=now, phase=phase_for(now, sunrise, sunset), weather="clear", stats=stats)
