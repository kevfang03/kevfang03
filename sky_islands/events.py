"""Rare and dated happenings in the sky.

Some are rolled once per hourly redraw, from a seed made of the date and hour, so every
image is repeatable and a visitor who comes back later may catch something new:

- a golden dragon (about 1 in 200 redraws), which flies even without a streak
- an aurora on clear winter nights (about 1 in 12)
- a comet on clear evenings (about 1 in 30)

Others follow the calendar: meteor showers on their peak nights, a big moon when it is
full, the holidays in holidays.py, and victory fireworks in team colours the day after a
Philadelphia win. The header names whatever is happening.
"""

from __future__ import annotations

import random
from dataclasses import dataclass

from . import holidays
from . import palette as pal
from .context import Ctx, W
from .model import World
from .svg import Layer

SHINY_ODDS, AURORA_ODDS, COMET_ODDS = 200, 12, 30
SHOWERS = {(8, 11): "PERSEIDS", (8, 12): "PERSEIDS", (8, 13): "PERSEIDS",
           (12, 13): "GEMINIDS", (12, 14): "GEMINIDS", (12, 15): "GEMINIDS"}
FULL_MOON = 0.034  # within about a day of full


@dataclass(frozen=True)
class Events:
    shiny: bool = False
    aurora: bool = False
    comet: bool = False
    meteors: str | None = None
    big_moon: bool = False
    fireworks: tuple[str, ...] = ()  # colours, when there are any
    reason: str | None = None  # why there are victory fireworks
    holiday: str | None = None  # the header line for today's holiday

    def headline(self) -> str | None:
        """One line for the header, the rarest first."""
        if self.shiny:
            return f"RARE SIGHTING · A GOLDEN DRAGON (1 IN {SHINY_ODDS})"
        if self.aurora:
            return "RARE SIGHTING · AN AURORA OVER THE ISLANDS"
        if self.comet:
            return "RARE SIGHTING · A COMET OVER PHILLY"
        if self.holiday:
            return self.holiday
        if self.reason:
            return self.reason
        if self.meteors:
            return f"TONIGHT · THE {self.meteors} METEOR SHOWER"
        if self.big_moon:
            return "TONIGHT · A FULL MOON"
        return None


def roll(w: World) -> Events:
    """What is happening in this hour's sky."""
    rng = random.Random(f"{w.when.date().isoformat()}-{w.when.hour}-events")
    shiny = rng.random() < 1 / SHINY_ODDS
    aurora_roll, comet_roll = rng.random(), rng.random()
    night = w.phase == "night"
    clear = w.weather in ("clear", "cloudy")
    key = (w.when.month, w.when.day)
    fireworks, reason = (), None
    if w.wins:
        team = pal.TEAMS[w.wins[0]]
        fireworks = (team["light"], team["secondary"], "#ffffff")
        reason = f"{team['label']} WON LAST NIGHT · VICTORY FIREWORKS"
    today = holidays.on(w.when.date())
    fireworks = holidays.fireworks(w.when.date(), w.phase) or fireworks
    return Events(
        shiny=shiny,
        aurora=night and clear and w.when.month in (12, 1, 2) and aurora_roll < 1 / AURORA_ODDS,
        comet=w.phase in ("dusk", "night") and w.weather == "clear"
        and comet_roll < 1 / COMET_ODDS,
        meteors=SHOWERS.get(key) if night and clear else None,
        big_moon=night and abs(w.moon - 0.5) < FULL_MOON,
        fireworks=fireworks,
        reason=reason,
        holiday=(today[0].headline + (" · FIREWORKS" if fireworks and not w.wins else ""))
        if today else None,
    )


CSS = (
    "@keyframes aurora{from{opacity:.45;transform:translateX(-10px)}"
    "to{opacity:.85;transform:translateX(10px)}}"
    ".aurora{animation:aurora 9s ease-in-out infinite alternate}"
    "@keyframes pop{0%{transform:scale(.15);opacity:0}6%{transform:scale(.35);opacity:1}"
    "40%{transform:scale(1.2);opacity:0}100%{transform:scale(1.2);opacity:0}}"
    ".pop{animation:pop 3.4s ease-out infinite;transform-box:fill-box;transform-origin:center}"
)


def aurora(L: Layer, c: Ctx) -> None:
    """Soft curtains of green and violet light over the night sky."""
    for k, (y, col, op) in enumerate(((70, "#5ff0a0", 0.5), (110, "#3ad1c8", 0.4),
                                      (60, "#b07aff", 0.3))):
        band = c.defs.linear(f"aurora{k}", [(0, col, 0), (0.5, col, op), (1, col, 0)])
        x0 = 80 + k * 140
        d = (f"M{x0} {y}C{x0 + 160} {y - 40} {x0 + 300} {y + 50} {x0 + 520} {y}"
             f"V{y + 90}C{x0 + 300} {y + 140} {x0 + 160} {y + 50} {x0} {y + 90}Z")
        L.path(d, band, filter=c.defs.blur(10), class_="aurora",
               style=f"animation-delay:-{k * 3}s")


def comet(L: Layer, c: Ctx) -> None:
    """A comet hanging in the evening sky, its tail pointing away from the sun."""
    x, y = 250, 95
    tail = c.defs.linear("comet", [(0, "#ffffff", 0.9), (1, "#bfe4ff", 0)], x2=1, y2=0)
    L.path(f"M{x} {y - 3}L{x + 190} {y - 46}L{x + 196} {y - 30}Z", tail,
           transform=f"rotate(-4 {x} {y})", filter=c.defs.blur(2))
    L.path(f"M{x} {y - 1.5}L{x + 120} {y - 36}", stroke="#ffffff", stroke_width=0.8,
           opacity=0.5)
    c.glow(L, x, y, 14, "#dff4ff", 0.9)
    L.circle(x, y, 2.4, "#ffffff")


def meteors(L: Layer, c: Ctx) -> None:
    """Extra shooting stars for a meteor shower, all streaking from the same corner."""
    tail = c.defs.linear("startail", [(0, "#ffffff", 1), (1, "#ffffff", 0)], x2=1, y2=0)
    for k in range(10):
        x, y = c.rng.uniform(220, W - 60), c.rng.uniform(30, 190)
        s = Layer()
        s.line(x, y, x + 60, y - 27, tail, 1.3, stroke_linecap="round")
        s.circle(x, y, 1.2, "#ffffff")
        L.group(s, class_="shoot", style=f"animation-delay:-{k * 1.3:.1f}s;"
                                         f"animation-duration:{5 + k % 4 * 1.5:.1f}s")


def fireworks(L: Layer, c: Ctx, colours: tuple[str, ...]) -> None:
    """Bursts over the Philly island and the town, shown during the overview."""
    from .stations import _burst  # imported here: stations needs the camera and the ride

    for k, (x, y) in enumerate(((120, 120), (230, 80), (470, 105), (620, 70), (760, 115),
                                (380, 60))):
        col = colours[k % len(colours)]
        L.raw(f'<g transform="translate({x} {y}) scale(.8)"><g class="pop" '
              f'style="animation-delay:-{k * 0.57:.2f}s">{_burst(c, col)}</g></g>')
