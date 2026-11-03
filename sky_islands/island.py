"""Floating islands seen from the side: a grassy ridge, rock tapering below with roots,
moss and crystals, a waterfall, small drifting rocks, and distant islands in the haze."""

from __future__ import annotations

import math
from dataclasses import dataclass

from . import palette as pal
from .context import Ctx
from .svg import Layer


@dataclass(frozen=True)
class Shape:
    cx: float
    top: float  # height of the ridge at its highest point
    w: float
    depth: float  # from the ridge down to the tip of the rock

    @property
    def x0(self) -> float:
        return self.cx - self.w / 2

    @property
    def x1(self) -> float:
        return self.cx + self.w / 2

    def ground(self, x: float) -> float:
        """Height of the ridge at x: flat in the middle, dropping toward the edges."""
        t = (x - self.cx) / (self.w / 2)
        return self.top + 14 * t ** 4


HOME = Shape(cx=520, top=274, w=500, depth=200)
PHILLY = Shape(cx=134, top=250, w=232, depth=160)
STADIUM = Shape(cx=888, top=262, w=184, depth=150)


def _ridge(s: Shape, n: int = 40) -> list[tuple[float, float]]:
    return [(s.x0 + s.w * k / n, s.ground(s.x0 + s.w * k / n)) for k in range(n + 1)]


# Each island's rock: four bands of colour from the grass down, how jagged its underside
# is, and how many stalactites hang from it.
STYLES: dict[str, tuple[tuple[str, str, str, str], float, int]] = {
    "town": (("#d9a87e", "#bf8a66", "#9c6c58", "#74504c"), 0.3, 3),
    "city": (("#b0786a", "#8f5e54", "#6f4a4c", "#4e3846"), 0.2, 2),
    "stadium": (("#93a0bc", "#76829f", "#5a6482", "#3e4664"), 0.15, 2),
    "wild": (("#6a948a", "#4d7670", "#365a56", "#223a3c"), 0.9, 9),
    "fields": (("#b98a50", "#98683e", "#7a5036", "#563832"), 0.3, 3),
    "starport": (("#8e9ab6", "#717d9a", "#56607c", "#3a425c"), 0.2, 2),
    "shrine": (("#b0a28c", "#8f8270", "#6e6256", "#4c4244"), 0.5, 4),
}


def _bands(c: Ctx, style: str, haze: float) -> list[str]:
    if style in STYLES:
        cols = STYLES[style][0]
        rock0 = c.P["rock"][0]
        return [c.haze(c.lit(pal.mix(col, rock0, 0.3)), haze) for col in cols]
    r0, r1 = c.P["rock"]
    return [c.haze(pal.mix(r0, r1, k / 3), haze) for k in range(4)]


def _outline(s: Shape, c: Ctx, style: str) -> tuple[str, str]:
    """The island's outline, and the underside alone (for the light bouncing off the clouds).
    The sides drop steeply for half the depth (room for the railway), then the rock tapers
    to a point with a few stalactites hanging from it."""
    jag, spikes = STYLES.get(style, ((), 0.3, 3))[1:]
    ridge = _ridge(s)
    wall = s.depth * 0.5
    inset = s.w * 0.04
    n = max(14, int(s.w / 12))
    under = []
    for k in range(n + 1):
        t = 1 - 2 * k / n
        x = s.cx + t * (s.w / 2 - inset)
        d = wall + (s.depth - wall) * (1 - abs(t) ** 1.7) ** 1.25
        if 0 < k < n:
            d += c.rng.uniform(-1, 1) * jag * 7
        under.append((x, s.top + d))
    tips = set(c.rng.sample(range(1, n - 1), min(spikes, n - 2)))
    pts = []
    for k, (x, y) in enumerate(under):
        pts.append((x, y))
        if k in tips:
            nx, ny = under[k + 1]
            t = abs(1 - 2 * (k + 0.5) / n)
            pts.append(((x + nx) / 2, max(y, ny) + c.rng.uniform(10, 34) * (1 - t * 0.7)))
    side_r = [(s.x1 - s.w * 0.012, s.top + wall * 0.45), (s.x1 - inset, s.top + wall)]
    side_l = [(s.x0 + inset, s.top + wall), (s.x0 + s.w * 0.012, s.top + wall * 0.45)]
    body = ridge + side_r + pts + side_l
    outline = "M" + "L".join(f"{x:.1f} {y:.1f}" for x, y in body) + "Z"
    bottom = "M" + "L".join(f"{x:.1f} {y:.1f}" for x, y in [side_r[-1], *pts, side_l[0]])
    return outline, bottom


