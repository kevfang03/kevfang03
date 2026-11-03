"""Everything seen through the window: sky, skyline, river bank, river and weather.

The view looks east across the Schuylkill River: Center City's towers in the
back, the train line and Boathouse Row on the far bank, and the river in front.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass

from . import palette as pal
from .clock import fireworks_day, season
from .font import text_width
from .growth import LOTS, TOWER_FLOORS, tower_progress
from .model import SceneState
from .raster import Mask, Raster, Sprite

W, H = 320, 204
GX0, GY0, GX1, GY1 = 14, 14, 202, 136  # the window glass
SKY_BOTTOM = 108  # where buildings meet the far bank
TRACK_Y = 102
HOUSE_BASE = 110
RIVER_TOP = 114


@dataclass
class Ctx:
    s: SceneState
    rng: random.Random
    P: dict

    @property
    def phase(self) -> str:
        return self.s.phase

    @property
    def dark(self) -> bool:
        return self.s.phase in ("dusk", "night")

    @property
    def overcast(self) -> bool:
        return self.s.weather in ("cloudy", "rain", "snow")

    @property
    def game_lights(self) -> bool:
        """Buildings light up in team colours only once it gets dark."""
        return bool(self.s.teams) and self.dark

    def team_at(self, x: int) -> dict | None:
        """With several games, the skyline is split left to right between teams."""
        teams = self.s.teams
        if not teams:
            return None
        i = (x - GX0) * len(teams) // (GX1 - GX0)
        return pal.TEAMS[teams[max(0, min(len(teams) - 1, i))]]

    def tint(self, c: str) -> str:
        return pal.outside(c, self.s.phase)

    def crown(self, x: int) -> str:
        """Colour for a tower's crown lights."""
        if self.game_lights:
            return self.team_at(x)["light"]
        return self.P["crown"]


def make_ctx(s: SceneState, rng: random.Random) -> Ctx:
    P = dict(pal.OUTSIDE[s.phase])
    if s.weather in ("cloudy", "rain", "snow"):
        gray = "#1e2433" if s.phase in ("dusk", "night") else "#6b7586"
        P["sky"] = [pal.mix(c, gray, 0.5) for c in P["sky"]]
        P["far"] = pal.mix(P["far"], gray, 0.3)
    return Ctx(s, rng, P)


def _sprite(cls: str, style: str = "") -> Sprite:
    return Sprite(cls, Raster(W, H), style)


# --- sky ---------------------------------------------------------------------

_BAYER = ((0, 2), (3, 1))


def _sky(r: Raster, c: Ctx) -> None:
    cols = c.P["sky"]
    n = len(cols)
    span = SKY_BOTTOM - GY0
    for y in range(GY0, SKY_BOTTOM):
        t = (y - GY0) / span * n
        i = min(n - 1, int(t))
        f = t - i
        for x in range(GX0, GX1):
            col = cols[i]
            # Ordered dither across the last 30% of each band.
            if i < n - 1 and f > 0.7 and (f - 0.7) / 0.3 * 4 > _BAYER[y % 2][x % 2] + 0.5:
                col = cols[i + 1]
            r.px(x, y, col)


def _stars(r: Raster, c: Ctx) -> list[Sprite]:
    if c.overcast or c.phase in ("day", "dawn"):
        return []
    count = 45 if c.phase == "night" else 10
    bottom = 72 if c.phase == "night" else 34
    for _ in range(count):
        x, y = c.rng.randrange(GX0, GX1), c.rng.randrange(GY0, bottom)
        r.px(x, y, c.rng.choice(["#e6ecff", "#8a9ad0", "#b8c4f0"]))
    if c.phase != "night":
        return []
    sprites = []
    for i in range(8):
        sp = _sprite("tw", f"animation-delay:-{c.rng.uniform(0, 4):.2f}s")
        x, y = c.rng.randrange(GX0 + 4, GX1 - 4), c.rng.randrange(GY0 + 2, 60)
        sp.raster.px(x, y, "#ffffff")
        if i % 3 == 0:  # a few brighter stars get a small cross
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                sp.raster.px(x + dx, y + dy, "#9fb0e8")
        sprites.append(sp)
    return sprites


def _halo(r: Raster, cx: float, cy: float, rad: float, color: str, amount: float) -> None:
    for y in range(int(cy - rad), int(cy + rad) + 1):
        for x in range(int(cx - rad), int(cx + rad) + 1):
            if math.hypot(x + 0.5 - cx, y + 0.5 - cy) <= rad and (x + y) % 2 == 0:
                cur = r.get(x, y)
                if cur is not None:
                    r.px(x, y, pal.mix(cur, color, amount))


