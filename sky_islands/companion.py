"""Your companion: a little sky kitsune that lives on the HQ's roof terrace and grows more
tails as you level up. An original design in three forms, facing right:

1. Puff: a round kit with one fluffy tail and a leaf on its head (the shape-shifting leaf
   of kitsune stories).
2. Drift: three tails, a crystal on its brow, and a wisp of blue fox-fire beside it.
3. Nimbus: nine tails fanned out like a halo; it hovers beside the terrace with fox-fire
   circling it, and its crystal glows after dark.

Snowy cream fur with sky-blue tail tips, peach ears and gold markings, outlined so it stays
readable at the banner's small size.
"""

from __future__ import annotations

from . import palette as pal
from .context import Ctx
from .progress import EVOLVE_LEVELS
from .svg import Layer

NAMES = ("Puff", "Drift", "Nimbus")
INK = "#3a2e48"  # the outline
# A plump tail that sweeps up at the end, and its sky-blue tip.
TAIL = "M0 0C3 -4 8 -8.5 12.5 -8C16.5 -7.5 18 -3.5 15.5 -0.5C12.5 2.5 5 2.5 0 0Z"
TIP = "M12.5 -8C16.5 -7.5 18 -3.5 15.5 -0.5C14.6 0.4 13.4 0.9 12.2 1C13.4 -2 13.6 -5 12.5 -8Z"
FIRE = "M0 0C-2.4 -2 -1.8 -5.4 0 -8C1.8 -5.4 2.4 -2 0 0Z"


def _lit(c: Ctx, col: str) -> str:
    """A sprite keeps some of its own light: only half dimmed by the time of day."""
    return pal.mix(c.lit(col), col, 0.82)


def stage(level: int) -> int:
    """1, 2 or 3: which form your companion has reached."""
    return 1 + sum(level >= lv for lv in EVOLVE_LEVELS)


def _tails(g: Layer, c: Ctx, angles: tuple[float, ...], length: float) -> None:
    """Fluffy tails from the rump, each with a sky-blue tip. They are mirrored so they sweep
    up and back, and their lengths vary a little so a full set looks like fur, not a fan."""
    fur, tip = _lit(c, "#fbf6ee"), _lit(c, "#7fc8f0")
    for k, a in enumerate(angles):
        ln = length * (1, 1.12, 1.05, 1.16)[k % 4]
        t = f"translate(-3.5 -3.5) rotate({a}) scale({ln:.2f} -{ln:.2f})"
        g.path(TAIL, fur, stroke=INK, stroke_width=0.5 / ln, transform=t)
        g.path(TIP, tip, transform=t)


def _fox(g: Layer, c: Ctx, crystal: bool) -> None:
    """The body and head, sitting, about 22 units tall with the ears."""
    fur, shade = _lit(c, "#fbf6ee"), _lit(c, "#e4d8c8")
    ear, mark = _lit(c, "#ffb3a0"), _lit(c, "#e8a83a")
    line = {"stroke": INK, "stroke_width": 0.5}
    g.ellipse(-2.6, -2.8, 3.2, 2.6, shade, **line)  # haunch
    g.ellipse(0, -5.2, 4.8, 5, fur, **line)  # body
    g.path("M1.4 -9.2q2 2.4 0.4 5.6q2.4 -1.2 3.2 -4.4z", "#ffffff")  # chest fluff
    for px in (1.4, 4):
        g.ellipse(px, -0.7, 1.4, 0.9, fur, **line)  # front paws
    # Ears first, so the head overlaps their base.
    g.path("M0.6 -15.2L1 -21.6L4.4 -16.4Z", fur, **line)
    g.path("M5.2 -16.6L8 -21.4L8.8 -15.2Z", fur, **line)
    g.path("M1.5 -16L1.8 -19.8L3.7 -16.6Z", ear)
    g.path("M5.9 -16.6L7.6 -19.6L8.1 -15.8Z", ear)
    g.path("M-1 -12.2C-1 -16.6 9.6 -17 9.8 -12.4C10 -9.4 7.4 -7.8 4.4 -7.8"
           "C1.4 -7.8 -1 -9.4 -1 -12.2Z", fur, **line)  # head
    g.path("M-1 -11.4l-1.4 0.8l1.6 0.6l-1 1l1.8 0.2", stroke=INK, stroke_width=0.4)  # cheek tuft
    g.ellipse(8.2, -10.6, 2.2, 1.6, "#ffffff")  # muzzle
    g.circle(10, -11.2, 0.7, INK)  # nose
    for ex in (3, 6.4):  # happy closed eyes
        g.path(f"M{ex - 1} -12.4q1 -1.2 2 0", stroke=INK, stroke_width=0.6,
               stroke_linecap="round")
    g.ellipse(2.2, -10.6, 1.1, 0.6, "#ff9fb8", opacity=0.7)  # blush
    if crystal:
        g.path("M4.6 -17.4l1 1.5l-1 1.5l-1 -1.5z", "#7fe3ff", stroke=INK, stroke_width=0.3)
    else:
        g.path("M4.6 -16.8q0.9 1 0 2q-0.9 -1 0 -2z", mark)


def _fire(g: Layer, c: Ctx, x: float, y: float, delay: float) -> None:
    """A wisp of blue fox-fire."""
    w = Layer()
    if c.dark:
        c.glow(w, 0, -4, 7, "#7fe3ff", 0.6)
    w.path(FIRE, "#9fe6ff", opacity=0.9)
    w.path(FIRE, "#ffffff", transform="translate(0 -0.6) scale(.45)")
    g.raw(f'<g transform="translate({x} {y})"><g class="bob" style="animation-duration:1.8s;'
          f'animation-delay:-{delay}s">{w.svg()}</g></g>')


def _puff(g: Layer, c: Ctx) -> None:
    _tails(g, c, (190,), 0.8)
    _fox(g, c, crystal=False)
    g.path("M4.2 -17q-1.4 -3.4 1.6 -5.4q0.8 3 -1.6 5.4z", _lit(c, "#5cbf6a"))  # the leaf
    g.line(4.2, -17, 4.6, -18.6, _lit(c, "#3f8a46"), 0.5)


def _drift(g: Layer, c: Ctx) -> None:
    _tails(g, c, (175, 200, 225), 0.9)
    _fox(g, c, crystal=True)
    _fire(g, c, 13, -16, 0)


def _nimbus(g: Layer, c: Ctx) -> None:
    if c.dark:
        c.glow(g, 4.6, -16, 9, "#7fe3ff", 0.7, class_="pulse")
    _tails(g, c, tuple(138 + k * 18 for k in range(9)), 1.05)
    _fox(g, c, crystal=True)
    for k, (x, y) in enumerate(((14, -18), (-14, -22), (2, -28))):
        _fire(g, c, x, y, k * 0.6)


def companion(L: Layer, c: Ctx, x: float, y: float, level: int) -> None:
    """Your companion sitting (or, once grown, hovering) on the terrace at (x, y)."""
    form = stage(level)
    g = Layer()
    (_puff, _drift, _nimbus)[form - 1](g, c)
    size = (0.72, 0.85, 1.0)[form - 1]  # sized to the old sprites, so the terrace still fits
    lift = -8 if form == 3 else 0
    L.raw(f'<g transform="translate({x:.1f} {y + lift:.1f}) scale({size})"><g class="bob" '
          f'style="animation-duration:{2.4 + form * 0.4:.1f}s">{g.svg()}</g></g>')
