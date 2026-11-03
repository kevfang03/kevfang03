"""The sky behind the islands: light, stars, sun or moon, clouds at every depth, birds,
and the sea of clouds below everything."""

from __future__ import annotations

import math

from . import palette as pal
from .context import Ctx, H, W
from .svg import Layer

MOON_AT = (860, 92)


def light_x(c: Ctx) -> float:
    """Where the light comes from, so clouds and rocks can be lit on that side."""
    return MOON_AT[0] if c.P["sun"] is None else c.P["sun"][0]


def sky(L: Layer, c: Ctx) -> None:
    cols = c.P["sky"]
    L.rect(0, 0, W, H, c.defs.linear(f"sky-{c.phase}",
                                     [(i / (len(cols) - 1), col) for i, col in enumerate(cols)]))


def stars(L: Layer, c: Ctx) -> None:
    n = c.P["stars"]
    if not n:
        return
    if c.phase == "night":
        L.ellipse(520, 200, 560, 64, c.defs.linear(
            "milkyway", [(0, "#b9a8ff", 0), (0.5, "#d9ccff", 0.18), (1, "#b9a8ff", 0)], x2=1, y2=0),
            transform="rotate(-22 520 200)", filter=c.defs.blur(6))
    still, tw = Layer(), Layer()
    for i in range(n):
        x, y = c.rng.uniform(0, W), c.rng.uniform(0, 260)
        r = c.rng.choice((0.5, 0.7, 0.9, 1.2))
        if i % 6 == 0:
            tw.circle(x, y, r + 0.2, "#ffffff", class_="tw",
                      style=f"animation-delay:-{c.rng.uniform(0, 4):.1f}s")
        else:
            still.circle(x, y, r, c.rng.choice(("#ffffff", "#ffeccc", "#dfe7ff")),
                         opacity=round(0.9 * (1 - y / 320), 2))
    L.add(still)
    L.add(tw)
    tail = c.defs.linear("startail", [(0, "#ffffff", 1), (1, "#ffffff", 0)], x2=1, y2=0)
    for k, (x, y) in enumerate(((640, 60), (300, 44), (520, 120))):
        s = Layer()
        s.line(x, y, x + 70, y - 32, tail, 1.6, stroke_linecap="round")
        s.circle(x, y, 1.5, "#ffffff")
        L.group(s, class_="shoot", style=f"animation-delay:-{k * 4 + 1}s;"
                                         f"animation-duration:{9 + k * 5}s")


def sun_or_moon(L: Layer, c: Ctx) -> None:
    if c.P["sun"] is None:
        x, y = MOON_AT
        c.glow(L, x, y, 90, "#fff0dc", 0.35)
        L.circle(x, y, 17, "#fff0dc")
        for dx, dy, r in ((-5, -4, 3), (4, 5, 2.4), (6, -5, 1.6)):
            L.circle(x + dx, y + dy, r, "#e8dcc0", opacity=0.7)
        p = c.w.moon
        off = -34 * (p / 0.5) if p < 0.5 else 34 * ((1 - p) / 0.5)
        if abs(off) < 33:
            clip = c.defs.clip("moon", f'<circle cx="{x}" cy="{y}" r="17"/>')
            L.raw(f'<g clip-path="{clip}"><circle cx="{x + off:.1f}" cy="{y}" r="17.5" '
                  f'fill="{c.P["sky"][0]}" opacity=".94"/></g>')
        return
    x, y, col = c.P["sun"]
    c.glow(L, x, y, 460 if c.phase in ("dusk", "golden") else 280, col, 0.6)
    if c.phase != "dusk":
        c.glow(L, x, y, 60, "#ffffff", 0.6)
        L.circle(x, y, 26 if c.phase == "golden" else 20, col)
    if c.phase in ("dusk", "golden", "dawn"):
        ray = c.defs.linear(f"ray-{c.phase}", [(0, col, 0), (1, col, 0.12)], x2=0, y2=0)
        for a, w in ((-40, 44), (-18, 26), (4, 36), (26, 22), (44, 30)):
            tx = x + math.tan(math.radians(a)) * y
            L.poly([(x, y), (tx - w, 0), (tx + w, 0)], ray, opacity=0.6)


def cumulus(L: Layer, c: Ctx, x: float, y: float, w: float, h: float,
            body: str, shadow: str, light: str, op: float = 1.0) -> None:
    """A billowing cloud: flat shadowed base, many rounded billows, and soft light on the
    tops facing the sun or moon."""
    n = max(4, int(w / 10))
    side = 1 if light_x(c) > x else -1
    bumps = []
    for i in range(n):
        t = (i + 0.5) / n
        r = h * (0.26 + 0.5 * math.sin(math.pi * t) ** 0.7) * c.rng.uniform(0.8, 1.15)
        bumps.append((x - w / 2 + t * w + c.rng.uniform(-3, 3), y - r * 0.3, r))
    for bx, by, r in bumps[1:-1:2]:  # a second, smaller tier of billows on top
        rr = r * c.rng.uniform(0.45, 0.6)
        bumps.append((bx + c.rng.uniform(-r * 0.3, r * 0.3), by - r * 0.55, rr))
    # Billows of one tone share a group's fill and use whole pixels, keeping the file small.
    g = Layer()
    g.ellipse(x, y + h * 0.1, w * 0.54, h * 0.26, shadow)
    for tone, discs, extra in (
        (shadow, [(bx, by + r * 0.22, r) for bx, by, r in bumps], {}),
        (body, [(bx, by, r * 0.9) for bx, by, r in bumps], {}),
        (light, [(bx + side * r * 0.25, by - r * 0.3, r * 0.6) for bx, by, r in bumps],
         {"filter": c.defs.blur(max(1.0, h * 0.06)), "opacity": 0.7}),
    ):
        g.raw(f'<g fill="{tone}"' + "".join(f' {k}="{v}"' for k, v in extra.items()) + ">"
              + "".join(f'<circle cx="{cx:.0f}" cy="{cy:.0f}" r="{r:.0f}"/>'
                        for cx, cy, r in discs) + "</g>")
    L.group(g, opacity=op if op < 1 else None)


