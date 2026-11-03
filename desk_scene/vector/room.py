"""The room around the window: frame, curtains, wall things, the desk and what is on it."""

from __future__ import annotations

import itertools
import math

from .. import palette as pal
from ..growth import TOWER_FLOORS, tower_progress
from .layout import DESK_Y, FOOTER_Y, GX0, GX1, GY0, GY1, HEADER_H, Ctx, W
from .svg import Layer, Rects

# Daytime colours; Ctx.room() tints them for the time of day.
BASE = {
    "wall": "#5f7598", "wall2": "#566b8c", "trim": "#efe6d2", "trim2": "#cbbfa5",
    "wood": "#9a6440", "wood_l": "#b77b51", "wood_d": "#6b4129",
    "curtain": "#25386e", "curtain_d": "#172654", "gold": "#e8b440",
    "brass": "#d8b45a", "brass_d": "#9a7a32",
    "navy": "#24398a", "navy_d": "#16245c", "navy_l": "#3d5bb0",
    "belly": "#f4c44e", "belly_d": "#d49b2b", "horn": "#f7ead0", "blush": "#ff98ae",
    "metal": "#262a33", "metal_l": "#3a404c", "paper": "#f5f1e6", "red": "#d9473f",
    "pot": "#c0673f", "leaf": "#4f9a4a", "leaf_l": "#6dbb5c", "ink": "#2b2f3a",
}

SCREEN = (697, 268, 216, 140)  # x, y, width, height of the monitor's screen
TICKETS = (
    "VPN RESET", "MFA LOOP", "PRINTER JAM", "WIFI DROP", "PW RESET", "2FA PUSH",
    "LAB PC SLOW", "EMAIL SYNC", "LMS LOGIN", "AUDIO FIX", "PORT DEAD", "DRIVE MAP",
)
CHAR_W = 0.6  # monospace glyph width as a share of the font size
DRAGON_X = 150
# The tail wags around where it joins the body.
TAIL_ORIGIN = f".tail{{transform-origin:{DRAGON_X + 26}px {DESK_Y - 14}px}}"
MONTHS = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]


def _colors(c: Ctx) -> dict[str, str]:
    return {k: c.room(v) for k, v in BASE.items()}


def commit_line(c: Ctx) -> str:
    return f'git commit -m "{c.s.stats.latest_commit[:24]}"'


def typing_css(c: Ctx) -> str:
    """A cover that slides off the commit message one character at a time."""
    n = len(commit_line(c))
    dist = n * 8 * CHAR_W
    return (
        f"@keyframes type{{0%{{transform:translateX(-{dist:.1f}px)}}"
        f"70%,100%{{transform:translateX(0)}}}}"
        f".typecov{{animation:type 8s steps({n}) infinite}}"
    )


# ---------------------------------------------------------------- walls and window

def _wall(L: Layer, c: Ctx, C: dict) -> None:
    top, bottom = HEADER_H, DESK_Y
    stripes = c.defs.pattern(
        f"paper-{c.phase}", 18, 18,
        f'<rect width="9" height="18" fill="{C["wall2"]}" opacity=".35"/>'
        f'<circle cx="13.5" cy="9" r="1" fill="{C["trim"]}" opacity=".18"/>',
    )
    for x, y, w, h in ((0, top, W, GY0 - top), (0, GY1, W, bottom - GY1),
                       (0, GY0, GX0, GY1 - GY0), (GX1, GY0, W - GX1, GY1 - GY0)):
        L.rect(x, y, w, h, C["wall"])
        L.rect(x, y, w, h, stripes)
    L.rect(0, DESK_Y - 16, W, 2, C["trim2"], opacity=0.6)


def _window(L: Layer, c: Ctx, C: dict) -> None:
    f = 12
    L.rect(GX0 - f, GY0 - f, GX1 - GX0 + 2 * f, f, C["trim"])
    L.rect(GX0 - f, GY0, f, GY1 - GY0, C["trim"])
    L.rect(GX1, GY0, f, GY1 - GY0, C["trim"])
    L.rect(GX0 - 3, GY0 - 3, GX1 - GX0 + 6, 3, C["trim2"])
    L.rect(GX0 - 3, GY0, 3, GY1 - GY0, C["trim2"])
    L.rect(GX1, GY0, 3, GY1 - GY0, C["trim2"])
    # Sill.
    L.rect(GX0 - 24, GY1, GX1 - GX0 + 48, 10, C["trim"])
    L.rect(GX0 - 24, GY1 + 10, GX1 - GX0 + 48, 4, C["trim2"])
    L.rect(GX0 - 24, GY1 + 14, GX1 - GX0 + 48, 3, "#000000", opacity=0.12)