def _boulder(L: Layer, c: Ctx, x: float, y: float, r: float, col: str, rim: str) -> None:
    """A lump of rock in the cliff: a rough polygon, lit along its upper edge."""
    pts = []
    for k in range(6):
        a = math.pi * 2 * k / 6 + c.rng.uniform(-0.3, 0.3)
        rr = r * c.rng.uniform(0.75, 1.15)
        pts.append((x + math.cos(a) * rr, y + math.sin(a) * rr * 0.7))
    L.poly(pts, col)
    upper = sorted(pts, key=lambda p: p[1])[:3]
    upper.sort()
    L.path("M" + "L".join(f"{px:.1f} {py:.1f}" for px, py in upper), stroke=rim,
           stroke_width=1, opacity=0.45)
    L.ellipse(x + r * 0.2, y + r * 0.5, r * 0.8, r * 0.18, "#000000", opacity=0.18)


def draw(L: Layer, c: Ctx, s: Shape, gid: str, haze: float = 0.0, detail: bool = True,
         style: str = "plain") -> None:
    """Draw an island in one of the STYLES: layered rock, boulders and cracks, a grassy lip
    with moss and roots, and light bouncing up off the clouds onto its underside."""
    outline, bottom = _outline(s, c, style)
    bands = _bands(c, style, haze)
    L.path(outline, bands[3])
    clip = c.defs.clip(f"{gid}-clip", f'<path d="{outline}"/>')
    inside = Layer()
    x0, x1, top, depth, w = s.x0, s.x1, s.top, s.depth, s.w
    wall = depth * 0.5
    rim = c.haze(c.P["rim"], haze)
    # Bands of rock, darker the deeper they lie, with a seam along each.
    for k, frac in ((2, 0.62), (1, 0.34), (0, 0.12)):
        y = top + 12 + depth * frac
        line = []
        x = x0 - 10
        while x < x1 + 20:
            line.append((x, y + c.rng.uniform(-5, 5)))
            x += 22
        seam = "L".join(f"{px:.0f} {py:.0f}" for px, py in line)
        inside.path(f"M{x0 - 10} {top - 30}L{seam}L{x1 + 20} {top - 30}Z", bands[k])
        inside.path("M" + seam, stroke="#000000", stroke_width=1.2, opacity=0.22)
        inside.path("M" + "L".join(f"{px:.0f} {py + 2:.0f}" for px, py in line), stroke=rim,
                    stroke_width=0.7, opacity=0.15)
    if detail:
        for _ in range(int(w / 34)):
            bx = c.rng.uniform(x0 + 16, x1 - 16)
            by = c.rng.uniform(top + 22, top + depth * 0.8)
            band = bands[min(3, int((by - top) / (depth * 0.28)))]
            _boulder(inside, c, bx, by, c.rng.uniform(6, 15), pal.shade(band, 1.08), rim)
        crack = pal.mix(bands[2], "#000000", 0.45)
        for _ in range(int(w / 70)):
            x, y = c.rng.uniform(x0 + 30, x1 - 30), c.rng.uniform(top + 20, top + wall)
            d = f"M{x:.0f} {y:.0f}"
            for _ in range(4):
                x += c.rng.uniform(-6, 6)
                y += c.rng.uniform(6, 14)
                d += f"L{x:.0f} {y:.0f}"
            inside.path(d, stroke=crack, stroke_width=1, opacity=0.55)
    # Light: the sun side catches it, the far side and the depths fall into shadow.
    inside.rect(x0, top - 20, w, depth + 80, c.defs.linear(
        f"{gid}-side", [(0, rim, 0.22), (0.3, rim, 0), (0.7, "#000000", 0),
                        (1, "#000000", 0.3)], x2=1, y2=0))
    inside.rect(x0, top + wall * 0.6, w, depth + 60, c.defs.linear(
        f"{gid}-deep", [(0, "#000000", 0), (1, "#000000", 0.4)]))
    bounce = c.haze(c.P["cloud"][1], haze)
    inside.path(bottom, stroke=bounce, stroke_width=5, opacity=0.35, filter=c.defs.blur(2))
    L.group(inside, clip_path=clip)
    if detail and style in EXTRAS:
        EXTRAS[style](L, c, s, haze)
    ridge = _ridge(s)
    top_path = "M" + "L".join(f"{x:.1f} {y:.1f}" for x, y in ridge)
    grass = c.haze(c.P["grass"], haze)
    lip = "L".join(f"{x:.1f} {y + 14:.1f}" for x, y in reversed(ridge))
    L.path(top_path + "L" + lip + "Z", grass)
    moss = c.haze(pal.shade(c.P["grass"], 0.8), haze)
    for x, y in ridge[2:-2:2]:
        L.ellipse(x + c.rng.uniform(-6, 6), y + 14, c.rng.uniform(6, 12), c.rng.uniform(2, 5), moss)
        if c.rng.random() < 0.4:  # grass spilling over the edge
            L.path(f"M{x:.0f} {y + 12:.0f}q2 {c.rng.uniform(6, 12):.0f} -1 {c.rng.uniform(10, 18):.0f}",
                   stroke=moss, stroke_width=1.6, stroke_linecap="round")
    L.path(top_path, stroke=rim, stroke_width=1.8, opacity=0.85)
    if detail:
        _roots(L, c, s, haze)


