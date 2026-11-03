"""Your companion: a young sky dragon that lives on the HQ's roof terrace and grows up as you
level. An original design, drawn in profile facing right: deep teal scales with glowing cyan
markings, gold belly plates and spines, swept-back ivory horns, glowing eyes and wide
bat-like wings with a teal-to-violet sheen. Three forms:

1. Pip: still in its egg, a dark scaled egg wrapped in gold filigree; its head has broken
   through the top, and the cracks glow.
2. Ember: a young dragon perched on the terrace, wings half raised and beating.
3. Zephyr: grown up. It leaves its nest on the terrace and flies loops around the town,
   wings spread, turning to face the way it is going.
"""

from __future__ import annotations

from . import palette as pal
from .context import Ctx
from .progress import EVOLVE_LEVELS
from .svg import Layer

NAMES = ("Pip", "Ember", "Zephyr")
INK = "#0e1a24"  # the outline
GLOW = "#7ff7ff"  # eyes and markings
LOOP_S = 18  # one loop of the grown dragon's flight round the town

CSS = (
    "@keyframes beat{from{transform:rotate(-16deg)}to{transform:rotate(10deg)}}"
    ".beat{animation:beat .6s ease-in-out infinite alternate;transform-box:fill-box;"
    "transform-origin:100% 100%}"
    "@keyframes turn{0%,49.9%{transform:scaleX(1)}50%,99.9%{transform:scaleX(-1)}"
    "100%{transform:scaleX(1)}}"
    f".turn{{animation:turn {LOOP_S}s linear infinite}}"
)

# Shapes in profile, facing right, feet on y=0. The wing rises from the shoulder at 0,0.
WING = ("M0 0C-2 -10 -8 -18 -16 -20C-14 -15 -15 -12 -17 -9C-13 -10 -10 -8 -9 -5"
        "C-6 -6 -3 -4 -2 -1Z")
WING_BONES = "M0 0L-16 -20M-0.6 -0.4L-17 -9M-1 -0.2L-9 -5"
TAIL = ("M-5 -9C-12 -9 -16 -4 -21 -4.5C-24 -5 -25 -8 -23 -10C-23 -7.5 -21 -6.6 -19 -6.8"
        "C-15 -7 -11 -5.6 -5 -5Z")
TORSO = "M-6 -10C-5 -14 3 -15 6 -12C8 -9 6 -6 2 -5.5C-2 -5 -6 -6 -6 -10Z"
NECK = "M3.6 -13C6 -18 5 -22 8 -25.2L11 -23.8C9 -21 10 -17 7 -11Z"
HEAD = "M7 -25.8C9 -28 13 -27.8 17 -25.8L18.6 -24.4C15 -23 12 -22.4 9 -22.6Z"
HORNS = ("M8.6 -26.8C6 -29.4 3.6 -30 1.4 -29.4C4 -28.6 5.6 -27.6 7.4 -25.8Z"
         "M10.4 -27.4C9 -29.6 7.4 -30.6 5.6 -31C7.4 -29.8 8.4 -28.8 9 -27.2Z")
HIND = "M-5 -9C-7 -6 -6 -3 -7 0H-3.6C-3 -3 -2 -6 -1 -8Z"
FORE = "M3 -7C4 -4 3 -2 4 0H6.6C6 -2 6.4 -5 5.6 -8Z"


def _lit(c: Ctx, col: str) -> str:
    """A sprite keeps most of its own light: only partly dimmed by the time of day."""
    return pal.mix(c.lit(col), col, 0.7)


def stage(level: int) -> int:
    """1, 2 or 3: which form your companion has reached."""
    return 1 + sum(level >= lv for lv in EVOLVE_LEVELS)


def _wing(c: Ctx, beating: bool, delay: float = 0.0) -> str:
    sheen = c.defs.linear("dragonwing", [(0, _lit(c, "#2fa8b8")), (1, _lit(c, "#5a4a9a"))])
    w = Layer()
    w.path(WING, sheen, stroke=INK, stroke_width=0.5, opacity=0.95)
    w.path(WING_BONES, stroke=_lit(c, "#d9b45a"), stroke_width=0.6)
    cls = f' class="beat" style="animation-delay:-{delay}s"' if beating else ""
    return f"<g{cls}>{w.svg()}</g>"


