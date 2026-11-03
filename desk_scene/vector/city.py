"""The Philadelphia skyline across the river, the towers your contributions build,
Boathouse Row, and the river reflecting all of it."""

from __future__ import annotations

from dataclasses import dataclass

from .. import palette as pal
from ..growth import LOTS, TOWER_FLOORS, tower_progress
from .layout import GX0, GX1, GY0, GY1, HORIZON, WATER_Y, Ctx
from .svg import Layer, Rects

GRID_X, GRID_Y = 5, 6  # window spacing shared by every building
FLOOR_H = 5.5
# Where each of your towers stands (x, width); one lot per milestone in growth.LOTS.
VLOTS = ((172, 34), (470, 34), (568, 30))
assert len(VLOTS) == len(LOTS)


@dataclass
class Tag:
    """A small label pinned above something in the view."""

    x: float
    y: float
    text: str
    color: str


# ---------------------------------------------------------------- building parts

def _window_patterns(c: Ctx) -> dict[str, str]:
    """Pattern fills for unlit windows on stone and glass buildings."""
    P = c.P
    day = not c.dark
    stone_win = c.out("#5b6b80") if day else pal.mix(P["base"], "#000000", 0.35)
    glass_line = pal.mix(P["glass2"], "#ffffff", 0.18) if day else pal.mix(P["base"], "#000000", 0.3)
    out = {}
    for kind, col in (("stone", stone_win), ("glass", glass_line)):
        pid = f"win-{kind}-{c.phase}"
        if kind == "stone" or c.dark:
            cell = f'<rect x="1.3" y="1.4" width="2.4" height="3.2" fill="{col}"/>'
        else:
            # Daytime glass shows floor lines and mullions instead of separate windows.
            cell = (f'<rect y="5" width="{GRID_X}" height=".7" fill="{col}"/>'
                    f'<rect x="4.4" width=".5" height="{GRID_Y}" fill="{col}" opacity=".6"/>')
        out[kind] = c.defs.pattern(pid, GRID_X, GRID_Y, cell)
    return out