# ---------------------------------------------------------------- what makes each island its own

def _dwellings(L: Layer, c: Ctx, s: Shape, haze: float) -> None:
    """Homes carved into the town's cliff: arched windows and doors, little balconies with
    flower boxes, and a stair zigzagging down between them."""
    wood = c.haze(c.lit("#6a4a34"), haze)
    dark = c.haze("#1c1420", haze)
    flowers = ("#ff9fb8", "#ffd27a", "#b49ae0")
    rows = (s.top + 24, s.top + s.depth * 0.5 - 22, s.top + s.depth * 0.5 + 8)
    for row, y in enumerate(rows):
        x = s.x0 + s.w * 0.12 + c.rng.uniform(0, 30)
        while x < s.x1 - s.w * 0.12:
            lit = c.P["lamps"] and c.rng.random() < 0.8
            if c.rng.random() < 0.35:  # a door with a balcony; wooden by day
                door = c.haze(pal.WINDOW, haze) if lit else dark if c.dark else wood
                L.path(f"M{x - 4} {y + 10}v-8a4 4 0 0 1 8 0v8z", door)
                L.path(f"M{x - 4} {y + 10}v-8a4 4 0 0 1 8 0v8", stroke=c.haze(c.lit("#d9c9a5"), haze),
                       stroke_width=0.7)
                L.rect(x - 8, y + 10, 16, 1.6, wood)
                for bx in range(-7, 9, 3):
                    L.line(x + bx, y + 10, x + bx, y + 6.5, wood, 0.6)
                L.line(x - 8, y + 6.5, x + 8, y + 6.5, wood, 0.8)
            else:
                glass = c.haze(c.lit("#9cbbe0"), haze)
                win = c.haze(pal.WINDOW, haze) if lit else dark if c.dark else glass
                L.path(f"M{x - 3} {y + 6}v-4a3 3 0 0 1 6 0v4z", win,
                       stroke=c.haze(c.lit("#d9c9a5"), haze), stroke_width=0.7)
                L.rect(x - 4, y + 6, 8, 2, wood)
                for k in range(3):
                    L.circle(x - 2.5 + k * 2.5, y + 5.4, 1.1, c.haze(c.lit(flowers[k]), haze))
            if lit:
                c.glow(L, x, y + 4, 12, "#ffcf7a", 0.45)
            x += c.rng.uniform(36, 70)
    # A stair cut into the rock, zigzagging down one side.
    x, y = s.x0 + s.w * 0.2, s.top + 18
    d = f"M{x:.0f} {y:.0f}"
    for k in range(5):
        x += 16 if k % 2 == 0 else -16
        y += 14
        d += f"L{x:.0f} {y:.0f}"
    L.path(d, stroke=c.haze(c.lit("#e8cfa8"), haze), stroke_width=2.4, opacity=0.8,
           stroke_dasharray="2 1.2")


