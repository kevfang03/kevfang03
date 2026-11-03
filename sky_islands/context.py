"""Canvas size, shared shapes and the drawing context passed to every layer."""

from __future__ import annotations

import functools
import random
from dataclasses import dataclass

from . import palette as pal
from .model import World
from .svg import Defs, Layer

W, H = 1000, 560
HEADER_H = 54
STRIP_Y = 522  # top of the activity timeline along the bottom
FONT = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"


@functools.cache
def _palette(phase: str, winter: bool) -> dict:
    """The phase's colours; in winter the grass on every island lies under snow."""
    if not winter:
        return pal.PHASE[phase]
    colours = dict(pal.PHASE[phase])
    colours["grass"] = pal.mix(colours["grass"], pal.lit_by("#e8eef8", phase), 0.62)
    return colours


@dataclass
class Ctx:
    """The world plus the derived values and shared definitions drawing code needs."""

    w: World
    rng: random.Random
    defs: Defs

    @property
    def phase(self) -> str:
        return self.w.phase

    @property
    def P(self) -> dict:
        return _palette(self.w.phase, self.w.when.month in (12, 1, 2))

    @property
    def dark(self) -> bool:
        return self.w.phase in ("dusk", "night")

    def lit(self, c: str) -> str:
        return pal.lit_by(c, self.w.phase)

    def haze(self, c: str, t: float) -> str:
        """Fade a colour toward the sky's distance colour."""
        return pal.mix(c, self.P["haze"], t)

    def glow(self, L: Layer, x: float, y: float, r: float, col: str, op: float = 1.0, **a) -> None:
        g = self.defs.radial(f"glow{col[1:]}", [(0, col, 0.9), (0.35, col, 0.35), (1, col, 0)])
        L.circle(x, y, r, g, opacity=op, **a)


def sign(L: Layer, x: float, y: float, text: str, col: str = "#ece8f8", size: float = 7.5,
         leader: float = 0) -> tuple[float, float, float, float]:
    """A small dark label; returns its box (x0, y0, x1, y1). Labels are too small to read
    when the banner is shown at phone width, so they hide there (class "fine")."""
    w = len(text) * size * 0.6 + 10
    g = Layer()
    if leader:
        g.line(x, y + 4, x, y + 4 + leader, col, 0.7, opacity=0.55)
    g.rect(x - w / 2, y - size - 1.5, w, size + 6, "#120e24", opacity=0.78, rx=3)
    g.text(x, y + 1, text, size, col, text_anchor="middle", font_weight="700")
    L.group(g, class_="fine")
    return (x - w / 2, y - size - 1.5, x + w / 2, y + 4.5)


def sign_width(text: str, size: float = 7.5) -> float:
    return len(text) * size * 0.6 + 10