def _sun_moon(r: Raster, c: Ctx) -> None:
    if c.s.weather in ("rain", "snow"):
        return
    if c.phase == "night":
        cx, cy, rad = 182.5, 30.5, 5.6
        _halo(r, cx, cy, rad + 3, "#f3ead0", 0.12)
        ph = c.s.moon
        d = 2 * rad * (1 - abs(ph - 0.5) * 2)  # 0 at new moon, full width at full
        sx = cx - d if ph < 0.5 else cx + d  # waxing moons are lit on the right
        lit, faint = "#f3ead0", pal.mix(c.P["sky"][0], "#f3ead0", 0.12)
        for y in range(int(cy - rad) - 1, int(cy + rad) + 2):
            for x in range(int(cx - rad) - 1, int(cx + rad) + 2):
                px, py = x + 0.5, y + 0.5
                if math.hypot(px - cx, py - cy) > rad:
                    continue
                shadow = math.hypot(px - sx, py - cy) <= rad
                r.px(x, y, faint if shadow else lit)
        for dx, dy in ((-2, -1), (1, 1), (-1, 2), (2, -2)):
            x, y = int(cx) + dx, int(cy) + dy
            if r.get(x, y) == lit:
                r.px(x, y, "#d6caa6")
        return
    spots = {
        "dawn": (44.5, 101.5, 9, "#ffd89a"),
        "day": (150.5, 30.5, 7, "#fff5c8"),
        "dusk": (176.5, 103.5, 9, "#ff9d5c"),
    }
    cx, cy, rad, col = spots[c.phase]
    _halo(r, cx, cy, rad + 5, col, 0.25 if c.overcast else 0.4)
    if not c.overcast:
        r.disc(cx, cy, rad, col)
        r.disc(cx - 2, cy - 2, rad * 0.45, pal.mix(col, "#ffffff", 0.5))