def _girders(L: Layer, c: Ctx, s: Shape, haze: float) -> None:
    """The city island is shored up underneath: steel piles with cross-braces and rivets,
    pipes, and red warning lights at the tips."""
    steel = c.haze(c.lit("#4c4a60"), haze)
    y0 = s.top + s.depth * 0.5
    xs = [s.cx + s.w * f for f in (-0.32, -0.12, 0.08, 0.28)]
    for k, x in enumerate(xs):
        ln = s.depth * (0.5 - abs(x - s.cx) / s.w * 0.6)
        L.rect(x - 2.5, y0 - 6, 5, ln, steel)
        L.rect(x - 4, y0 + ln - 8, 8, 3, steel)
        L.line(x, y0, x, y0 + ln - 10, c.haze(c.lit("#9a98b0"), haze), 1.4,
               stroke_dasharray="1.4 7.6")
        if k:
            px = xs[k - 1]
            L.line(px, y0 + 4, x, y0 + ln * 0.6, steel, 1.2)
            L.line(px, y0 + ln * 0.6, x, y0 + 4, steel, 1.2)
        tip = y0 + ln - 6
        L.circle(x, tip + 4, 1.4, "#ff5a4a" if c.P["lamps"] else c.lit("#a84a40"))
        if c.P["lamps"]:
            c.glow(L, x, tip + 4, 10, "#ff5a4a", 0.8, class_="blink",
                   style=f"animation-delay:-{k * .5:.1f}s")
    pipe = c.haze(c.lit("#7a6a70"), haze)
    L.path(f"M{s.x0 + s.w * 0.2} {s.top + 30}c0 30 30 20 30 50v30", stroke=pipe, stroke_width=3)
    L.circle(s.x0 + s.w * 0.2 + 30, s.top + 110, 2, c.haze("#9fd8ff", haze), opacity=0.8,
             class_="pulse")
    # Brick courses showing through the top band of rock.
    brick = c.haze(c.lit("#6e4a44"), haze)
    tile = c.defs.pattern(f"bricks-{haze:g}", 12, 12,
                          f'<rect width="10" height="4.4" fill="{brick}"/>'
                          f'<rect x="6" y="6" width="10" height="4.4" fill="{brick}"/>'
                          f'<rect x="-6" y="6" width="10" height="4.4" fill="{brick}"/>')
    L.rect(s.x0 + 20, s.top + 18, s.w - 40, 24, tile, opacity=0.35)


def _steel_ring(L: Layer, c: Ctx, s: Shape, haze: float) -> None:
    """The stadium island wears a riveted steel band, with team banners hanging from the rim
    and lamps shining down from underneath."""
    steel = c.haze(c.lit("#8a8fa8"), haze)
    y = s.top + s.depth * 0.32
    L.rect(s.x0 + 4, y, s.w - 8, 6, steel)
    L.line(s.x0 + 4, y, s.x1 - 4, y, c.P["rim"], 0.8, opacity=0.6)
    L.line(s.x0 + 10, y + 3, s.x1 - 6, y + 3, c.haze(c.lit("#4c4a60"), haze), 1.6,
           stroke_dasharray="1.6 6.4")
    teams = list(pal.TEAMS.values())
    for k, x in enumerate(range(int(s.x0 + 22), int(s.x1 - 16), 22)):
        team = teams[k % len(teams)]
        col = c.haze(c.lit(team["primary"]), haze)
        L.path(f"M{x - 4} {s.top + 12}h8v16l-4 -4l-4 4z", col)
        L.rect(x - 4, s.top + 15, 8, 2, c.haze(c.lit(team["secondary"]), haze))
        L.line(x - 5, s.top + 12, x + 5, s.top + 12, steel, 0.8)
    if c.P["lamps"]:
        for x in (s.cx - s.w * 0.25, s.cx, s.cx + s.w * 0.25):
            L.poly([(x - 2, y + 6), (x - 26, y + 70), (x + 26, y + 70), (x + 2, y + 6)],
                   "#fff3c4", opacity=0.08)
            c.glow(L, x, y + 7, 8, "#fff3c4", 0.8)


