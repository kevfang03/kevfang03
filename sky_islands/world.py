"""The rest of the archipelago: the Philly island, the stadium island, islands still
locked behind a level, the bridges between them and the traffic in the air."""

from __future__ import annotations

from dataclasses import dataclass

from . import palette as pal
from .context import Ctx
from .hud import game_text
from .island import HOME, PHILLY, STADIUM, Shape, draw, waterfall
from .progress import level_info
from .svg import Layer, Rects
from .town import Label
from .wonders import ship_count, shrine, starport

# Level needed before each island opens up.
UNLOCK = {"philly": 3, "stadium": 4, "starport": 6, "shrine": 8}


@dataclass(frozen=True)
class Locked:
    key: str
    name: str
    shape: Shape


LOCKED = (
    Locked("starport", "STARPORT", Shape(300, 132, 100, 78)),
    Locked("shrine", "SKY SHRINE", Shape(772, 112, 90, 70)),
)

DRIFTING = ((262, 330, 7, True), (790, 356, 6, False), (455, 196, 4, False), (40, 300, 6, False),
            (978, 300, 5, True), (680, 214, 3.5, False))


def level(c: Ctx) -> int:
    return level_info(c.w.stats.contributions_total).level


def _fog(L: Layer, c: Ctx, s: Shape) -> None:
    L.ellipse(s.cx, s.top + 4, s.w * 0.7, 22, c.P["haze"], opacity=0.55, filter=c.defs.blur(8))


def _padlock(L: Layer, c: Ctx, x: float, y: float) -> None:
    c.glow(L, x, y - 6, 20, "#ffd27a", 0.6)
    L.rect(x - 6, y - 10, 12, 10, "#e8b440", rx=2)
    L.path(f"M{x - 3.5} {y - 10}v-4a3.5 3.5 0 0 1 7 0v4", stroke="#e8b440", stroke_width=2)
    L.circle(x, y - 5, 1.4, "#6b4a10")


def wonder(L: Layer, c: Ctx, key: str, s: Shape, gid: str, labels: list[Label] | None,
           name: str) -> None:
    """The Starport or the Sky Shrine on shape s: shown in full once your level opens it,
    otherwise a hazy glimpse in the fog with a padlock."""
    locked = level(c) < UNLOCK[key]
    haze = 0.45 if locked else 0.0
    draw(L, c, s, gid, haze, detail=not locked, style=key)
    if key == "starport":
        starport(L, c, s.cx, s.top, s.w, ship_count(c.w.stats.merged_prs), haze)
    else:
        shrine(L, c, s.cx, s.top, s.w, haze)
    text = f"{name} · UNLOCKS AT LV {UNLOCK[key]}" if locked else name
    if locked:
        _fog(L, c, s)
        _padlock(L, c, s.cx, s.top - 2)
    if labels is not None:
        labels.append(Label(s.cx, s.top - (22 if locked else 46), text,
                            "#ffe08a" if locked else "#9fe6ff"))


def locked_islands(L: Layer, c: Ctx, labels: list[Label]) -> None:
    """The Starport and the Sky Shrine, floating high above the main islands."""
    for k, isl in enumerate(LOCKED):
        g = Layer()
        wonder(g, c, isl.key, isl.shape, f"wonder{k}", labels, isl.name)
        L.group(g, class_="bob", style=f"animation-duration:{5 + k}s")


# ---------------------------------------------------------------- Philly island

