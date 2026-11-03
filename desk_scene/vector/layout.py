"""Where things sit in the vector scene, and the shared drawing context."""

from __future__ import annotations

import random
from dataclasses import dataclass

from .. import palette as pal
from ..clock import season
from ..model import Game, SceneState
from .svg import Defs

W, H = 960, 620
HEADER_H = 64
FOOTER_Y = 540
DESK_Y = 440

# The glass of the big window: x0, y0, x1, y1.
GX0, GY0, GX1, GY1 = 44, 94, 632, 402
HORIZON = 306  # where the skyline's buildings stand
WATER_Y = 328  # top of the river

FONT = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"

# Header and footer use GitHub's dark theme colours so the card sits well on a profile.
UI = {
    "bg": "#0d1117", "panel": "#161b22", "line": "#30363d",
    "text": "#e6edf3", "muted": "#8b949e", "green": "#3fb950",
    "blue": "#79c0ff", "gold": "#e3b341",
}

OVERCAST = {"day": "#9aa4b2", "dawn": "#9a8d9c", "dusk": "#4f4a63", "night": "#1a2133"}


@dataclass
class Ctx:
    """The scene state plus everything derived from it that drawing code needs."""

    s: SceneState
    rng: random.Random
    defs: Defs

    @property
    def phase(self) -> str:
        return self.s.phase

    @property
    def P(self) -> dict:
        return pal.OUTSIDE[self.s.phase]

    @property
    def dark(self) -> bool:
        return self.s.phase in ("dusk", "night")

    @property
    def overcast(self) -> bool:
        return self.s.weather != "clear"

    @property
    def season(self) -> str:
        return season(self.s.when.month)

    @property
    def december(self) -> bool:
        return self.s.when.month == 12

    @property
    def games(self) -> tuple[Game, ...]:
        if self.s.games:
            return self.s.games
        return tuple(Game(t, "") for t in self.s.teams)

    def team_light(self, i: int) -> str | None:
        """Light colour for the i-th lit thing on a game day, cycling through the teams."""
        g = self.games
        if not g:
            return None
        return pal.TEAMS[g[i % len(g)].team]["light"]

    def out(self, c: str) -> str:
        """A daytime colour as it looks outside right now."""
        return pal.outside(c, self.s.phase)

    def room(self, c: str) -> str:
        """A daytime colour as it looks inside the room right now."""
        return pal.room(c, self.s.phase)