def _lit(R: Rects, c: Ctx, x: float, top: float, w: float, h: float, ratio: float = 1.0,
         pad: float = 3) -> None:
    """Light some of the windows inside a box, snapped to the shared window grid."""
    if not c.P["lit"]:
        return
    colors = c.P["lit"]
    x0 = (int((x + pad) // GRID_X) + 1) * GRID_X
    y0 = (int((top + pad) // GRID_Y) + 1) * GRID_Y
    gx = x0
    while gx + 4 <= x + w - pad:
        gy = y0
        while gy + 5 <= top + h - 1:
            if c.rng.random() < c.P["lit_ratio"] * ratio:
                col = c.rng.choice(colors)
                light = c.team_light(int(gx + gy))
                if light and c.rng.random() < 0.18:
                    col = light
                R.add(gx + 1.3, gy + 1.4, 2.4, 3.2, col)
            gy += GRID_Y
        gx += GRID_X


def _body(L: Layer, R: Rects, c: Ctx, x: float, top: float, w: float, kind: str,
          pats: dict[str, str], base: float = HORIZON, ratio: float = 1.0,
          colors: tuple[str, str] | None = None) -> None:
    """A plain tower block with shading and windows."""
    P = c.P
    h = base - top
    if colors:
        light, dark = colors
    elif kind == "glass":
        light, dark = P["glass"], P["glass2"]
    else:
        light, dark = P["base"], P["shade"]
    if c.phase == "night" and kind == "glass" and not colors:
        light, dark = P["base"], P["shade"]
    fill = c.defs.linear(f"b-{light[1:]}-{dark[1:]}", [(0, light), (1, dark)], x2=1, y2=0)
    L.rect(x, top, w, h, fill)
    L.rect(x + 2, top + 2, w - 4, h - 2, pats[kind])
    L.rect(x, top, 0.8, h, P["edge"], opacity=0.5)
    _lit(R, c, x, top, w, h, ratio)


def _tank(L: Layer, c: Ctx, x: float, top: float) -> None:
    """A wooden rooftop water tank, a fixture of older Philly roofs."""
    col = c.out("#6b4a34")
    L.rect(x + 1, top - 4, 1, 4, col)
    L.rect(x + 7, top - 4, 1, 4, col)
    L.rect(x, top - 11, 9, 7, col)
    L.poly([(x - 0.5, top - 11), (x + 4.5, top - 15), (x + 9.5, top - 11)], c.out("#4e3524"))
    L.rect(x, top - 9, 9, 0.6, c.out("#3a281b"))
    L.rect(x, top - 6, 9, 0.6, c.out("#3a281b"))


def _crown_color(c: Ctx, i: int = 0) -> str:
    return c.team_light(i) or c.P["crown"]


# ---------------------------------------------------------------- landmarks

def _far(L: Layer, c: Ctx) -> None:
    far = c.P["far"]
    x = GX0
    while x < GX1:
        w = c.rng.uniform(10, 24)
        h = c.rng.uniform(16, 52)
        L.rect(x, HORIZON - h, w + 0.5, h, far)
        if c.dark:
            for _ in range(int(h // 9)):
                L.rect(x + c.rng.uniform(2, w - 3), HORIZON - c.rng.uniform(4, h - 3), 1.6, 2,
                       c.rng.choice(c.P["lit"]), opacity=0.55)
        x += w


def _cira(L: Layer, R: Rects, c: Ctx, pats: dict, x: float = 74, w: float = 40,
          h: float = 98) -> None:
    """Cira Centre: angular glass facets, with an LED facade that shows messages at night."""
    P = c.P
    top = HORIZON - h
    shape = [(x, HORIZON), (x, top + 22), (x + w * 0.58, top), (x + w, top + 30), (x + w, HORIZON)]
    L.poly(shape, c.defs.linear("cira", [(0, P["glass"]), (1, P["glass2"])], x2=1, y2=0))
    L.poly([(x + w * 0.58, top), (x + w, top + 30), (x + w, HORIZON), (x + w * 0.58, HORIZON)],
           P["shade"], opacity=0.35)
    L.rect(x + 2, top + 30, w - 4, h - 32, pats["glass"])
    _lit(R, c, x, top + 56, w, h - 56, 0.6)  # keep clear of the LED sign
    if c.dark:
        g = c.games
        msg = pal.TEAMS[g[0].team]["cheer"] if g else f"{c.s.stats.contributions_year}"
        col = c.team_light(0) or "#7fd7ff"
        L.rect(x + 2, top + 40, w - 4, 12, "#050914", opacity=0.75)
        L.text(x + w / 2, top + 49, msg, 6.4, col, text_anchor="middle", font_weight="700")


def _fmc(L: Layer, R: Rects, c: Ctx, pats: dict, x: float = 136, w: float = 26,
         h: float = 130) -> None:
    top = HORIZON - h
    _body(L, R, c, x, top + 10, w, "glass", pats)
    L.rect(x + 3, top, w - 6, 10, c.P["glass2"])
    L.rect(x + 3, top, w - 6, 1.2, c.P["edge"])
    if c.dark:
        L.rect(x + 4, top + 3, w - 8, 3, _crown_color(c, 1), opacity=0.8)


def _liberty(L: Layer, R: Rects, c: Ctx, pats: dict, x: float, w: float, h: float,
             spire: float, i: int) -> None:
    """One and Two Liberty Place: setbacks topped by a striped, gabled crown and a spire."""
    P = c.P
    top = HORIZON - h
    crown_base = top + h * 0.2
    _body(L, R, c, x, crown_base + 10, w, "glass", pats)
    L.rect(x + 2, crown_base + 4, w - 4, 6, P["glass2"])
    L.rect(x + 4, crown_base, w - 8, 4, P["glass2"])
    cx = x + w / 2
    L.poly([(x + 4, crown_base), (cx, top), (x + w - 4, crown_base)], P["glass"])
    L.poly([(cx, top), (x + w - 4, crown_base), (cx, crown_base)], P["shade"], opacity=0.4)
    stripe = _crown_color(c, i) if c.dark else P["edge"]
    for k in range(1, 6):
        t = k / 6
        y = top + (crown_base - top) * t
        half = (w / 2 - 4) * t
        L.line(cx - half, y, cx + half, y, stripe, 0.9, opacity=0.95 if c.dark else 0.6)
    L.line(cx, top, cx, top - spire, P["edge"] if not c.dark else stripe, 1.1)
    if c.dark:
        L.circle(cx, top - spire, 1.2, "#ff4d4d", class_="av")


def _bny(L: Layer, R: Rects, c: Ctx, pats: dict, x: float = 322, w: float = 30,
         h: float = 146) -> None:
    """BNY Mellon Center: granite with a stepped, lit pyramid crown."""
    P = c.P
    top = HORIZON - h
    _body(L, R, c, x, top + 22, w, "stone", pats)
    for k, inset in enumerate((2, 5, 8)):
        L.rect(x + inset, top + 22 - (k + 1) * 5, w - 2 * inset, 5, P["shade"] if k % 2 else P["base"])
    L.poly([(x + 10, top + 7), (x + w / 2, top), (x + w - 10, top + 7)], P["base"])
    if c.dark:
        col = _crown_color(c, 2)
        for k, inset in enumerate((2, 5, 8)):
            L.rect(x + inset, top + 22 - (k + 1) * 5, w - 2 * inset, 0.9, col, opacity=0.9)


def _comcast_center(L: Layer, R: Rects, c: Ctx, pats: dict, x: float = 362, w: float = 34,
                    h: float = 168) -> None:
    P = c.P
    top = HORIZON - h
    _body(L, R, c, x, top + 8, w, "glass", pats)
    L.poly([(x, top + 8), (x + 6, top), (x + w, top), (x + w, top + 8)], P["glass2"])
    L.line(x + 6, top, x + w, top, P["edge"], 1)
    L.rect(x + w * 0.35, top + 8, 0.8, h - 8, P["edge"], opacity=0.35)
    if c.dark:
        L.rect(x + 7, top + 2, w - 9, 2.5, _crown_color(c, 0), opacity=0.85)


def _comcast_tech(L: Layer, R: Rects, c: Ctx, pats: dict, x: float = 402, w: float = 38,
                  h: float = 188) -> None:
    """Comcast Technology Center: the tallest, with an open, lantern-like crown."""
    P = c.P
    top = HORIZON - h
    _body(L, R, c, x, top + 22, w, "glass", pats)
    L.rect(x, top, w, 22, P["glass2"])
    L.rect(x + 3, top + 4, w - 6, 15, pal.mix(P["sky"][1], P["glass2"], 0.4))
    glow = _crown_color(c, 1) if c.dark else P["edge"]
    for k in range(3):
        L.rect(x + 3, top + 6 + k * 4.5, w - 6, 1.2, glow, opacity=0.9 if c.dark else 0.45)
    L.rect(x, top, w, 1.4, P["edge"])
    L.rect(x + w * 0.5, top + 22, 0.8, h - 22, P["edge"], opacity=0.3)
    if c.dark:
        L.circle(x + 3, top - 1, 1.2, "#ff4d4d", class_="av")
        L.circle(x + w - 3, top - 1, 1.2, "#ff4d4d", class_="av", style="animation-delay:-.8s")


def _psfs(L: Layer, R: Rects, c: Ctx, pats: dict, x: float = 536, w: float = 26,
          h: float = 108) -> None:
    """The PSFS building and its red rooftop sign."""
    top = HORIZON - h
    _body(L, R, c, x, top + 14, w, "stone", pats, colors=(c.out("#5b5f6b"), c.out("#41444f")))
    L.rect(x + 3, top + 14, 2, h - 14, c.out("#7a7e8a"), opacity=0.6)
    L.rect(x + 8, top + 2, 1, 12, c.out("#2f3138"))
    L.rect(x + w - 9, top + 2, 1, 12, c.out("#2f3138"))
    L.rect(x - 2, top - 8, w + 4, 10, "#1b0a0c" if c.dark else c.out("#3a3d46"))
    red = "#ff3b3b" if c.dark else c.out("#c8312f")
    L.text(x + w / 2, top, "PSFS", 8.5, red, text_anchor="middle", font_weight="700",
           letter_spacing=0.6)


def _city_hall(L: Layer, R: Rects, c: Ctx) -> None:
    """City Hall with its clock tower, dome and the statue of William Penn on top."""
    P = c.P
    stone, dark = P["stone"], P["stone_shade"]
    bx, bw, bh = 300, 86, 32
    L.rect(bx, HORIZON - bh, bw, bh, stone)
    L.rect(bx, HORIZON - bh, bw, 2.5, dark)
    for k in range(int(bw // 6)):
        L.rect(bx + 3 + k * 6, HORIZON - bh + 7, 2.2, 5, dark)
        L.rect(bx + 3 + k * 6, HORIZON - bh + 17, 2.2, 5, dark)
    for px in (bx, bx + bw - 12):  # corner pavilions
        L.rect(px, HORIZON - bh - 8, 12, 8, stone)
        L.poly([(px - 1, HORIZON - bh - 8), (px + 6, HORIZON - bh - 13), (px + 13, HORIZON - bh - 8)],
               dark)
    cx = 343
    sw = 16
    shaft_top = HORIZON - 112
    L.rect(cx - sw / 2, shaft_top, sw, HORIZON - bh - shaft_top, stone)
    L.rect(cx + 2, shaft_top, sw / 2 - 2, HORIZON - bh - shaft_top, dark, opacity=0.5)
    for k in range(5):
        L.rect(cx - 4, shaft_top + 14 + k * 14, 2, 7, dark)
        L.rect(cx + 2, shaft_top + 14 + k * 14, 2, 7, dark)
    # Clock stage.
    L.rect(cx - 11, shaft_top - 16, 22, 16, stone)
    L.rect(cx - 11, shaft_top - 16, 22, 1.5, dark)
    L.circle(cx, shaft_top - 8, 5, P["clock"])
    L.line(cx, shaft_top - 8, cx, shaft_top - 11.5, dark, 0.8)
    L.line(cx, shaft_top - 8, cx + 2.5, shaft_top - 8, dark, 0.8)
    if c.dark:
        L.circle(cx, shaft_top - 8, 9, c.defs.radial(
            "clockglow", [(0, "#fff1b0", 0.6), (1, "#fff1b0", 0)]))
    # Drum, dome and the statue.
    L.rect(cx - 8, shaft_top - 24, 16, 8, dark)
    L.rect(cx - 6, shaft_top - 23, 1.5, 6, stone)
    L.rect(cx + 4.5, shaft_top - 23, 1.5, 6, stone)
    L.path(f"M{cx - 8} {shaft_top - 24}q8 -16 16 0z", stone)
    L.rect(cx - 1, shaft_top - 37, 2, 3, P["bronze"])
    L.path(f"M{cx - 1.6} {shaft_top - 34}h3.2l-.6 -5h-2z", P["bronze"])
    L.circle(cx, shaft_top - 40, 1.4, P["bronze"])
    L.rect(cx - 2.6, shaft_top - 38.5, 5.2, 0.9, P["bronze"])
    if c.dark:
        flood = c.defs.radial("hallflood", [(0, "#ffe7a8", 0.32), (1, "#ffe7a8", 0)])
        L.ellipse(cx, shaft_top + 10, 26, 70, flood)


def _generic(L: Layer, R: Rects, c: Ctx, pats: dict, x: float, w: float, h: float, kind: str,
             roof: str | None) -> None:
    top = HORIZON - h
    _body(L, R, c, x, top, w, kind, pats, ratio=0.8)
    if roof == "tank":
        _tank(L, c, x + w / 2 - 4.5, top)
    elif roof == "step":
        L.rect(x + 3, top - 6, w - 6, 6, c.P["shade"])
        L.rect(x + 6, top - 10, w - 12, 4, c.P["base"])


GENERICS = (
    (48, 24, 62, "stone", "tank"), (116, 18, 80, "glass", None), (208, 22, 94, "stone", "tank"),
    (298, 20, 112, "glass", None), (444, 22, 98, "stone", "step"), (506, 26, 86, "glass", None),
    (600, 30, 70, "stone", "tank"),
)


# ---------------------------------------------------------------- your towers

def _tower_palette(c: Ctx) -> tuple[str, str]:
    if c.phase == "night":
        return c.P["base"], c.P["shade"]
    return c.out("#78b8c8"), c.out("#4f8c9f")


def _finished(L: Layer, R: Rects, c: Ctx, pats: dict, x: float, w: float, n: int,
              tags: list[Tag]) -> None:
    top = HORIZON - TOWER_FLOORS * FLOOR_H
    _body(L, R, c, x, top, w, "glass", pats, colors=_tower_palette(c), ratio=1.2)
    crown_top = top - 16
    L.rect(x + 3, crown_top, w - 6, 16, c.P["shade"])
    L.rect(x + 3, crown_top, w - 6, 1.2, c.P["edge"])
    glow = _crown_color(c, n) if c.dark else c.out("#f2f5fa")
    L.text(x + w / 2, crown_top + 11.5, c.s.monogram, 9, glow, text_anchor="middle",
           font_weight="800", letter_spacing=1)
    L.line(x + w / 2, crown_top, x + w / 2, crown_top - 12, c.P["edge"], 1)
    if c.dark:
        L.circle(x + w / 2, crown_top - 12, 1.3, "#ff4d4d", class_="av")
    tags.append(Tag(x + w / 2, crown_top - 16, f"TOWER {n + 1} · BUILT", "#3fb950"))


def _construction(L: Layer, R: Rects, c: Ctx, pats: dict, x: float, w: float, floors: int,
                  tags: list[Tag]) -> None:
    P = c.P
    steel = c.out("#c9772f") if not c.dark else "#d58a3e"
    framed = min(3, floors)
    glazed = floors - framed
    glass_top = HORIZON - glazed * FLOOR_H
    if glazed:
        _body(L, R, c, x, glass_top, w, "glass", pats, colors=_tower_palette(c), ratio=0.7)
    frame_top = glass_top - framed * FLOOR_H
    for k in range(framed):
        y = glass_top - (k + 1) * FLOOR_H
        L.rect(x, y + FLOOR_H - 1, w, 1, P["shade"])
        for col_x in range(int(x), int(x + w) + 1, 6):
            L.rect(min(col_x, x + w - 1), y, 1, FLOOR_H, steel)
    # Concrete core rising above the steel.
    core = c.out("#a9a39a") if not c.dark else P["stone_shade"]
    L.rect(x + w / 2 - 4, frame_top - 6, 8, 6, core)

    # Crane: lattice mast beside the tower, jib reaching back over it.
    yellow = "#f2c230" if c.dark else c.out("#f2c230")
    mx = x + w + 6
    jib_y = max(GY0 + 14, frame_top - 26)
    L.rect(mx, jib_y, 5, HORIZON - jib_y, "none", stroke=yellow, stroke_width=0.9)
    zig = "".join(f"L{mx + (5 if k % 2 else 0)} {jib_y + k * 5}" for k in range(
        int((HORIZON - jib_y) / 5) + 1))
    L.path(f"M{mx} {jib_y}{zig}", stroke=yellow, stroke_width=0.6)
    jl, jr = x - 14, mx + 30
    L.rect(jl, jib_y, jr - jl, 3, "none", stroke=yellow, stroke_width=0.9)
    L.path(f"M{mx - 2} {jib_y}L{mx + 2.5} {jib_y - 12}L{mx + 7} {jib_y}", stroke=yellow,
           stroke_width=0.9)
    L.line(mx + 2.5, jib_y - 12, jl + 4, jib_y, yellow, 0.5)
    L.line(mx + 2.5, jib_y - 12, jr - 2, jib_y, yellow, 0.5)
    L.rect(jr - 9, jib_y + 3, 8, 6, c.out("#8a8f98"))
    L.rect(mx - 1, jib_y + 3, 7, 6, yellow)
    L.rect(mx + 3, jib_y + 4, 2.5, 2.5, "#bfe3ff" if not c.dark else "#ffe9a8")
    trolley = x + w * 0.35
    hook = Layer()
    hook.line(trolley, jib_y + 3, trolley, frame_top - 12, c.out("#3b3f48"), 0.6)
    hook.rect(trolley - 6, frame_top - 12, 12, 2.4, steel)
    L.group(hook, class_="sway")
    if c.dark:
        for ax in (jl + 1, jr - 1):
            L.circle(ax, jib_y - 0.5, 1.3, "#ff4d4d", class_="av")
        flood = c.defs.radial("craneflood", [(0, "#fff3c4", 0.3), (1, "#fff3c4", 0)])
        L.ellipse(x + w / 2, frame_top + 6, w, 22, flood)
    label = f"BUILDING {c.s.stats.now_building} · {floors}/{TOWER_FLOORS} FL"
    tags.append(Tag((jl + jr) / 2, jib_y - 18, label, "#e3b341"))


def towers(L: Layer, R: Rects, c: Ctx, pats: dict, tags: list[Tag]) -> None:
    done, floors = tower_progress(c.s.stats.contributions_total)
    for n, (x, w) in enumerate(VLOTS):
        if n < done:
            _finished(L, R, c, pats, x, w, n, tags)
        elif n == done:
            _construction(L, R, c, pats, x, w, floors, tags)


# ---------------------------------------------------------------- bank, boathouses, river

def _trees(L: Layer, c: Ctx) -> None:
    leaves = [c.out(t) for t in pal.TREES[c.season]]
    trunk = c.out("#4a3a2c")
    x = GX0 - 4
    while x < GX1 + 4:
        y = HORIZON + c.rng.uniform(2, 6)
        L.rect(x - 0.6, y, 1.2, 9, trunk)
        if leaves:
            for _ in range(3):
                L.circle(x + c.rng.uniform(-3, 3), y + c.rng.uniform(-3, 2), c.rng.uniform(3.5, 5.5),
                         c.rng.choice(leaves))
        else:
            for dx in (-4, -2, 2, 4):
                L.line(x, y + 4, x + dx, y - 3 + abs(dx) / 2, trunk, 0.7)
        x += c.rng.uniform(7, 12)


HOUSES = (  # x, width, height, colour, turret
    (58, 30, 16, "#d8cdb6", False), (90, 26, 19, "#a8503c", True), (118, 34, 15, "#cfc7b4", False),
    (154, 24, 20, "#8c8a86", True), (180, 32, 17, "#d9c39a", False), (214, 28, 18, "#b6563f", False),
    (244, 30, 21, "#cbbfa8", True), (276, 26, 15, "#9a958c", False), (304, 32, 18, "#dcd2bd", False),
)


def _house_outline(x: float, w: float, h: float, turret: bool) -> str:
    base = WATER_Y
    roof = base - h
    peak = roof - h * 0.55
    d = f"M{x} {base}V{roof}L{x + w / 2} {peak}L{x + w} {roof}V{base}"
    if turret:
        tx = x + w - 7
        d += f"M{tx} {roof}V{peak - 2}L{tx + 3} {peak - 9}L{tx + 6} {peak - 2}V{roof - 1}"
    return d


def boathouses(L: Layer, c: Ctx, tags: list[Tag]) -> None:
    """Boathouse Row; one house is outlined in lights for each public repo."""
    repos = c.s.stats.repo_count
    for i, (x, w, h, col, turret) in enumerate(HOUSES):
        base, roof = WATER_Y, WATER_Y - h
        peak = roof - h * 0.55
        body = c.out(col)
        L.rect(x, roof, w, h, body)
        L.poly([(x - 1.5, roof + 0.5), (x + w / 2, peak), (x + w + 1.5, roof + 0.5)],
               c.out("#3f3a3a"))
        if turret:
            tx = x + w - 7
            L.rect(tx, peak - 2, 6, roof - peak + 2, body)
            L.poly([(tx - 0.8, peak - 2), (tx + 3, peak - 9), (tx + 6.8, peak - 2)], c.out("#3f3a3a"))
        win = "#ffe2a0" if c.dark and i < repos else c.out("#4a4f5c")
        for k in range(int(w // 7)):
            L.rect(x + 3 + k * 7, roof + 4, 3, 5, win)
        L.rect(x + w / 2 - 3, base - 6, 6, 6, c.out("#3a2f2a"))
        if c.dark and i < repos:
            light = c.team_light(i) or (
                pal.HOLIDAY_LIGHTS[i % 4] if c.december else pal.WARM_LIGHT)
            d = _house_outline(x, w, h, turret)
            L.path(d, stroke=light, stroke_width=3, opacity=0.25, stroke_linejoin="round")
            L.path(d, stroke=light, stroke_width=1.3, stroke_dasharray="0.1 2.4",
                   stroke_linecap="round", stroke_linejoin="round")
    lit = min(repos, len(HOUSES))
    if c.dark:
        tags.append(Tag(186, WATER_Y - 42, f"BOATHOUSE ROW · {lit} REPOS LIT", "#79c0ff"))
    else:
        tags.append(Tag(186, WATER_Y - 42, f"BOATHOUSE ROW · {repos} REPOS", "#79c0ff"))
    L.rect(GX0, WATER_Y - 1, GX1 - GX0, 1.5, c.out("#6f6a60"))


def bank(L: Layer, c: Ctx) -> None:
    grass = c.out(pal.GRASS[c.season])
    if c.s.weather == "snow":
        grass = c.out("#e8eef5")
    L.rect(GX0, HORIZON - 1, GX1 - GX0, 3, c.out("#4b4f58"))
    L.rect(GX0, HORIZON + 2, GX1 - GX0, WATER_Y - HORIZON - 2, grass)
    _trees(L, c)


def river(L: Layer, c: Ctx) -> None:
    water = c.P["water"]
    fill = c.defs.linear(f"water-{c.phase}", [(0, water[0]), (0.5, water[1]), (1, water[2])])
    clip = c.defs.clip("river", f'<rect x="{GX0}" y="{WATER_Y}" width="{GX1 - GX0}" '
                                f'height="{GY1 - WATER_Y}"/>')
    g = Layer()
    g.rect(GX0, WATER_Y, GX1 - GX0, GY1 - WATER_Y, fill)
    g.raw(f'<use href="#city" transform="matrix(1 0 0 -1 0 {2 * WATER_Y})" opacity=".42"/>')
    g.rect(GX0, WATER_Y, GX1 - GX0, GY1 - WATER_Y,
           c.defs.linear(f"waterfade-{c.phase}", [(0, water[1], 0.1), (1, water[2], 0.85)]))
    shimmer, moving = Layer(), Layer()
    hi = pal.mix(water[0], "#ffffff", 0.35)
    for i in range(60):
        y = c.rng.uniform(WATER_Y + 3, GY1 - 2)
        x = c.rng.uniform(GX0, GX1)
        w = c.rng.uniform(4, 16) * (1 + (y - WATER_Y) / 60)
        (moving if i % 3 == 0 else shimmer).rect(x, y, w, 0.7, hi, opacity=0.35)
    g.add(shimmer)
    g.group(moving, class_="rip")
    _scull(g, c)
    L.group(g, clip_path=clip)


def _scull(L: Layer, c: Ctx) -> None:
    """A rowing crew, a common sight on the Schuylkill."""
    hull = c.out("#e8e2d0") if not c.dark else "#3a4466"
    oar = c.out("#3b3f48") if not c.dark else "#2a3150"
    b = Layer()
    y = WATER_Y + 30
    b.path(f"M0 {y}h46l-4 2h-38z", hull)
    for k in range(4):
        ox = 8 + k * 9
        b.circle(ox, y - 2, 1.6, c.out("#2d3b6b"))
        b.line(ox, y - 1, ox - 5, y + 4, oar, 0.7)
    if c.dark:
        b.circle(44, y - 0.5, 0.9, "#ffffff")
    L.group(b, class_="boat", transform=f"translate({GX0} 0)")


def draw(c: Ctx) -> tuple[Layer, list[Tag]]:
    """Everything outside the window below the sky, plus labels to pin over it."""
    L = Layer()
    tags: list[Tag] = []
    pats = _window_patterns(c)
    city, lit = Layer(), Rects()
    _far(city, c)
    for spec in GENERICS:
        _generic(city, lit, c, pats, *spec)
    _cira(city, lit, c, pats)
    _fmc(city, lit, c, pats)
    _liberty(city, lit, c, pats, 234, 32, 162, 26, 0)
    _liberty(city, lit, c, pats, 270, 26, 140, 0, 1)
    _bny(city, lit, c, pats)
    _comcast_center(city, lit, c, pats)
    _comcast_tech(city, lit, c, pats)
    _psfs(city, lit, c, pats)
    towers(city, lit, c, pats, tags)
    city.add(lit)
    _city_hall(city, lit, c)
    bank(city, c)
    boathouses(city, c, tags)
    L.group(city, id="city")
    river(L, c)
    return L, tags


__all__ = ["GX1", "GY1", "Tag", "draw"]