def _tower(L: Layer, c: Ctx, x: float, w: float, top: float, base: float, glass: bool) -> None:
    body = c.lit("#8fa4c4" if glass else "#b8aa94")
    L.rect(x, top, w, base - top, body)
    L.rect(x + w * 0.6, top, w * 0.4, base - top, "#000000", opacity=0.18)
    lit = c.P["lit"]
    for row in range(int((base - top - 6) // 6)):
        for col in range(int((w - 4) // 4)):
            on = c.rng.random() < lit
            col_ = pal.WINDOW if on else (c.lit("#c9d8ee") if not c.dark else "#1d1a36")
            L.rect(x + 2.5 + col * 4, top + 4 + row * 6, 2, 3, col_,
                   opacity=1 if on or not c.dark else 0.8)


def philly(L: Layer, c: Ctx, labels: list[Label]) -> None:
    s = PHILLY
    if level(c) < UNLOCK["philly"]:
        draw(L, c, s, "philly", 0.3, style="city")
        _fog(L, c, s)
        _padlock(L, c, s.cx, s.top - 4)
        labels.append(Label(s.cx, s.top - 22, f"PHILLY ISLAND · UNLOCKS AT LV {UNLOCK['philly']}",
                            "#ffe08a"))
        return
    draw(L, c, s, "philly", style="city")
    base = s.top + 4
    # Back to front: generic towers, the Liberty Place pair, the Comcast towers, City Hall.
    for x, w, h in ((s.x0 + 22, 18, 52), (s.x0 + 168, 20, 60), (s.x0 + 196, 16, 40)):
        _tower(L, c, x, w, base - h, base, glass=False)
    crown = pal.TEAMS[c.w.games[0].team]["light"] if c.w.games else None
    trim = crown or ("#8fe3ff" if c.dark else c.lit("#e8eef8"))
    for x, w, h, spire in ((s.x0 + 62, 20, 92, 18), (s.x0 + 86, 16, 76, 0)):
        top = base - h
        _tower(L, c, x, w, top + 16, base, glass=True)
        L.poly([(x + 2, top + 16), (x + w / 2, top), (x + w - 2, top + 16)], c.lit("#7f94b8"))
        for k in range(1, 4):
            t = k / 4
            L.line(x + w / 2 - (w / 2 - 2) * t, top + 16 * t, x + w / 2 + (w / 2 - 2) * t,
                   top + 16 * t, trim, 0.9)
        if spire:
            L.line(x + w / 2, top, x + w / 2, top - spire, trim, 0.9)
            L.circle(x + w / 2, top - spire, 1.3, "#ff4d4d", class_="av")
    for x, w, h in ((s.x0 + 130, 22, 112), (s.x0 + 106, 18, 88)):
        _tower(L, c, x, w, base - h + 10, base, glass=True)
        L.rect(x, base - h, w, 10, c.lit("#6f84a8"))
        L.rect(x + 3, base - h + 3, w - 6, 3, trim, opacity=0.9)
    cx = s.x0 + 150
    stone = c.lit("#d9c49a")
    L.rect(cx - 22, base - 20, 44, 20, stone)
    L.rect(cx - 5, base - 64, 10, 46, stone)
    L.rect(cx - 7, base - 72, 14, 9, stone)
    L.circle(cx, base - 67, 2.6, "#fff1b0" if c.dark else c.lit("#f5ecd2"))
    L.path(f"M{cx - 5} {base - 72}q5 -9 10 0z", stone)
    L.line(cx, base - 80, cx, base - 86, c.lit("#7a6648"), 1.4)
    if c.dark:
        c.glow(L, cx, base - 50, 40, "#ffe7a8", 0.45)
    # Boathouse Row along the front edge, outlined in lights after dark.
    for k in range(6):
        hx = s.x0 + 30 + k * 26
        hy = s.ground(hx) + 4
        L.rect(hx, hy - 8, 16, 8, c.lit("#e8dcc4"))
        L.poly([(hx - 1, hy - 8), (hx + 8, hy - 15), (hx + 17, hy - 8)], c.lit("#5a4a5a"))
        if c.P["lamps"]:
            L.path(f"M{hx} {hy}v-8l8 -7l8 7v8", stroke="#fff2c4", stroke_width=1,
                   stroke_dasharray="0.1 2", stroke_linecap="round", stroke_linejoin="round")
    waterfall(L, c, s, s.x0 + 26)
    labels.append(Label(s.cx, base - 124, "PHILLY ISLAND", "#9fd8ff"))


# ---------------------------------------------------------------- stadium island

def stadium(L: Layer, c: Ctx, labels: list[Label]) -> None:
    s = STADIUM
    if level(c) < UNLOCK["stadium"]:
        draw(L, c, s, "stadium", 0.3, style="stadium")
        _fog(L, c, s)
        _padlock(L, c, s.cx, s.top - 4)
        labels.append(Label(s.cx, s.top - 22, f"STADIUM · UNLOCKS AT LV {UNLOCK['stadium']}",
                            "#ffe08a"))
        return
    draw(L, c, s, "stadium", style="stadium")
    games = c.w.games
    team = pal.TEAMS[games[0].team] if games else None
    glow_col = team["light"] if team else "#fff3d0"
    base = s.top + 4
    x0, x1 = s.cx - 66, s.cx + 66
    if games:
        c.glow(L, s.cx, base - 30, 150, glow_col, 0.45)
    L.path(f"M{x0} {base}L{x0 + 8} {base - 34}Q{s.cx} {base - 48} {x1 - 8} {base - 34}L{x1} {base}Z",
           c.lit("#bdb6cf"))
    L.path(f"M{x0 + 8} {base - 34}Q{s.cx} {base - 48} {x1 - 8} {base - 34}", stroke=c.P["rim"],
           stroke_width=1.2)
    for k in range(5):
        y = base - 8 - k * 6
        L.line(x0 + 4 + k * 1.6, y, x1 - 4 - k * 1.6, y, c.lit("#8a84a0"), 1)
    if games:
        colors = (team["primary"], team["secondary"], "#ffffff", team["light"])
        crowd = Rects()  # the fans in team colours, one path per colour
        for _ in range(110):
            x = c.rng.uniform(x0 + 8, x1 - 8)
            y = c.rng.uniform(base - 32, base - 6)
            crowd.add(x, y, 1.8, 1.8, c.rng.choice(colors))
        L.add(crowd)
    for fx in (x0 + 2, x1 - 2):
        L.line(fx, base, fx, base - 70, c.lit("#5a5470"), 2)
        L.rect(fx - 8, base - 76, 16, 6, "#f2fff8" if games else c.lit("#9a94b0"))
        if games:
            c.glow(L, fx, base - 73, 34, glow_col, 0.9)
            L.poly([(fx - 7, base - 70), (fx + 7, base - 70), (s.cx + (fx - s.cx) * 0.2, base - 20)],
                   glow_col, opacity=0.12)
    # Arched entrances, a concourse band, flags on the rim and a scoreboard.
    for k in range(9):
        ax = x0 + 14 + k * (x1 - x0 - 28) / 8
        lit = c.P["lamps"]
        L.path(f"M{ax - 3:.1f} {base}v-5a3 3 0 0 1 6 0v5z", "#ffcf7a" if lit else c.lit("#4a4460"))
    L.rect(x0 + 5, base - 18, x1 - x0 - 10, 3, c.lit("#2f6f7a"))
    L.rect(x0 + 7, base - 28, x1 - x0 - 14, 2, "#bff4ff" if c.P["lamps"] else c.lit("#d9e4f0"),
           opacity=0.8)
    for k, team_key in enumerate(("eagles", "phillies", "sixers")):
        fx = s.cx - 40 + k * 40
        fy = base - 44 + abs(k - 1) * 3
        L.line(fx, fy, fx, fy - 12, c.lit("#5a5470"), 0.8)
        L.path(f"M{fx} {fy - 12}l8 2.4l-8 2.4z", c.lit(pal.TEAMS[team_key]["primary"]),
               class_="sway")
    bx, by = x1 - 30, base - 64
    L.line(bx + 4, by + 12, bx + 4, base - 40, c.lit("#5a5470"), 1.2)
    L.line(bx + 18, by + 12, bx + 18, base - 40, c.lit("#5a5470"), 1.2)
    L.rect(bx, by, 22, 12, c.lit("#1a1622"), rx=1)
    L.text(bx + 11, by + 8.6, "PHI", 7, "#ffcf5a" if c.P["lamps"] or games else c.lit("#c9a24a"),
           text_anchor="middle", font_weight="bold")
    waterfall(L, c, s, s.x1 - 24)
    if games:
        labels.append(Label(s.cx, base - 92, "GAME DAY · " + game_text(games[0]), glow_col))
    else:
        labels.append(Label(s.cx, base - 92, "STADIUM · NO GAME TODAY", "#cfc6ea"))


# ---------------------------------------------------------------- bridges and traffic

def rope_bridge(L: Layer, c: Ctx, a: Shape, b: Shape) -> None:
    """A plank bridge on ropes from the east edge of one island to the west edge of the next."""
    x1, x2 = a.x1 - 8, b.x0 + 8
    y1, y2 = a.ground(x1) + 2, b.ground(x2) + 2
    mx, my = (x1 + x2) / 2, max(y1, y2) + 16
    rope = c.lit("#6a4a34")
    L.path(f"M{x1} {y1}Q{mx} {my} {x2} {y2}", stroke=c.lit("#a8774a"), stroke_width=4,
           stroke_dasharray="2.5 1.5")
    L.path(f"M{x1} {y1 - 10}Q{mx} {my - 10} {x2} {y2 - 10}", stroke=rope, stroke_width=0.9)
    for k in range(1, 8):
        t = k / 8
        x = (1 - t) ** 2 * x1 + 2 * (1 - t) * t * mx + t * t * x2
        y = (1 - t) ** 2 * y1 + 2 * (1 - t) * t * my + t * t * y2
        L.line(x, y, x, y - 10, rope, 0.6)


def sky_taxi(c: Ctx, scale: float = 1.0, left: bool = False) -> str:
    """A little hover car facing right (or left): a rounded coral cab under a glass bubble,
    a tail fin, two thruster pods and a soft blue glow beneath them."""
    body, trim = c.lit("#e8735a"), c.lit("#f6ead8")
    glass = "#ffe6a8" if c.P["lamps"] else c.lit("#bfe4f8")
    return (f'<g transform="scale({-scale if left else scale} {scale})">'
            '<ellipse cx="0" cy="5.4" rx="7" ry="1.8" fill="#7fd0ff" opacity=".45"/>'
            f'<path d="M-8 -1l-2.4 -4.6h3.2l2.4 3.6z" fill="{body}"/>'
            f'<path d="M-4.2 -3a4.2 3.6 0 0 1 8.4 0z" fill="{glass}" opacity=".92"/>'
            f'<path d="M-8.5 1.4q0 -4.4 4.4 -4.4h7.6q5 0 6 4.4z" fill="{body}"/>'
            f'<rect x="-8" y="0" width="16" height="1.2" fill="{trim}"/>'
            '<circle cx="-4.6" cy="3" r="1.4" fill="#2a2440"/>'
            '<circle cx="4.6" cy="3" r="1.4" fill="#2a2440"/>'
            '<circle cx="9" cy="0.2" r="1" fill="#fff6d0"/></g>')


def fly(L: Layer, car: str, path: str, dur: float, begin: float) -> None:
    """Send a car along a path, level (no tilting), fading in and out at the ends."""
    L.raw(f'<g opacity="0">{car}<animateMotion dur="{dur}s" begin="{begin}s" '
          f'repeatCount="indefinite" path="{path}"/>'
          f'<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;.1;.9;1" '
          f'dur="{dur}s" begin="{begin}s" repeatCount="indefinite"/></g>')


def flying_cars(L: Layer, c: Ctx) -> None:
    """Sky taxis hopping between the islands."""
    routes = (((f"M{PHILLY.x1 - 20} {PHILLY.top - 40}Q{(PHILLY.x1 + HOME.x0) / 2} {PHILLY.top - 90} "
               f"{HOME.cx - 80} {HOME.top - 50}"), 10, 0, False),
              ((f"M{STADIUM.cx} {STADIUM.top - 60}Q{(HOME.x1 + STADIUM.x0) / 2} {STADIUM.top - 120} "
               f"{HOME.cx + 60} {HOME.top - 70}"), 12, -5, True),
              ((f"M{HOME.cx - 40} {HOME.top - 90}Q{HOME.x0} {HOME.top - 140} "
               f"{PHILLY.cx} {PHILLY.top - 120}"), 11, -8, True))
    for path, dur, begin, left in routes:
        fly(L, sky_taxi(c, 1.0, left), path, dur, begin)
