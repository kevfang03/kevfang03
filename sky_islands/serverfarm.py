"""The west side of the ride: the Server Farm.

Terraces stepping up a hill, each lined with server racks whose lights blink, one rack per 30
contributions this year. Cables drape down the terrace walls like vines. A red barn turned
data centre stands beside a cooling-fan windmill, a satellite dish and an antenna crown the
hill, a robot scarecrow keeps watch, drones buzz about doing maintenance, and down by the
old wheat patch there is a help desk kiosk with someone in a headset taking questions.
"""

from __future__ import annotations

from . import palette as pal
from .context import Ctx
from .island import Shape, draw, waterfall
from .svg import Layer

RACKS_PER = 30  # contributions this year per server rack
MAX_RACKS = 15
LEDS = ("#5cf08a", "#3ad1ff", "#ffcf5a")
CABLES = ("#3d9bd1", "#e8b440", "#e2574c", "#5cbf6a")


def rack_count(contributions_year: int) -> int:
    return max(3, min(MAX_RACKS, contributions_year // RACKS_PER))


def _rack(L: Layer, c: Ctx, x: float, base: float, k: int) -> None:
    """A server cabinet with rows of blinking lights."""
    body, face = c.lit("#2a2f44"), c.lit("#3a4058")
    L.rect(x - 6, base - 19, 12, 19, body, rx=1)
    L.rect(x - 5, base - 18, 10, 17, face)
    L.line(x - 6, base - 19, x + 6, base - 19, c.P["rim"], 0.8, opacity=0.6)
    for row in range(5):
        y = base - 16 + row * 3.2
        L.line(x - 4, y + 1, x + 1, y + 1, c.lit("#262a3c"), 0.8)
        col = LEDS[(k + row) % 3]
        L.circle(x + 2.6, y + 1, 0.7, col, class_="fa" if (k + row) % 2 else "fb")
        if row % 2 == 0:
            L.circle(x + 4, y + 1, 0.6, LEDS[(k + row + 1) % 3], class_="av",
                     style=f"animation-delay:-{(k * 3 + row) % 7 * 0.23:.2f}s")
    if c.P["lamps"]:
        c.glow(L, x, base - 10, 10, "#3ad1ff", 0.35)


def _hill(s: Shape) -> list[tuple[float, float]]:
    """The hill's ridge as points, left to right."""
    x0, x1, top = s.x0 + 230, s.x1 - 30, s.top - 70
    p0, p1, p2 = (x0, s.ground(x0) + 2), (x0 + 120, top), ((x0 + x1) / 2, top + 6)
    p3, p4 = (x1 - 90, top + 10), (x1, s.ground(x1) + 2)
    pts = []
    for (a, m, b) in ((p0, p1, p2), (p2, p3, p4)):
        for k in range(21):
            u = k / 20
            pts.append(((1 - u) ** 2 * a[0] + 2 * (1 - u) * u * m[0] + u * u * b[0],
                        (1 - u) ** 2 * a[1] + 2 * (1 - u) * u * m[1] + u * u * b[1]))
    return pts


def _terraces(L: Layer, c: Ctx, s: Shape, racks: int) -> list[tuple[float, float, float]]:
    """A green hill cut into terraces, like rice terraces, with a row of racks along each.
    Returns (left, right, height) for each terrace, lowest first."""
    ridge = _hill(s)
    path = "M" + "L".join(f"{x:.0f} {y:.0f}" for x, y in ridge) + "Z"
    L.path(path, c.defs.linear(f"hill-{c.phase}", [(0, c.lit("#78b860")), (1, c.lit("#4f8a4a"))]))
    clip = c.defs.clip("hill", f'<path d="{path}"/>')
    rows = Layer()
    steps = []
    for k, y in enumerate((s.top - 6, s.top - 28, s.top - 50)):
        inside = [x for x, ry in ridge if ry < y - 6]
        if not inside:
            break
        a, b = min(inside) + 10, max(inside) - 10
        steps.append((a, b, y))
        # The terrace edge: a lit lip and a darker bank below it, with a cable or two.
        rows.path(f"M{a - 30} {y}Q{(a + b) / 2} {y + 4} {b + 30} {y}V{y + 22}H{a - 30}Z",
                  c.lit("#3f7040"), opacity=0.45)
        rows.path(f"M{a - 30} {y}Q{(a + b) / 2} {y + 4} {b + 30} {y}", stroke=c.lit("#a8d878"),
                  stroke_width=1.2, opacity=0.8)
        for j in range(3):
            cx = a + (b - a) * (j + 0.3 + c.rng.random() * 0.4) / 3
            rows.path(f"M{cx:.0f} {y + 1:.0f}q{c.rng.uniform(-6, 6):.0f} 10 "
                      f"{c.rng.uniform(-3, 3):.0f} 18", stroke=c.lit(CABLES[(j + k) % 4]),
                      stroke_width=1.2, stroke_linecap="round")
    L.group(rows, clip_path=clip)
    L.path("M" + "L".join(f"{x:.0f} {y:.0f}" for x, y in ridge), stroke=c.P["rim"],
           stroke_width=1.6, opacity=0.8)
    # Racks, spread along every row; the lowest row fills first.
    placed = 0
    for a, b, y in steps:
        share = -(-(racks - placed) // (len(steps) - steps.index((a, b, y))))
        n = min(share, int((b - a) // 20))
        if n <= 0:
            continue
        gap = (b - a) / n
        for j in range(n):
            _rack(L, c, a + gap * (j + 0.5), y + 1, placed + j)
        placed += n
        if placed >= racks:
            break
    return steps


def _barn(L: Layer, c: Ctx, x: float, base: float) -> None:
    """A red barn turned data centre: solar panels on the gambrel roof, vents, and a door
    glowing with racks inside."""
    red, roof = c.lit("#b5523f"), c.lit("#5a3436")
    w, h = 62, 34
    L.rect(x, base - h, w, h, red)
    L.path(f"M{x - 4} {base - h}L{x + 8} {base - h - 16}L{x + w / 2} {base - h - 24}"
           f"L{x + w - 8} {base - h - 16}L{x + w + 4} {base - h}Z", roof)
    L.path(f"M{x + 10} {base - h - 13}L{x + w / 2} {base - h - 20}L{x + w / 2} {base - h - 13}Z",
           c.lit("#2a3a6a"))
    L.path(f"M{x + 12} {base - h - 14}L{x + w / 2 - 2} {base - h - 18.5}", stroke=c.lit("#8ab0e8"),
           stroke_width=0.6)
    L.rect(x, base - h, w, 2, c.lit("#f2ead6"))
    door = "#3ad1ff" if c.P["lamps"] else c.lit("#9fd8f0")
    L.rect(x + w / 2 - 10, base - 22, 20, 22, door)
    for k in range(3):
        L.rect(x + w / 2 - 8 + k * 6, base - 20, 4, 20, c.lit("#2a2f44"))
        L.circle(x + w / 2 - 6 + k * 6, base - 16, 0.7, LEDS[k], class_="fa" if k % 2 else "fb")
    L.path(f"M{x + w / 2 - 10} {base - 22}h20M{x + w / 2} {base - 22}v22", stroke=c.lit("#f2ead6"),
           stroke_width=1)
    for vx in (x + 6, x + w - 16):
        for k in range(3):
            L.line(vx, base - h + 8 + k * 3, vx + 10, base - h + 8 + k * 3, c.lit("#7a3a32"), 1)
    if c.P["lamps"]:
        c.glow(L, x + w / 2, base - 10, 26, "#3ad1ff", 0.5)


def _fan_mill(L: Layer, c: Ctx, x: float, base: float) -> None:
    """A windmill whose sails are a big cooling fan in a round shroud."""
    steel = c.lit("#8a90a8")
    L.path(f"M{x - 7} {base}L{x - 2} {base - 46}M{x + 7} {base}L{x + 2} {base - 46}"
           f"M{x - 6} {base - 10}L{x + 5} {base - 22}M{x + 6} {base - 10}L{x - 5} {base - 22}"
           f"M{x - 4} {base - 26}L{x + 3} {base - 38}M{x + 4} {base - 26}L{x - 3} {base - 38}",
           stroke=steel, stroke_width=1.1)
    for dx in (-7, 7):
        L.rect(x + dx - 2.5, base - 1.5, 5, 2.5, c.lit("#9a9488"), rx=0.6)
    cy = base - 54
    L.circle(x, cy, 13, c.lit("#3a4058"), opacity=0.35)
    blades = Layer()
    # The spin turns the blades about the centre of their bounding box. Three blades are
    # lopsided, so an unfilled ring around the hub makes that centre the hub itself.
    blades.circle(x, cy, 12.5, "none")
    for a in (0, 120, 240):
        blades.path(f"M{x} {cy}q4 -6 1 -12q-4 4 -1 12z", c.lit("#dfe3ec"),
                    transform=f"rotate({a} {x} {cy})")
    L.group(blades, class_="spin")
    L.circle(x, cy, 13, "none", stroke=steel, stroke_width=1.6)
    L.circle(x, cy, 2, c.lit("#5a6480"))


def _robot_scarecrow(L: Layer, c: Ctx, x: float, base: float) -> None:
    pole = c.lit("#6a4a32")
    L.line(x, base, x, base - 26, pole, 1.4)
    L.line(x - 10, base - 18, x + 10, base - 18, pole, 1.2)
    L.rect(x - 4, base - 22, 8, 9, c.lit("#c9cede"), rx=1)
    L.rect(x - 2, base - 19, 4, 3, c.lit("#e2574c"))
    L.rect(x - 4, base - 31, 8, 7, c.lit("#dfe3ec"), rx=1.5)
    eye = "#7fe3ff"
    for dx in (-1.8, 1.8):
        L.circle(x + dx, base - 27.5, 0.9, eye)
    if c.dark:
        c.glow(L, x, base - 27.5, 7, eye, 0.7)
    L.path(f"M{x - 8} {base - 30}h16l-3 -2h-10z", c.lit("#e8c45a"))
    L.path(f"M{x - 4} {base - 32}l4 -6l4 6z", c.lit("#e8c45a"))
    L.line(x, base - 31, x, base - 36, c.lit("#5a6480"), 0.6)
    L.circle(x, base - 36.6, 0.8, "#ff5a4a", class_="av")


def _dish(L: Layer, c: Ctx, x: float, base: float) -> None:
    steel = c.lit("#c9cede")
    L.line(x, base, x, base - 10, c.lit("#5a6480"), 1.6)
    L.path(f"M{x - 10} {base - 18}a12 7 -30 0 0 18 8z", steel)
    L.line(x - 1, base - 13, x + 4, base - 21, c.lit("#5a6480"), 0.8)
    L.circle(x + 4.5, base - 21.5, 1.1, c.lit("#5a6480"))
    mast = x + 24
    L.line(mast, base, mast, base - 34, c.lit("#5a6480"), 1)
    for k in range(3):
        L.line(mast - 4 + k, base - 12 - k * 8, mast + 4 - k, base - 12 - k * 8, c.lit("#5a6480"), 0.8)
    L.circle(mast, base - 35, 1.2, "#ff5a4a", class_="av")


def _drones(L: Layer, c: Ctx, spots: list[tuple[float, float]]) -> None:
    for k, (x, y) in enumerate(spots):
        g = Layer()
        g.rect(x - 3, y - 1, 6, 2.4, c.lit("#3a4058"), rx=1)
        for dx in (-4, 4):
            g.line(x + dx * 0.6, y - 1, x + dx, y - 2.4, c.lit("#5a6480"), 0.6)
            g.ellipse(x + dx, y - 2.6, 2.4, 0.5, c.lit("#c9cede"), opacity=0.8)
        g.circle(x, y + 1.6, 0.6, LEDS[k % 3], class_="av")
        L.group(g, class_="bob", style=f"animation-duration:{1.6 + k * 0.4:.1f}s")


def _help_desk(L: Layer, c: Ctx, x: float, base: float) -> None:
    """A little help desk kiosk: someone in a headset behind the counter, a question-mark
    lamp, and a visitor waiting with their laptop."""
    teal = c.lit("#2f8a8a")
    awning = c.defs.pattern(f"desk-{c.phase}", 6, 6,
                            f'<rect width="3" height="6" fill="{c.lit("#f2ead6")}"/>'
                            f'<rect x="3" width="3" height="6" fill="{teal}"/>')
    L.rect(x - 15, base - 24, 2, 24, c.lit("#5a3f2e"))
    L.rect(x + 13, base - 24, 2, 24, c.lit("#5a3f2e"))
    L.rect(x - 16, base - 32, 32, 8, c.lit("#1f2a3a"), rx=1)
    L.text(x, base - 26.2, "HELP DESK", 4.6, "#7fe3ff" if c.P["lamps"] else c.lit("#bff4ff"),
           text_anchor="middle", font_weight="bold")
    L.poly([(x - 18, base - 24), (x + 18, base - 24), (x + 16, base - 19), (x - 16, base - 19)],
           awning)
    # The person on shift, with a headset and a screen.
    L.circle(x - 3, base - 15, 2.6, c.lit("#f2c9a8"))
    L.path(f"M{x - 5.8} {base - 15.6}a2.9 2.9 0 0 1 5.6 0", stroke=c.lit("#2a2440"),
           stroke_width=0.9)
    L.line(x - 5.6, base - 15, x - 5, base - 12.6, c.lit("#2a2440"), 0.6)
    L.rect(x - 6, base - 12, 6, 4, c.lit("#3d5bb0"), rx=1)
    L.rect(x + 2, base - 14, 7, 5, c.lit("#2a2f44"))
    L.rect(x + 2.6, base - 13.4, 5.8, 3.8, "#9fd8ff" if c.P["lamps"] else c.lit("#bfe4f8"))
    L.rect(x - 16, base - 9, 32, 9, c.lit("#d9c9a5"))
    L.line(x - 16, base - 9, x + 16, base - 9, c.lit("#8a6a4a"), 1)
    # The question-mark lamp.
    lx, ly = x + 22, base - 22
    L.line(lx, base, lx, ly + 4, c.lit("#1f1a2a"), 1)
    L.circle(lx, ly, 4, "#ffd27a" if c.P["lamps"] else c.lit("#f2e2b0"))
    L.text(lx, ly + 1.8, "?", 5.4, "#5a3a10", text_anchor="middle", font_weight="bold")
    if c.P["lamps"]:
        c.glow(L, lx, ly, 12, "#ffd27a", 0.7)
    # A visitor waiting with a laptop.
    vx = x - 26
    L.circle(vx, base - 11, 2.2, c.lit("#c98f6a"))
    L.rect(vx - 2.4, base - 9, 4.8, 6, c.lit("#e2574c"), rx=1)
    L.line(vx - 1, base - 3, vx - 1, base, c.lit("#2a2440"), 1)
    L.line(vx + 1, base - 3, vx + 1, base, c.lit("#2a2440"), 1)
    L.rect(vx + 1.6, base - 7, 4, 3, c.lit("#c9cede"))


def _wheat(L: Layer, c: Ctx, s: Shape, x0: float, x1: float) -> None:
    """The old farm's wheat patch, still growing beside the kiosk."""
    gold, dark = c.lit("#e0b44a"), c.lit("#b08a2a")
    for k in range(3):
        y = s.ground(x0) + 1 - k * 2.5
        x = x0 + k * 3
        while x < x1 - k * 3:
            L.path(f"M{x:.1f} {y:.1f}q-0.5 -4 0.6 -7", stroke=dark, stroke_width=0.7)
            L.ellipse(x + 0.6, y - 7.4, 0.9, 1.8, gold)
            x += 2.6
    fence = c.lit("#8a6a4a")
    x = x0 - 4
    while x < x1 + 4:
        b = s.ground(x) + 4
        L.line(x, b, x, b - 7, fence, 1)
        L.line(x, b - 5, x + 8, b - 5, fence, 0.8)
        x += 8


def server_farm(L: Layer, c: Ctx, s: Shape) -> None:
    draw(L, c, s, "fields", style="fields")
    waterfall(L, c, s, s.x1 - 40)
    racks = rack_count(c.w.stats.contributions_year)
    steps = _terraces(L, c, s, racks)
    _wheat(L, c, s, s.x0 + 30, s.x0 + 92)
    _help_desk(L, c, s.x0 + 136, s.ground(s.x0 + 136) + 3)
    bx = s.x0 + 168
    _barn(L, c, bx, s.ground(bx + 30) + 3)
    # In front of the hill's lower slope, standing on the flat island ground; the slope
    # itself falls away under one leg.
    _fan_mill(L, c, s.x0 + 244, s.ground(s.x0 + 244) + 3)
    top_a, top_b, top_y = steps[-1]
    _dish(L, c, top_b - 50, top_y - 2)
    _, mid_b, mid_y = steps[1]
    _robot_scarecrow(L, c, mid_b - 22, mid_y - 2)
    _drones(L, c, [(top_a + 30, top_y - 40), ((top_a + top_b) / 2, top_y - 62),
                   (mid_b - 60, mid_y - 46)])
    for x in (s.x1 - 70, s.x0 + 14):
        L.circle(x, s.ground(x) - 6, 6, pal.shade(c.P["grass"], 0.9))
