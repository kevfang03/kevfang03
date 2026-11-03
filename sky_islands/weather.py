"""The weather over the whole frame: an overcast tint, rain, storms, snow and fog.

Rain and snow are tiles of streaks and flakes, repeated with an SVG pattern and slid along
by CSS, so a whole sky of them costs a few hundred bytes. They sit over both the overview
and the ride, under the HUD.
"""

from __future__ import annotations

from .context import Ctx, H, W
from .svg import Layer

CSS = (
    "@keyframes rain1{to{transform:translate(-24px,96px)}}"
    "@keyframes rain2{to{transform:translate(-36px,144px)}}"
    "@keyframes snow1{to{transform:translate(18px,120px)}}"
    "@keyframes snow2{to{transform:translate(-14px,90px)}}"
    "@keyframes flash{0%,61%,64%,66%,100%{opacity:0}62%{opacity:.55}65%{opacity:.35}}"
    ".rain1{animation:rain1 .55s linear infinite}.rain2{animation:rain2 .42s linear infinite}"
    ".snow1{animation:snow1 7s linear infinite}.snow2{animation:snow2 11s linear infinite}"
    ".flash{animation:flash 9s linear infinite}"
)

# How much the sky greys over, by weather, for daylight and for the dark phases.
TINT = {
    "cloudy": (("#7a8098", 0.22), ("#121424", 0.25)),
    "rain": (("#5a6480", 0.32), ("#0c0e1c", 0.35)),
    "storm": (("#3a4058", 0.42), ("#06070f", 0.42)),
    "snow": (("#c8cede", 0.18), ("#1a1e30", 0.22)),
    "fog": (("#d0d4e0", 0.2), ("#2a2e40", 0.25)),
}


def _streaks(n: int, size: int, length: float, seed) -> str:
    """A tile of slanted rain streaks."""
    out = []
    for _ in range(n):
        x, y = seed.uniform(0, size), seed.uniform(0, size)
        ln = seed.uniform(length * 0.6, length)
        out.append(f"M{x:.0f} {y:.0f}l{-ln / 4:.1f} {ln:.1f}")
    return "".join(out)


def _flakes(n: int, size: int, r: tuple[float, float], seed) -> str:
    return "".join(f'<circle cx="{seed.uniform(0, size):.0f}" cy="{seed.uniform(0, size):.0f}" '
                   f'r="{seed.uniform(*r):.1f}"/>' for _ in range(n))


def _sheet(L: Layer, fill: str, tile: int, cls: str, **a) -> None:
    """A tile-filled sheet one tile bigger than the frame each way, so sliding it by one
    tile loops without a seam."""
    g = Layer()
    g.rect(-tile, -tile, W + 2 * tile, H + 2 * tile, fill, **a)
    L.group(g, class_=cls)


def overlay(L: Layer, c: Ctx) -> None:
    kind = c.w.weather
    if kind not in TINT:
        return
    (day_col, day_op), (dark_col, dark_op) = TINT[kind]
    col, op = (dark_col, dark_op) if c.dark else (day_col, day_op)
    L.rect(0, 0, W, H, col, opacity=op)
    rng = c.rng
    if kind in ("rain", "storm"):
        streak = "#c8d4ec" if not c.dark else "#9aa8c8"
        for name, tile, n, ln, width, op in (("rain1", 96, 14, 14, 0.8, 0.45),
                                             ("rain2", 144, 10, 22, 1.1, 0.55)):
            if kind == "rain" and name == "rain2":
                n = 6
            body = (f'<path d="{_streaks(n, tile, ln, rng)}" stroke="{streak}" '
                    f'stroke-width="{width}" stroke-linecap="round" fill="none"/>')
            _sheet(L, c.defs.pattern(f"{name}-{kind}", tile, tile, body), tile, name, opacity=op)
        if kind == "storm":
            L.rect(0, 0, W, H, "#eef2ff", opacity=0, class_="flash")
    elif kind == "snow":
        for name, tile, n, r, op in (("snow1", 120, 9, (1.2, 2.2), 0.9),
                                     ("snow2", 90, 8, (0.6, 1.2), 0.7)):
            body = f'<g fill="#ffffff">{_flakes(n, tile, r, rng)}</g>'
            _sheet(L, c.defs.pattern(name, tile, tile, body), tile, name, opacity=op)
    elif kind == "fog":
        haze = "#e4e8f0" if not c.dark else "#8a90a8"
        for k, (y, rx, op) in enumerate(((330, 560, 0.45), (420, 620, 0.55), (250, 480, 0.3))):
            L.ellipse(W / 2 + (k - 1) * 120, y, rx, 46, haze, opacity=op,
                      filter=c.defs.blur(18), class_="drift",
                      style=f"animation-delay:-{k * 9}s")
