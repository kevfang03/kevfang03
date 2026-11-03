"""Your companion: a baby sky dragon that lives on the HQ's roof terrace and grows up as you
level. An original design, emerald and gold like the great sky dragon that flies over on
streak days, in three forms facing right:

1. Pip: a hatchling peeking out of its cracked egg, a bit of shell still on its head.
2. Ember: a young dragon standing on the terrace, beating its little wings.
3. Zephyr: grown up. It leaves an empty nest on the terrace and flies loops around the town,
   turning to face the way it is going.

Outlined so it stays readable at the banner's small size.
"""

from __future__ import annotations

from . import palette as pal
from .context import Ctx
from .progress import EVOLVE_LEVELS
from .svg import Layer

NAMES = ("Pip", "Ember", "Zephyr")
INK = "#1f3a2c"  # the outline
LOOP_S = 18  # one loop of the grown dragon's flight round the town

CSS = (
    "@keyframes beat{from{transform:rotate(-14deg)}to{transform:rotate(12deg)}}"
    ".beat{animation:beat .5s ease-in-out infinite alternate;transform-box:fill-box;"
    "transform-origin:100% 100%}"
    "@keyframes turn{0%,49.9%{transform:scaleX(1)}50%,99.9%{transform:scaleX(-1)}"
    "100%{transform:scaleX(1)}}"
    f".turn{{animation:turn {LOOP_S}s linear infinite}}"
)


def _lit(c: Ctx, col: str) -> str:
    """A sprite keeps most of its own light: only partly dimmed by the time of day."""
    return pal.mix(c.lit(col), col, 0.75)


def stage(level: int) -> int:
    """1, 2 or 3: which form your companion has reached."""
    return 1 + sum(level >= lv for lv in EVOLVE_LEVELS)


def _wing(c: Ctx, beating: bool) -> str:
    """A small bat-like wing rising from the shoulder at 0,0."""
    w = Layer()
    w.path("M0 0C-2 -7 -8 -11 -12 -9.5C-9.6 -8 -9.8 -6 -8.6 -4.4C-7 -5.4 -5 -4.6 -4.4 -3"
           "C-3 -3.6 -1.6 -2.4 -1 0Z", _lit(c, "#8fe0b8"), stroke=INK, stroke_width=0.5)
    w.path("M0 0L-11 -9M-0.6 -0.4L-8.4 -4.4M-0.8 -0.2L-4.4 -3", stroke=_lit(c, "#2a8a5a"),
           stroke_width=0.5)
    cls = ' class="beat"' if beating else ""
    return f"<g{cls}>{w.svg()}</g>"


def _dragon(g: Layer, c: Ctx, beating: bool) -> None:
    """A little dragon standing with its feet on y=0, about 20 units tall with its horns."""
    body, belly = _lit(c, "#3fbf7f"), _lit(c, "#f6e7a8")
    gold = _lit(c, "#f2c46d")
    line = {"stroke": INK, "stroke_width": 0.5}
    # The tail, curling up behind, with a spade at its tip.
    tail = "M-3 -3C-9 -2 -13 -5 -12 -9.4C-11.6 -11.4 -9.4 -11.4 -9 -9.8"
    g.path(tail, stroke=INK, stroke_width=3.4, stroke_linecap="round")
    g.path(tail, stroke=body, stroke_width=2.4, stroke_linecap="round")
    g.path("M-9 -9.8l-1.6 -2.2l2.8 -0.4z", gold, **line)
    g.raw(f'<g transform="translate(-0.5 -9.5)">{_wing(c, beating)}</g>')
    g.ellipse(-2.6, -1.6, 2.4, 1.6, body, **line)  # back leg
    g.ellipse(0, -5.6, 5, 5, body, **line)  # body
    g.path("M1.2 -9.6C4.6 -8.4 5 -3 2.4 -1.2C1 -2.6 0.4 -6.6 1.2 -9.6Z", belly)
    g.path("M1.6 -7.6h2.6M1.4 -5.4h3.1M1.6 -3.3h2.4", stroke=_lit(c, "#d9c47a"),
           stroke_width=0.4)
    g.ellipse(2.8, -1, 1.7, 1.1, body, **line)  # front foot
    for k, (sx, sy) in enumerate(((-1.6, -10.4), (-3.8, -9.2), (-5.6, -7.2))):  # back spikes
        g.path(f"M{sx - 1} {sy + 0.6}l{0.8 + k * 0.1:.1f} -2.2l1 1.8z", gold)
    # The head: round with a short snout, big eyes and two little gold horns.
    g.path("M2.4 -15.6q-1.2 -3.4 -3.4 -4.2q1.6 1.8 1.2 4.6z", gold, **line)
    g.path("M4.6 -16.2q-0.2 -3.4 -1.8 -4.8q0.8 2.2 -0.2 4.8z", gold, **line)
    g.ellipse(4.2, -12.4, 4.6, 3.9, body, **line)
    g.path("M6.4 -14.2C9.4 -14.6 11.8 -13 11.8 -11.2C11.8 -9.6 9.6 -9 6.8 -9.4Z", body, **line)
    g.circle(10.7, -12.2, 0.35, INK)  # nostril
    g.path("M7.6 -10.2q1.8 0.8 3.4 0", stroke=INK, stroke_width=0.4)  # smile
    g.ellipse(5.4, -12.8, 1.15, 1.45, INK)
    g.circle(5.8, -13.3, 0.45, "#ffffff")
    g.ellipse(3.2, -11, 1, 0.55, "#ff9fb8", opacity=0.7)  # blush


