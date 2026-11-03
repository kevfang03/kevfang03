"""What each season adds on top of the trees, crops and flowers that already change colour:

- **Winter:** snow on every island's top, with icicles hanging off the lip.
- **Spring:** blossom petals drifting down from the town's trees.
- **Summer:** butterflies over the town by day.
- **Fall:** leaves tumbling down from the trees.

Petals and leaves are a handful of single pieces, each on its own clock; they stay away in
rain and snow, which have the sky to themselves.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .clock import season
from .context import Ctx
from .svg import Layer

if TYPE_CHECKING:  # the island module draws the snow cap, so it imports this one
    from .island import Shape

CSS = (
    "@keyframes drop{0%{transform:translate(0,0) rotate(0deg);opacity:0}12%{opacity:1}"
    "35%{transform:translate(6px,13px) rotate(120deg)}65%{transform:translate(-5px,27px) "
    "rotate(230deg)}82%{opacity:1}100%{transform:translate(4px,40px) rotate(340deg);opacity:0}}"
    ".drop{animation:drop 8s ease-in-out infinite;transform-box:fill-box;transform-origin:center}"
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


def fallers(L: Layer, c: Ctx, s: Shape) -> None:
    """A few leaves (fall) or blossom petals (spring) drifting down from the town's trees,
    each tumbling and swaying on its own clock. Each fades in at the branch and out before it
    lands, so the loop never shows them jump back up. Kept to a handful on purpose: a
    full-frame sheet of them crowded the picture and made every frame heavier to draw."""
    if c.w.weather in ("rain", "storm", "snow"):
        return
    now = season(c.w.when.month)
    if now not in ("spring", "fall"):
        return
    cols = PETALS if now == "spring" else LEAVES
    for k in range(9):
        x = s.x0 + 70 + (s.w - 140) * ((k * 41) % 100) / 100
        y = s.ground(x) - 30 - (k % 3) * 6
        col = cols[k % len(cols)]
        if now == "spring":
            shape = f'<ellipse rx="2" ry="1.1" fill="{col}"/>'
        else:
            shape = f'<path d="M-3 0q1.5 -2.4 3 -2.4q1.5 0 3 2.4q-1.5 2.4 -3 2.4q-1.5 0 -3 -2.4z" fill="{col}"/>'
        L.raw(f'<g transform="translate({x:.0f} {y:.0f})"><g class="drop" '
              f'style="animation-duration:{7 + k % 4 * 1.3:.1f}s;animation-delay:-{k * 1.7:.1f}s">'
              f"{shape}</g></g>")


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