def _cloud(r: Raster, cx: int, cy: int, width: int, top: str, bottom: str, rng) -> None:
    puffs = []
    x = cx - width // 2
    while x < cx + width // 2:
        puffs.append((x, cy - rng.randint(0, 3), rng.randint(3, 6)))
        x += rng.randint(3, 6)
    for y in range(cy - 10, cy + 2):
        for xx in range(cx - width // 2 - 6, cx + width // 2 + 7):
            if any(math.hypot(xx - px, (y - py) * 1.3) <= pr for px, py, pr in puffs):
                r.px(xx, y, bottom if y >= cy - 1 else top)


def _clouds(r: Raster, c: Ctx) -> None:
    top, bottom = c.P["cloud"]
    if c.overcast:
        gray = "#4a5262" if c.dark else "#9aa3b2"
        top, bottom = pal.mix(top, gray, 0.4), pal.mix(bottom, gray, 0.5)
        count = 9 if c.s.weather != "cloudy" else 6
    else:
        count = 0 if c.phase == "night" else 2
    for _ in range(count):
        _cloud(
            r, c.rng.randrange(GX0, GX1), c.rng.randrange(GY0 + 8, 70),
            c.rng.randint(14, 34), top, bottom, c.rng,
        )


def _fireworks(c: Ctx) -> list[Sprite]:
    if not (fireworks_day(c.s.when.date()) and c.dark):
        return []
    sprites = []
    for i, (cx, cy, col) in enumerate(
        ((52, 34, "#ff5a5a"), (118, 26, "#ffd25a"), (176, 44, "#5ad1ff"), (84, 46, "#b07aff"))
    ):
        sp = _sprite("fw", f"animation-delay:-{i * 0.8:.1f}s")
        for k in range(12):
            a = k * math.pi / 6
            for rad, colr in ((4, "#ffffff"), (7, col), (9, col)):
                sp.raster.px(round(cx + rad * math.cos(a)), round(cy + rad * math.sin(a)), colr)
        sp.raster.px(cx, cy, "#ffffff")
        sprites.append(sp)
    return sprites


# --- skyline -------------------------------------------------------------------


def _windows(r: Raster, c: Ctx, x0: int, y0: int, x1: int, y1: int, sx=2, sy=3, wh=2) -> None:
    P = c.P
    for y in range(y0, y1 - wh + 1, sy):
        for x in range(x0, x1, sx):
            if P["lit"] and c.rng.random() < P["lit_ratio"]:
                team = c.team_at(x) if c.game_lights else None
                if team and c.rng.random() < 0.35:
                    col = team["light"]
                else:
                    col = c.rng.choice(P["lit"])
            else:
                col = P["glass"] if ((x // sx) + (y // sy)) % 3 else P["glass2"]
            r.rect(x, y, 1, wh, col)


def _tower(r: Raster, c: Ctx, x: int, w: int, top: int, sx=2, sy=3) -> None:
    P = c.P
    h = SKY_BOTTOM - top
    r.rect(x, top, w, h, P["base"])
    r.vline(x, top, h, P["edge"])
    r.rect(x + w - 2, top, 2, h, P["shade"])
    r.hline(x, top, w, P["shade"])
    _windows(r, c, x + 2, top + 2, x + w - 2, SKY_BOTTOM, sx=sx, sy=sy)


def _far_skyline(r: Raster, c: Ctx) -> None:
    far = c.P["far"]
    far_lit = pal.mix(c.P["lit"][0], far, 0.45) if c.P["lit"] else None
    x = GX0
    while x < GX1:
        w, h = c.rng.randint(5, 12), c.rng.randint(16, 42)
        top = SKY_BOTTOM - h
        r.rect(x, top, w, h, far)
        if c.rng.random() < 0.25:
            r.vline(x + w // 2, top - 4, 4, far)
        if c.dark and far_lit:
            for yy in range(top + 2, SKY_BOTTOM - 1, 3):
                for xx in range(x + 1, x + w - 1, 2):
                    if c.rng.random() < 0.12:
                        r.px(xx, yy, far_lit)
        x += w


def _cira(r: Raster, c: Ctx) -> None:
    """Cira Centre: faceted glass with a slanted top and an LED face at night."""
    P = c.P
    a = P["base"] if c.dark else pal.mix(P["glass"], P["sky"][3], 0.35)
    b = P["shade"] if c.dark else P["glass2"]
    r.poly([(14, 40), (25, 34), (25, SKY_BOTTOM), (14, SKY_BOTTOM)], a)
    r.poly([(25, 34), (36, 28), (36, SKY_BOTTOM), (25, SKY_BOTTOM)], b)
    r.line(14, 40, 36, 28, P["edge"])
    for y in range(44, SKY_BOTTOM, 4):
        r.hline(14, y, 11, pal.mix(a, P["edge"], 0.35))
        r.hline(25, y, 11, pal.mix(b, P["edge"], 0.35))
    if c.dark:
        led = c.team_at(25)["light"] if c.game_lights else "#6fe3ff"
        label = str(c.s.stats.contributions_year)
        tw = text_width(label)
        r.rect(16, 54, 18, 13, pal.shade(P["shade"], 0.8))
        r.text(25 - tw // 2, 58, label, led)
        for x in range(17, 34, 2):
            r.px(x, 55, pal.mix(led, P["shade"], 0.5))
            r.px(x + 1, 65, pal.mix(led, P["shade"], 0.5))


def _liberty(r: Raster, c: Ctx) -> None:
    """One and Two Liberty Place, with their stepped, gabled crowns and spires."""
    P = c.P
    _tower(r, c, 52, 12, 46)
    cr = c.crown(58)
    r.rect(53, 41, 10, 5, P["base"])
    r.poly([(52.5, 41), (58, 35), (63.5, 41)], cr)
    r.poly([(55, 41), (58, 38), (61, 41)], P["base"])
    r.rect(55, 31, 6, 4, P["base"])
    r.poly([(54.5, 31), (58, 27), (61.5, 31)], cr)
    r.rect(57, 24, 2, 4, cr)
    r.vline(57, 13, 12, cr)
    if c.dark:
        for x in (54, 57, 60):
            r.vline(x, 42, 4, cr)
    _tower(r, c, 66, 10, 58)
    cr2 = c.crown(71)
    r.rect(67, 54, 8, 4, P["base"])
    r.poly([(66.5, 54), (71, 49.5), (75.5, 54)], cr2)
    r.poly([(68.5, 54), (71, 51.5), (73.5, 54)], P["base"])
    r.vline(71, 38, 12, cr2)


def _city_hall(r: Raster, c: Ctx) -> None:
    """City Hall: wide stone base, clock tower, dome and the William Penn statue."""
    P = c.P
    st, sts = P["stone"], P["stone_shade"]
    hi = pal.mix(st, "#ffffff", 0.15)
    win = P["lit"][0] if c.dark else sts
    r.rect(84, 92, 38, 16, st)
    r.hline(84, 92, 38, sts)
    r.hline(84, 93, 38, hi)
    for x in range(86, 120, 3):
        r.rect(x, 96, 1, 3, win if c.rng.random() < 0.5 else sts)
        r.rect(x, 101, 1, 3, sts)
    for px in (84, 116):
        r.rect(px, 88, 6, 20, st)
        r.poly([(px, 88), (px + 1, 85), (px + 5, 85), (px + 6, 88)], sts)
    r.rect(97, 86, 12, 6, st)
    r.rect(98, 58, 10, 30, st)
    for x in (98, 101, 104, 107):
        r.vline(x, 58, 30, sts)
    for y in range(62, 86, 6):
        r.rect(102, y, 2, 3, win)
    r.rect(97, 51, 12, 7, st)
    r.hline(97, 51, 12, sts)
    r.disc(103.5, 54.5, 2.4, P["clock"])
    r.vline(103, 53, 2, "#2a2420")
    r.px(104, 54, "#2a2420")
    r.rect(99, 44, 8, 7, st)
    r.vline(99, 44, 7, sts)
    r.vline(106, 44, 7, sts)
    r.poly([(99, 44), (100, 40), (103, 37), (106, 40), (107, 44)], st)
    r.poly([(103, 37), (106, 40), (107, 44), (103, 44)], sts)
    r.rect(101, 33, 4, 4, st)
    r.px(103, 34, sts)
    br = P["bronze"]
    r.rect(102, 30, 2, 3, sts)
    r.rect(102, 23, 2, 7, br)
    r.px(104, 25, br)
    r.rect(101, 22, 4, 1, br)
    r.rect(102, 21, 2, 1, br)


def _bny(r: Raster, c: Ctx) -> None:
    """BNY Mellon Center, with its stepped, notched top."""
    P = c.P
    _tower(r, c, 126, 12, 60)
    edge = c.crown(132) if c.dark else P["edge"]
    for x, y, w in ((127, 56, 10), (129, 52, 6), (131, 48, 2)):
        r.rect(x, y, w, 4, P["base"])
        r.hline(x, y, w, edge)


def _comcast_center(r: Raster, c: Ctx) -> None:
    """Comcast Center: a tall glass obelisk with a slanted top."""
    P = c.P
    shape = [(142, SKY_BOTTOM), (142, 42), (150, 33), (158, 37), (158, SKY_BOTTOM)]
    r.poly(shape, P["base"])
    for x in range(143, 157, 2):
        r.vline(x, 44, SKY_BOTTOM - 44, P["glass2"])
    _windows(r, c, 144, 46, 156, SKY_BOTTOM, sx=2, sy=3)
    r.rect(156, 38, 2, SKY_BOTTOM - 38, P["shade"])
    r.line(142, 42, 150, 33, P["edge"])
    if c.dark:
        glow = pal.mix(c.crown(150), P["base"], 0.35)
        r.poly([(143, 42), (150, 34), (157, 38), (157, 43)], glow)


def _comcast_tech(r: Raster, c: Ctx) -> None:
    """Comcast Technology Center: the tallest tower, topped by an open frame."""
    P = c.P
    _tower(r, c, 162, 16, 28, sy=2)
    frame = c.crown(170) if c.dark else P["base"]
    r.rect(162, 17, 2, 11, frame)
    r.rect(176, 17, 2, 11, frame)
    r.rect(162, 17, 16, 2, frame)
    r.rect(167, 21, 6, 7, P["shade"])
    if c.dark:
        r.hline(168, 23, 4, c.crown(170))


def _water_tank(r: Raster, c: Ctx, x: int, top: int) -> None:
    """The wooden rooftop water tanks found on older Center City buildings."""
    wood, dark = c.tint("#7a5838"), c.tint("#4e3624")
    r.vline(x, top - 2, 2, dark)
    r.vline(x + 4, top - 2, 2, dark)
    r.rect(x, top - 6, 5, 4, wood)
    r.vline(x + 4, top - 6, 4, dark)
    r.hline(x, top - 4, 5, dark)
    r.poly([(x - 0.5, top - 6), (x + 2.5, top - 9), (x + 5.5, top - 6)], dark)


def _psfs(r: Raster, c: Ctx) -> None:
    """The PSFS Building, with its red rooftop letters that glow at night."""
    P = c.P
    _tower(r, c, 188, 13, 64)
    r.rect(190, 61, 9, 3, P["base"])
    for x in (190, 197):
        r.vline(x, 58, 3, P["shade"])
    sign = "#ff3b30" if c.dark else c.tint("#a83a30")
    r.rect(186, 52, 16, 7, pal.shade(P["shade"], 0.7))
    r.text(187, 53, "PSFS", sign)


def _mid_generics(r: Raster, c: Ctx) -> None:
    for x, w, top in ((34, 10, 72), (44, 8, 62), (78, 8, 76), (112, 10, 68)):
        _tower(r, c, x, w, top)
        if c.rng.random() < 0.5:
            r.rect(x + 2, top - 2, 3, 2, c.P["shade"])
    _water_tank(r, c, 80, 76)
    _water_tank(r, c, 114, 68)
    _psfs(r, c)


# --- your towers ----------------------------------------------------------------

FLOOR_H = 3


def _tower_colors(c: Ctx) -> tuple[str, str, str]:
    return c.tint("#4a7f96"), c.tint("#86c3d4"), c.tint("#b8e2ec")


def _glazed_floors(r: Raster, c: Ctx, x: int, w: int, top: int) -> None:
    body, glass, edge = _tower_colors(c)
    r.rect(x, top, w, SKY_BOTTOM - top, body)
    r.vline(x, top, SKY_BOTTOM - top, edge)
    r.rect(x + w - 2, top, 2, SKY_BOTTOM - top, pal.shade(body, 0.8))
    for y in range(top + 1, SKY_BOTTOM, FLOOR_H):
        for xx in range(x + 2, x + w - 2, 2):
            lit = c.dark and c.rng.random() < 0.55
            col = c.rng.choice(c.P["lit"]) if lit else (glass if not c.dark else c.P["glass"])
            r.rect(xx, y, 1, 2, col)


def _finished_tower(r: Raster, c: Ctx, x: int, w: int) -> None:
    """A completed tower with the owner's monogram lit on its crown."""
    body, _, edge = _tower_colors(c)
    top = SKY_BOTTOM - TOWER_FLOORS * FLOOR_H
    _glazed_floors(r, c, x, w, top)
    r.rect(x, top - 7, w, 7, body)
    r.hline(x, top - 7, w, edge)
    r.vline(x + w // 2, top - 12, 5, edge)
    if c.dark:
        mono_col = c.crown(x)
    else:
        mono_col = pal.mix(edge, "#ffffff", 0.5)
    mono = c.s.monogram[:2].upper()
    r.text(x + (w - text_width(mono)) // 2, top - 6, mono, mono_col)


def _construction(r: Raster, c: Ctx, x: int, w: int, floors: int) -> list[Sprite]:
    """The tower going up now: glass below, bare steel on top, a crane beside it."""
    steel, steel_d = c.tint("#a0a6b0"), c.tint("#5e6470")
    frame_n = min(3, floors)
    glazed = floors - frame_n
    glass_top = SKY_BOTTOM - glazed * FLOOR_H
    top = SKY_BOTTOM - floors * FLOOR_H
    if glazed:
        _glazed_floors(r, c, x, w, glass_top)
    for k in range(frame_n):
        fy = glass_top - (k + 1) * FLOOR_H
        r.hline(x, fy, w, steel)
        for cx in [*range(x, x + w - 1, 4), x + w - 1]:
            r.vline(cx, fy, FLOOR_H, steel_d)
    r.hline(x - 1, SKY_BOTTOM - 1, w + 2, steel_d)  # site fence
    if c.dark and floors:
        _halo(r, x + w / 2, top + 1, w / 2 + 4, "#fff2b0", 0.25)
        for xx in (x + 1, x + w // 2, x + w - 2):
            r.px(xx, top + 1, "#fff2b0")

    crane, crane_d = c.tint("#e8b830"), c.tint("#a87e1a")
    if c.dark:  # site floodlights keep the crane visible after dark
        crane = pal.mix(crane, "#e8b830", 0.55)
        crane_d = pal.mix(crane_d, "#a87e1a", 0.45)
    mx = x - 4
    jib_y = max(GY0 + 8, min(top - 12, 46))  # stays above the PSFS sign
    for y in range(jib_y, SKY_BOTTOM):
        r.px(mx, y, crane)
        r.px(mx + 2, y, crane)
        if y % 3 == 0:
            r.px(mx + 1, y, crane_d)
    x0, x1 = mx - 9, x + w + 3
    r.hline(x0, jib_y, x1 - x0, crane)
    r.hline(mx + 3, jib_y + 2, x1 - mx - 3, crane)
    for xx in range(mx + 3, x1, 2):
        r.px(xx, jib_y + 1, crane_d)
    r.hline(x0, jib_y + 1, mx - x0, crane)
    r.rect(x0, jib_y + 2, 4, 3, c.tint("#7a7a80"))
    r.vline(mx + 1, jib_y - 5, 5, crane)
    r.line(mx + 1, jib_y - 5, x0, jib_y, crane_d)
    r.line(mx + 1, jib_y - 5, x1 - 5, jib_y, crane_d)
    r.rect(mx + 3, jib_y + 3, 3, 3, crane)
    r.px(mx + 4, jib_y + 4, "#ffe9a8" if c.dark else c.tint("#2a3342"))

    load = _sprite("sway")
    tx = x + w // 2
    drop = max(4, top - jib_y - 6)
    load.raster.vline(tx, jib_y + 3, drop, steel_d)
    load.raster.hline(tx - 3, jib_y + 3 + drop, 7, steel)
    load.raster.hline(tx - 3, jib_y + 4 + drop, 7, steel_d)
    light = _sprite("av", "animation-delay:-.7s")
    light.raster.px(mx + 1, jib_y - 6, "#ff3b30")
    light.raster.px(x1 - 1, jib_y - 1, "#ff3b30")
    return [load, light]


def _your_towers(r: Raster, c: Ctx) -> list[Sprite]:
    done, floors = tower_progress(c.s.stats.contributions_total)
    for x, w in LOTS[:done]:
        _finished_tower(r, c, x, w)
    if done < len(LOTS):
        x, w = LOTS[done]
        return _construction(r, c, x, w, floors)
    return []


def _aviation(c: Ctx) -> list[Sprite]:
    if not (c.dark or c.overcast):
        return []
    sprites = []
    for i, (x, y) in enumerate(((162, 16), (177, 16), (150, 32), (57, 12))):
        sp = _sprite("av", f"animation-delay:-{i * 0.4:.1f}s")
        sp.raster.px(x, y, "#ff3b30")
        sprites.append(sp)
    return sprites


def _track(r: Raster, c: Ctx) -> None:
    r.rect(GX0, TRACK_Y, GX1 - GX0, 2, c.tint("#5a5a62"))
    for x in range(GX0, GX1, 3):
        r.px(x, TRACK_Y + 1, c.tint("#3a3238"))


def draw_back(r: Raster, c: Ctx) -> list[Sprite]:
    """Sky and skyline. Returns the animated layers that sit just in front."""
    _sky(r, c)
    sprites = _stars(r, c)
    _sun_moon(r, c)
    _clouds(r, c)
    _far_skyline(r, c)
    _mid_generics(r, c)
    _cira(r, c)
    _liberty(r, c)
    _city_hall(r, c)
    _bny(r, c)
    _comcast_center(r, c)
    _comcast_tech(r, c)
    sprites += _your_towers(r, c)
    _track(r, c)
    return sprites + _aviation(c) + _fireworks(c) + _plane(c)


def _plane(c: Ctx) -> list[Sprite]:
    """A plane heading for PHL, shown as its navigation lights after dark."""
    if not c.dark or c.s.weather in ("rain", "snow"):
        return []
    white, red = _sprite("plane"), _sprite("planeb")
    white.raster.hline(GX0, 40, 2, "#e8ecf6")
    red.raster.px(GX0 + 3, 40, "#ff4a4a")
    return [white, red]


def glass_glints(c: Ctx) -> Sprite:
    """Faint diagonal reflections on the window glass."""
    sp = _sprite("", "opacity:.07" if c.dark else "opacity:.12")
    for x0, y0, length, width in ((20, 58, 44, 3), (30, 62, 36, 1), (118, 70, 50, 2)):
        for k in range(width):
            sp.raster.line(x0 + k, y0, x0 + k + length, y0 - length, "#ffffff")
    return sp


def train(c: Ctx) -> Sprite:
    """A regional rail train that crosses the far bank every few seconds."""
    sp = _sprite("train")
    t = sp.raster
    body, roof = c.tint("#c4cad1"), c.tint("#9aa1aa")
    stripe, stripe2 = c.tint("#c8343a"), c.tint("#2b4b8c")
    win = "#ffe9a8" if c.dark else c.tint("#2a3342")
    x = GX0
    for _ in range(6):
        t.rect(x, 96, 22, 6, body)
        t.hline(x + 1, 95, 20, roof)
        t.hline(x, 99, 22, stripe)
        t.hline(x, 100, 22, stripe2)
        for wx in range(x + 2, x + 20, 3):
            t.rect(wx, 97, 2, 2, win)
        t.rect(x + 1, 102, 3, 1, "#22222a")
        t.rect(x + 18, 102, 3, 1, "#22222a")
        x += 24
    t.clear(x - 4, 95, 2, 2)  # sloped nose on the lead car
    t.px(x - 4, 96, roof)
    return sp


# --- far bank and river -------------------------------------------------------


def _bank(r: Raster, c: Ctx) -> None:
    snow = c.s.weather == "snow"
    grass = c.tint("#e9eef4" if snow else pal.GRASS[season(c.s.when.month)])
    r.rect(GX0, 104, GX1 - GX0, 6, grass)
    r.dither(GX0, 104, GX1 - GX0, 1, grass, c.P["far"])
    r.hline(GX0, 108, GX1 - GX0, c.tint("#c9b994"))  # riverside path


def _trees(r: Raster, c: Ctx) -> None:
    sea = season(c.s.when.month)
    leaves = [c.tint(col) for col in pal.TREES[sea]]
    trunk = c.tint("#4a3628")
    snow = c.s.weather == "snow"
    for x, size in ((18, 4), (36, 3), (52, 4), (69, 3), (86, 4), (104, 3), (122, 4),
                    (140, 3), (156, 5), (168, 4), (182, 5), (195, 4)):
        top = 108 - size * 2 - 3
        r.vline(x, top + size, 108 - top - size, trunk)
        if not leaves:  # bare winter branches
            r.line(x, top + size, x - 2, top + 1, trunk)
            r.line(x, top + size, x + 2, top, trunk)
            if snow:
                r.px(x - 2, top, "#f4f7fb")
                r.px(x + 2, top - 1, "#f4f7fb")
            continue
        cy = top + size * 0.8
        r.disc(x + 0.5, cy, size, leaves[0])
        r.disc(x - 0.5, cy - 1, size * 0.6, leaves[1])
        for _ in range(size + 1):
            r.px(x + c.rng.randint(-size + 1, size - 1),
                 int(cy) + c.rng.randint(-size + 1, size - 1), leaves[2])
        if snow:
            r.hline(x - size + 2, int(cy - size) + 1, size * 2 - 3, "#f4f7fb")


def _house(t: Raster, x: int, w: int, top: int, kind: int, wall: str, roof: str) -> None:
    t.rect(x, top, w, HOUSE_BASE - top, wall)
    if kind == 0:
        t.poly([(x - 1, top), (x + w / 2, top - 5), (x + w + 1, top)], roof)
    elif kind == 1:
        t.poly([(x - 1, top), (x + w / 2 - 2, top - 4), (x + w - 3, top)], roof)
        t.rect(x + w - 4, top - 5, 4, 5, wall)
        t.poly([(x + w - 5, top - 5), (x + w - 2, top - 10), (x + w + 1, top - 5)], roof)
    else:
        t.rect(x - 1, top - 3, w + 2, 3, roof)
        t.rect(x + 2, top - 5, w - 4, 2, roof)


def _boathouses(r: Raster, c: Ctx) -> list[tuple[int, int]]:
    """Boathouse Row. At night one house is outlined in lights for each repo.

    Returns the tops of the flagpoles on the towered houses.
    """
    poles = []
    widths = [14, 12, 16, 12, 14, 13, 15]
    heights = [9, 11, 8, 10, 9, 11, 8]
    kinds = [0, 1, 2, 0, 1, 0, 2]
    walls = ["#d8cdb4", "#c49a7a", "#e2d6bc", "#b9a58a", "#d3c2a0", "#c8b08c", "#ddd0b6"]
    lit_houses = min(len(widths), c.s.stats.repo_count)
    snow = c.s.weather == "snow"
    teams = c.s.teams
    x = 22
    for i, (w, h, kind) in enumerate(zip(widths, heights, kinds, strict=True)):
        top = HOUSE_BASE - h
        wall, roof = c.tint(walls[i]), c.tint("#5e3b30")
        _house(r, x, w, top, kind, wall, roof)
        if snow:
            m = Mask(W, H)
            _house(m, x, w, top, kind, "", "")
            for px, py in m.points:
                if py < top and (px, py - 1) not in m.points:
                    r.px(px, py, "#f4f7fb")
        win = c.tint("#3a2e28")
        for wx in range(x + 2, x + w - 2, 3):
            r.px(wx, top + 3, "#ffd679" if c.dark and c.rng.random() < 0.3 else win)
        r.rect(x + w // 2 - 1, HOUSE_BASE - 3, 2, 3, win)
        if (c.dark or c.phase == "dawn") and i < lit_houses:
            m = Mask(W, H)
            _house(m, x, w, top, kind, "", "")
            for px, py in sorted(m.outline()):
                if c.game_lights:
                    col = pal.TEAMS[teams[i % len(teams)]]["light"]
                elif c.s.when.month == 12:
                    col = pal.HOLIDAY_LIGHTS[(px + py) % 4]
                else:
                    col = pal.WARM_LIGHT
                if c.phase == "dawn":
                    col = pal.mix(col, wall, 0.5)
                if py < HOUSE_BASE - 1 or (px + py) % 2 == 0:
                    r.px(px, py, col)
        if kind == 1:
            pole_x, pole_top = x + w - 2, top - 15
            r.vline(pole_x, pole_top, 5, c.tint("#3a3238"))
            poles.append((pole_x + 1, pole_top))
        x += w + 4
    return poles


def _flags(c: Ctx, poles: list[tuple[int, int]]) -> list[Sprite]:
    """Two-frame flags that flutter on the boathouse towers."""
    cloth = c.tint("#d83a3a")
    a, b = _sprite("fa"), _sprite("fb")
    for x, y in poles:
        a.raster.hline(x, y, 3, cloth)
        a.raster.hline(x, y + 1, 2, cloth)
        b.raster.hline(x, y, 2, cloth)
        b.raster.hline(x, y + 1, 3, cloth)
    return [a, b]


def _traffic(c: Ctx) -> list[Sprite]:
    """Cars on Kelly Drive in both directions, and joggers by day."""
    paints = ["#c8343a", "#2b4b8c", "#e8e2d6", "#3a3a40", "#e8b830", "#5a8a5a"]
    sprites = []
    for direction, y, cls in ((1, 106, "carr"), (-1, 105, "carl")):
        sp = _sprite(cls)
        for k in range(5):
            x = GX0 + k * 40 + c.rng.randint(0, 18)
            body = c.tint(c.rng.choice(paints))
            sp.raster.rect(x, y, 5, 2, body)
            sp.raster.hline(x + 1, y - 1, 3, body)
            sp.raster.px(x + 2, y - 1, c.tint("#9ab4cc"))
            if c.dark:
                head, tail = (x + 5, x - 1) if direction > 0 else (x - 1, x + 5)
                sp.raster.px(head, y + 1, "#fff2b0")
                sp.raster.px(head + direction, y + 1, pal.mix("#fff2b0", c.P["far"], 0.5))
                sp.raster.px(tail, y + 1, "#ff3b30")
        sprites.append(sp)
    if c.phase in ("dawn", "day") and c.s.weather in ("clear", "cloudy"):
        jog = _sprite("jog")
        for x, shirt in ((GX0 + 10, "#e05a5a"), (GX0 + 90, "#5a8ae0")):
            jog.raster.px(x, 105, c.tint("#d9a07a"))
            jog.raster.px(x, 106, c.tint(shirt))
            jog.raster.px(x, 107, c.tint("#2a2a30"))
        sprites.append(jog)
    return sprites


def _embankment(r: Raster, c: Ctx) -> None:
    stone = c.tint("#8a8172")
    r.rect(GX0, HOUSE_BASE, GX1 - GX0, RIVER_TOP - HOUSE_BASE, stone)
    r.hline(GX0, HOUSE_BASE, GX1 - GX0, pal.mix(stone, "#ffffff", 0.2))
    for x in range(GX0 + 3, GX1, 6):
        r.vline(x, HOUSE_BASE + 1, 3, pal.shade(stone, 0.8))


def _river(r: Raster, bank: Raster, back: Raster, c: Ctx) -> None:
    """Water with a broken, wavy reflection of everything above it."""
    water = c.P["water"]
    bright = set(c.P["lit"]) | {pal.WARM_LIGHT, *pal.HOLIDAY_LIGHTS}
    bright |= {t["light"] for t in pal.TEAMS.values()}
    depth = GY1 - RIVER_TOP
    for y in range(RIVER_TOP, GY1):
        d = y - RIVER_TOP
        band = water[min(2, d * 3 // depth)]
        sy = RIVER_TOP - 1 - int(d * 1.5)
        wob = 1 if d % 4 in (1, 2) else 0
        fade = round(max(0.25, 1 - d / 26), 1)
        for x in range(GX0, GX1):
            src = None
            if sy >= GY0 and d % 3 != 2:
                src = r.get(x + wob, sy) or bank.get(x + wob, sy) or back.get(x + wob, sy)
            if src is None:
                col = band
            else:
                col = pal.mix(band, src, (0.6 if src in bright else 0.3) * fade)
            r.px(x, y, col)


def _boardwalk(r: Raster, c: Ctx) -> None:
    """The Schuylkill Banks boardwalk on this side of the river, with its lamps."""
    rail, post = c.tint("#6a7080"), c.tint("#3a3f4c")
    deck = c.tint("#8a8578")
    r.rect(GX0, 133, GX1 - GX0, 3, deck)
    r.hline(GX0, 133, GX1 - GX0, pal.mix(deck, "#ffffff", 0.15))
    r.hline(GX0, 127, GX1 - GX0, rail)
    r.hline(GX0, 130, GX1 - GX0, pal.shade(rail, 0.85))
    for x in range(GX0 + 3, GX1, 8):
        r.vline(x, 127, 6, post)
    for x in (84, 154):
        r.vline(x, 112, 21, post)
        r.rect(x - 1, 110, 3, 2, post)
        if c.dark:
            _halo(r, x + 0.5, 113, 3.5, "#ffe2a0", 0.35)
            for dx in range(-4, 5):  # pool of light on the deck
                if (x + dx) % 2 == 0 or abs(dx) < 3:
                    r.px(x + dx, 134, pal.mix(deck, "#ffe2a0", 0.4 - abs(dx) * 0.06))
            r.rect(x - 1, 112, 3, 2, "#ffe2a0")
        else:
            r.rect(x - 1, 112, 3, 2, c.tint("#d8d2c0"))


def _ripples(c: Ctx) -> list[Sprite]:
    col = pal.mix(c.P["water"][0], "#ffffff", 0.35) if not c.dark else c.P["lit"][0]
    sprites = []
    for i in range(4):
        sp = _sprite("rip", f"animation-delay:-{i * 0.75:.2f}s")
        for _ in range(7):
            x = c.rng.randrange(GX0, GX1 - 4)
            y = c.rng.randrange(RIVER_TOP + 2, 126)  # above the boardwalk railing
            sp.raster.hline(x, y, c.rng.randint(2, 4), col)
        sprites.append(sp)
    return sprites


def _boat(c: Ctx) -> Sprite:
    """A rowing eight heading downriver, as crews do every morning."""
    sp = _sprite("boat")
    t = sp.raster
    hull, rower = c.tint("#efe9dc"), c.tint("#2a2a30")
    t.hline(0, 124, 18, hull)
    t.hline(1, 125, 16, c.tint("#b03a3a"))
    for x in (3, 6, 9, 12):
        t.vline(x, 122, 2, rower)
        t.px(x - 1, 125, rower)
        t.px(x - 2, 126, rower)
    t.px(16, 123, rower)
    return sp


def _birds(c: Ctx) -> list[Sprite]:
    col = c.tint("#2a2f3a")
    sprites = []
    for i, (x, y) in enumerate(((0, 40), (6, 44), (-8, 52))):
        sp = _sprite("bird", f"animation-delay:-{i * 7}s")
        for dx, dy in ((-1, -1), (0, 0), (1, 0), (2, -1)):
            sp.raster.px(GX0 + x + dx, y + dy, col)
        sprites.append(sp)
    return sprites


def draw_bank(r: Raster, c: Ctx) -> list[Sprite]:
    """Grass and Kelly Drive. Returns the traffic, which passes behind the houses."""
    _bank(r, c)
    return _traffic(c)


def draw_front(r: Raster, bank: Raster, back: Raster, c: Ctx) -> list[Sprite]:
    """Trees, Boathouse Row and the river. Returns their animated layers."""
    _trees(r, c)
    poles = _boathouses(r, c)
    _embankment(r, c)
    _river(r, bank, back, c)
    _boardwalk(r, c)
    sprites = _ripples(c) + _flags(c, poles)
    if c.phase in ("dawn", "day") and c.s.weather in ("clear", "cloudy"):
        sprites.append(_boat(c))
        sprites += _birds(c)
    return sprites


def weather(c: Ctx) -> list[Sprite]:
    sprites = []
    if c.s.weather == "rain":
        col = "#5a6c8f" if c.dark else "#b4c3dc"
        for g in range(2):
            sp = _sprite("rain", f"animation-delay:-{g * 0.22:.2f}s")
            for _ in range(70):
                x, y = c.rng.randrange(GX0, GX1 + 6), c.rng.randrange(GY0 - 10, GY1)
                for k in range(3):
                    sp.raster.px(x - k // 2, y + k, col)
            sprites.append(sp)
    elif c.s.weather == "snow":
        col = "#c8d2e6" if c.dark else "#ffffff"
        for g in range(3):
            sp = _sprite("snow", f"animation-delay:-{g * 1.6:.1f}s")
            for _ in range(45):
                x, y = c.rng.randrange(GX0, GX1), c.rng.randrange(GY0 - 10, GY1)
                sp.raster.px(x, y, col)
                if c.rng.random() < 0.3:
                    sp.raster.px(x + 1, y, col)
            sprites.append(sp)
    return sprites
