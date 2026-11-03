"""Everything built on the home island: the HQ, one building per repo, the current
project under a crane, trees, a windmill, terraced farm rows and lanterns."""

from __future__ import annotations

import math
from dataclasses import dataclass

from . import holidays
from . import palette as pal
from .clock import season
from .companion import companion
from .context import Ctx
from .island import Shape
from .model import Repo
from .progress import activity, current_quest, level_info, style_for, tier_for
from .svg import Layer

TIER_W = (32, 38, 44, 52)
TIER_H = (30, 44, 58, 76)
GAP = 9
CRANE_ROOM = 30  # extra space to the right of the building under construction
HQ_SIZE = ((2, 60, 58), (5, 72, 84), (99, 86, 100))  # (up to level, width, height)

WALL = {"cottage": "#efe2c8", "observatory": "#d9d4ec", "workshop": "#e8c9a0",
        "bookshop": "#cfe2d6", "lab": "#c9d3e2"}
ROOF = {"cottage": "#b5523f", "observatory": "#5a6ab8", "workshop": "#7a5a3a",
        "bookshop": "#3f7a6a", "lab": "#68707e"}
TREES = {"spring": ("#f4a6c6", "#8ccd74", "#f8c0d8"), "summer": ("#4f9a4a", "#5cae55", "#3f8a42"),
         "fall": ("#d9822b", "#c0552e", "#e8b23a"), "winter": ()}
FLOWERS = {"spring": ("#ffd1e6", "#ffffff", "#ffe27a"), "summer": ("#ffe27a", "#ff9fb2", "#ffffff"),
           "fall": ("#ffb35a", "#e8873a"), "winter": ()}
CROPS = {"spring": "#9ad67a", "summer": "#5cae55", "fall": "#e8873a", "winter": "#eef2f8"}


@dataclass
class Plot:
    kind: str  # hq, repo
    x: float
    w: float
    repo: Repo | None = None


@dataclass(frozen=True)
class Label:
    x: float
    y: float  # bottom of the space the label may use
    text: str
    color: str


@dataclass
class Town:
    plots: list[Plot]
    overflow: int
    span: tuple[float, float]


def hq_size(level: int) -> tuple[float, float]:
    for upto, w, h in HQ_SIZE:
        if level <= upto:
            return w, h
    return HQ_SIZE[-1][1], HQ_SIZE[-1][2]


def building_width(repo: Repo, quest_repo: Repo | None) -> float:
    w = TIER_W[tier_for(repo.commits) - 1] + (4 if style_for(repo) == "observatory" else 0)
    return w + (CRANE_ROOM if repo is quest_repo else 0)


def plan(repos: tuple[Repo, ...], level: int, s: Shape) -> Town:
    """Place the HQ in the middle and repos outward from it, biggest first, never overlapping."""
    lo, hi = s.x0 + 58, s.x1 - 30
    hw, _ = hq_size(level)
    hq = Plot("hq", s.cx - hw / 2, hw)
    plots = [hq]
    quest = current_quest(repos)
    quest_repo = quest.repo if quest else None
    left, right = hq.x - GAP, hq.x + hw + GAP
    overflow = 0
    for i, repo in enumerate(sorted(repos, key=lambda r: (-r.commits, r.name))):
        w = building_width(repo, quest_repo)
        room_r, room_l = hi - right, left - lo
        go_right = (i % 2 == 0 and room_r >= w) or room_l < w
        if go_right and room_r >= w:
            plots.append(Plot("repo", right, w, repo))
            right += w + GAP
        elif room_l >= w:
            plots.append(Plot("repo", left - w, w, repo))
            left -= w + GAP
        else:
            overflow += 1
    plots.sort(key=lambda p: p.x)
    return Town(plots, overflow, (lo, hi))


# ---------------------------------------------------------------- drawing parts

def _window(L: Layer, c: Ctx, x: float, y: float, w: float, h: float, on: bool,
            frame: str, arched: bool = False) -> None:
    """One framed window with a sill; lit ones glow warm."""
    if on:
        L.rect(x - 1.5, y - 1.5, w + 3, h + 3, pal.WINDOW, opacity=0.16, rx=2)
    fill = pal.WINDOW if on else (c.lit("#9cbbe0") if not c.dark else "#231d3c")
    if arched:
        r = w / 2
        L.path(f"M{x:.1f} {y + h:.1f}v{-(h - r):.1f}a{r:.1f} {r:.1f} 0 0 1 {w:.1f} 0"
               f"v{h - r:.1f}z", fill, stroke=frame, stroke_width=0.8)
    else:
        L.rect(x, y, w, h, fill, stroke=frame, stroke_width=0.8)
        L.line(x, y + h * 0.45, x + w, y + h * 0.45, frame, 0.6)
    L.rect(x - 1, y + h, w + 2, 1.4, frame)


