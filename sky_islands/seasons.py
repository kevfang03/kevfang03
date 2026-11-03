"""What each season adds on top of the trees, crops and flowers that already change colour:

- **Winter:** snow on every island's top, with icicles hanging off the lip.
- **Spring:** blossom petals drifting across the sky.
- **Summer:** butterflies over the town by day.
- **Fall:** leaves tumbling down.

Petals and leaves are pattern tiles slid by CSS, like the rain, so they cost little. They
stay away in rain and snow, which have the sky to themselves.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .clock import season
from .context import Ctx
from .svg import Layer
from .weather import _sheet

if TYPE_CHECKING:  # the island module draws the snow cap, so it imports this one
    from .island import Shape

CSS = (
    "@keyframes petals1{to{transform:translate(-80px,160px)}}"
    "@keyframes petals2{to{transform:translate(-110px,220px)}}"
    ".petals1{animation:petals1 14s linear infinite}.petals2{animation:petals2 21s linear infinite}"
    "@keyframes flap{from{transform:scaleX(1)}to{transform:scaleX(.2)}}"
    ".flap{animation:flap .22s ease-in-out infinite alternate;transform-box:fill-box;"
    "transform-origin:center}"
)

PETALS = ("#ffc9dc", "#ffb7d0", "#ffe0ea", "#ffffff")
LEAVES = ("#e8873a", "#c0552e", "#e8b23a", "#a8432a")


def snow_cap(L: Layer, c: Ctx, ridge: list[tuple[float, float]], haze: float) -> None:
    """A layer of snow along an island's top and icicles under its grassy lip (winter only)."""
    if season(c.w.when.month) != "winter":
        return
    snow = c.haze(c.lit("#eef2fb"), haze)
    # One thick line along the ridge (every other point is plenty) costs far less than
    # outlining a band, and there are many islands.
    pts = [*ridge[::2], ridge[-1]]
    L.path("M" + "L".join(f"{x:.0f} {y + 2:.0f}" for x, y in pts), stroke=snow,
           stroke_width=5, stroke_linejoin="round", stroke_linecap="round")
    ice = c.haze(c.lit("#d6ecff"), haze)
    drips = []
    for k, (x, y) in enumerate(ridge[3:-3:3]):
        drips.append(f"M{x - 2:.1f} {y + 13:.1f}l2 {4 + (k * 7) % 6}l2 -{4 + (k * 7) % 6}z")
    L.path("".join(drips), ice, opacity=0.85)


def overlay(L: Layer, c: Ctx) -> None:
    """Petals in spring and leaves in fall, across the whole frame."""
    if c.w.weather in ("rain", "storm", "snow"):
        return
    now = season(c.w.when.month)
    if now not in ("spring", "fall"):
        return
    rng = c.rng
    cols = PETALS if now == "spring" else LEAVES
    for name, tile, n, size in (("petals1", 160, 6, 1.0), ("petals2", 220, 4, 1.5)):
        bits = []
        for k in range(n):
            x, y, turn = rng.uniform(0, tile), rng.uniform(0, tile), rng.uniform(0, 180)
            col = cols[k % len(cols)]
            if now == "spring":
                shape = f'<ellipse rx="{2.2 * size:.1f}" ry="{1.2 * size:.1f}" fill="{col}"/>'
            else:
                shape = (f'<path d="M0 0q{3 * size:.1f} -{4 * size:.1f} {6 * size:.1f} 0'
                         f'q-{3 * size:.1f} {4 * size:.1f} -{6 * size:.1f} 0z" fill="{col}"/>')
            bits.append(f'<g transform="translate({x:.0f} {y:.0f}) rotate({turn:.0f})">'
                        f"{shape}</g>")
        pattern = c.defs.pattern(f"{name}-{now}", tile, tile, "".join(bits))
        _sheet(L, pattern, tile, name, opacity=0.85)


def butterflies(L: Layer, c: Ctx, s: Shape) -> None:
    """A few butterflies fluttering over the town on summer days."""
    if season(c.w.when.month) != "summer" or c.dark or c.w.weather != "clear":
        return
    for k, (x, col) in enumerate(((s.x0 + 90, "#ffd27a"), (s.cx - 40, "#9fd8ff"),
                                  (s.cx + 120, "#ff9fd8"), (s.x1 - 70, "#ffffff"))):
        y = s.ground(x) - 26 - (k % 2) * 14
        wings = Layer()
        wings.path(f"M{x} {y}q-4 -5 -5 -1q0 3 5 1zM{x} {y}q4 -5 5 -1q0 3 -5 1z", col)
        wings.path(f"M{x} {y}q-3 4 -1 4zM{x} {y}q3 4 1 4z", col, opacity=0.8)
        b = Layer()
        b.group(wings, class_="flap", style=f"animation-delay:-{k * 0.07:.2f}s")
        b.line(x, y - 1.5, x, y + 2.5, "#2a2440", 0.7)
        L.group(b, class_="bob", style=f"animation-duration:{1.6 + k * 0.3:.1f}s")