def _wild_extras(L: Layer, c: Ctx, s: Shape, haze: float) -> None:
    """Curtains of moss hanging over the wild cliff, and a glowing cave."""
    moss = c.haze(c.lit("#3f7a4a"), haze)
    for _ in range(int(s.w / 60)):
        x = c.rng.uniform(s.x0 + 30, s.x1 - 60)
        y = s.ground(x) + 12
        for k in range(6):
            ln = c.rng.uniform(16, 46)
            L.path(f"M{x + k * 4:.0f} {y:.0f}q2 {ln / 2:.0f} -1 {ln:.0f}", stroke=moss,
                   stroke_width=2.2, stroke_linecap="round", opacity=0.9)
    cx, cy = s.cx + s.w * 0.28, s.top + s.depth * 0.3
    L.ellipse(cx, cy, 22, 14, c.haze("#0c1416", haze))
    L.path(f"M{cx - 22} {cy}a22 14 0 0 1 44 0", stroke=c.P["rim"], stroke_width=1, opacity=0.5)
    c.glow(L, cx, cy + 4, 18, "#7fe3ff", 0.6 if c.dark else 0.3, class_="pulse")
    for k in range(3):
        L.poly([(cx - 12 + k * 10, cy + 8), (cx - 9 + k * 10, cy - 4 - k % 2 * 4),
                (cx - 6 + k * 10, cy + 8)], "#9fe6ff", opacity=0.8)


def _soil(L: Layer, c: Ctx, s: Shape, haze: float) -> None:
    """Rich farm soil: carrots and turnips growing down into it, and pebbles."""
    for _ in range(int(s.w / 40)):
        x = c.rng.uniform(s.x0 + 30, s.x1 - 30)
        y = s.ground(x) + 14
        if c.rng.random() < 0.6:
            L.poly([(x - 2.5, y), (x, y + c.rng.uniform(9, 14)), (x + 2.5, y)],
                   c.haze(c.lit("#f08a3a"), haze))
        else:
            L.circle(x, y + 4, 3.4, c.haze(c.lit("#e8d8f0"), haze))
            L.path(f"M{x - 3.4} {y + 3}a3.4 3.4 0 0 1 6.8 0z", c.haze(c.lit("#b05ab0"), haze))
            L.line(x, y + 7, x, y + 11, c.haze(c.lit("#c9b8a8"), haze), 0.6)
    for _ in range(int(s.w / 32)):
        x = c.rng.uniform(s.x0 + 20, s.x1 - 20)
        y = c.rng.uniform(s.top + 30, s.top + s.depth * 0.55)
        L.ellipse(x, y, c.rng.uniform(1.5, 3), c.rng.uniform(1, 2),
                  c.haze(c.lit("#c8a880"), haze), opacity=0.6)


def _thrusters(L: Layer, c: Ctx, s: Shape, haze: float) -> None:
    """The Starport floats on engines: nozzles under the rock with blue light pouring down,
    and a strip of panel lights along the cliff."""
    steel = c.haze(c.lit("#4c5470"), haze)
    for f in (-0.22, 0.22):
        x, y = s.cx + s.w * f, s.top + s.depth * 0.78
        L.rect(x - 5, y, 10, 6, steel, rx=1.5)
        L.poly([(x - 4, y + 6), (x + 4, y + 6), (x + 9, y + 34), (x - 9, y + 34)], "#7fe3ff",
               opacity=0.35, class_="flick")
        c.glow(L, x, y + 8, 12, "#bff4ff", 0.9)
    y = s.top + 22
    L.line(s.x0 + s.w * 0.15, y, s.x1 - s.w * 0.15, y, "#7fe3ff", 1.4, stroke_dasharray="2 6",
           opacity=0.8, class_="pulse")


