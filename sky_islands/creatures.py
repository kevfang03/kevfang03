"""Background life, all original designs: a sky whale and her calf gliding behind the
archipelago, sky jellies drifting up out of the cloud sea, and a cargo airship on the ride.
They stay hazy and slow so the islands keep the attention.
"""

from __future__ import annotations

from . import palette as pal
from .context import Ctx
from .svg import Layer

# The overview shows from 92% of the loop, through the wrap, to 13.5%: about 18 seconds. The
# whales glide across during that stretch and slip back while the ride hides them.
WHALE_FROM, WHALE_TO = (372, 96), (548, 88)
# In the open gaps between the islands, where the cloud sea shows through.
JELLIES = ((248, 346, 0.9), (268, 384, 1.1), (300, 420, 0.8), (760, 352, 1.0),
           (776, 396, 0.8), (744, 424, 1.2))


def css() -> str:
    """Keyframes for the creatures, timed to the camera loop."""
    from .camera import LOOP_S  # imported here: the camera module imports the ride, which needs us

    sx, sy = WHALE_FROM
    ex, ey = WHALE_TO
    # Linear from 92% to 113.5% (the wrap), so the 0% position sits 8/21.5 of the way along.
    f = 8 / 21.5
    mx, my = (ex - sx) * f, (ey - sy) * f
    dx, dy = ex - sx, ey - sy
    return (
        f"@keyframes glide{{0%{{transform:translate({mx:.1f}px,{my:.1f}px)}}"
        f"13.5%{{transform:translate({dx}px,{dy}px)}}"
        f"92%{{transform:translate(0px,0px)}}"
        f"100%{{transform:translate({mx:.1f}px,{my:.1f}px)}}}}"
        f".glide{{animation:glide {LOOP_S}s linear infinite}}"
        "@keyframes fluke{from{transform:rotate(-7deg)}to{transform:rotate(7deg)}}"
        ".fluke{animation:fluke 2.6s ease-in-out infinite alternate;transform-box:fill-box;"
        "transform-origin:100% 50%}"
        "@keyframes rise{0%{transform:translateY(0);opacity:0}15%{opacity:1}"
        "80%{opacity:1}100%{transform:translateY(-56px);opacity:0}}"
        ".rise{animation:rise 14s ease-in-out infinite}"
        "@keyframes pulse2{0%,100%{transform:scaleY(1)}50%{transform:scaleY(.82)}}"
        ".bell{animation:pulse2 1.8s ease-in-out infinite;transform-box:fill-box;"
        "transform-origin:50% 0}"
    )


def _whale(g: Layer, c: Ctx, body: str, belly: str, glow: bool) -> None:
    """A whale facing right, about 190 units long, centred on its middle."""
    tail = Layer()
    tail.path("M-78 0C-90 -4 -98 -14 -106 -17C-101 -8 -97 -2 -93 0C-97 2 -101 8 -106 17"
              "C-98 14 -90 4 -78 0Z", body)
    g.group(tail, class_="fluke")
    g.path("M-80 1C-62 -2 -40 -16 -6 -22C30 -27 62 -20 76 -10C88 -2 86 9 74 13"
           "C44 22 -12 18 -80 3Z", body)
    g.path("M-46 9C-6 18 40 19 74 11C52 16 4 15 -46 9Z", belly)
    for k in range(4):
        y = 9 + k * 1.8
        g.path(f"M{40 - k * 6} {y}C{52 - k * 4} {y + 1} {64 - k * 2} {y} {72 - k} {y - 1.5}",
               stroke=pal.shade(belly, 0.85), stroke_width=0.6, opacity=0.7)
    g.path("M14 12C20 22 12 31 0 34C8 25 9 18 8 12Z", pal.shade(body, 0.9))
    g.circle(58, -3, 1.6, pal.shade(body, 0.45))
    g.path("M-20 -21C-4 -26 30 -27 56 -19", stroke="#ffffff", stroke_width=1, opacity=0.18)
    if glow:
        for k, (x, y) in enumerate(((-50, -6), (-30, -12), (-8, -16), (16, -18), (38, -15),
                                    (-38, 2), (-14, 4), (10, 4))):
            g.circle(x, y, 1.3, "#9ff0ff", class_="pulse",
                     style=f"animation-delay:-{k * 0.4:.1f}s")


def whale(c: Ctx, glow: bool) -> Layer:
    """One whale on its own, facing right."""
    g = Layer()
    _whale(g, c, c.haze(c.lit("#4a6a9a"), 0.55), c.haze(c.lit("#c4d8ec"), 0.55), glow)
    return g


