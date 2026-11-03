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

# Shapes in profile, facing right, feet on y=0. The wing rises from the shoulder at 0,0: an
# arm to the wrist, four finger bones fanning out, and a membrane scalloped between them.
WING = ("M0 0L-2 -6L-7 -15L-21 -23Q-18 -18 -22.5 -14Q-18 -11.5 -19.5 -7.5Q-15 -6 -13 -2.6"
        "Q-8 -2.6 -3 0Z")
WING_INNER = "M0 0L-2 -6L-7 -15L-13 -2.6Q-8 -2.6 -3 0Z"
WING_ARM = "M0 0L-2 -6L-7 -15"
WING_FINGERS = "M-7 -15L-21 -23M-7 -15L-22.5 -14M-7 -15L-19.5 -7.5M-7 -15L-13 -2.6"


def _bezier(t: float, p: tuple) -> tuple[float, float]:
    (x0, y0), (x1, y1), (x2, y2), (x3, y3) = p
    u = 1 - t
    return (u ** 3 * x0 + 3 * u * u * t * x1 + 3 * u * t * t * x2 + t ** 3 * x3,
            u ** 3 * y0 + 3 * u * u * t * y1 + 3 * u * t * t * y2 + t ** 3 * y3)


def _tail_shapes() -> tuple[str, str, str, str]:
    """The tail: a long S-curve from the hip that tapers to a diamond blade, with bands
    across it and spines along its top. Built once from a curve."""
    curve = ((-4, -8), (-14, -9.5), (-21, 0.5), (-31, -9))
    n = 14
    top, bottom, bands, spines = [], [], [], []
    for k in range(n + 1):
        t = k / n
        x, y = _bezier(t, curve)
        x2, y2 = _bezier(min(1, t + 0.01), curve)
        x1, y1 = _bezier(max(0, t - 0.01), curve)
        dx, dy = x2 - x1, y2 - y1
        ln = (dx * dx + dy * dy) ** 0.5 or 1
        nx, ny = -dy / ln, dx / ln
        half = (4.6 * (1 - t) + 0.7) / 2
        a, b = (x + nx * half, y + ny * half), (x - nx * half, y - ny * half)
        top.append(a)
        bottom.append(b)
        if k in (2, 4, 6, 8, 10):
            bands.append(f"M{a[0]:.1f} {a[1]:.1f}L{b[0]:.1f} {b[1]:.1f}")
        if k in (1, 3, 5, 7, 9, 11):
            up = a if a[1] < b[1] else b
            spines.append(f"M{up[0] - 0.8:.1f} {up[1]:.1f}l{0.4 - dx / ln:.1f} -2l1.2 1.6z")
    outline = ("M" + "L".join(f"{x:.1f} {y:.1f}" for x, y in top)
               + "L" + "L".join(f"{x:.1f} {y:.1f}" for x, y in reversed(bottom)) + "Z")
    tx, ty = _bezier(1, curve)
    px, py = _bezier(0.97, curve)
    dx, dy = tx - px, ty - py
    ln = (dx * dx + dy * dy) ** 0.5
    ux, uy, nx, ny = dx / ln, dy / ln, -dy / ln, dx / ln
    blade = (f"M{tx - ux:.1f} {ty - uy:.1f}L{tx + nx * 2 + ux * 2:.1f} {ty + ny * 2 + uy * 2:.1f}"
             f"L{tx + ux * 8:.1f} {ty + uy * 8:.1f}"
             f"L{tx - nx * 2 + ux * 2:.1f} {ty - ny * 2 + uy * 2:.1f}Z")
    return outline, "".join(bands), "".join(spines), blade


TAIL, TAIL_BANDS, TAIL_SPINES, TAIL_BLADE = _tail_shapes()
TORSO = "M-6 -10C-5 -14 3 -15 6 -12C8 -9 6 -6 2 -5.5C-2 -5 -6 -6 -6 -10Z"
NECK = "M3.6 -13C6 -18 5 -22 8 -25.2L11 -23.8C9 -21 10 -17 7 -11Z"
HEAD = "M7 -25.8C9 -28 13 -27.8 17 -25.8L18.6 -24.4C15 -23 12 -22.4 9 -22.6Z"
HORNS = ("M8.6 -26.8C6 -29.4 3.6 -30 1.4 -29.4C4 -28.6 5.6 -27.6 7.4 -25.8Z"
         "M10.4 -27.4C9 -29.6 7.4 -30.6 5.6 -31C7.4 -29.8 8.4 -28.8 9 -27.2Z")
# Four legs: standing, a muscled hind leg and a foreleg; flying, the forelegs tuck under the
# chest and the hind legs trail back. The far pair is drawn a little behind and darker.
HIND = "M-7 -10C-9.2 -7 -8.8 -4 -7.6 -2.4L-8.4 0H-4.4L-4.6 -2C-3.2 -4 -2.4 -7 -2.6 -9.4Z"
FORE = "M2.4 -8.4C3 -5.4 2.6 -2.8 3.4 -1.4L3 0H6.8L6.4 -1.6C6 -4 6.4 -6.2 5.8 -8.8Z"
HIND_TUCK = "M-4.6 -9C-7.4 -7.4 -10.6 -7.2 -13.4 -7.8L-13.6 -6.2C-10.4 -5.2 -6.8 -5.2 -3.6 -6.8Z"
FORE_TUCK = "M3.4 -8.4C4.2 -6 6 -4.8 8.6 -5L8.8 -3.6C5.8 -3 3 -4.4 1.8 -7Z"
CLAWS = "M-8.4 0l-.9 .9M-6.6 0l-.3 1M-4.8 0l.3 .9M3 0l-.9 .9M4.8 0l-.3 1M6.6 0l.3 .9"
CLAWS_TUCK = "M-13.5 -7.6l-1.2 -.4M-13.6 -6.4l-1.2 .4M8.8 -5l1 -.6M8.9 -3.8l1 .4"
FAR = "translate(2.2 -0.8)"