def _paper_lanterns(L: Layer, c: Ctx, s: Shape, haze: float) -> None:
    """Red paper lanterns strung along the Shrine's lip."""
    string = c.haze(c.lit("#3a2a2a"), haze)
    x0, x1 = s.x0 + s.w * 0.12, s.x1 - s.w * 0.12
    y = s.top + 16
    L.path(f"M{x0} {y}Q{s.cx} {y + 14} {x1} {y}", stroke=string, stroke_width=0.7)
    for k in range(1, 6):
        t = k / 6
        x = (1 - t) ** 2 * x0 + 2 * (1 - t) * t * s.cx + t * t * x1
        ly = (1 - t) ** 2 * y + 2 * (1 - t) * t * (y + 14) + t * t * y
        L.ellipse(x, ly + 4, 3, 3.8, c.haze(c.lit("#e0452f"), haze))
        L.rect(x - 2, ly - 0.2, 4, 1.2, string)
        if c.P["lamps"]:
            c.glow(L, x, ly + 4, 9, "#ff8a5a", 0.7, class_="flick")


EXTRAS = {
    "starport": _thrusters,
    "shrine": _paper_lanterns,
    "town": _dwellings,
    "city": _girders,
    "stadium": _steel_ring,
    "wild": _wild_extras,
    "fields": _soil,
}


def _roots(L: Layer, c: Ctx, s: Shape, haze: float) -> None:
    root = c.haze(pal.mix(c.P["rock"][1], "#3a2a1a", 0.4), haze)
    vine = c.haze("#2f5a4a" if not c.dark else "#24463e", haze)
    for _ in range(int(s.w / 26)):
        x = c.rng.uniform(s.x0 + s.w * 0.15, s.x1 - s.w * 0.15)
        y = s.ground(x) + 14
        ln = c.rng.uniform(30, 90)
        bend = c.rng.uniform(-10, 10)
        L.path(f"M{x:.0f} {y:.0f}q{bend:.0f} {ln * 0.5:.0f} {bend * 0.4:.0f} {ln:.0f}",
               stroke=vine if c.rng.random() < 0.6 else root, stroke_width=c.rng.uniform(1, 2.2),
               stroke_linecap="round", opacity=0.85)
        if c.rng.random() < 0.5:
            L.circle(x + bend * 0.4, y + ln, 1.6, vine)
    for side in (-1, 1):
        x = s.cx + side * s.w * 0.36
        y = s.ground(x) + 22
        L.path(f"M{x:.0f} {y:.0f}c{side * 18} 20 {side * 4} 50 {side * 22} 80",
               stroke=root, stroke_width=3, stroke_linecap="round")
        L.path(f"M{x + side * 8:.0f} {y + 30:.0f}q{side * 10} 10 {side * 6} 30",
               stroke=root, stroke_width=1.4, stroke_linecap="round")


def hanging_lanterns(L: Layer, c: Ctx, s: Shape) -> None:
    on = c.P["lamps"]
    for dx, ln in ((-150, 46), (-40, 70), (110, 54)):
        x = s.cx + dx
        y = s.top + 40 + abs(dx) * 0.25
        L.line(x, y, x, y + ln, pal.shade(c.P["rock"][1], 0.7), 0.8)
        L.rect(x - 3, y + ln, 6, 8, pal.WINDOW if on else c.lit("#b89a6a"), rx=1.5)
        L.rect(x - 4, y + ln - 1.5, 8, 2, c.lit("#3a2a20"))
        if on:
            c.glow(L, x, y + ln + 4, 22, "#ffb35a", 0.8, class_="flick",
                   style=f"animation-delay:-{abs(dx) % 5 * .4:.1f}s")


def _shard(L: Layer, x: float, y: float, h: float, w: float, angle: float, col: str) -> None:
    """One crystal growing out of the rock at (x, y): a six-sided prism with a pointed tip,
    its left faces lit and its right faces in shade, and a bright edge down the middle."""
    tip = h * 0.22
    light, dark = pal.mix(col, "#ffffff", 0.45), pal.shade(col, 0.72)
    g = Layer()
    g.poly([(-w, 0), (-w, -h + tip), (0, -h), (0, 0)], light)
    g.poly([(0, 0), (0, -h), (w, -h + tip), (w, 0)], dark)
    g.poly([(-w * 0.35, 0), (-w * 0.35, -h + tip * 1.2), (0, -h), (w * 0.25, -h + tip),
            (w * 0.25, 0)], col)
    g.line(0, -h, 0, 0, "#ffffff", 0.6, opacity=0.7)
    L.group(g, transform=f"translate({x:.1f} {y:.1f}) rotate({angle:.0f})")