def _curtains(L: Layer, c: Ctx, C: dict) -> None:
    rod_y = GY0 - 22
    folds = c.defs.linear(
        f"folds-{c.phase}",
        [(i / 8, C["curtain"] if i % 2 else C["curtain_d"]) for i in range(9)], x2=1, y2=0,
    )
    tie_y = GY1 - 92
    for side in (-1, 1):
        edge = GX0 - 30 if side < 0 else GX1 + 30
        inner = edge - side * 48
        tie_in = edge - side * 22
        bottom_in = edge - side * 38
        L.path(
            f"M{edge} {rod_y}L{inner} {rod_y}Q{inner + side * 18} {tie_y - 30} {tie_in} {tie_y}"
            f"Q{tie_in + side * 2} {tie_y + 40} {bottom_in} {GY1 + 12}L{edge} {GY1 + 12}Z",
            folds,
        )
        L.rect(min(edge, tie_in) - 2, tie_y - 3, abs(tie_in - edge) + 4, 6, C["gold"], rx=2)
    L.rect(GX0 - 46, rod_y - 4, GX1 - GX0 + 92, 4, C["brass_d"], rx=2)
    L.circle(GX0 - 48, rod_y - 2, 4, C["brass"])
    L.circle(GX1 + 48, rod_y - 2, 4, C["brass"])


