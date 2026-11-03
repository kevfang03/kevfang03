"""Sky, sun and moon, stars, clouds, things that fly, and weather on the glass."""

from __future__ import annotations

import math

from .. import palette as pal
from ..clock import fireworks_day
from .layout import GX0, GX1, GY0, GY1, HORIZON, OVERCAST, Ctx
from .svg import Layer

SUN_AT = {"dawn": (120, 258), "day": (470, 146), "dusk": (566, 262)}
MOON_AT = (548, 142)


def sky_colors(c: Ctx) -> list[str]:
    cols = list(c.P["sky"])
    if c.overcast:
        cols = [pal.mix(x, OVERCAST[c.phase], 0.6) for x in cols]
    return cols


def sky(L: Layer, c: Ctx) -> None:
    cols = sky_colors(c)
    stops = [(i / (len(cols) - 1), col) for i, col in enumerate(cols)]
    fill = c.defs.linear(f"sky-{c.phase}-{c.overcast}", stops)
    L.rect(GX0, GY0, GX1 - GX0, HORIZON + 24 - GY0, fill)


def sun_or_moon(L: Layer, c: Ctx) -> None:
    if c.phase == "night":
        _moon(L, c)
        return
    x, y = SUN_AT[c.phase]
    core = "#fff6d8" if c.phase == "day" else "#ffd98a"
    glow = c.defs.radial(
        f"sunglow-{c.phase}", [(0, core, 0.85), (0.25, core, 0.35), (1, core, 0)]
    )
    strength = 0.35 if c.overcast else 1
    L.circle(x, y, 90, glow, opacity=strength)
    if not c.overcast:
        L.circle(x, y, 15, core)


def _moon(L: Layer, c: Ctx) -> None:
    x, y = MOON_AT
    r = 13
    glow = c.defs.radial("moonglow", [(0, "#dfe8ff", 0.35), (1, "#dfe8ff", 0)])
    L.circle(x, y, 60, glow, opacity=0.5 if c.overcast else 1)
    if c.overcast:
        return
    body = Layer()
    body.circle(x, y, r, "#f3eed8")
    for dx, dy, rr in ((-4, -3, 2.6), (3, 4, 2), (5, -4, 1.4), (-2, 6, 1.2)):
        body.circle(x + dx, y + dy, rr, "#ddd5b8")
    p = c.s.moon
    # The unlit part is a disc of night sky slid across the moon.
    if p < 0.5:
        off = -2 * r * (p / 0.5)
    else:
        off = 2 * r * ((1 - p) / 0.5)
    if abs(off) < 2 * r - 0.5:
        body.circle(x + off, y, r + 0.4, c.P["sky"][1], opacity=0.93)
    clip = c.defs.clip("moonclip", f'<circle cx="{x}" cy="{y}" r="{r}"/>')
    L.group(body, clip_path=clip)


def stars(L: Layer, c: Ctx) -> None:
    if c.phase not in ("night", "dawn") or c.overcast:
        return
    n = 90 if c.phase == "night" else 25
    still, twinkle = Layer(), Layer()
    mx, my = MOON_AT
    for i in range(n):
        x = c.rng.uniform(GX0, GX1)
        y = c.rng.uniform(GY0 + 2, HORIZON - 70 if c.phase == "night" else GY0 + 60)
        if math.hypot(x - mx, y - my) < 26:
            continue
        r = c.rng.choice((0.5, 0.6, 0.7, 0.9, 1.1))
        col = c.rng.choice(("#ffffff", "#dfe8ff", "#fff1c9"))
        if i % 6 == 0:
            twinkle.circle(x, y, r + 0.2, col, class_="tw",
                           style=f"animation-delay:-{c.rng.uniform(0, 4):.1f}s")
        else:
            still.circle(x, y, r, col, opacity=0.55 if c.phase == "dawn" else 0.85)
    L.add(still)
    L.add(twinkle)


def _cloud(L: Layer, x: float, y: float, scale: float, light: str, dark: str, op: float) -> None:
    puffs = ((0, 0, 22, 9), (-18, 3, 15, 7), (18, 2, 17, 8), (6, -6, 14, 9), (-8, -4, 11, 8))
    g = Layer()
    for dx, dy, rx, ry in puffs:
        g.ellipse(x + dx * scale, y + 3 * scale + dy * scale, rx * scale, ry * scale, dark)
    for dx, dy, rx, ry in puffs:
        g.ellipse(x + dx * scale, y + dy * scale, rx * scale * 0.95, ry * scale * 0.85, light)
    L.group(g, opacity=op)