def crystals(L: Layer, c: Ctx, s: Shape) -> None:
    """Crystal clusters growing out of pockets in the cliff: a dark hollow in the rock with a
    lit rim, a spray of shards leaning out of it at different angles, small chips around
    it, and a glow that is soft by day and strong at night."""
    strength = 0.85 if c.dark else 0.3
    for k, (dx, dy, col, size) in enumerate(((-70, 0.56, "#7fe3ff", 1.0), (60, 0.5, "#c58bff", 1.1),
                                             (-4, 0.76, "#9fb8ff", 0.75))):
        x, y = s.cx + dx, s.top + s.depth * dy
        L.ellipse(x, y + 2, 13 * size, 5 * size, "#0a0712", opacity=0.75)
        L.path(f"M{x - 13 * size:.1f} {y + 2:.1f}a{13 * size:.1f} {5 * size:.1f} 0 0 0 "
               f"{26 * size:.1f} 0", stroke=c.P["rim"], stroke_width=0.8, opacity=0.5)
        c.glow(L, x, y - 6 * size, 30 * size, col, strength, class_="flick",
               style=f"animation-delay:-{k * 0.6:.1f}s")
        for sx, h, w, ang in ((-8, 14, 2.6, -28), (6, 16, 2.8, 22), (-2, 26, 3.6, -4),
                              (3, 19, 3, 10), (-5, 11, 2.2, -45), (10, 10, 2, 48)):
            _shard(L, x + sx * size, y + 2, h * size, w * size, ang, col)
        for _ in range(3):
            L.poly([(0, 0), (1.6, -3.6), (3.2, 0)], pal.mix(col, "#ffffff", 0.3),
                   transform=f"translate({x + c.rng.uniform(-20, 16) * size:.1f} "
                             f"{y + c.rng.uniform(4, 12) * size:.1f})")
        for j in range(2):
            L.circle(x + c.rng.uniform(-10, 10) * size, y - c.rng.uniform(10, 26) * size, 0.9,
                     "#ffffff", class_="tw", style=f"animation-delay:-{(k + j) * 1.3:.1f}s")


def waterfall(L: Layer, c: Ctx, s: Shape, x: float | None = None) -> None:
    """Water spilling over the edge: it starts at the grass, falls straight down as a smooth,
    soft-edged curtain with fine streaks, and thins out into a plume of mist before it
    reaches the clouds."""
    x = s.x1 - 30 if x is None else x
    y = s.ground(x) + 4
    bottom = 452
    fall = bottom - y
    w = 11
    tint = c.lit("#b8def2") if not c.dark else "#8aa4d0"
    foam = "#ffffff" if not c.dark else "#e4ecfa"
    # The shadow the water casts on the cliff behind it.
    L.rect(x - w / 2 - 2, y + 6, w + 4, fall * 0.5, "#000000", opacity=0.12, filter=c.defs.blur(3))
    # The curtain: smooth and soft-edged, fading out two thirds of the way down.
    curtain = c.defs.linear(f"fall-{c.phase}", [(0, foam, 0.95), (0.12, tint, 0.85),
                                                (0.6, tint, 0.55), (1, tint, 0)])
    reach = fall * 0.72
    L.path(f"M{x - w / 2:.1f} {y:.0f}L{x + w / 2:.1f} {y:.0f}L{x + w / 2 + 3:.1f} {y + reach:.0f}"
           f"L{x - w / 2 - 3:.1f} {y + reach:.0f}Z", curtain, filter=c.defs.blur(0.7))
    L.rect(x - w / 2, y, 2, reach * 0.8, c.P["rim"], opacity=0.35, filter=c.defs.blur(0.6))
    # Fine streaks running straight down it.
    for k, dx in enumerate((-3.6, -1.2, 1, 3.2)):
        dash = ("18 7 5 18", "9 5 22 12", "6 9 14 19", "24 10 7 7")[k]  # each adds up to 48
        L.line(x + dx, y + 2, x + dx * 1.2, y + reach * (0.75 + 0.06 * k), foam, 0.9,
               stroke_dasharray=dash, opacity=0.8, class_="fall",
               style=f"animation-duration:{0.6 + k * 0.1:.1f}s;animation-delay:-{k * .3:.1f}s")
    # The plume of mist it breaks into, swelling as it falls.
    mist = Layer()
    for k in range(6):
        f = k / 5
        my = y + reach * 0.55 + (fall - reach * 0.55) * f
        mist.ellipse(x + c.rng.uniform(-3, 3), my, 6 + f * 18, 5 + f * 9, foam,
                     opacity=0.45 - f * 0.2)
    L.group(mist, filter=c.defs.blur(4), class_="pulse")
    for _ in range(8):
        L.circle(x + c.rng.uniform(-10, 10), c.rng.uniform(y + reach * 0.5, bottom - 10),
                 c.rng.uniform(0.6, 1.2), foam, class_="tw",
                 style=f"animation-delay:-{c.rng.uniform(0, 4):.1f}s")