def _windows(L: Layer, c: Ctx, x: float, top: float, w: float, h: float, state: str,
             frame: str, arched: bool = False, shutters: str | None = None) -> None:
    cols = max(1, int((w - 6) // 10))
    rows = max(1, int((h - 8) // 14))
    p_lit = c.P["lit"] * (1.15 if state == "active" else 0.25 if state == "dormant" else 0.7)
    x0 = x + (w - cols * 10) / 2 + 2.25
    for r in range(rows):
        for k in range(cols):
            wx, wy = x0 + k * 10, top + 6 + r * 14
            if wy + 8 > top + h - 2:
                continue
            _window(L, c, wx, wy, 5.5, 8, c.rng.random() < p_lit, frame, arched)
            if shutters:
                L.rect(wx - 2.2, wy, 1.8, 8, shutters)
                L.rect(wx + 5.9, wy, 1.8, 8, shutters)


def _facade(L: Layer, c: Ctx, style: str, x: float, top: float, w: float, h: float,
            base: float, wall: str) -> float:
    """The wall's character, by style. Returns how far down the upper windows may go."""
    if style == "cottage":  # half-timbered upper floor
        beam = c.lit("#5a3f2e")
        mid = top + h * 0.5
        L.rect(x, mid - 1, w, 2, beam)
        for bx in (x, x + w / 2 - 1, x + w - 2):
            L.rect(bx, top, 2, mid - top, beam)
        L.line(x + 2, mid, x + w / 2 - 1, top + 1, beam, 1.1)
        L.line(x + w - 2, mid, x + w / 2 + 1, top + 1, beam, 1.1)
        return h - 12
    if style == "workshop":  # brick
        brick = pal.shade(wall, 0.78)
        tile = c.defs.pattern(f"brick-{c.phase}", 10, 8,
                              f'<path d="M0 3.6h10M0 7.6h10M3 0v3.6M8 4v3.6" stroke="{brick}" '
                              f'stroke-width=".8"/>')
        L.rect(x, top, w, h, tile)
        return h - 14
    if style == "bookshop":  # a shopfront with books in the window
        sign = c.lit("#2f5a4e")
        L.rect(x + 1, base - 24, w - 2, 5, sign)
        L.rect(x + 1, base - 24, w - 2, 5, "none", stroke=c.lit("#e8c46a"), stroke_width=0.6)
        for side in (0, 1):
            sx = x + 3 if side == 0 else x + w / 2 + 5
            sw = w / 2 - 8
            L.rect(sx, base - 16, sw, 12, pal.WINDOW if c.P["lamps"] else c.lit("#cfe6f0"),
                   stroke=c.lit("#f6f0e6"), stroke_width=0.8)
            for k in range(int(sw // 2.6)):
                col = c.lit(("#c9473f", "#3d5bb0", "#e8b440", "#3f7a6a")[k % 4])
                L.rect(sx + 1 + k * 2.6, base - 10 - (k % 3), 2, 6 + (k % 3), col)
        return h - 30
    if style == "lab":  # a glass curtain wall
        glass = c.defs.linear(f"labglass-{c.phase}", [(0, c.lit("#bfe4f2")), (1, c.lit("#6a8ab0"))])
        gx, gy, gw, gh = x + 3, top + 4, w - 6, h - 18
        L.rect(gx, gy, gw, gh, glass)
        grid = c.defs.pattern(f"labgrid-{c.phase}", 6, 8,
                              f'<path d="M0 0h6M0 0v8" stroke="{c.lit("#e8eef6")}" '
                              f'stroke-width=".7"/>')
        L.rect(gx, gy, gw, gh, grid)
        if c.P["lamps"]:
            for _ in range(3):
                fy = gy + 8 * c.rng.randrange(int(gh // 8))
                L.rect(gx, fy, gw, 8, "#ffe6a8", opacity=0.55)
        L.poly([(gx + gw * 0.2, gy), (gx + gw * 0.45, gy), (gx + gw * 0.1, gy + gh),
                (gx - 0.01, gy + gh)], "#ffffff", opacity=0.18)
        return 0
    if style == "observatory":  # dressed stone
        L.path("".join(f"M{x} {y:.0f}h{w}" for y in range(int(top + 7), int(base), 7)),
               stroke=pal.shade(wall, 0.85), stroke_width=0.6)
        return h - 12
    return h - 10


def _roof(L: Layer, c: Ctx, style: str, x: float, top: float, w: float, roof: str,
          chimney: bool, dormer: bool = False) -> float:
    """Draw the roof; returns the height of its highest point."""
    rim = c.P["rim"]
    if style == "observatory":
        r = w / 2 - 2
        L.path(f"M{x + 2} {top}a{r} {r} 0 0 1 {w - 4} 0z", roof)
        L.path(f"M{x + 2} {top}a{r} {r} 0 0 1 {r} {-r}", stroke=rim, stroke_width=1.2, opacity=0.9)
        L.rect(x + w / 2 - 2, top - r - 1, 4, r * 0.7, pal.shade(roof, 0.6))
        L.rect(x + w / 2 - 1.5, top - r - 8, 3, 10, c.lit("#c9c4dc"),
               transform=f"rotate(-32 {x + w / 2} {top - r})")
        return top - r - 8
    if style in ("lab", "bookshop"):
        L.rect(x - 2, top - 4, w + 4, 4, roof)
        L.line(x - 2, top - 4, x + w + 2, top - 4, rim, 1.2, opacity=0.9)
        if style == "lab":
            L.line(x + w - 8, top - 4, x + w - 8, top - 20, c.lit("#5a5a6a"), 1.2)
            L.circle(x + w - 8, top - 21, 1.6, "#ff4d4d", class_="av")
            return top - 22
        stripes = c.defs.pattern(f"awning-{c.phase}", 8, 8,
                                 f'<rect width="4" height="8" fill="{c.lit("#f2ead6")}"/>'
                                 f'<rect x="4" width="4" height="8" fill="{roof}"/>')
        L.poly([(x - 3, top + 12), (x + w + 3, top + 12), (x + w + 6, top + 20), (x - 6, top + 20)],
               stripes)
        return top - 4
    peak = top - w * 0.45
    if chimney:
        L.rect(x + w * 0.68, top - w * 0.4, 5, w * 0.3, pal.shade(roof, 0.7))
    L.poly([(x - 3, top), (x + w / 2, peak), (x + w + 3, top)], roof)
    tiles = pal.shade(roof, 0.72)
    y = top - 4.5
    while y > peak + 3:
        hw = (y - peak) / (top - peak) * (w / 2 + 3)
        L.line(x + w / 2 - hw, y, x + w / 2 + hw, y, tiles, 0.8, stroke_dasharray="3 1.2",
               opacity=0.8)
        y -= 4.5
    if dormer and w >= 40:
        dx, dy = x + w * 0.24, top - w * 0.14
        L.rect(dx, dy - 7, 9, 8, c.lit("#efe6d8"))
        L.poly([(dx - 1.5, dy - 7), (dx + 4.5, dy - 12), (dx + 10.5, dy - 7)], pal.shade(roof, 0.85))
        L.rect(dx + 2.5, dy - 5, 4, 4.5, pal.WINDOW if c.P["lamps"] else c.lit("#9cbbe0"))
    L.poly([(x + w / 2, peak), (x + w + 3, top), (x + w / 2, top)], "#000000", opacity=0.15)
    L.line(x - 3, top, x + w / 2, peak, rim, 1.2, opacity=0.9)
    return peak


def _vines(L: Layer, c: Ctx, x: float, top: float, w: float, base: float) -> None:
    col = c.lit("#4f8a46")
    for k in range(3):
        vx = x + 4 + k * (w - 8) / 2
        L.path(f"M{vx:.1f} {base}q{c.rng.uniform(-6, 6):.0f} {-(base - top) * 0.5:.0f} "
               f"{c.rng.uniform(-3, 3):.0f} {-(base - top) * 0.8:.0f}", stroke=col, stroke_width=1.6)
        for j in range(3):
            L.circle(vx + c.rng.uniform(-4, 4), base - (base - top) * (0.2 + j * 0.25), 2.2, col)


def building(L: Layer, c: Ctx, p: Plot, base: float, quest, labels: list[Label]) -> None:
    repo = p.repo
    style = style_for(repo)
    tier = tier_for(repo.commits)
    state = activity(repo, c.w.when)
    under_construction = quest is not None and quest.repo is repo
    w = p.w - (CRANE_ROOM if under_construction else 0)
    h = TIER_H[tier - 1]
    x, top = p.x, base - h
    wall, roof = c.lit(WALL[style]), c.lit(ROOF[style])
    if tier == 4:
        c.glow(L, x + w / 2, top + h / 2, w, "#ffe6a0", 0.35)
    L.rect(x, top, w, h, wall)
    window_h = _facade(L, c, style, x, top, w, h, base, wall)
    if tier >= 3 and style not in ("cottage", "lab"):
        L.rect(x, top + h * 0.5, w, 2, pal.shade(wall, 0.8))
    frame = c.lit("#f6f0e6") if style != "cottage" else c.lit("#fbf6ec")
    if window_h:
        _windows(L, c, x, top, w, window_h, state, frame, arched=style == "observatory",
                 shutters=c.lit("#3f7a5a") if style == "cottage" else None)
    L.rect(x, top, 2, h, c.P["rim"], opacity=0.25)
    L.rect(x + w * 0.7, top, w * 0.3, h, "#000000", opacity=0.16)
    L.rect(x - 1, base - 3, w + 2, 3, pal.shade(wall, 0.65))
    door = c.lit("#6b4a36")
    if style == "workshop":
        L.path(f"M{x + w / 2 - 7} {base}v-11a7 7 0 0 1 14 0v11z", door)
        L.path(f"M{x + w / 2 - 7} {base - 11}a7 7 0 0 1 14 0", stroke=c.lit("#d9c9a5"),
               stroke_width=1)
    else:
        L.rect(x + w / 2 - 3.5, base - 11, 7, 11, door, rx=1,
               stroke=c.lit("#f6f0e6"), stroke_width=0.6)
    lamp_x = x + w / 2 + (10 if style == "workshop" else 6)
    L.rect(lamp_x - 1, base - 13, 2, 3, "#ffd27a" if c.P["lamps"] else c.lit("#9a8a6a"))
    if c.P["lamps"]:
        c.glow(L, lamp_x, base - 11.5, 8, "#ffb35a", 0.7)
    chimney = style in ("cottage", "workshop")
    L.rect(x - 2, top - 1, w + 4, 2.4, pal.shade(wall, 0.72))
    peak = _roof(L, c, style, x, top, w, roof, chimney, dormer=tier >= 3)
    if tier == 4:
        L.line(x, top, x + w, top, "#e8b440", 1.6)
    if state == "dormant":
        _vines(L, c, x, top, w, base)
    if chimney and state == "active":
        cx = x + w * 0.68 + 2.5
        for k in range(3):
            L.circle(cx + k * 2, top - w * 0.42 - 6 - k * 6, 3 + k, "#e8e4f2", opacity=0.45,
                     class_="smoke", style=f"animation-delay:-{k}s")
    name = repo.name if len(repo.name) <= 14 else repo.name[:13] + "…"
    if under_construction:
        _construction(L, c, x, w, top, base, quest, labels)
    else:
        labels.append(Label(x + w / 2, peak - 6, name, "#ece8f8"))


def _construction(L: Layer, c: Ctx, x, w, top, base, quest, labels) -> None:
    steel = "#e08a3e"
    for z in (12, 24):
        L.line(x, top - z, x + w, top - z, steel, 1.2)
    for vx in (x, x + w / 2, x + w):
        L.line(vx, top, vx, top - 24, steel, 1.2)
    yellow = "#f2c230" if c.dark else c.lit("#f2c230")
    mx = x + w + 12
    jib = top - 70
    L.rect(mx, jib, 5, base - jib, "none", stroke=yellow, stroke_width=1)
    L.path("M" + "L".join(f"{mx + (5 if k % 2 else 0)} {jib + k * 6}"
                          for k in range(int((base - jib) / 6))), stroke=yellow, stroke_width=0.6)
    L.rect(x - 24, jib - 4, w + 70, 4, yellow)
    L.rect(mx + 18, jib, 12, 8, c.lit("#4a4a5a"))
    hook = Layer()
    hook.line(x + 6, jib, x + 6, top - 34, c.lit("#c9c4dc"), 0.7)
    hook.rect(x - 2, top - 34, 16, 4, steel)
    L.group(hook, class_="sway")
    L.circle(x - 24, jib - 4, 1.8, "#ff4d4d", class_="av")
    L.circle(x + w + 46, jib - 4, 1.8, "#ff4d4d", class_="av")
    text = f"{quest.repo.name} · TIER {quest.tier} · {quest.remaining} COMMITS TO GO"
    labels.append(Label(x + w / 2 + 10, jib - 12, text, "#ffd27a"))


def hq(L: Layer, c: Ctx, p: Plot, base: float, level: int, labels: list[Label]) -> None:
    """Your HQ: a town hall with a stone arcade, pilasters, arched windows and a clock that
    shows the time in Philly, with you, the cat and your companion on the roof terrace."""
    w, h = hq_size(level)
    x, top = p.x, base - h
    wall, stone = c.lit("#e8dfd0"), c.lit("#b9a68c")
    trim, frame = c.lit("#f8f2e8"), c.lit("#f8f2e8")
    ground_h = min(24, h * 0.3)
    L.rect(x, top, w, h, wall)
    bays = 5 if w < 80 else 7
    bay = w / bays
    floors = max(2, int((h - ground_h - 6) // 20))
    fh = (h - ground_h - 6) / floors
    clock_bay = bays // 2
    for f in range(floors):
        fy = top + 6 + f * fh
        L.rect(x - 1, fy + fh - 2, w + 2, 2, pal.shade(wall, 0.8))
        for k in range(bays):
            if f == 0 and k == clock_bay:
                continue
            on = c.rng.random() < c.P["lit"] * 1.1
            _window(L, c, x + k * bay + bay / 2 - 3, fy + 3, 6, fh - 8, on, frame, arched=True)
    for k in range(bays + 1):
        L.rect(x + k * bay - (1.5 if 0 < k < bays else 0 if k == 0 else 3), top + 4, 3,
               h - ground_h - 4, trim, opacity=0.9)
    # The clock, set to the time in Philly.
    cx, cy, r = x + w / 2, top + 6 + fh / 2, min(7.5, fh * 0.42, bay * 0.6)
    L.circle(cx, cy, r + 1.3, c.lit("#e8b440"))
    L.circle(cx, cy, r, "#fff6e0" if c.P["lamps"] else c.lit("#fbf6ec"))
    if c.P["lamps"]:
        c.glow(L, cx, cy, r * 3, "#ffe6a8", 0.5)
    for a in range(0, 360, 90):
        L.line(cx + math.sin(math.radians(a)) * r * 0.75, cy - math.cos(math.radians(a)) * r * 0.75,
               cx + math.sin(math.radians(a)) * r * 0.95, cy - math.cos(math.radians(a)) * r * 0.95,
               "#3a3050", 0.8)
    when = c.w.when
    for turn, ln, wd in (((when.hour % 12 + when.minute / 60) / 12, 0.5, 1.1),
                         (when.minute / 60, 0.8, 0.7)):
        a = math.tau * turn
        L.line(cx, cy, cx + math.sin(a) * r * ln, cy - math.cos(a) * r * ln, "#2a2440", wd)
    # The ground floor: a stone arcade with the door in the middle.
    gy = base - ground_h
    L.rect(x, gy, w, ground_h, stone)
    L.path("".join(f"M{x} {y:.0f}h{w}" for y in range(int(gy + 6), int(base), 6)),
           stroke=pal.shade(stone, 0.85), stroke_width=0.6)
    L.rect(x - 2, gy - 2, w + 4, 3, pal.shade(stone, 1.12))
    arches = 3 if w < 70 else 5
    for k in range(arches):
        ax = x + (k + 0.5) * w / arches
        aw = w / arches * 0.55
        door = k == arches // 2
        fill = c.lit("#4a3326") if door else (pal.WINDOW if c.P["lamps"] else c.lit("#9cbbe0"))
        ah = ground_h * 0.72
        L.path(f"M{ax - aw / 2:.1f} {base}v{-(ah - aw / 2):.1f}a{aw / 2:.1f} {aw / 2:.1f} 0 0 1 "
               f"{aw:.1f} 0v{ah - aw / 2:.1f}z", fill, stroke=trim, stroke_width=1)
        if door and c.P["lamps"]:
            for side in (-1, 1):
                c.glow(L, ax + side * (aw / 2 + 3), base - ah * 0.8, 9, "#ffb35a", 0.8)
    for side in (-1, 1):  # banners either side of the door
        bx = x + w / 2 + side * w / arches * 0.75
        L.path(f"M{bx - 3} {gy + 1}h6v13l-3 -3l-3 3z", c.lit("#5a6ab8"))
        L.circle(bx, gy + 6, 1.2, c.lit("#e8b440"))
    L.rect(x, top, 2, h, c.P["rim"], opacity=0.25)
    L.rect(x + w * 0.72, top, w * 0.28, h, "#000000", opacity=0.14)
    # Roof terrace.
    L.rect(x - 3, top - 3, w + 6, 3, c.lit("#3a3460"))
    L.line(x - 3, top - 3, x + w + 3, top - 3, c.P["rim"], 1.2)
    rail = c.lit("#3a3456")
    for k in range(int(w // 10) + 1):
        L.line(x + 2 + k * 10, top - 3, x + 2 + k * 10, top - 11, rail, 1)
    L.line(x, top - 11, x + w, top - 11, rail, 1.4)
    pole = x + w - 6
    L.line(pole, top - 3, pole, top - 44, rail, 1.4)
    L.path(f"M{pole} {top - 44}l16 4l-16 5z", "#e8b440")
    if level >= 6:
        L.rect(x + 8, top - 30, 18, 27, wall)
        L.poly([(x + 6, top - 30), (x + 17, top - 44), (x + 28, top - 30)], c.lit("#5a6ab8"))
    for end in (x + 4, x + w * 0.45):
        _string(L, c, (pole, top - 38), (end, top - 13), 10, 6)
    _you(L, c, x + w * 0.42, top - 3)
    companion(L, c, x + w * 0.7, top - 3, level)
    labels.append(Label(x + w / 2, top - 52, f"HQ · LEVEL {level}", "#ffffff"))


def _string(L: Layer, c: Ctx, a, b, sag: float, n: int) -> None:
    (x1, y1), (x2, y2) = a, b
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2 + sag
    L.path(f"M{x1} {y1}Q{mx} {my} {x2} {y2}", stroke=c.lit("#2a2440"), stroke_width=0.6)
    on = c.P["lamps"]
    for k in range(1, n):
        t = k / n
        x = (1 - t) ** 2 * x1 + 2 * (1 - t) * t * mx + t * t * x2
        y = (1 - t) ** 2 * y1 + 2 * (1 - t) * t * my + t * t * y2
        col = pal.LIGHTS[k % len(pal.LIGHTS)]
        if on:
            L.circle(x, y, 3.6, col, opacity=0.25, class_="fa" if k % 2 else "fb")
        L.circle(x, y, 1.3, col if on else pal.mix(col, "#888888", 0.5))


def _you(L: Layer, c: Ctx, x: float, y: float) -> None:
    """You, on the roof terrace with a laptop, and the cat asleep beside you."""
    body = "#2a2240" if c.dark else c.lit("#4a3f7a")
    hair = "#17131f"
    c.glow(L, x + 9, y - 8, 22, "#9fc4ff", 0.8 if c.dark else 0.35)
    L.path(f"M{x - 6} {y}q0 -12 6 -14q6 2 6 14z", body)
    L.circle(x, y - 18, 4.2, hair)
    L.path(f"M{x - 4.5} {y - 18}a4.5 4.5 0 0 1 9 0", stroke="#c9c4dc", stroke_width=1.2)
    L.poly([(x + 6, y - 4), (x + 15, y - 4), (x + 15, y - 12), (x + 7, y - 11)], "#bfd4ff")
    cat = "#e39a4f" if not c.dark else "#2a2034"
    L.path(f"M{x - 20} {y}q0 -6 6 -6q5 0 6 6z", cat)
    L.poly([(x - 19, y - 4), (x - 18, y - 9), (x - 15, y - 6)], cat)


def tree(L: Layer, c: Ctx, x: float, base: float, h: float) -> None:
    trunk = c.lit("#5a3f2e")
    L.rect(x - 1.5, base - h * 0.45, 3, h * 0.45, trunk)
    cols = TREES[season(c.w.when.month)]
    if not cols:  # bare winter branches, as one path
        L.path("".join(f"M{x:.1f} {base - h * 0.4:.1f}L{x + dx:.1f} {base - h * 0.75 + abs(dx):.1f}"
                       for dx in (-5, -2, 3, 6)), stroke=trunk, stroke_width=1)
        return
    for dx, dy, r in ((0, -0.68, 0.3), (-0.18, -0.52, 0.22), (0.18, -0.52, 0.22)):
        L.circle(x + dx * h, base + dy * h, r * h, c.lit(c.rng.choice(cols)))
    L.path(f"M{x - h * 0.28} {base - h * 0.78}a{h * 0.3} {h * 0.3} 0 0 1 {h * 0.46} -{h * 0.14}",
           stroke=c.P["rim"], stroke_width=1.1, opacity=0.7)


def windmill(L: Layer, c: Ctx, x: float, base: float) -> None:
    L.poly([(x - 9, base), (x - 5, base - 50), (x + 5, base - 50), (x + 9, base)], c.lit("#e8e0f0"))
    L.poly([(x - 7, base - 50), (x, base - 60), (x + 7, base - 50)], c.lit("#b5523f"))
    blades = Layer()
    for a in (0, 90, 180, 270):
        blades.rect(x - 1.5, base - 74, 3, 20, c.lit("#cfc8e2"), transform=f"rotate({a} {x} {base - 54})")
    L.group(blades, class_="spin")


def farm(L: Layer, c: Ctx, s: Shape) -> None:
    """A small field at the island's west end: one row of crops per 60 contributions this
    year (up to 4), changing with the season."""
    rows = max(1, min(4, c.w.stats.contributions_year // 60))
    crop = c.lit(CROPS[season(c.w.when.month)])
    soil = c.lit("#6a4a32")
    x0, x1 = s.x0 + 14, s.x0 + 40
    for k in range(rows):
        y = s.ground(x0) - 1 - k * 3
        L.rect(x0 + k * 2, y, x1 - x0 - k * 4, 3, soil)
        for x in range(int(x0 + 2 + k * 2), int(x1 - k * 2), 4):
            L.circle(x, y - 1, 1.8, crop)
    L.rect(x0 - 2, s.ground(x0) - 14, 1.2, 14, c.lit("#5a3f2e"))
    L.circle(x0 - 1.4, s.ground(x0) - 16, 2.6, c.lit("#c9a24a"))


def lanterns(L: Layer, c: Ctx, s: Shape, span: tuple[float, float]) -> None:
    """Iron street lamps along the main street."""
    on = c.P["lamps"]
    post = c.lit("#1f1a2a")
    x = span[0] - 10
    while x < span[1] + 20:
        base = s.ground(x) + 4
        L.path(f"M{x} {base}V{base - 16}q0 -3 4 -3", stroke=post, stroke_width=1.1)
        L.rect(x - 1.4, base - 2, 2.8, 2, post)
        L.path(f"M{x + 2.4} {base - 19}h3.2l-0.6 4h-2z", pal.WINDOW if on else c.lit("#c9b48a"))
        if on:
            c.glow(L, x + 4, base - 17, 12, "#ffb35a", 0.7, class_="flick",
                   style=f"animation-delay:-{int(x) % 7 * .3:.1f}s")
        x += 34


def verge(L: Layer, c: Ctx, s: Shape) -> None:
    """A strip of grass and bushes along the front that hides every building's footing."""
    xs = [s.x0 + 30 + k * (s.w - 60) / 40 for k in range(41)]
    top = "L".join(f"{x:.1f} {s.ground(x) + 2:.1f}" for x in xs)
    bottom = "L".join(f"{x:.1f} {s.ground(x) + 9:.1f}" for x in reversed(xs))
    L.path(f"M{top}L{bottom}Z", pal.shade(c.P["grass"], 0.85))
    for x in xs[::3]:
        L.circle(x + c.rng.uniform(-4, 4), s.ground(x) + 3, c.rng.uniform(3, 5),
                 pal.shade(c.P["grass"], c.rng.uniform(0.75, 0.95)))
    flowers = FLOWERS[season(c.w.when.month)]
    if flowers:
        for _ in range(60):
            x = c.rng.uniform(s.x0 + 40, s.x1 - 40)
            L.circle(x, s.ground(x) + c.rng.uniform(2, 8), 1.1, c.lit(c.rng.choice(flowers)))


def hedges(L: Layer, c: Ctx, s: Shape) -> None:
    """A soft row of bushes along the back of the ridge, behind everything built."""
    x = s.x0 + 40
    while x < s.x1 - 40:
        r = c.rng.uniform(6, 11)
        L.circle(x, s.ground(x) - r * 0.4, r, pal.shade(c.P["grass"], c.rng.uniform(0.7, 0.9)))
        x += r * 1.3


def back_row(L: Layer, c: Ctx, s: Shape) -> None:
    """Small houses and rooftops behind the main street, a little hazy, for depth."""
    x = s.x0 + 66
    while x < s.x1 - 46:
        w, h = c.rng.uniform(14, 24), c.rng.uniform(16, 34)
        base = s.ground(x) - 2
        wall = c.haze(c.lit(c.rng.choice(("#e6dccb", "#d4cbe0", "#e2cdb4"))), 0.25)
        roof = c.haze(c.lit(c.rng.choice(("#9a4a3a", "#4a5a8a", "#6a5a4a"))), 0.25)
        L.rect(x, base - h, w, h, wall)
        L.poly([(x - 2, base - h), (x + w / 2, base - h - w * 0.4), (x + w + 2, base - h)], roof)
        if c.rng.random() < c.P["lit"]:
            L.rect(x + w / 2 - 2, base - h + 5, 4, 5, pal.WINDOW, opacity=0.85)
        x += w + c.rng.uniform(2, 8)


def stall(L: Layer, c: Ctx, x: float, base: float) -> None:
    """A market stall with a striped awning and crates of produce."""
    awning = c.defs.pattern(f"stall-{c.phase}", 6, 6,
                            f'<rect width="3" height="6" fill="{c.lit("#f2ead6")}"/>'
                            f'<rect x="3" width="3" height="6" fill="{c.lit("#c9473f")}"/>')
    L.rect(x - 9, base - 9, 18, 9, c.lit("#8a5a3a"))
    L.line(x - 9, base - 9, x - 9, base - 20, c.lit("#5a3f2e"), 1)
    L.line(x + 9, base - 9, x + 9, base - 20, c.lit("#5a3f2e"), 1)
    L.poly([(x - 12, base - 18), (x + 12, base - 18), (x + 10, base - 23), (x - 10, base - 23)], awning)
    for k, col in enumerate(("#e8873a", "#9ad67a", "#e2574c")):
        L.circle(x - 5 + k * 5, base - 10, 2, c.lit(col))
    if c.P["lamps"]:
        c.glow(L, x, base - 14, 14, "#ffb35a", 0.6)


def bench(L: Layer, c: Ctx, x: float, base: float) -> None:
    wood = c.lit("#7a5236")
    L.rect(x - 7, base - 5, 14, 1.6, wood)
    L.rect(x - 7, base - 9, 14, 1.4, wood)
    L.line(x - 6, base - 5, x - 6, base, wood, 1)
    L.line(x + 6, base - 5, x + 6, base, wood, 1)


def villagers(L: Layer, c: Ctx, s: Shape, span: tuple[float, float]) -> None:
    """A few people strolling along the main street."""
    shirts = ("#3d5bb0", "#e2574c", "#e8b440", "#3db0a0")
    for k in range(4):
        x = c.rng.uniform(span[0] + 10, span[1] - 50)
        base = s.ground(x) + 4
        g = Layer()
        g.circle(x, base - 9, 2, c.lit("#f2c9a8"))
        g.rect(x - 2, base - 7, 4, 5, c.lit(shirts[k]), rx=1)
        g.line(x - 1, base - 2, x - 1, base, c.lit("#2a2440"), 1)
        g.line(x + 1, base - 2, x + 1, base, c.lit("#2a2440"), 1)
        L.group(g, class_="walk", style=f"animation-duration:{14 + k * 4}s;"
                                        f"animation-delay:-{k * 3}s")


def draw(L: Layer, c: Ctx, s: Shape) -> list[Label]:
    stats = c.w.stats
    level = level_info(stats.contributions_total).level
    town = plan(stats.repos, level, s)
    quest = current_quest(stats.repos)
    labels: list[Label] = []
    back_row(L, c, s)
    hedges(L, c, s)
    farm(L, c, s)
    windmill(L, c, s.x0 + 48, s.ground(s.x0 + 48) + 3)
    # Gaps between buildings get a tree, a market stall or a bench.
    edges = [town.span[0] - 10] + [v for p in town.plots for v in (p.x, p.x + p.w)] + [town.span[1]]
    k = 0
    for a, b in zip(edges[::2], edges[1::2], strict=False):
        if b - a < 14:
            continue
        n = int((b - a) // 22) + 1
        for j in range(n):
            x = a + (b - a) * (j + 0.5) / n
            base = s.ground(x) + 3
            kind = ("tree", "stall", "tree", "bench")[k % 4] if b - a >= 24 else "tree"
            if kind == "stall":
                stall(L, c, x, base)
            elif kind == "bench":
                tree(L, c, x - 6, base, c.rng.uniform(22, 28))
                bench(L, c, x + 5, base)
            else:
                tree(L, c, x, base, c.rng.uniform(24, 34))
            k += 1
    for p in town.plots:
        base = s.ground(p.x + p.w / 2) + 3
        if p.kind == "hq":
            hq(L, c, p, base, level, labels)
        else:
            building(L, c, p, base, quest, labels)
    lanterns(L, c, s, town.span)
    holidays.town(L, c, s, town.span)
    villagers(L, c, s, town.span)
    verge(L, c, s)
    if town.overflow:
        x = town.span[1] + 8
        labels.append(Label(x, s.ground(x) - 30, f"+{town.overflow} MORE", "#cfc6ea"))
    return labels