def clouds(L: Layer, c: Ctx) -> None:
    light, dark = c.P["cloud"]
    if c.overcast:
        light = pal.mix(light, OVERCAST[c.phase], 0.4)
        dark = pal.mix(dark, OVERCAST[c.phase], 0.4)
    count = {"clear": 3, "cloudy": 9, "rain": 11, "snow": 10}[c.s.weather]
    if c.phase == "night" and c.s.weather == "clear":
        count = 1
    drift = Layer()
    for i in range(count):
        x = c.rng.uniform(GX0 + 10, GX1 - 10)
        y = c.rng.uniform(GY0 + 14, GY0 + (120 if c.overcast else 90))
        scale = c.rng.uniform(0.8, 1.6) if c.overcast else c.rng.uniform(0.6, 1.1)
        _cloud(drift, x, y, scale, light, dark, 0.95 if c.overcast else 0.85)
        if i == count // 2:
            L.group(drift, class_="cloud")
            drift = Layer()
    L.group(drift, class_="cloud", style="animation-delay:-20s")


def plane(L: Layer, c: Ctx) -> None:
    if c.s.weather in ("rain", "snow"):
        return
    p = Layer()
    body = c.out("#d9dee6") if not c.dark else "#2a3350"
    p.path("M0 0h16l4 -2h2l-2 3h-20z", body)
    p.path("M7 0l-3 4h3l4 -4z", body)
    p.path("M15 -1l2 -4h2l-1 4z", body)
    if c.dark:
        p.circle(1, 1, 1, "#ff4d4d", class_="av")
        p.circle(20, -1, 0.9, "#ffffff", class_="av", style="animation-delay:-.8s")
    L.group(p, class_="plane", transform=f"translate({GX0} {GY0 + 34})")


def birds(L: Layer, c: Ctx) -> None:
    if c.dark or c.s.weather in ("rain", "snow"):
        return
    b = Layer()
    col = c.out("#3b4250")
    for dx, dy in ((0, 0), (10, 4), (18, -2)):
        b.path(f"M{dx} {dy}q3 -3 5 0q2 -3 5 0", stroke=col, stroke_width=1.1)
    L.group(b, class_="bird", transform=f"translate({GX0} {GY0 + 70})")


def fireworks(L: Layer, c: Ctx) -> None:
    if c.phase != "night" or not fireworks_day(c.s.when.date()):
        return
    cols = ("#ff6b6b", "#ffd36b", "#6bd8ff", "#c38bff", "#8aff8a")
    for i in range(5):
        x = c.rng.uniform(GX0 + 60, GX1 - 60)
        y = c.rng.uniform(GY0 + 30, GY0 + 110)
        col = cols[i % len(cols)]
        burst = Layer()
        for k in range(14):
            a = k / 14 * math.tau
            r1, r2 = 6, c.rng.uniform(16, 24)
            burst.line(x + math.cos(a) * r1, y + math.sin(a) * r1,
                       x + math.cos(a) * r2, y + math.sin(a) * r2, col, 1.4,
                       stroke_linecap="round")
            burst.circle(x + math.cos(a) * (r2 + 2), y + math.sin(a) * (r2 + 2), 1.1, col)
        burst.circle(x, y, 3, "#ffffff")
        L.group(burst, class_="fw", style=f"animation-delay:-{i * 0.7:.1f}s")


def weather(L: Layer, c: Ctx) -> None:
    w = c.s.weather
    if w == "rain":
        for layer in range(2):
            drops = Layer()
            for _ in range(70):
                x = c.rng.uniform(GX0, GX1 + 20)
                y = c.rng.uniform(GY0 - 20, GY1)
                drops.line(x, y, x - 3, y + 11, "#c9d6ea", 1, opacity=0.45, stroke_linecap="round")
            L.group(drops, class_="rain", style=f"animation-delay:-{layer * 0.22:.2f}s")
        # Drops running down the glass.
        g = Layer()
        for _ in range(26):
            x = c.rng.uniform(GX0 + 4, GX1 - 4)
            y = c.rng.uniform(GY0 + 10, GY1 - 20)
            g.path(f"M{x:.1f} {y:.1f}q-1 6 0 {c.rng.uniform(6, 14):.1f}", stroke="#dfe8f5",
                   stroke_width=1.2, opacity=0.4, stroke_linecap="round")
            g.circle(x, y, 1.4, "#e8f0fa", opacity=0.55)
        L.add(g)
    elif w == "snow":
        for layer in range(3):
            flakes = Layer()
            for _ in range(45):
                x = c.rng.uniform(GX0, GX1)
                y = c.rng.uniform(GY0, GY1)
                flakes.circle(x, y, c.rng.choice((1, 1.3, 1.7)), "#ffffff", opacity=0.9)
            L.group(flakes, class_="snow", style=f"animation-delay:-{layer * 1.6:.1f}s")


def glass_glints(L: Layer, c: Ctx) -> None:
    """Faint diagonal reflections on the window glass."""
    op = 0.08 if c.dark else 0.13
    g = Layer()
    for x0, w in ((GX0 + 40, 26), (GX0 + 80, 9), (GX1 - 150, 30), (GX1 - 112, 8)):
        g.poly([(x0, GY0), (x0 + w, GY0), (x0 + w - 70, GY1), (x0 - 70, GY1)], "#ffffff")
    L.group(g, opacity=op)