def _fairy_lights(L: Layer, c: Ctx, C: dict) -> None:
    """Lights strung under the curtain rod; team colours on game days, rainbow in December."""
    y0 = GY0 - 14
    hooks = [GX0 - 20, GX0 + 130, GX0 + 290, GX0 + 440, GX1 + 20]
    wire = Layer()
    on = c.dark or c.phase == "dawn"
    bulbs = {0: Layer(), 1: Layer()}
    k = 0
    for a, b in itertools.pairwise(hooks):
        mid = (a + b) / 2
        sag = 16
        wire.path(f"M{a} {y0}Q{mid} {y0 + sag * 2} {b} {y0}", stroke=c.room("#3b3a35"),
                  stroke_width=0.8)
        for t in (0.12, 0.3, 0.5, 0.7, 0.88):
            x = (1 - t) ** 2 * a + 2 * (1 - t) * t * mid + t * t * b
            y = y0 + 2 * (1 - t) * t * sag * 2
            if c.december:
                col = pal.HOLIDAY_LIGHTS[k % 4]
            else:
                col = (c.team_light(k // 2) if k % 2 else None) or "#ffd98a"
            g = bulbs[k % 2]
            if on:
                g.circle(x, y + 3, 6, col, opacity=0.18)
                g.circle(x, y + 3, 3.6, col, opacity=0.35)
                g.circle(x, y + 3, 2.2, col)
            else:
                g.circle(x, y + 3, 1.8, pal.mix(col, "#888888", 0.5))
            k += 1
    L.add(wire)
    L.group(bulbs[0], class_="fa" if on else None)
    L.group(bulbs[1], class_="fb" if on else None)


def _wreath(L: Layer, c: Ctx, C: dict) -> None:
    if not c.december:
        return
    x, y = GX0 + 40, GY0 + 46
    L.line(x, GY0, x, y - 16, C["red"], 1.2)
    L.circle(x, y, 16, "none", stroke=c.room("#2f6b3a"), stroke_width=9)
    for k in range(16):
        a = k / 16 * math.tau
        L.circle(x + math.cos(a) * 16, y + math.sin(a) * 16, 2.6, c.room("#3f8a4a"))
    for k in range(6):
        a = k / 6 * math.tau + 0.3
        L.circle(x + math.cos(a) * 16, y + math.sin(a) * 16, 1.8, C["red"])
    L.path(f"M{x - 6} {y + 16}l6 -4l6 4l-2 7l-4 -5l-4 5z", C["red"])


# ---------------------------------------------------------------- wall decor

def _pennants(L: Layer, c: Ctx, C: dict) -> None:
    """A felt pennant per team playing today; a plain PHILA one otherwise."""
    games = c.games
    flags = [(pal.TEAMS[g.team]["primary"], pal.TEAMS[g.team]["secondary"],
              pal.TEAMS[g.team]["label"]) for g in games] or [(C["navy"], C["gold"], "PHILA")]
    x, y = 676, 90
    for i, (bg, trim, label) in enumerate(flags[:3]):
        yy = y + i * 36
        bg, trim = c.room(bg), c.room(trim)
        L.poly([(x, yy), (x + 120, yy + 14), (x, yy + 28)], bg)
        L.rect(x, yy, 9, 28, trim)
        L.circle(x + 4.5, yy + 4, 1.4, c.room("#cfcfcf"))
        L.text(x + 14, yy + 18, label, 10.5, c.room("#ffffff") if games else C["gold"],
               font_weight="800", letter_spacing=1.2)
        L.line(x + 1, yy - 4, x + 4.5, yy + 4, c.room("#555555"), 0.6)


def _corkboard(L: Layer, c: Ctx, C: dict) -> None:
    """Help-desk notes pinned above the monitor."""
    x, y, w, h = 676, 196, 112, 60
    L.rect(x + 2, y + 2, w, h, "#000000", opacity=0.15, rx=2)
    L.rect(x, y, w, h, C["wood_d"], rx=2)
    L.rect(x + 3, y + 3, w - 6, h - 6, c.room("#c49a6c"))
    notes = (("#ffe680", "REBOOT", "FIRST", -4), ("#9fd8ff", "SHIP IT", "", 3),
             ("#ffb3c7", "TICKETS", "→ ZERO", -2))
    for i, (col, a, b, rot) in enumerate(notes):
        nx, ny = x + 8 + i * 34, y + 9 + (i % 2) * 4
        g = Layer()
        g.rect(nx, ny, 28, 26, c.room(col))
        g.text(nx + 14, ny + 11, a, 6, C["ink"], text_anchor="middle", font_weight="700")
        if b:
            g.text(nx + 14, ny + 20, b, 6, C["ink"], text_anchor="middle", font_weight="700")
        g.circle(nx + 14, ny + 2, 1.8, C["red"])
        L.group(g, transform=f"rotate({rot} {nx + 14} {ny + 13})")


def _calendar(L: Layer, c: Ctx, C: dict) -> None:
    x, y, w, h = 822, 88, 48, 54
    L.rect(x + 2, y + 2, w, h, "#000000", opacity=0.15, rx=2)
    L.rect(x, y, w, h, C["paper"], rx=2)
    L.rect(x, y, w, 15, C["red"], rx=2)
    L.rect(x, y + 10, w, 5, C["red"])
    L.text(x + w / 2, y + 11.5, MONTHS[c.s.when.month - 1], 9, c.room("#ffffff"),
           text_anchor="middle", font_weight="700", letter_spacing=1)
    L.text(x + w / 2, y + 44, str(c.s.when.day), 24, C["ink"], text_anchor="middle",
           font_weight="800")
    for hx in (x + 10, x + w - 10):
        L.circle(hx, y + 1, 1.8, C["metal"])


def _clock(L: Layer, c: Ctx, C: dict) -> None:
    """A wall clock showing the real Philadelphia time."""
    x, y, r = 914, 116, 22
    L.circle(x + 1.5, y + 2, r, "#000000", opacity=0.15)
    L.circle(x, y, r, C["metal"])
    L.circle(x, y, r - 3, C["paper"])
    for k in range(12):
        a = k / 12 * math.tau
        r1 = r - 6 if k % 3 == 0 else r - 5
        L.line(x + math.sin(a) * r1, y - math.cos(a) * r1, x + math.sin(a) * (r - 4),
               y - math.cos(a) * (r - 4), C["ink"], 1.2 if k % 3 == 0 else 0.7)
    t = c.s.when
    ha = ((t.hour % 12) + t.minute / 60) / 12 * math.tau
    ma = t.minute / 60 * math.tau
    L.line(x, y, x + math.sin(ha) * 9, y - math.cos(ha) * 9, C["ink"], 2.2, stroke_linecap="round")
    L.line(x, y, x + math.sin(ma) * 14, y - math.cos(ma) * 14, C["ink"], 1.4,
           stroke_linecap="round")
    L.circle(x, y, 1.6, C["red"])


def _shelf(L: Layer, c: Ctx, C: dict) -> None:
    y = 236
    L.rect(808, y, 140, 5, C["wood_l"])
    L.rect(808, y + 5, 140, 2, C["wood_d"])
    x = 814
    spines = ("#3d5bb0", "#d9473f", "#e8b440", "#4f9a4a", "#7a5aa8", "#2b8a9a", "#c0673f")
    for i, (bw, bh) in enumerate(((7, 24), (9, 20), (6, 26), (8, 22), (10, 19), (7, 23))):
        col = c.room(spines[i % len(spines)])
        L.rect(x, y - bh, bw, bh, col)
        L.rect(x + 1, y - bh + 4, bw - 2, 1.2, c.room("#f2e6c8"), opacity=0.7)
        x += bw + 1
    L.rect(x + 2, y - 7, 22, 7, c.room("#7a5aa8"))  # a book lying flat
    # A small brass Liberty Bell, crack and all.
    bx = 912
    L.path(f"M{bx - 9} {y}q1 -4 3 -6q1 -12 6 -13q5 1 6 13q2 2 3 6z", C["brass"])
    L.rect(bx - 1, y - 23, 2, 4, C["brass_d"])
    L.line(bx - 2, y - 14, bx + 1, y - 4, C["brass_d"], 0.8)
    L.rect(bx - 10, y - 1.5, 20, 1.5, C["brass_d"])


# ---------------------------------------------------------------- desk

def _desk(L: Layer, c: Ctx, C: dict) -> None:
    top = DESK_Y
    L.rect(0, top, W, 9, C["wood_l"])
    L.rect(0, top, W, 1.5, c.room("#d8a274"))
    L.rect(0, top + 9, W, FOOTER_Y - top - 9, C["wood"])
    L.rect(0, top + 9, W, 3, "#000000", opacity=0.18)
    grain = c.defs.pattern(
        f"grain-{c.phase}", 120, 14,
        f'<path d="M0 4q30 -2 60 0t60 0M10 10q40 2 80 0" stroke="{C["wood_d"]}" '
        f'stroke-width=".8" fill="none" opacity=".45"/>',
    )
    L.rect(0, top + 12, W, FOOTER_Y - top - 12, grain)
    for x0, w in ((60, 300), (600, 300)):
        L.rect(x0, top + 24, w, 56, "none", stroke=C["wood_d"], stroke_width=2, rx=3)
        L.rect(x0 + w / 2 - 22, top + 48, 44, 6, C["brass"], rx=3)
        L.rect(x0 + w / 2 - 22, top + 52, 44, 2, C["brass_d"], rx=1)


def _lamp(L: Layer, c: Ctx, C: dict, glow: Layer) -> None:
    """A brass desk lamp; it is switched on from dusk until morning."""
    bx = 566
    on = c.dark
    # Drawn for a desk top at y=420, then shifted onto the real desk.
    move = f"translate(0 {DESK_Y - 420})"
    lamp, light = Layer(), Layer()
    if on:
        cone = c.defs.linear("lampcone", [(0, "#ffe2a0", 0.45), (1, "#ffe2a0", 0.03)])
        light.poly([(502, 348), (530, 354), (600, 421), (380, 421)], cone)
        light.ellipse(480, 423, 110, 7, "#ffe2a0", opacity=0.22)
        light.circle(518, 350, 40, c.defs.radial(
            "lampglow", [(0, "#ffe2a0", 0.55), (1, "#ffe2a0", 0)]))
        glow.group(light, transform=move)
    lamp.ellipse(bx, 419, 18, 4.5, C["brass_d"])
    lamp.path(f"M{bx - 14} 418q14 -9 28 0z", C["brass"])
    lamp.path(f"M{bx} 414L{bx - 14} 360L526 336", stroke=C["brass"], stroke_width=3.2,
              stroke_linecap="round", stroke_linejoin="round")
    lamp.circle(bx - 14, 360, 3, C["brass_d"])
    lamp.circle(526, 336, 2.6, C["brass_d"])
    lamp.poly([(512, 322), (540, 330), (530, 354), (500, 346)], C["brass"])
    lamp.poly([(512, 322), (540, 330), (538, 335), (510, 327)], c.room("#f2d68a"))
    lamp.ellipse(515, 350, 15, 3.4, "#fff3c4" if on else C["brass_d"],
                 transform="rotate(15 515 350)")
    L.group(lamp, transform=move)


def _mug(L: Layer, c: Ctx, C: dict) -> None:
    x, y = 616, DESK_Y - 22
    L.ellipse(x + 11, DESK_Y, 13, 2.5, "#000000", opacity=0.2)
    L.path(f"M{x + 22} {y + 6}q8 0 8 7t-8 7", stroke=C["navy"], stroke_width=3.2)
    L.rect(x, y, 22, 22, C["navy"], rx=3)
    L.rect(x, y + 8, 22, 4, C["gold"])
    L.ellipse(x + 11, y + 1, 10, 2.4, c.room("#4a2c1c"))
    steam = Layer()
    for k, dx in enumerate((6, 12, 17)):
        steam.path(f"M{x + dx} {y - 2}q-3 -5 0 -9t0 -9", stroke=c.room("#ffffff"),
                   stroke_width=1.4, opacity=0.6, stroke_linecap="round",
                   class_="steam", style=f"animation-delay:-{k}s")
    L.add(steam)


def _plant(L: Layer, c: Ctx, C: dict) -> None:
    """A plant on the sill that grows a leaf for every five days of streak."""
    x, base = 456, GY1 + 2
    leaves = min(9, 3 + c.s.stats.streak_days // 5)
    for k in range(leaves):
        a = -math.pi / 2 + (k - (leaves - 1) / 2) * 0.42
        ln = 20 + (k % 3) * 4
        lx, ly = x + math.cos(a) * ln * 0.55, base - 20 + math.sin(a) * ln * 0.55
        deg = math.degrees(a) + 90
        L.ellipse(lx, ly, 4.2, ln / 2, C["leaf"] if k % 2 else C["leaf_l"],
                  transform=f"rotate({deg:.0f} {lx:.1f} {ly:.1f})")
    L.path(f"M{x - 12} {base - 20}h24l-3 20h-18z", C["pot"])
    L.rect(x - 13, base - 22, 26, 4, c.room("#d47a50"), rx=1)


def _books_and_globe(L: Layer, c: Ctx, C: dict) -> None:
    x = 250
    for i, (w, h, col) in enumerate(((60, 9, "#2b8a9a"), (54, 8, "#d9473f"), (58, 7, "#3d5bb0"))):
        y = DESK_Y - 9 - sum((9, 8, 7)[:i])
        L.rect(x + i * 2, y, w, h, c.room(col), rx=1)
        L.rect(x + i * 2 + w - 4, y + 1, 3, h - 2, C["paper"], opacity=0.8)
    # Snow globe with City Hall inside.
    gx, gy = x + 30, DESK_Y - 24 - 14
    L.rect(gx - 11, gy + 9, 22, 6, C["wood_d"], rx=1)
    L.circle(gx, gy, 12, c.room("#bfe3ff"), opacity=0.35)
    L.rect(gx - 2, gy - 6, 4, 14, c.room("#cdbf9e"))
    L.rect(gx - 7, gy + 3, 14, 5, c.room("#cdbf9e"))
    L.path(f"M{gx - 2} {gy - 6}q2 -4 4 0z", c.room("#cdbf9e"))
    for dx, dy in ((-6, -4), (5, -6), (-3, 2), (7, 1), (0, -9), (-8, 3)):
        L.circle(gx + dx, gy + dy, 0.9, "#ffffff")
    L.circle(gx, gy, 12, "none", stroke=c.room("#ffffff"), stroke_width=0.8, opacity=0.6)
    L.path(f"M{gx - 7} {gy - 6}q3 -4 8 -5", stroke="#ffffff", stroke_width=1.4, opacity=0.7)


def _controller(L: Layer, c: Ctx, C: dict) -> None:
    x, y = 360, DESK_Y + 2
    body = c.room("#3a3f4b")
    L.path(f"M{x} {y + 6}q0 -6 8 -6h22q8 0 8 6l2 6q0 4 -4 4l-6 -3h-22l-6 3q-4 0 -4 -4z", body)
    L.rect(x + 7, y + 4, 6, 2, c.room("#9aa0ab"))
    L.rect(x + 9, y + 2, 2, 6, c.room("#9aa0ab"))
    for dx, dy, col in ((28, 3, "#e05a5a"), (32, 5, "#5ab0e0"), (28, 7, "#5ad07a"),
                        (24, 5, "#e0c45a")):
        L.circle(x + dx, y + dy, 1.2, c.room(col))


def _monitor(L: Layer, c: Ctx, C: dict, glow: Layer) -> None:
    sx, sy, sw, sh = SCREEN
    if c.dark:
        glow.ellipse(sx + sw / 2, sy + sh / 2, 190, 130, c.defs.radial(
            "screenglow", [(0, "#6fa8ff", 0.28), (1, "#6fa8ff", 0)]))
    L.rect(sx + sw / 2 - 9, sy + sh + 8, 18, DESK_Y - sy - sh - 8, C["metal_l"])
    L.ellipse(sx + sw / 2, DESK_Y - 1, 34, 4, C["metal"])
    L.rect(sx - 9, sy - 9, sw + 18, sh + 18, C["metal"], rx=7)
    L.rect(sx - 9, sy - 9, sw + 18, 2, C["metal_l"], rx=1)
    L.rect(sx, sy, sw, sh, "#0b1220")
    L.circle(sx + sw / 2, sy + sh + 4.5, 1.2, "#3fb950" if c.dark else "#2a6b3a")

    ui = {"t": "#e6edf3", "m": "#8b949e", "g": "#7ee787", "b": "#79c0ff", "y": "#e3b341"}
    s = Layer()
    for k, col in enumerate(("#ff5f56", "#ffbd2e", "#27c93f")):
        s.circle(sx + 9 + k * 8, sy + 8, 2.4, col)
    s.text(sx + 38, sy + 11, "help-desk · queue", 8, ui["m"])
    s.rect(sx, sy + 16, sw, 0.8, "#30363d")
    tickets = c.rng.sample(TICKETS, 3)
    numbers = sorted(c.rng.sample(range(4810, 4899), 3))
    for i, name in enumerate(tickets):
        y = sy + 32 + i * 14
        s.text(sx + 8, y, f"#{numbers[i]}", 9, ui["m"])
        s.text(sx + 50, y, name, 9, ui["t"])
        s.text(sx + sw - 30, y, "...", 9, ui["m"])
        s.raw(f'<g class="ok" style="animation-delay:{i * 1.6:.1f}s">'
              f'<rect x="{sx + sw - 34}" y="{y - 9}" width="28" height="12" fill="#0b1220"/>'
              f'<text x="{sx + sw - 30}" y="{y}" font-size="9" fill="{ui["g"]}" '
              f'font-weight="700">OK</text></g>')
    st = c.s.stats
    _done, floors = tower_progress(st.contributions_total)
    y = sy + 82
    s.text(sx + 8, y, "streak", 9, ui["m"])
    s.text(sx + 58, y, f"{st.streak_days} days", 9, ui["y"], font_weight="700")
    y += 14
    s.text(sx + 8, y, "tower", 9, ui["m"])
    s.text(sx + 58, y, f"{floors}/{TOWER_FLOORS} fl", 9, ui["b"], font_weight="700")
    bar = Rects()
    for k in range(11):
        filled = k < round(floors / TOWER_FLOORS * 11)
        bar.add(sx + 118 + k * 8, y - 7, 6, 7, "#3fb950" if filled else "#21262d")
    s.add(bar)
    y += 22
    line = commit_line(c)
    s.text(sx + 8, y, "$", 8, ui["g"], font_weight="700")
    s.text(sx + 18, y, line, 8, ui["t"])
    # The cover rests just past the text, so a still frame shows the whole line; the
    # animation starts it over the text and slides it off one character at a time.
    end = sx + 18 + len(line) * 8 * CHAR_W
    s.raw(f'<g class="typecov"><rect x="{end:.1f}" y="{y - 9}" width="{sw:.0f}" '
          f'height="12" fill="#0b1220"/><rect x="{end + 1:.1f}" y="{y - 8}" width="5" '
          f'height="10" fill="{ui["g"]}" class="cur"/></g>')
    clip = c.defs.clip("screen", f'<rect x="{sx}" y="{sy}" width="{sw}" height="{sh}"/>')
    L.group(s, clip_path=clip)
    L.rect(sx, sy, sw, sh, c.defs.linear(
        "screenglare", [(0, "#ffffff", 0.07), (0.5, "#ffffff", 0), (1, "#ffffff", 0)], x2=1, y2=1))

    # Keyboard and mouse.
    kx, ky = sx + 4, DESK_Y + 6
    L.poly([(kx + 6, ky), (kx + 190, ky), (kx + 196, ky + 16), (kx, ky + 16)], C["metal"])
    keys = Rects()
    keycol = c.room("#4a5160")
    for row in range(3):
        for k in range(17):
            keys.add(kx + 8 + k * 10.8 - row * 0.8 + row * 0.2, ky + 2.5 + row * 4.4, 8.6, 3,
                     keycol)
    L.add(keys)
    L.ellipse(kx + 222, ky + 8, 8, 5.5, C["metal"])
    L.line(kx + 222, ky + 3, kx + 222, ky + 7, C["metal_l"], 0.8)


# ---------------------------------------------------------------- the dragon plush

def _dragon(L: Layer, c: Ctx, C: dict) -> None:
    """An original navy-and-gold dragon plush who keeps the desk company."""
    x, base = DRAGON_X, DESK_Y
    navy, navy_d, navy_l = C["navy"], C["navy_d"], C["navy_l"]
    gold, gold_d = C["belly"], C["belly_d"]
    plush = c.defs.radial(f"plush-{c.phase}", [(0, navy_l), (0.6, navy), (1, navy_d)],
                          cx=0.38, cy=0.32, r=0.75)
    L.ellipse(x, base + 1, 50, 4.5, "#000000", opacity=0.25)

    # Tail, wagging behind the body.
    tail = Layer()
    tail.path(f"M{x + 26} {base - 14}q26 4 34 -10q4 -10 -2 -16", stroke=navy, stroke_width=10,
              stroke_linecap="round")
    tail.path(f"M{x + 56} {base - 42}l-6 -10l12 2l2 12z", gold)
    L.group(tail, class_="tail")

    # Wings.
    for side in (-1, 1):
        # A soft bat wing: a navy arm along the top, gold membrane scalloped underneath.
        sx, sy = x + side * 22, base - 50
        tx, ty = sx + side * 34, sy - 30
        d = (f"M{sx} {sy}Q{sx + side * 10} {sy - 26} {tx} {ty}"
             f"Q{tx - side * 2} {ty + 14} {tx - side * 4} {ty + 22}"
             f"Q{tx - side * 10} {ty + 20} {tx - side * 12} {ty + 28}"
             f"Q{tx - side * 18} {ty + 26} {tx - side * 20} {ty + 34}"
             f"Q{sx + side * 6} {sy + 2} {sx} {sy + 8}Z")
        L.path(d, gold, stroke=navy_d, stroke_width=1.6, stroke_linejoin="round")
        L.path(f"M{sx} {sy}Q{sx + side * 10} {sy - 26} {tx} {ty}", stroke=navy,
               stroke_width=4, stroke_linecap="round")
        for k in (4, 12):
            L.line(tx - side * 1, ty + 3, tx - side * k, ty + 22 + k, gold_d, 1)

    # Body, belly, arms, feet.
    L.ellipse(x, base - 30, 35, 31, plush)
    L.ellipse(x, base - 24, 21, 22, gold)
    for k in range(3):
        L.path(f"M{x - 15 + k} {base - 34 + k * 9}q{15 - k} 5 {30 - 2 * k} 0", stroke=gold_d,
               stroke_width=1.3)
    L.ellipse(x, base - 24, 23, 24, "none", stroke=pal.mix(gold, "#ffffff", 0.4),
              stroke_width=0.9, stroke_dasharray="2 2.5", opacity=0.8)
    for side in (-1, 1):
        ax = x + side * 30
        L.ellipse(ax, base - 28, 8, 13, navy, transform=f"rotate({side * -28} {ax} {base - 28})")
        L.ellipse(x + side * 19, base - 5, 14, 7.5, navy)
        for t in (-5, 0, 5):
            L.circle(x + side * 19 + t, base - 1.5, 1.7, gold)
    L.rect(x - 34, base - 18, 9, 11, C["paper"], rx=1, transform=f"rotate(-12 {x - 30} {base - 12})")

    # Head.
    hy = base - 80
    for side in (-1, 1):
        hx = x + side * 20
        L.path(f"M{hx - side * 6} {hy - 24}q{side * 2} -22 {side * 16} -26q{side * -8} 14 "
               f"{side * -4} 28z", C["horn"])
        L.path(f"M{x + side * 38} {hy - 4}l{side * 14} -12l{side * -4} 22z", gold)
    for dx in (-8, 0, 8):
        L.path(f"M{x + dx - 4} {hy - 30}l4 -8l4 8z", gold)
    L.ellipse(x, hy, 41, 33, plush)
    L.ellipse(x, hy + 15, 21, 12, navy_l)
    L.ellipse(x - 6, hy + 12, 2, 1.4, navy_d)
    L.ellipse(x + 6, hy + 12, 2, 1.4, navy_d)
    for side in (-1, 1):
        ex = x + side * 17
        L.circle(ex, hy - 2, 9, "#070b18")
        L.circle(ex, hy - 2, 9, "none", stroke=navy_l, stroke_width=1)
        L.circle(ex - 3, hy - 5.5, 3.2, "#ffffff")
        L.circle(ex + 3, hy + 2, 1.5, "#ffffff", opacity=0.85)
        L.ellipse(x + side * 29, hy + 11, 6.5, 3.6, C["blush"], opacity=0.55)
    L.path(f"M{x - 7} {hy + 20}q3.5 4 7 0q3.5 4 7 0", stroke=navy_d, stroke_width=1.6,
           stroke_linecap="round")
    L.path(f"M{x + 2} {hy + 21.5}l1.5 3l1.5 -3z", "#ffffff")
    lids = Layer()
    for side in (-1, 1):
        lids.ellipse(x + side * 17, hy - 2, 10, 10, navy)
        lids.path(f"M{x + side * 17 - 8} {hy - 1}q8 5 16 0", stroke=navy_d, stroke_width=1.4)
    L.group(lids, class_="lid")

    # A team scarf on game days.
    games = c.games
    if games:
        team = pal.TEAMS[games[0].team]
        p, s2 = c.room(team["primary"]), c.room(team["secondary"])
        L.rect(x - 30, base - 58, 60, 10, p, rx=5)
        for k in range(5):
            L.rect(x - 22 + k * 11, base - 58, 3, 10, s2, opacity=0.9)
        L.path(f"M{x + 12} {base - 50}l12 26l-9 3l-10 -27z", p)
        L.rect(x + 14, base - 30, 10, 3, s2, transform=f"rotate(-20 {x + 19} {base - 28})")


# ---------------------------------------------------------------- put the room together

def draw(c: Ctx) -> Layer:
    C = _colors(c)
    L, glow = Layer(), Layer()
    _wall(L, c, C)
    _wreath(L, c, C)
    _window(L, c, C)
    _calendar(L, c, C)
    _clock(L, c, C)
    _pennants(L, c, C)
    _corkboard(L, c, C)
    _shelf(L, c, C)
    _curtains(L, c, C)
    _fairy_lights(L, c, C)
    _plant(L, c, C)
    _desk(L, c, C)
    front = Layer()
    _monitor(front, c, C, glow)
    _lamp(front, c, C, glow)
    _books_and_globe(front, c, C)
    _controller(front, c, C)
    _mug(front, c, C)
    _dragon(front, c, C)
    L.add(glow)
    L.add(front)
    return L