def _dragon(g: Layer, c: Ctx, flying: bool) -> None:
    """The dragon in profile. Standing it rests on its legs; flying, the legs tuck in and a
    second wing beats in front of the body."""
    scales, gold, horn = _lit(c, "#1f5f6e"), _lit(c, "#d9b45a"), _lit(c, "#efe6d0")
    line = {"stroke": INK, "stroke_width": 0.5}
    g.raw(f'<g transform="translate(1 -12.5)">{_wing(c, True, 0.3)}</g>')  # far wing
    g.path(TAIL, scales, **line)
    g.path("M-23 -10l-3.4 -2.2l1.2 3.6z", gold, **line)  # the tail's blade
    if flying:
        g.path("M-5 -8.6q-3 1.4 -6 0.6M3 -7q2 1.6 4.6 1.2", stroke=scales, stroke_width=2.2,
               stroke_linecap="round")
    else:
        g.path(HIND, scales, **line)
        g.path(FORE, scales, **line)
        g.path("M-7 0l-1 1M-5.4 0l-0.4 1.1M4 0l-0.6 1M5.6 0l0.2 1.1", stroke=horn,
               stroke_width=0.5)
    g.path(TORSO, scales, **line)
    g.path(NECK, scales, **line)
    g.path("M-3 -6.2C0 -5.4 4 -6 6.4 -9.4C7.6 -13 8.6 -18 9.4 -22.4", stroke=gold,
           stroke_width=1.5)  # belly plates, down the throat
    g.path("M-1 -6h0M2 -6.2h0M5 -7.6h0M7.4 -12h0M8.4 -16h0", stroke=_lit(c, "#a8843a"),
           stroke_width=1.6, stroke_linecap="round")
    spines = "".join(f"M{x} {y}l{d} -2.2l1.4 1.6z" for x, y, d in
                     ((5.6, -23.6, -0.6), (4.6, -19.6, -0.8), (4, -15.6, -1), (1.6, -13.8, -1),
                      (-2.4, -13.4, -1), (-6, -11.6, -1), (-11, -8.4, -1), (-16, -6.4, -1)))
    g.path(spines, gold)
    g.path(HORNS, horn, **line)
    g.path(HEAD, scales, **line)
    g.path("M10 -23.4C13 -23.2 15.6 -23.8 18 -24.6", stroke=INK, stroke_width=0.4)  # jaw
    g.circle(17.4, -25.4, 0.3, INK)  # nostril
    # Glowing markings and eye.
    if c.dark:
        c.glow(g, 12.4, -25.4, 4, GLOW, 0.9)
    g.path("M11.6 -25.6l1.8 -0.5l-0.4 0.9z", GLOW)
    g.path("M-3 -11.6q3 -1.6 6 -0.6M-12 -7.6q2.6 -1 5 -0.4", stroke=GLOW, stroke_width=0.5,
           opacity=0.85, class_="pulse")
    if flying:
        g.raw(f'<g transform="translate(-1 -12)">{_wing(c, True)}</g>')  # near wing


def _pip(g: Layer, c: Ctx) -> None:
    """A scaled egg wrapped in gold filigree, glowing cracks, and a head breaking through."""
    shell, gold, horn = _lit(c, "#1c4652"), _lit(c, "#d9b45a"), _lit(c, "#efe6d0")
    if c.dark:
        c.glow(g, 0, -9, 14, GLOW, 0.5, class_="pulse")
    # The head and a little neck rising out of the broken top.
    g.raw(f'<g transform="translate(-5.2 -0.4) scale(.62)">'
          f'<path d="{NECK}" fill="{_lit(c, "#1f5f6e")}" stroke="{INK}" stroke-width=".7"/>'
          f'<path d="{HORNS}" fill="{horn}" stroke="{INK}" stroke-width=".7"/>'
          f'<path d="{HEAD}" fill="{_lit(c, "#1f5f6e")}" stroke="{INK}" stroke-width=".7"/>'
          f'<path d="M11.6 -25.6l1.8 -0.5l-0.4 0.9z" fill="{GLOW}"/></g>')
    g.path("M-6.4 -9.6L-4.6 -12.2L-2.6 -10L-0.4 -12.8L1.6 -10.2L3.6 -12.4L6.4 -9.6"
           "C7.6 -4 5 0 0 0C-5 0 -7.6 -4 -6.4 -9.6Z", shell, stroke=INK, stroke_width=0.5)
    g.path("M-6 -6.4q6 2.4 12 0M-5.4 -3q5.4 2 10.8 0", stroke=gold, stroke_width=0.6)
    g.path("M-1 -10.6l1 2.4l-1.6 2l1.4 2.4", stroke=GLOW, stroke_width=0.6, class_="pulse")


def _nest(g: Layer, c: Ctx) -> None:
    """The nest left on the terrace, with pieces of the dark egg in it."""
    g.ellipse(0, -1.6, 7.5, 2.6, _lit(c, "#8a5d42"))
    g.path("M-7 -2.4q3.5 -2 7 -0.6q3.5 -1.6 7 0.4M-6 -0.6q3 1 6 0q3 -1 6 0.2",
           stroke=_lit(c, "#5a3f2e"), stroke_width=0.6)
    g.path("M-2 -3.4l1.6 -1.8l1.2 1.6zM2 -3.2l1.4 -1.2l0.8 1.4z", _lit(c, "#1c4652"))


def companion(L: Layer, c: Ctx, x: float, y: float, level: int) -> None:
    """Your companion on the terrace at (x, y); once grown, flying loops around the town."""
    form = stage(level)
    g = Layer()
    if form == 1:
        _pip(g, c)
    elif form == 2:
        _dragon(g, c, flying=False)
    else:
        _nest(g, c)
    size = (0.8, 0.62, 1.0)[form - 1]  # sized so the terrace still fits
    L.raw(f'<g transform="translate({x:.1f} {y:.1f}) scale({size})"><g class="bob" '
          f'style="animation-duration:{2.4 + form * 0.4:.1f}s">{g.svg()}</g></g>')
    if form == 3:
        flyer = Layer()
        _dragon(flyer, c, flying=True)
        cy, rx, ry = y - 46, 150, 34
        path = (f"M{x - rx:.0f} {cy:.0f}A{rx} {ry} 0 0 1 {x + rx:.0f} {cy:.0f}"
                f"A{rx} {ry} 0 0 1 {x - rx:.0f} {cy:.0f}")
        L.raw(f'<g><g class="turn"><g transform="scale(.95) translate(0 14)">{flyer.svg()}</g>'
              f'</g><animateMotion dur="{LOOP_S}s" repeatCount="indefinite" path="{path}"/></g>')
