"""The room: window frame, curtains, desk, monitor, wall decor and the dragon plush."""

from __future__ import annotations

import itertools
import math
import random

from . import palette as pal
from .font import text_width
from .growth import LOTS, TOWER_FLOORS, tower_progress
from .model import SceneState
from .raster import Mask, Raster, Sprite

W, H = 320, 204
DESK_Y = 146
STATUS_Y = 180

BASE = {
    "wall": "#8c9aa6", "wall_stripe": "#84929e", "wall_top": "#74818c",
    "trim": "#ece6da", "trim_hi": "#f8f4ec", "trim_shade": "#cfc6b6", "trim_dark": "#a89e8d",
    "curtain": "#3f5f86", "curtain_shade": "#2e4867", "curtain_light": "#58789f",
    "tie": "#d4a72c",
    "wood": "#a8744a", "wood_light": "#bd8858", "wood_dark": "#7d5131",
    "wood_front": "#6e4529", "wood_front_dark": "#5a3720",
    "metal": "#2b2f3a", "metal_light": "#4a5060",
    "navy": "#1f3a6b", "navy_dark": "#142850", "navy_light": "#2f5694",
    "gold": "#f2b632", "gold_dark": "#c98a1a", "gold_light": "#ffd36b",
    "paper": "#f2efe8", "paper_shade": "#d8d2c4", "red": "#c0392b",
    "pot": "#b5653a", "pot_dark": "#8f4a28", "pot_rim": "#c97a4a",
    "leaf": "#3f7d3a", "leaf_mid": "#5a9a4a", "leaf_hi": "#7ab85e",
    "mug": "#ece8e0", "mug_shade": "#c9c3b8", "coffee": "#4a2e1e",
    "lamp": "#d8b45a", "lamp_dark": "#9a7a32", "lamp_hi": "#f2d68a",
    "pad": "#3a3d4a", "pad_dark": "#2a2c36", "pad_hi": "#8a8e9c",
    "blush": "#e88aa0", "ink": "#0b0f1a", "white": "#ffffff",
}

TICKETS = [
    "VPN RESET", "MFA LOOP", "PRINTER JAM", "WIFI DROP", "PW RESET", "2FA PUSH",
    "LAB PC SLOW", "EMAIL SYNC", "LMS LOGIN", "AUDIO FIX", "PORT DEAD", "DRIVE MAP",
]

SCREEN = (242, 66, 66, 56)  # monitor screen: x, y, width, height


def _commit_text(s: SceneState) -> str:
    return s.stats.latest_commit[:13]


def typing_css(s: SceneState) -> str:
    """Keyframes that reveal the commit message one letter per step."""
    n = max(1, len(_commit_text(s)))
    d = n * 4
    return (
        f"@keyframes type{{0%{{transform:translateX(0)}}60%,100%{{transform:translateX({d}px)}}}}"
        f".type{{animation:type 7s steps({n}) infinite}}"
        f".typecur{{animation:type 7s steps({n}) infinite,blink .8s steps(1) infinite}}"
    )


MONTHS = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]


def _sprite(cls: str, style: str = "") -> Sprite:
    return Sprite(cls, Raster(W, H), style)


def _glow(r: Raster, cx: int, cy: int, radius: int, color: str, strength: float) -> None:
    """Light falling on the wall and desk, in three dithered bands."""
    for y in range(max(0, cy - radius), min(STATUS_Y, cy + radius)):
        for x in range(max(0, cx - radius), min(W, cx + radius)):
            cur = r.grid[y][x]
            if cur is None:
                continue
            d = math.hypot(x - cx, y - cy) / radius
            if d >= 1:
                continue
            t = (1 - d) * 3
            level = int(t)
            if t - level > 0.5 and (x + y) % 2:
                level += 1
            if level:
                r.grid[y][x] = pal.mix(cur, color, strength * min(level, 3) / 3)


# --- architecture ---------------------------------------------------------------


def _wall(r: Raster, C: dict) -> None:
    r.rect(0, 0, W, DESK_Y, C["wall"])
    for x in range(0, W, 8):
        r.rect(x + 5, 0, 2, DESK_Y, C["wall_stripe"])
    r.rect(0, 0, W, 3, C["wall_top"])


