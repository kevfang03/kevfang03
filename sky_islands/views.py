"""Extra pictures for the README's buttons: today's world at dawn, day, dusk and night, and a
preview of the world fully grown at level 10."""

from __future__ import annotations

from dataclasses import replace
from datetime import date, datetime, timedelta
from pathlib import Path

from .clock import approx_sun_times
from .model import Stats, world_at
from .progress import level_threshold
from .render import render
from .serverfarm import MAX_RACKS, RACKS_PER
from .wonders import DRAGON_STREAK

TIMES = ("dawn", "day", "dusk", "night")
PREVIEW_LEVEL = 10
PREVIEW_PRS = 9  # three starfighters at the Starport


def moment(day: date, phase: str) -> datetime:
    """A time on `day` that falls in the middle of `phase`, from that day's sun times."""
    sunrise, sunset = approx_sun_times(day)
    return {
        "dawn": sunrise,
        "day": sunrise + (sunset - sunrise) / 2,
        "golden": sunset - timedelta(minutes=50),
        "dusk": sunset + timedelta(minutes=15),
        "night": sunset + timedelta(hours=3),
    }[phase]


def grown(stats: Stats) -> Stats:
    """The same account at level 10, with the dragon, the full squadron and a full Server Farm
    showing. Real numbers that are already higher are kept."""
    return replace(
        stats,
        contributions_total=max(stats.contributions_total, level_threshold(PREVIEW_LEVEL)),
        contributions_year=max(stats.contributions_year, RACKS_PER * MAX_RACKS),
        streak_days=max(stats.streak_days, DRAGON_STREAK),
        merged_prs=max(stats.merged_prs, PREVIEW_PRS),
    )


def render_views(stats: Stats, now: datetime, out: Path) -> list[Path]:
    """Write dawn, day, dusk and night for today, and the level 10 preview at dusk."""
    out.mkdir(parents=True, exist_ok=True)
    written = []
    for phase in TIMES:
        path = out / f"{phase}.svg"
        path.write_text(render(world_at(stats, moment(now.date(), phase))), encoding="utf-8")
        written.append(path)
    path = out / f"level-{PREVIEW_LEVEL}.svg"
    path.write_text(render(world_at(grown(stats), moment(now.date(), "dusk"))), encoding="utf-8")
    written.append(path)
    return written