def _lit(c: Ctx, col: str) -> str:
    """A sprite keeps most of its own light: only partly dimmed by the time of day."""
    return pal.mix(c.lit(col), col, 0.7)


def stage(level: int) -> int:
    """1, 2 or 3: which form your companion has reached."""
    return 1 + sum(level >= lv for lv in EVOLVE_LEVELS)


def _wing(c: Ctx, beating: bool, delay: float = 0.0) -> str:
    sheen = c.defs.linear("dragonwing", [(0, _lit(c, "#3fc0c8")), (1, _lit(c, "#5a4a9a"))])
    w = Layer()
    w.path(WING, sheen, stroke=INK, stroke_width=0.5, opacity=0.95)
    w.path(WING_INNER, _lit(c, "#2a2a6a"), opacity=0.35)
    w.path(WING_FINGERS, stroke=_lit(c, "#d9b45a"), stroke_width=0.6)
    w.path(WING_ARM, stroke=_lit(c, "#1f5f6e"), stroke_width=1.6, stroke_linecap="round")
    w.path("M-7 -15l-1.2 -2.6l1.9 1.3z", _lit(c, "#efe6d0"))  # the wrist claw
    cls = f' class="beat" style="animation-delay:-{delay}s"' if beating else ""
    return f"<g{cls}>{w.svg()}</g>"


def _dragon(g: Layer, c: Ctx, flying: bool) -> None:
    """The dragon in profile, four legs and two wings. The body (tail, near legs, torso,
    neck and head) is outlined as one silhouette: every part is first drawn in the outline
    colour with a thick edge, then filled over without one, so no seams show where the parts
    meet."""
    scales, far, gold, horn = (_lit(c, "#1f5f6e"), _lit(c, "#164a56"), _lit(c, "#d9b45a"),
                               _lit(c, "#efe6d0"))
    dark = _lit(c, "#164a56")
    hind, fore = (HIND_TUCK, FORE_TUCK) if flying else (HIND, FORE)
    g.raw(f'<g transform="translate(1 -12.5)">{_wing(c, True, 0.3)}</g>')  # far wing
    for leg in (hind, fore):  # the far legs, behind the body
        g.path(leg, far, stroke=INK, stroke_width=0.6, transform=FAR)
    g.path(TAIL_SPINES, gold)
    g.path("".join(f"M{x} {y}l{d} -2.2l1.4 1.6z" for x, y, d in
                   ((5.6, -23.6, -0.6), (4.6, -19.6, -0.8), (4, -15.6, -1), (1.6, -13.8, -1),
                    (-2.4, -13.4, -1), (-6, -11.6, -1))), gold)  # back spines
    g.path(HORNS, horn, stroke=INK, stroke_width=0.5)
    body = (TAIL, hind, fore, TORSO, NECK, HEAD)
    for part in body:
        g.path(part, INK, stroke=INK, stroke_width=1.1, stroke_linejoin="round")
    for part in body:
        g.path(part, scales)
    g.path(TAIL_BANDS, stroke=dark, stroke_width=0.5)
    g.path(TAIL_BLADE, gold, stroke=INK, stroke_width=0.5)
    g.path(CLAWS_TUCK if flying else CLAWS, stroke=horn, stroke_width=0.5)
    # Scales on the flank and up the neck, and gold plates down the belly and throat.
    g.path("M-4.6 -9.6q1 1 2 0M-1.6 -10.6q1 1 2 0M1.4 -11q1 1 2 0M-3.2 -7.4q1 1 2 0"
           "M-0.2 -8q1 1 2 0M5.4 -15.4q1 .8 1.8 0M6.4 -19q.9 .7 1.6 0", stroke=dark,
           stroke_width=0.45)
    g.path("M-3 -6.2C0 -5.4 4 -6 6.2 -9.2C7.4 -13 8.4 -18 9.4 -22.2", stroke=gold,
           stroke_width=1.4, stroke_linecap="round")
    g.path("M-1 -6h0M2 -6.2h0M5 -7.6h0M7.2 -12h0M8.2 -16h0", stroke=_lit(c, "#a8843a"),
           stroke_width=1.5, stroke_linecap="round")
    g.path("M10 -23.4C13 -23.2 15.6 -23.8 18 -24.6", stroke=INK, stroke_width=0.4)  # jaw
    g.path("M9.2 -23.6l-3.4 1.8l3 -.2l-2 1.6l3 -1z", gold)  # frill behind the jaw
    g.path("M9 -26.6q3 -1.6 6.4 -.6", stroke=INK, stroke_width=0.5)  # brow ridge
    g.circle(17.4, -25.4, 0.3, INK)  # nostril
    if c.dark:
        c.glow(g, 12.4, -25.4, 4, GLOW, 0.9)
    g.path("M11.6 -25.6l1.8 -0.5l-0.4 0.9z", GLOW)  # the eye
    g.path("M-3 -11.6q3 -1.6 6 -0.6M-12 -8.2q2.6 -1 5 -0.4", stroke=GLOW, stroke_width=0.5,
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