def _window(r: Raster, C: dict) -> None:
    r.rect(10, 10, 196, 130, C["trim"])
    r.hline(10, 10, 196, C["trim_dark"])
    r.vline(10, 10, 130, C["trim_dark"])
    r.vline(205, 10, 130, C["trim_dark"])
    r.hline(11, 11, 194, C["trim_hi"])
    r.hline(13, 13, 190, C["trim_shade"])
    r.vline(13, 13, 124, C["trim_shade"])
    r.clear(14, 14, 188, 122)
    r.rect(106, 14, 4, 122, C["trim"])
    r.vline(106, 14, 122, C["trim_hi"])
    r.vline(109, 14, 122, C["trim_shade"])
    # Sill
    r.rect(6, 136, 204, 2, C["trim_hi"])
    r.rect(6, 138, 204, 3, C["trim_shade"])
    r.hline(6, 141, 204, C["trim_dark"])
    r.hline(8, 142, 200, pal.shade(C["wall"], 0.8))


def _desk(r: Raster, C: dict) -> None:
    r.rect(0, DESK_Y, W, 4, C["wood_light"])
    for x in range(3, W, 11):
        r.hline(x, DESK_Y + 1 + (x // 11) % 2, 5, C["wood"])
    r.rect(0, DESK_Y + 4, W, 2, C["wood_dark"])
    r.rect(0, DESK_Y + 6, W, STATUS_Y - DESK_Y - 6, C["wood_front"])
    # Wood grain: long, slightly broken streaks
    grain = pal.mix(C["wood_front"], C["wood_front_dark"], 0.6)
    for y in range(154, STATUS_Y, 3):
        x = (y * 37) % 23
        while x < W:
            length = 6 + (x * 13 + y * 7) % 18
            r.hline(x, y, length, grain)
            x += length + 4 + (x + y) % 9
    for x0 in (8, 168):  # drawers, recessed: dark on top and left, light below
        r.rect(x0, 158, 144, 18, C["wood_front"])
        r.hline(x0, 158, 144, C["wood_front_dark"])
        r.vline(x0, 158, 18, C["wood_front_dark"])
        r.hline(x0, 175, 144, C["wood"])
        r.vline(x0 + 143, 158, 18, C["wood"])
        r.rect(x0 + 68, 165, 8, 3, C["lamp_dark"])
        r.hline(x0 + 68, 165, 8, C["lamp"])
        r.px(x0 + 69, 165, C["lamp_hi"])
    r.hline(0, DESK_Y + 6, W, C["wood_front_dark"])


def _shelf(r: Raster, C: dict, phase: str) -> None:
    """A small wall shelf of books between the curtain and the monitor."""
    shadow = pal.shade(C["wall"], 0.78)
    r.rect(218, 100, 19, 2, C["wood_light"])
    r.hline(218, 102, 19, C["wood_dark"])
    r.hline(219, 103, 18, shadow)
    r.vline(220, 103, 4, C["metal"])
    r.vline(234, 103, 4, C["metal"])
    books = [(3, 12, "#8a3b3b"), (2, 10, "#3b5a8a"), (3, 13, "#c9a54a"), (2, 9, "#3a6b4a"),
             (3, 11, "#6b4a8a")]
    x = 219
    for w, h, col in books:
        col = pal.room(col, phase)
        r.rect(x, 100 - h, w, h, col)
        r.vline(x + w - 1, 100 - h, h, pal.shade(col, 0.75))
        r.hline(x, 100 - h + 2, w, pal.mix(col, "#ffffff", 0.35))
        x += w
    r.poly([(x, 100), (x + 2, 100), (x + 6, 90), (x + 4, 89)], pal.room("#b0703a", phase))


def _curtains(r: Raster, C: dict) -> None:
    r.rect(2, 4, 214, 2, C["metal"])
    r.rect(0, 3, 3, 4, C["metal_light"])
    r.rect(215, 3, 3, 4, C["metal_light"])
    folds = [C["curtain"], C["curtain_light"], C["curtain"], C["curtain_shade"]]
    for side in (0, 1):
        for y in range(6, 132):
            if y < 88:
                w = 13
            elif y < 96:
                w = round(13 - (y - 88) * 7 / 8)
            else:
                w = round(6 + (y - 96) * 4 / 36)
            for i in range(w):
                k = int(i * 13 / w)
                col = folds[(k // 2) % 4]
                if y >= 130:
                    col = C["curtain_shade"]
                x = 2 + i if side == 0 else 215 - i
                r.px(x, y, col)
        tx = 2 if side == 0 else 208
        r.rect(tx, 94, 8, 3, C["tie"])
        r.px(tx + 4, 97, C["gold_dark"])
        r.px(tx + 4, 98, C["tie"])


# --- wall decor -----------------------------------------------------------------


def _calendar(r: Raster, C: dict, s: SceneState) -> None:
    x0, y0 = 220, 16
    r.rect(x0, y0, 22, 27, C["paper"])
    r.rect(x0 + 1, y0 + 27, 22, 1, pal.shade(C["wall"], 0.75))
    r.rect(x0, y0, 22, 8, C["red"])
    for x in (x0 + 4, x0 + 17):
        r.rect(x, y0 - 2, 1, 3, C["metal"])
    month = MONTHS[s.when.month - 1]
    r.text(x0 + 11 - text_width(month) // 2, y0 + 2, month, C["paper"])
    day = str(s.when.day)
    r.text(x0 + 11 - text_width(day, 2) // 2, y0 + 11, day, C["ink"], scale=2)
    for x in range(x0 + 3, x0 + 20, 3):
        r.px(x, y0 + 23, C["paper_shade"])
        r.px(x, y0 + 25, C["paper_shade"])


def _clock(r: Raster, C: dict, s: SceneState) -> None:
    cx, cy = 304, 26
    r.disc(cx + 0.5, cy + 1.5, 10, pal.shade(C["wall"], 0.75))
    r.disc(cx + 0.5, cy + 0.5, 10, C["metal"])
    r.disc(cx + 0.5, cy + 0.5, 8.6, C["paper"])
    for k in range(12):
        a = k * math.pi / 6
        col = C["ink"] if k % 3 == 0 else C["paper_shade"]
        r.px(round(cx + 7 * math.sin(a)), round(cy - 7 * math.cos(a)), col)
    minute = s.when.minute
    hour = s.when.hour % 12 + minute / 60
    for length, frac, col in ((4, hour / 12, C["ink"]), (6, minute / 60, C["metal_light"])):
        a = frac * 2 * math.pi
        r.line(cx, cy, round(cx + length * math.sin(a)), round(cy - length * math.cos(a)), col)
    r.px(cx, cy, C["red"])


def _pennants(r: Raster, C: dict, teams: tuple[str, ...]) -> None:
    """One pennant per team playing today, stacked on the wall."""
    n = len(teams)
    h = 18 if n == 1 else (13 if n == 2 else 9)
    gap = 2
    total = n * h + (n - 1) * gap
    y = 30 - total // 2
    for key in teams:
        t = pal.TEAMS[key]
        r.vline(250, y - 1, h + 2, C["wood_dark"])
        r.poly([(251, y), (290, y + h / 2), (251, y + h)], t["primary"])
        r.poly([(251, y), (290, y + h / 2), (251, y + 1.5)], pal.shade(t["primary"], 0.8))
        r.rect(251, y, 4, h, t["secondary"])
        r.vline(252, y, h, pal.mix(t["secondary"], "#ffffff", 0.3))
        r.text(257, y + (h - 5) // 2, "PHILA", t["secondary"])
        y += h + gap


def _liberty_bell_print(r: Raster, C: dict) -> None:
    """A framed print of the Liberty Bell, shown when there's no game."""
    r.rect(252, 14, 36, 30, C["wood_dark"])
    r.rect(254, 16, 32, 26, C["paper"])
    bronze, bronze_dark = "#9a7238", "#6e4f22"
    r.rect(262, 18, 16, 2, C["wood"])  # yoke
    r.rect(269, 20, 2, 2, bronze_dark)
    r.poly([(266, 22), (274, 22), (275, 30), (279, 37), (261, 37), (265, 30)], bronze)
    r.poly([(271, 22), (274, 22), (275, 30), (279, 37), (272, 37)], bronze_dark)
    r.hline(260, 37, 20, bronze_dark)
    r.line(268, 28, 267, 36, C["ink"])  # the crack
    r.px(270, 38, bronze_dark)


def _wreath(r: Raster, C: dict) -> None:
    m = Mask(W, H)
    m.disc(108.5, 26.5, 8, "x")
    inner = Mask(W, H)
    inner.disc(108.5, 26.5, 4.5, "x")
    for x, y in m.points - inner.points:
        r.px(x, y, C["leaf"] if (x * 3 + y) % 4 else C["leaf_hi"])
        if (x * 7 + y * 5) % 11 == 0:
            r.px(x, y, C["red"])
    r.rect(106, 33, 6, 2, C["red"])
    r.px(105, 35, C["red"])
    r.px(112, 35, C["red"])


def _fairy_lights(r: Raster, C: dict, s: SceneState) -> list[Sprite]:
    """Lights draped from the curtain rod; warm white, or coloured in December."""
    hooks = [4, 74, 144, 214]
    wire = []
    for a, b in itertools.pairwise(hooks):
        for x in range(a, b):
            t = (x - a) / (b - a)
            wire.append((x, 7 + round(24 * t * (1 - t))))
    for x, y in wire:
        r.px(x, y, C["metal"])
    december = s.when.month == 12
    lit = s.phase != "day"
    a, b = _sprite("fa"), _sprite("fb")
    for i, (x, y) in enumerate(wire[3::7]):
        col = pal.HOLIDAY_LIGHTS[i % 4] if december else "#ffd98a"
        if not lit:
            r.px(x, y + 1, pal.room(pal.mix(col, "#ffffff", 0.4), s.phase))
            continue
        r.px(x, y + 1, pal.shade(col, 0.55))
        (a if i % 2 else b).raster.px(x, y + 1, col)
        (a if i % 2 else b).raster.px(x, y + 2, pal.shade(col, 0.8))
    return [a, b] if lit else []


def _sill_items(r: Raster, C: dict, phase: str) -> None:
    """A Philly snow globe and a puzzle cube on the window sill."""
    r.rect(122, 132, 12, 4, C["wood_dark"])
    r.hline(122, 132, 12, C["wood"])
    r.disc(128, 126.5, 5.5, pal.mix(C["paper"], pal.room("#9fd0f0", phase), 0.5))
    r.rect(125, 129, 6, 3, C["paper_shade"])
    r.rect(127, 123, 2, 6, C["paper_shade"])
    r.px(127, 122, C["paper_shade"])
    r.px(127, 125, C["ink"])
    for x, y in ((124, 125), (130, 124), (126, 128), (131, 127), (129, 122)):
        r.px(x, y, C["white"])
    r.px(124, 122, C["white"])
    stickers = ["#d83a3a", "#f2f2f2", "#2b6bd8", "#f2c83a", "#3ab85a", "#f28a2a"]
    r.rect(141, 129, 8, 7, C["ink"])
    for i in range(3):
        for j in range(3):
            col = pal.room(stickers[(i * 3 + j * 2) % 6], phase)
            r.rect(142 + i * 2, 130 + j * 2, 1, 1, col)
            r.rect(142 + i * 2, 130 + j * 2, 2, 2, col)
    r.hline(141, 128, 8, pal.room("#3a3a40", phase))


def _chair(r: Raster, C: dict, s: SceneState) -> None:
    """The back of an office chair in the foreground."""
    fabric = pal.room("#2e3240", s.phase)
    mesh = pal.room("#3a3f50", s.phase)
    rim = pal.room("#5a6078", s.phase)
    if s.phase in ("dusk", "night"):
        rim = pal.mix(rim, "#5b8fe0", 0.35)  # caught by the monitor's glow
    r.ellipse(272, 182, 36, 20, fabric)
    for y in range(162, STATUS_Y):
        for x in range(236, 309):
            if r.get(x, y) == fabric and (x + y) % 4 == 0:
                r.px(x, y, mesh)
    for x in range(236, 309):
        for y in range(160, STATUS_Y):
            if r.get(x, y) in (fabric, mesh):
                r.px(x, y, rim)
                break


def _window_light(s: SceneState) -> Sprite:
    """Light falling through the window onto the desk."""
    color, opacity = {
        "day": ("#fff1c4", 0.16), "dawn": ("#ffb07a", 0.12),
        "dusk": ("#ff9a6a", 0.09), "night": ("#9fb8ff", 0.06),
    }[s.phase]
    if s.weather != "clear" and s.phase in ("day", "dawn"):
        opacity /= 2
    sp = _sprite("", f"opacity:{opacity:.3f}")
    sp.raster.poly([(14, DESK_Y), (202, DESK_Y), (236, STATUS_Y), (48, STATUS_Y)], color)
    return sp


# --- desk objects ---------------------------------------------------------------


def _plant(r: Raster, C: dict, s: SceneState) -> None:
    """A plant on the sill that grows one leaf for every five days of streak."""
    r.poly([(164, 128), (175, 128), (174, 136), (165, 136)], C["pot"])
    r.poly([(171, 128), (175, 128), (174, 136), (171, 136)], C["pot_dark"])
    r.rect(163, 127, 13, 2, C["pot_rim"])
    leaves = [
        (166.5, 123.5, 4, 2, C["leaf"]), (172.5, 122.5, 4, 2, C["leaf_mid"]),
        (169.5, 119.5, 2, 4, C["leaf"]), (164.5, 119.5, 3, 1.5, C["leaf_mid"]),
        (174.5, 118.5, 3, 1.5, C["leaf"]), (167.5, 115.5, 1.5, 3, C["leaf_mid"]),
        (172.5, 114.5, 1.5, 3, C["leaf"]), (170.5, 111.5, 1.5, 3, C["leaf_mid"]),
    ]
    count = min(len(leaves), 3 + s.stats.streak_days // 5)
    for cx, cy, rx, ry, col in leaves[:count]:
        r.ellipse(cx, cy, rx, ry, col)
        r.px(int(cx) - 1, int(cy) - 1, C["leaf_hi"])
    r.vline(169, 118, 9, C["leaf"])


def _lamp(r: Raster, C: dict, s: SceneState, sprites: list[Sprite]) -> None:
    """A brass desk lamp angled over the desk."""
    brass, brass_dark, brass_hi = C["lamp"], C["lamp_dark"], C["lamp_hi"]
    r.ellipse(190, 145.5, 7, 1.6, brass_dark)
    r.hline(185, 144, 10, brass)
    for dx in (0, 1):
        r.line(189 + dx, 144, 185 + dx, 124, brass_dark)
        r.line(185 + dx, 124, 195 + dx, 112, brass_dark)
    r.disc(186, 124, 1.6, brass)
    r.poly([(187, 109), (200, 103), (209, 113), (193, 120)], brass)
    r.poly([(196, 106), (200, 103), (209, 113), (202, 117)], brass_dark)
    r.line(188, 109, 199, 104, brass_hi)
    r.line(193, 120, 209, 113, C["metal"])
    on = s.phase != "day"
    if on:
        r.line(195, 119, 207, 114, "#fff1b8")
        r.line(196, 118, 205, 114, "#ffe08a")
        cone = _sprite("", "opacity:.16" if s.phase in ("night", "dusk") else "opacity:.08")
        cone.raster.poly([(194, 119), (207, 115), (230, DESK_Y + 4), (170, DESK_Y + 4)],
                         "#ffe2a0")
        sprites.append(cone)


def _mug(r: Raster, C: dict, sprites: list[Sprite]) -> None:
    r.hline(207, DESK_Y, 13, C["wood_dark"])
    r.ellipse(212.5, 136.5, 4.5, 1.5, C["mug_shade"])
    r.ellipse(212.5, 136.5, 3.5, 1, C["coffee"])
    r.rect(208, 137, 9, 9, C["mug"])
    r.rect(215, 137, 2, 9, C["mug_shade"])
    r.ellipse(212.5, 145.5, 4.5, 1, C["mug_shade"])
    r.rect(210, 140, 4, 3, C["navy"])  # a small dragon-blue badge on the mug
    r.px(211, 141, C["gold"])
    r.px(212, 141, C["gold"])
    for x, y in ((217, 139), (218, 139), (219, 140), (219, 141), (219, 142), (218, 143),
                 (217, 143)):
        r.px(x, y, C["mug_shade"])
    for i, x in enumerate((210, 214)):
        sp = _sprite("steam", f"animation-delay:-{i * 1.5:.1f}s")
        for k, dx in enumerate((0, 1, 1, 0, -1, -1, 0)):
            sp.raster.px(x + dx, 135 - k, "#d8dce4")
        sprites.append(sp)


def _controller(r: Raster, C: dict) -> None:
    r.rect(222, 142, 11, 4, C["pad"])
    r.disc(222.5, 144.5, 2.4, C["pad"])
    r.disc(232.5, 144.5, 2.4, C["pad"])
    r.hline(222, 146, 11, C["pad_dark"])
    r.hline(224, 143, 3, C["pad_hi"])
    r.vline(225, 142, 3, C["pad_hi"])
    r.px(230, 142, "#d65a5a")
    r.px(232, 143, "#5ad16a")
    r.px(230, 144, "#5a9ad6")
    r.px(228, 143, "#e8c65a")


def _monitor(r: Raster, C: dict, s: SceneState, rng: random.Random,
             sprites: list[Sprite]) -> None:
    bezel, bezel_hi, bezel_lo = "#2b3040", "#3d4458", "#1f2330"
    r.rect(238, 62, 74, 64, bezel)
    r.hline(238, 62, 74, bezel_hi)
    r.vline(238, 62, 64, bezel_hi)
    r.hline(238, 125, 74, bezel_lo)
    r.rect(271, 59, 8, 3, bezel)
    r.px(274, 60, "#5ad1ff")
    r.rect(271, 126, 8, 15, C["metal"])
    r.vline(271, 126, 15, C["metal_light"])
    r.poly([(262, DESK_Y), (266, 141), (284, 141), (288, DESK_Y)], C["metal"])
    r.px(308, 123, "#3fb950")
    screen = "#0d1117"
    r.rect(242, 66, 66, 56, screen)
    for k in range(6):
        r.px(244 + k, 67 + k, "#161c26")
    gray, white, green, amber = "#8b949e", "#c9d1d9", "#3fb950", "#d29922"
    clock = s.when.strftime("%H:%M")
    r.text(244, 69, "QUEUE", gray)
    r.text(307 - text_width(clock), 69, clock, gray)
    for i, name in enumerate(rng.sample(TICKETS, 3)):
        y = 77 + i * 7
        r.text(244, y, name[:12], white)
        sp = _sprite("ok", f"animation-delay:{i * 1.5:.1f}s")
        sp.raster.text(300, y, "OK", green)
        sprites.append(sp)
    r.hline(244, 98, 62, "#30363d")
    r.text(244, 101, f"STREAK {s.stats.streak_days}D", amber)
    done, floors = tower_progress(s.stats.contributions_total)
    tower = "SKYLINE DONE" if done == len(LOTS) else f"TOWER {floors}/{TOWER_FLOORS} FL"
    r.text(244, 108, tower, "#7fc0d0")
    # The latest commit message types itself out: a screen-coloured cover slides
    # right one letter at a time, with the cursor riding along its edge.
    r.text(244, 115, ">", green)
    r.text(252, 115, _commit_text(s), gray)
    cover = _sprite("type")
    cover.clip = "screen"
    cover.raster.rect(252, 115, 64, 5, screen)
    cur = _sprite("typecur")
    cur.clip = "screen"
    cur.raster.rect(252, 115, 3, 5, white)
    sprites += [cover, cur]
    # Keyboard and mouse
    r.rect(244, DESK_Y - 1, 56, 3, "#3a3f4c")
    for x in range(245, 299, 3):
        r.rect(x, DESK_Y - 1, 2, 1, "#5a6070")
    r.hline(244, DESK_Y + 2, 56, "#252832")
    r.rect(304, DESK_Y - 1, 6, 3, "#3a3f4c")
    r.px(306, DESK_Y - 1, "#5a6070")


def _seam(cx: float, cy: float, rad: float, x: int, y: int, side: int) -> bool:
    """True for pixels on a curved seam bulging in from the left or right edge."""
    ox = cx + side * rad * 1.55
    d = math.hypot(x + 0.5 - ox, y + 0.5 - cy)
    return abs(d - rad * 1.05) < 0.6


# Half-width and half-height of each keepsake ball. The baseball is close to
# real size next to the mug; the football and basketball are souvenir minis.
BALL_SIZE = {"baseball": (4.2, 4.2), "basketball": (5.6, 5.6), "football": (6.5, 4.0)}


def _keepsake_ball(r: Raster, C: dict, kind: str, cx: float, cy: float) -> None:
    """A team ball with seams or laces that read clearly at desk size."""
    if kind == "football":
        rx, ry = BALL_SIZE["football"]
        r.ellipse(cx, cy, rx, ry, "#5e3418")
        r.ellipse(cx - 0.5, cy - 0.5, rx - 0.7, ry - 0.6, "#8a4f26")
        r.ellipse(cx - 2, cy - 1.5, 2.5, 1, "#a8673a")
        for x in (int(cx) - 5, int(cx) + 4):
            r.vline(x, int(cy) - 2, 3, C["paper"])
        r.hline(int(cx) - 2, int(cy) - 2, 5, C["paper"])
        for x in range(int(cx) - 2, int(cx) + 3, 2):
            r.px(x, int(cy) - 3, C["paper"])
            r.px(x, int(cy) - 1, C["paper"])
        return
    rad = BALL_SIZE[kind][0]
    m = Mask(W, H)
    m.disc(cx, cy, rad, "x")
    if kind == "baseball":
        base, shade_col, seam = C["paper"], C["paper_shade"], C["red"]
    else:
        base, shade_col, seam = "#e07a2a", "#b85a1a", "#3a1a0a"
    for x, y in m.points:
        lower_right = (x + 0.5 - cx) + (y + 0.5 - cy) > rad * 0.9
        r.px(x, y, shade_col if lower_right else base)
    for x, y in m.points:
        on_seam = _seam(cx, cy, rad, x, y, -1) or _seam(cx, cy, rad, x, y, 1)
        if kind == "basketball":
            on_seam = on_seam or x == int(cx) or y == int(cy)
            if on_seam:
                r.px(x, y, seam)
        elif on_seam and (x + y) % 2 == 0:  # baseball stitches
            r.px(x, y, seam)
    r.px(int(cx - rad * 0.4), int(cy - rad * 0.55), "#ffffff" if kind == "baseball" else "#f2a060")


def _desk_balls(r: Raster, C: dict, s: SceneState) -> None:
    """Each team playing today gets its ball on a small wooden display stand."""
    x = 82
    for key in s.teams:
        team = pal.TEAMS[key]
        kind = team["ball"]
        hw, hh = BALL_SIZE[kind]
        w = round(hw * 2) + 2
        top = DESK_Y - 3
        r.hline(x - 1, DESK_Y, w + 2, C["wood_dark"])  # shadow
        r.rect(x, top, w, 3, C["wood"])
        r.hline(x, top, w, C["wood_light"])
        r.hline(x + 1, top + 1, w - 2, team["primary"])  # team-colour band
        r.poly([(x + w / 2 - 2, top), (x + w / 2, top - 1.5), (x + w / 2 + 2, top)],
               C["wood_dark"])  # the cup the ball rests in
        _keepsake_ball(r, C, kind, x + w / 2, top - hh + 0.3)
        x += w + 4


def _dragon(r: Raster, C: dict, s: SceneState, sprites: list[Sprite]) -> None:
    """A navy-and-gold dragon plush sitting on the desk."""
    navy, navy_d, navy_l = C["navy"], C["navy_dark"], C["navy_light"]
    gold, gold_d, gold_l = C["gold"], C["gold_dark"], C["gold_light"]

    r.hline(28, DESK_Y, 32, C["wood_dark"])  # shadow on the desk
    # Tail base; the curled tip is two frames that alternate, so it wags.
    r.poly([(52, 141), (61, 137), (63, 143), (56, 146)], navy)
    r.poly([(57, 139), (58, 135), (60, 138)], gold)
    up, down = _sprite("wa"), _sprite("wb")
    up.raster.poly([(60, 138), (63, 137), (66, 130), (69, 131), (67, 139), (62, 144)], navy)
    up.raster.poly([(63, 133), (65, 128), (66, 132)], gold)
    up.raster.px(68, 130, gold_l)
    down.raster.poly([(60, 138), (65, 137), (70, 133), (72, 135), (67, 141), (62, 144)], navy)
    down.raster.poly([(65, 136), (68, 131), (68, 135)], gold)
    down.raster.px(71, 133, gold_l)
    sprites += [up, down]
    # Wings behind the body
    for sign in (1, -1):
        def m(x: float, sign: int = sign) -> float:
            return 42 + (x - 42) * sign
        r.poly([(m(31), 125), (m(18), 115), (m(21), 121), (m(16), 124), (m(22), 127),
                (m(18), 131), (m(31), 132)], gold)
        r.line(round(m(31)), 125, round(m(18)), 115, navy_d)
        r.line(round(m(30)), 128, round(m(16)), 124, gold_d)
        r.line(round(m(30)), 131, round(m(18)), 131, gold_d)
    # Body
    r.ellipse(42.5, 136.5, 12, 10, navy_d)
    r.ellipse(41.5, 135.5, 11, 9, navy)
    r.ellipse(37, 131, 3, 2, navy_l)
    r.ellipse(42.5, 138.5, 7, 6.5, gold)
    for y in (135, 138, 141):
        for x in range(36, 50):
            if r.get(x, y) == gold and r.get(x - 1, y) == gold and r.get(x + 1, y) == gold:
                r.px(x, y, gold_d)
    # Arms and feet
    r.ellipse(31.5, 137.5, 2.5, 3.5, navy)
    r.ellipse(53.5, 137.5, 2.5, 3.5, navy_d)
    for fx in (35.5, 49.5):
        r.ellipse(fx, 145, 4, 2, navy_d)
        r.hline(int(fx) - 1, 145, 3, gold)
    # Plush tag sewn into the side seam
    r.rect(27, 139, 3, 4, C["paper"])
    r.hline(27, 141, 3, C["red"])
    # Head
    for sign in (1, -1):
        def m(x: float, sign: int = sign) -> float:
            return 42 + (x - 42) * sign
        r.poly([(m(35), 111), (m(32), 103), (m(34), 102), (m(38), 110)], gold)
        r.px(round(m(33)) - (1 if sign < 0 else 0), 102, gold_l)
        r.poly([(m(31.5), 116), (m(27), 112), (m(32), 113)], gold)
    r.ellipse(42.5, 118.5, 11, 9.5, navy_d)
    r.ellipse(42, 117.5, 10.3, 8.8, navy)
    r.ellipse(37, 113, 3, 2, navy_l)
    for y in range(109, 113, 2):
        r.px(42, y, navy_l)
    r.poly([(40, 109), (42, 105), (44, 109)], gold)
    # Face
    r.ellipse(42.5, 122.5, 5.5, 3, navy_l)
    r.px(40, 121, navy_d)
    r.px(45, 121, navy_d)
    for x, y in ((40, 124), (41, 125), (42, 125), (43, 125), (44, 125), (45, 124)):
        r.px(x, y, navy_d)
    # Shiny button eyes keep their highlights even in a dark room.
    for ex in (37.5, 47.5):
        r.disc(ex, 117.5, 2.6, "#05070d")
        r.rect(int(ex) - 1, 115, 2, 2, "#ffffff")
        r.px(int(ex) + 1, 119, "#7f93c0")
    for x in (34, 35, 50, 51):
        r.px(x, 121, C["blush"])
    # Game-day scarf in the first team's colours
    if s.teams:
        t = pal.TEAMS[s.teams[0]]
        for x in range(32, 54):
            for y in range(125, 129):
                if r.get(x, y) is not None:
                    r.px(x, y, t["primary"] if (x // 2) % 2 else t["secondary"])
        r.rect(46, 128, 4, 9, t["primary"])
        r.rect(46, 131, 4, 2, t["secondary"])
        for x in (46, 48):
            r.px(x, 137, t["secondary"])
    # Blink
    lid = _sprite("lid")
    for ex in (35, 45):
        lid.raster.rect(ex, 115, 5, 5, navy)
        lid.raster.hline(ex, 118, 5, navy_d)
    sprites.append(lid)


HEATMAP = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]


def _heatmap(r: Raster, s: SceneState, x0: int, y0: int, weeks: int = 26) -> None:
    """The last six months of contributions, laid out like GitHub's graph."""
    counts = s.stats.calendar
    today_row = (s.when.weekday() + 1) % 7  # GitHub's rows start on Sunday
    today_cell = (weeks - 1) * 7 + today_row
    for k in range(today_cell + 1):
        cell = today_cell - k
        n = counts[-1 - k] if k < len(counts) else 0
        level = 0 if n == 0 else 1 if n < 3 else 2 if n < 6 else 3 if n < 10 else 4
        r.rect(x0 + (cell // 7) * 3, y0 + (cell % 7) * 3, 2, 2, HEATMAP[level])


def _status(r: Raster, s: SceneState) -> None:
    r.rect(0, STATUS_Y, W, H - STATUS_Y, "#0d1117")
    r.hline(0, STATUS_Y, W, "#30363d")
    st = s.stats
    login = st.login.upper()
    r.text(6, 185, login, "#e6edf3")
    rest = (f"  {st.contributions_year} CONTRIBUTIONS  {st.streak_days}D STREAK"
            f"  {st.repo_count} REPOS")
    r.text(6 + text_width(login) + 4, 185, rest, "#8b949e")
    hour = s.when.strftime("%I:%M %p").lstrip("0")
    line = f"PHILLY {hour}  {s.weather.upper()}"
    if s.temp_f is not None:
        line += f" {s.temp_f}F"
    r.text(6, 194, line, "#8b949e")
    if s.teams:
        game = " + ".join(pal.TEAMS[t]["label"] for t in s.teams) + " GAME DAY"
        r.text(6 + text_width(line) + 8, 194, game, pal.TEAMS[s.teams[0]]["light"])
    _heatmap(r, s, W - 6 - 26 * 3 + 1, 182)


def draw_room(r: Raster, s: SceneState, rng: random.Random) -> list[Sprite]:
    """Draw the room over the window view. Returns its animated layers."""
    C = {k: pal.room(v, s.phase) for k, v in BASE.items()}
    sprites: list[Sprite] = []
    _wall(r, C)
    _window(r, C)
    _desk(r, C)
    if s.phase != "day":
        _glow(r, 200, 120, 64, "#ffcf7a", 0.24 if s.phase == "night" else 0.12)
    if s.phase in ("dusk", "night"):
        _glow(r, 275, 94, 48, "#5b8fe0", 0.14)
    _curtains(r, C)
    _calendar(r, C, s)
    _clock(r, C, s)
    if s.teams:
        _pennants(r, C, s.teams)
    else:
        _liberty_bell_print(r, C)
    sprites += _fairy_lights(r, C, s)
    if s.when.month == 12:
        _wreath(r, C)
    _sill_items(r, C, s.phase)
    if s.weather == "snow":
        r.hline(14, 135, 188, "#f4f7fb")  # snow piled on the outside ledge
    _shelf(r, C, s.phase)
    _plant(r, C, s)
    _lamp(r, C, s, sprites)
    _mug(r, C, sprites)
    _controller(r, C)
    _monitor(r, C, s, rng, sprites)
    _desk_balls(r, C, s)
    _dragon(r, C, s, sprites)
    _chair(r, C, s)
    sprites.append(_window_light(s))
    _status(r, s)
    return sprites
