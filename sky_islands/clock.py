"""Time of day, moon phase and calendar rules, all on Philadelphia time."""

from __future__ import annotations

from datetime import UTC, date, datetime, timedelta
from zoneinfo import ZoneInfo

PHILLY = ZoneInfo("America/New_York")
PHASES = ("dawn", "day", "golden", "dusk", "night")

_SYNODIC_DAYS = 29.530588853
_REFERENCE_NEW_MOON = datetime(2000, 1, 6, 18, 14, tzinfo=UTC)

# Rough Philadelphia sunrise and sunset (local hour, minute) by month, used
# when no live forecast is available.
_SUN_BY_MONTH = {
    1: ((7, 20), (16, 55)), 2: ((6, 55), (17, 30)), 3: ((7, 0), (19, 0)),
    4: ((6, 25), (19, 35)), 5: ((5, 50), (20, 5)), 6: ((5, 35), (20, 30)),
    7: ((5, 45), (20, 25)), 8: ((6, 15), (19, 50)), 9: ((6, 45), (19, 0)),
    10: ((7, 15), (18, 15)), 11: ((6, 50), (16, 45)), 12: ((7, 15), (16, 40)),
}


def moon_phase(when: datetime) -> float:
    """Fraction through the lunar cycle: 0 is a new moon, 0.5 is full."""
    days = (when.astimezone(UTC) - _REFERENCE_NEW_MOON).total_seconds() / 86400
    return (days % _SYNODIC_DAYS) / _SYNODIC_DAYS


def approx_sun_times(day: date) -> tuple[datetime, datetime]:
    (rh, rm), (sh, sm) = _SUN_BY_MONTH[day.month]
    rise = datetime(day.year, day.month, day.day, rh, rm, tzinfo=PHILLY)
    sets = datetime(day.year, day.month, day.day, sh, sm, tzinfo=PHILLY)
    return rise, sets


def phase_for(now: datetime, sunrise: datetime, sunset: datetime) -> str:
    """Pick the light of the moment from where it falls around sunrise and sunset."""
    m = timedelta(minutes=1)
    if sunrise - 45 * m <= now < sunrise + 45 * m:
        return "dawn"
    if sunrise + 45 * m <= now < sunset - 90 * m:
        return "day"
    if sunset - 90 * m <= now < sunset - 10 * m:
        return "golden"
    if sunset - 10 * m <= now < sunset + 45 * m:
        return "dusk"
    return "night"


def season(month: int) -> str:
    if month in (3, 4, 5):
        return "spring"
    if month in (6, 7, 8):
        return "summer"
    if month in (9, 10, 11):
        return "fall"
    return "winter"