def _pip(g: Layer, c: Ctx) -> None:
    """The hatchling in the bottom half of its egg, wearing a bit of the top half."""
    shell, spot = _lit(c, "#fbf3e0"), _lit(c, "#f2c46d")
    _dragon(g, c, beating=False)
    g.path("M-7 -4.4L-5 -6.6L-3 -4.6L-1 -7L1 -4.6L3 -6.6L5 -4.6L7 -6.2C7.6 0.6 -7.6 0.6 -7 -4.4Z",
           shell, stroke=INK, stroke_width=0.5)
    for sx, sy in ((-3.6, -2.4), (1.6, -1.6), (4.4, -3.4)):
        g.circle(sx, sy, 0.7, spot)
    g.path("M1.4 -15.4C1.8 -18.2 6.6 -18.2 7.2 -15.6L6 -16.4L5 -15.2L3.8 -16.4L2.6 -15.2Z",
           shell, stroke=INK, stroke_width=0.4)


def _nest(g: Layer, c: Ctx) -> None:
    """The nest left on the terrace, with a few shell pieces in it."""
    twig = _lit(c, "#8a5d42")
    g.ellipse(0, -1.6, 7.5, 2.6, twig)
    g.path("M-7 -2.4q3.5 -2 7 -0.6q3.5 -1.6 7 0.4M-6 -0.6q3 1 6 0q3 -1 6 0.2",
           stroke=_lit(c, "#5a3f2e"), stroke_width=0.6)
    g.path("M-2 -3.4l1.6 -1.8l1.2 1.6zM2 -3.2l1.4 -1.2l0.8 1.4z", _lit(c, "#fbf3e0"))


def companion(L: Layer, c: Ctx, x: float, y: float, level: int) -> None:
    """Your companion on the terrace at (x, y); once grown, flying loops around the town."""
    form = stage(level)
    g = Layer()
    if form == 1:
        _pip(g, c)
    elif form == 2:
        _dragon(g, c, beating=True)
    else:
        _nest(g, c)
    size = (0.72, 0.9, 1.0)[form - 1]  # sized so the terrace still fits
    L.raw(f'<g transform="translate({x:.1f} {y:.1f}) scale({size})"><g class="bob" '
          f'style="animation-duration:{2.4 + form * 0.4:.1f}s">{g.svg()}</g></g>')
    if form == 3:
        flyer = Layer()
        if c.dark:
            c.glow(flyer, 4, -10, 16, "#7fe3ff", 0.4)
        _dragon(flyer, c, beating=True)
        cy, rx, ry = y - 46, 150, 34
        path = (f"M{x - rx:.0f} {cy:.0f}A{rx} {ry} 0 0 1 {x + rx:.0f} {cy:.0f}"
                f"A{rx} {ry} 0 0 1 {x - rx:.0f} {cy:.0f}")
        L.raw(f'<g><g class="turn"><g transform="scale(1.3) translate(0 8)">{flyer.svg()}</g>'
              f'</g><animateMotion dur="{LOOP_S}s" repeatCount="indefinite" path="{path}"/></g>')