def whales(L: Layer, c: Ctx) -> None:
    """A sky whale and her calf, far behind the islands, gliding during the overview."""
    haze = 0.55
    body = c.haze(c.lit("#4a6a9a"), haze)
    belly = c.haze(c.lit("#c4d8ec"), haze)
    mom, calf = Layer(), Layer()
    _whale(mom, c, body, belly, c.dark)
    _whale(calf, c, body, belly, c.dark)
    sx, sy = WHALE_FROM
    L.raw(f'<g transform="translate({sx} {sy})" opacity=".78"><g class="glide">'
          f'<g class="bob" style="animation-duration:5s">'
          f'<g transform="scale(.62)">{mom.svg()}</g>'
          f'<g transform="translate(-58 26) scale(.26)">{calf.svg()}</g>'
          "</g></g></g>")


def jelly(c: Ctx, scale: float = 1.0) -> Layer:
    """A small sky jelly: a pulsing bell with a scalloped rim and wavy trailing threads."""
    g = Layer()
    tint = "#ffb7e0" if not c.dark else "#ff9fd8"
    edge = "#bff4ff" if c.dark else "#ffffff"
    if c.dark:
        c.glow(g, 0, 0, 12 * scale, "#ff9fd8", 0.45)
    for k, dx in enumerate((-3.5, -1.2, 1.2, 3.5)):
        g.path(f"M{dx * scale:.1f} {2 * scale:.1f}q{-2 * scale:.1f} {4 * scale:.1f} 0 "
               f"{8 * scale:.1f}t0 {8 * scale:.1f}", stroke=tint, stroke_width=0.7 * scale,
               opacity=0.65, class_="sway", style=f"animation-delay:-{k * 0.6:.1f}s")
    bell = Layer()
    bell.path(f"M{-6 * scale:.1f} {2 * scale:.1f}C{-6 * scale:.1f} {-6 * scale:.1f} "
              f"{6 * scale:.1f} {-6 * scale:.1f} {6 * scale:.1f} {2 * scale:.1f}"
              f"q-1.5 {1.4 * scale:.1f} -3 0q-1.5 {1.4 * scale:.1f} -3 0"
              f"q-1.5 {1.4 * scale:.1f} -3 0q-1.5 {1.4 * scale:.1f} -3 0z",
              tint, opacity=0.75 if c.dark else 0.6)
    bell.path(f"M{-3.5 * scale:.1f} {-2 * scale:.1f}q{3.5 * scale:.1f} {-3 * scale:.1f} "
              f"{7 * scale:.1f} 0", stroke=edge, stroke_width=0.8 * scale, opacity=0.7)
    g.group(bell, class_="bell")
    return g


def jellies(L: Layer, c: Ctx, spots=JELLIES) -> None:
    """Sky jellies drifting up out of the clouds in the gaps between islands."""
    for k, (x, y, s) in enumerate(spots):
        L.raw(f'<g transform="translate({x} {y})"><g class="rise" '
              f'style="animation-delay:-{k * 2.9:.1f}s;animation-duration:{12 + k * 1.5:.1f}s">'
              f"{jelly(c, s).svg()}</g></g>")


def airship(c: Ctx) -> Layer:
    """A small cargo airship: a striped envelope with fins, a gondola with lit windows and a
    turning propeller. Faces right."""
    g = Layer()
    env = c.lit("#e8e0d0")
    stripe = c.lit("#e2574c")
    dark = c.lit("#4a4460")
    g.path("M-40 0l-8 -9h7l7 6zM-40 0l-8 9h7l7 -6z", stripe)
    g.ellipse(0, 0, 40, 11, env)
    g.path("M-38 -3H38", stroke=stripe, stroke_width=2.2)
    g.path("M-36 2H36", stroke=pal.shade(env, 0.85), stroke_width=1)
    g.ellipse(0, 3, 38, 8, "#000000", opacity=0.08)
    g.line(-10, 10, -12, 15, dark, 0.7)
    g.line(10, 10, 12, 15, dark, 0.7)
    g.rect(-14, 14, 28, 6, c.lit("#6a4a32"), rx=2)
    for k in range(4):
        g.rect(-11 + k * 6, 15.5, 3.4, 2.4, "#ffcf7a" if c.P["lamps"] else c.lit("#bfe4f8"))
    g.rect(-44, -1, 2, 2, dark)
    blades = Layer()
    blades.circle(-46, 0, 4, "none")
    blades.line(-46, -4, -46, 4, dark, 1)
    g.group(blades, class_="spin", style="animation-duration:.6s")
    if c.P["lamps"]:
        g.circle(40, 0, 1.2, "#ff5a4a", class_="av")
    return g