def drifting_rocks(L: Layer, c: Ctx, spots: tuple[tuple[float, float, float, bool], ...]) -> None:
    """Small rocks bobbing in the air; some carry a tiny tree."""
    for k, (x, y, r, tree) in enumerate(spots):
        g = Layer()
        g.path(f"M{x - r} {y}Q{x - r * 0.6} {y + r * 1.4} {x} {y + r * 2}"
               f"Q{x + r * 0.5} {y + r * 1.2} {x + r} {y}Z", c.P["rock"][1])
        g.ellipse(x, y, r, r * 0.32, c.P["grass"])
        g.path(f"M{x - r} {y}q{r * 0.5} {-r * 0.3} {r * 1.5} {-r * 0.1}", stroke=c.P["rim"],
               stroke_width=0.8, opacity=0.8)
        if tree:
            g.rect(x - 0.8, y - r * 1.2, 1.6, r * 1.2, c.lit("#5a3f2e"))
            g.circle(x, y - r * 1.4, r * 0.6, pal.shade(c.P["grass"], 1.2))
        L.group(g, class_="bob", style=f"animation-delay:-{k * .7:.1f}s;"
                                       f"animation-duration:{2.6 + k * 0.4:.1f}s")


FAR: tuple = ()  # cx, top, width, depth, haze, extra: none at the moment


def far_islands(L: Layer, c: Ctx) -> None:
    """Islands far off in the haze: a peak, a ruin, a grove, each with a thread of water."""
    for k, (cx, top, w, depth, haze, extra) in enumerate(FAR):
        s = Shape(cx, top, w, depth)
        g = Layer()
        draw(g, c, s, f"far{k}", haze, detail=False)
        rock = c.haze(c.P["rock"][0], haze)
        grass = c.haze(c.P["grass"], haze)
        if extra == "peak":
            g.poly([(cx - 46, top + 2), (cx - 10, top - 54), (cx + 6, top - 36), (cx + 22, top - 62),
                    (cx + 56, top + 4)], rock)
            snow = c.haze("#f4f2fa", haze * 0.7)
            g.poly([(cx - 18, top - 40), (cx - 10, top - 54), (cx - 2, top - 42)], snow)
            g.poly([(cx + 14, top - 50), (cx + 22, top - 62), (cx + 30, top - 49)], snow)
        elif extra == "ruin":
            g.path(f"M{cx - 14} {top + 2}v-22a14 14 0 0 1 28 0v22h-5v-20a9 9 0 0 0 -18 0v20z", rock)
            g.rect(cx + 18, top - 30, 5, 32, rock)
        else:
            for dx in (-30, -14, 4, 22, 36):
                g.rect(cx + dx - 0.8, top - 10, 1.6, 10, rock)
                g.circle(cx + dx, top - 14, 7, grass)
        wx = cx + w * 0.3
        g.line(wx, s.ground(wx) + 10, wx + 2, top + depth + 30, c.haze("#ffffff", haze * 0.5),
               1, opacity=0.5)
        L.group(g, filter=c.defs.blur(0.6), class_="bob",
                style=f"animation-duration:{5 + k}s;animation-delay:-{k}s")