def _cloud_tones(c: Ctx, haze: float) -> tuple[str, str, str]:
    body, top = c.P["cloud"]
    deep = "#0a0818" if c.dark else pal.shade(body, 0.72)
    body = c.haze(body, haze)
    return body, c.haze(pal.mix(body, deep, 0.45), haze), c.haze(top, haze * 0.6)


def sky_clouds(L: Layer, c: Ctx) -> None:
    """A few clouds hanging mid-sky, far behind the islands, plus high streaks at dusk."""
    if c.phase in ("dusk", "golden", "dawn"):
        streak = pal.mix(c.P["cloud"][1], "#ffffff", 0.2)
        for _ in range(6):
            x, y = c.rng.uniform(0, W), c.rng.uniform(70, 190)
            L.ellipse(x, y, c.rng.uniform(80, 180), c.rng.uniform(2, 4), streak, opacity=0.35,
                      transform=f"rotate({c.rng.uniform(-4, 4):.1f} {x:.0f} {y:.0f})")
    g = Layer()
    body, shadow, light = _cloud_tones(c, 0.55)
    for x, y, w in ((210, 250, 150), (640, 228, 120), (900, 270, 170)):
        cumulus(g, c, x, y, w, w * 0.36, body, shadow, light, 0.85)
    L.group(g, class_="drift", filter=c.defs.blur(1.2))


def _billows(c: Ctx, x0: float, x1: float, y: float, size: float) -> str:
    """One path holding a bank of overlapping billows: big ones along the bottom, smaller
    ones heaped on top of them, and a flat base, so its outline reads as one cloud bank."""
    parts = []
    x = x0
    while x < x1:
        r = c.rng.uniform(30, 70) * size
        h = r * c.rng.uniform(0.55, 0.8)
        cy = y + c.rng.uniform(-6, 8) * size
        parts.append((x, cy, r, h))
        if c.rng.random() < 0.35:  # a smaller billow heaped on top
            rr = r * c.rng.uniform(0.4, 0.6)
            parts.append((x + c.rng.uniform(-r * 0.4, r * 0.4), cy - h * 0.6, rr, rr * 0.75))
        x += r * c.rng.uniform(1.1, 1.5)
    d = "".join(f"M{px - r:.0f} {py:.0f}a{r:.0f} {h:.0f} 0 1 0 {2 * r:.0f} 0"
                f"a{r:.0f} {h:.0f} 0 1 0 {-2 * r:.0f} 0" for px, py, r, h in parts)
    # The base starts a little below the billows' centres, so its flat top never shows
    # between two billows. It is drawn anticlockwise like the billows; drawn the other way,
    # the overlaps would cancel out and leave holes.
    return d + f"M{x0:.0f} {y + 4 * size:.0f}V{y + 90 * size:.0f}H{x1:.0f}V{y + 4 * size:.0f}Z"


def cloud_sea(L: Layer, c: Ctx) -> None:
    """Banks of cloud below the islands, back to front: far ones small and hazy, near ones
    big. Each bank is lit from the top and shaded underneath, with a softer fold inside it."""
    body, _, _ = _cloud_tones(c, 0)
    deep = "#0a0818" if c.dark else pal.shade(body, 0.7)
    L.rect(0, 470, W, H - 470, c.defs.linear(f"seabase-{c.phase}",
                                             [(0, pal.mix(body, deep, 0.3)), (1, deep)]))
    rows = ((424, 0.45, 0.55, 1.6), (446, 0.65, 0.35, 0.9), (474, 0.85, 0.15, 0.5), (508, 1.05, 0.0, 0.4))
    for k, (y, size, haze, blur) in enumerate(rows):
        body, shadow, light = _cloud_tones(c, haze)
        bank = _billows(c, -80, W + 80, y, size)
        row = Layer()
        row.path(bank, c.defs.linear(f"bank{k}-{c.phase}", [(0, light), (0.3, body), (1, shadow)]))
        row.path(_billows(c, -40, W + 60, y + 34 * size, size * 0.7), shadow, opacity=0.3)
        L.group(row, filter=c.defs.blur(blur) if blur else None)
        L.ellipse(W / 2, y - 4, 620, 12, c.P["haze"], opacity=0.18, filter=c.defs.blur(6))


def birds(L: Layer, c: Ctx) -> None:
    if c.phase == "night":
        return
    col = pal.shade(c.P["sky"][1], 0.6)
    g = Layer()
    for dx, dy in ((0, 0), (14, 6), (26, -3), (38, 8), (50, 2)):
        g.path(f"M{dx} {150 + dy}q3 -3 5 0q2 -3 5 0", stroke=col, stroke_width=1.1)
    L.group(g, class_="flock")
