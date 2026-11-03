"""Your companion: a little sky sprite that lives on the HQ's roof terrace and evolves as
you level up. An original creature in three forms:

1. Puff: a round cloud sprite with a leaf sprouting from its head.
2. Drift: a fox-like sprite with a fluffy cloud tail, small wings and a crystal on its brow.
3. Nimbus: Drift grown up, with wide feathered wings; it hovers beside the terrace and its
   crystal glows after dark.
"""

from __future__ import annotations

from . import palette as pal
from .context import Ctx
from .progress import EVOLVE_LEVELS
from .svg import Layer

NAMES = ("Puff", "Drift", "Nimbus")


def _lit(c: Ctx, col: str) -> str:
    """A sprite keeps some of its own light: only half dimmed by the time of day."""
    return pal.mix(c.lit(col), col, 0.55)


def stage(level: int) -> int:
    """1, 2 or 3: which form your companion has reached."""
    return 1 + sum(level >= lv for lv in EVOLVE_LEVELS)


def _eyes(g: Layer, x: float, y: float, gap: float, r: float) -> None:
    for dx in (-gap / 2, gap / 2):
        g.circle(x + dx, y, r, "#1a1622")
        g.circle(x + dx + r * 0.35, y - r * 0.35, r * 0.4, "#ffffff")


def _puff(g: Layer, c: Ctx) -> None:
    fur, belly = _lit(c, "#cfeeff"), _lit(c, "#ffffff")
    g.ellipse(-3.2, -0.6, 2, 1, fur)
    g.ellipse(3.2, -0.6, 2, 1, fur)
    g.ellipse(0, -5.5, 6, 5.4, fur)
    g.circle(-3.6, -8.5, 2.6, fur)
    g.circle(3.4, -9, 2.4, fur)
    g.ellipse(0, -4, 3.6, 3, belly, opacity=0.8)
    g.path("M0 -10.6q-1 -3 1.6 -4.6q0.4 2.6 -1.6 4.6z", _lit(c, "#5cbf6a"))
    g.line(0, -10.4, 0, -12, _lit(c, "#3f8a46"), 0.6)
    _eyes(g, 0, -6.4, 4.2, 0.95)
    for dx in (-3.4, 3.4):
        g.ellipse(dx, -4.8, 1.1, 0.6, "#ff9fb8", opacity=0.8)


def _drift(g: Layer, c: Ctx, size: float = 1.0) -> None:
    fur, belly, tail = _lit(c, "#bfe6ff"), _lit(c, "#f4fbff"), _lit(c, "#ffffff")
    s = size
    for dx, dy, r in ((-9, -9, 3.4), (-11.5, -12.5, 2.8), (-8, -13.5, 2.4)):
        g.circle(dx * s, dy * s, r * s, tail)
    g.ellipse(-1 * s, -5 * s, 7 * s, 4.4 * s, fur)
    g.ellipse(-1 * s, -3.6 * s, 4.6 * s, 2.4 * s, belly, opacity=0.85)
    for dx in (-5, -1.5, 2, 4.5):
        g.rect(dx * s - 0.8 * s, -2 * s, 1.6 * s, 2 * s, fur, rx=0.8 * s)
    g.path(f"M{-4 * s:.1f} {-8 * s:.1f}q{-3 * s:.1f} {-6 * s:.1f} {3 * s:.1f} {-5 * s:.1f}"
           f"q{-1 * s:.1f} {3 * s:.1f} {-3 * s:.1f} {5 * s:.1f}z", _lit(c, "#e8f6ff"))
    g.circle(5 * s, -9.5 * s, 4.2 * s, fur)
    g.path(f"M{2.4 * s:.1f} {-12.6 * s:.1f}l{0.6 * s:.1f} {-4.6 * s:.1f}"
           f"l{2.4 * s:.1f} {3.6 * s:.1f}z", fur)
    g.path(f"M{6.4 * s:.1f} {-13 * s:.1f}l{1.6 * s:.1f} {-4.4 * s:.1f}"
           f"l{1.4 * s:.1f} {4.4 * s:.1f}z", fur)
    g.ellipse(8.6 * s, -8.6 * s, 1.6 * s, 1.2 * s, belly)
    g.circle(9.8 * s, -8.8 * s, 0.5 * s, "#1a1622")
    _eyes(g, 5.4 * s, -10 * s, 3.4 * s, 0.85 * s)
    g.poly([(5.4 * s, -14.6 * s), (6.4 * s, -13 * s), (5.4 * s, -12 * s), (4.4 * s, -13 * s)],
           "#7fe3ff")


def _nimbus(g: Layer, c: Ctx) -> None:
    wing = _lit(c, "#f4fbff")
    for k, (dx, dy, ln) in enumerate(((-3, -14, 16), (-1, -15, 13), (1, -15.5, 10))):
        g.path(f"M{dx} {dy}q{-6 - k * 2} {-10 + k} {-ln} {-6 + k}q{ln * 0.5} {4} {ln - 2} {7}z",
               wing, opacity=0.95 - k * 0.15)
    _drift(g, c, 1.45)
    g.circle(-6, -27, 0.8, "#fff3a0", class_="tw")
    g.circle(14, -24, 0.7, "#fff3a0", class_="tw", style="animation-delay:-2s")


def companion(L: Layer, c: Ctx, x: float, y: float, level: int) -> None:
    """Your companion standing (or, once grown, hovering) on the terrace at (x, y)."""
    form = stage(level)
    g = Layer()
    if form == 1:
        _puff(g, c)
    elif form == 2:
        _drift(g, c)
    else:
        if c.dark:
            c.glow(g, 7.8, -19, 26, "#7fe3ff", 0.45, class_="pulse")
        _nimbus(g, c)
    lift = -8 if form == 3 else 0
    L.raw(f'<g transform="translate({x:.1f} {y + lift:.1f})"><g class="bob" '
          f'style="animation-duration:{2.4 + form * 0.4:.1f}s">{g.svg()}</g></g>')
