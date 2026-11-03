"""The data one drawing of the scene is made from."""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from datetime import datetime

from .clock import PHILLY, moon_phase


@dataclass(frozen=True)
class Stats:
    """Public GitHub numbers shown in the scene."""

    login: str
    contributions_year: int
    streak_days: int
    repo_count: int
    top_language: str
    latest_commit: str
    now_building: str
    # Daily contribution counts, oldest first, ending today.
    calendar: tuple[int, ...] = ()
    # Every contribution since the account was made; this builds the towers.
    contributions_total: int = 0


@dataclass(frozen=True)
class Game:
    """A Philadelphia team playing today."""

    team: str  # key into palette.TEAMS
    opponent: str  # short name such as "DAL"
    start: datetime | None = None  # local Philadelphia time
    home: bool = True


@dataclass(frozen=True)
class SceneState:
    """Everything that decides how one frame of the scene looks."""

    when: datetime  # local Philadelphia time
    phase: str  # dawn, day, dusk or night
    weather: str  # clear, cloudy, rain or snow
    stats: Stats
    temp_f: int | None = None
    teams: tuple[str, ...] = field(default_factory=tuple)  # teams playing today
    monogram: str = "KF"  # lit on the crown of each finished tower
    seed: int = 7
    games: tuple[Game, ...] = ()  # opponent and start time for each team in `teams`

    @property
    def moon(self) -> float:
        return moon_phase(self.when)


def _demo_calendar(days: int = 182, streak: int = 14) -> tuple[int, ...]:
    """Plausible placeholder activity: busier on weekdays, ending in a streak."""
    rng = random.Random(42)
    counts = []
    for i in range(days):
        weekday = i % 7 not in (5, 6)
        active = rng.random() < (0.7 if weekday else 0.3)
        counts.append(rng.choice((1, 2, 3, 4, 6, 9)) if active else 0)
    for i in range(1, streak + 1):
        counts[-i] = max(counts[-i], 1)
    return tuple(counts)


DEMO_STATS = Stats(
    login="kevfang03",
    contributions_year=240,
    streak_days=14,
    repo_count=6,
    top_language="Python",
    latest_commit="fix dst-safe test times",
    now_building="ops-suite",
    calendar=_demo_calendar(),
    contributions_total=300,
)

# A representative local time for each phase, used by demo drawings.
_DEMO_HOURS = {"dawn": (6, 50), "day": (12, 30), "dusk": (16, 20), "night": (23, 40)}


def demo_state(
    phase: str = "night",
    weather: str = "clear",
    teams: tuple[str, ...] = (),
    day: tuple[int, int, int] = (2026, 11, 2),
    temp_f: int | None = 48,
) -> SceneState:
    """A scene built from placeholder stats, for previews and tests."""
    hour, minute = _DEMO_HOURS[phase]
    when = datetime(*day, hour, minute, tzinfo=PHILLY)
    games = tuple(
        Game(t, opp, datetime(*day, gh, gm, tzinfo=PHILLY), home)
        for t in teams
        for opp, gh, gm, home in [_DEMO_GAMES[t]]
    )
    return SceneState(
        when=when, phase=phase, weather=weather, stats=DEMO_STATS, temp_f=temp_f, teams=teams,
        games=games,
    )


# Placeholder opponents and start times for demo game days.
_DEMO_GAMES = {
    "eagles": ("DAL", 20, 20, True),
    "phillies": ("NYM", 19, 5, True),
    "sixers": ("BOS", 19, 30, False),
}
