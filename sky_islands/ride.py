"""The ride: one lap around the home island, unrolled into a long strip that loops.

The camera follows the train past four sides of the island, each with its own scenery
and its own sky: the town station, the stadium bridge, the wild side, and the west
Server Farm at sunset, then over one last bridge back into the town station. Behind the
islands, a small hazy copy of the far side of the loop drifts the other way, so the
places the train has passed come back round behind it. The town and stadium are drawn once for the overview and reused here
by reference (<use>), so the ride adds little to the file size.
"""

from __future__ import annotations

import itertools

from . import creatures, holidays
from . import palette as pal
from .clock import season
from .context import Ctx, H, W, sign
from .island import HOME, STADIUM, Shape, crystals, draw, waterfall
from .progress import cargo
from .rail import _train, _truss, _viaduct, cars_for, signal, train_length
from .serverfarm import server_farm
from .svg import Layer
from .world import UNLOCK, fly, level, sky_taxi, wonder

RAIL_Y = 408  # the track's height on screen during the ride
SCALE = 1.6  # the overview's islands are shown this much bigger on the ride
PAN = 3700  # one lap: the strip repeats after this, so the ride ends where it began
BG_DEPTH = 0.3  # the sky's distant scenery moves this fraction as fast (parallax)
FAR_K = 0.34  # size of the far side of the loop, seen across the island
FAR_RAIL_Y = 250  # where the far side's track sits on screen


def _place(shape: Shape, x0: float) -> tuple[float, float]:
    """Translate that puts an overview island's west edge at x0 and its rail on RAIL_Y."""
    rail_in_island = shape.top + 56
    return x0 - shape.x0 * SCALE, RAIL_Y - rail_in_island * SCALE


HOME_AT = 380
HOME_T = _place(HOME, HOME_AT)
HOME_END = HOME_AT + HOME.w * SCALE
STADIUM_AT = 1460
STADIUM_T = _place(STADIUM, STADIUM_AT)
STADIUM_END = STADIUM_AT + STADIUM.w * SCALE
WILD = Shape(cx=2400, top=258, w=820, depth=330)
FIELDS = Shape(cx=3500, top=300, w=760, depth=260)
# Scale railway parts drawn at overview size up to the ride's size, keeping the rail height.
TRACK_SPACE = f"translate(0 {RAIL_Y * (1 - SCALE):.1f}) scale({SCALE})"

# Stations the train stops at on the way round: (key, the strip's x the train is centred on).
# The wild-side stop sits between the Starport and the Shrine, so both are in view.
STOPS = (("stadium", STADIUM_AT + STADIUM.w * SCALE / 2), ("wild", WILD.cx), ("farm", FIELDS.cx))

SIDES = (  # (centre x, label) for the signs that name each side as it comes into view
    (760, "FRONT · THE TOWN"), (1600, "EAST · STADIUM BRIDGE"), (2400, "NORTH · THE WILDWOOD"),
    (3500, "WEST · THE SERVER FARM"),
)


# ---------------------------------------------------------------- the wild side

def _pine(L: Layer, x: float, base: float, h: float, col: str, snow: bool) -> None:
    """A pine of three tiers. Each tier set is one path (and the snow on it another), since
    the wild side draws dozens of these."""
    L.rect(x - 1, base - h * 0.25, 2, h * 0.25, "#3a2a20")
    tiers, caps = [], []
    for k in range(3):
        w = h * (0.42 - k * 0.1)
        y = base - h * (0.2 + k * 0.25)
        tiers.append(f"M{x - w:.1f} {y:.1f}L{x:.1f} {y - h * 0.38:.1f}L{x + w:.1f} {y:.1f}Z")
        caps.append(f"M{x - w * 0.3:.1f} {y - h * 0.26:.1f}L{x:.1f} {y - h * 0.38:.1f}"
                    f"L{x + w * 0.3:.1f} {y - h * 0.26:.1f}Z")
    L.path("".join(tiers), col)
    if snow:
        L.path("".join(caps), "#eef2f8")


def _wild_rock(c: Ctx) -> tuple[str, str]:
    """Mossy blue-grey stone for the wild side, still lit by the time of day."""
    r0, r1 = c.P["rock"]
    return pal.mix(r0, "#3e5a5c", 0.55), pal.mix(r1, "#0e1a1c", 0.5)


def wild_side(L: Layer, c: Ctx) -> None:
    """Cliffs and forest on the far side: jagged peaks, waterfalls, a ruin, glowing
    crystals and mushrooms. The forest gets denser with your streak."""
    s = WILD
    rock = _wild_rock(c)
    winter = season(c.w.when.month) == "winter"
    # Jagged peaks rising behind the forest.
    peak = pal.mix(rock[0], c.P["haze"], 0.25)
    pts = [(s.x0 + 40, s.top + 4)]
    x = s.x0 + 60
    while x < s.x1 - 60:
        pts.append((x, s.top - c.rng.uniform(40, 120)))
        x += c.rng.uniform(40, 80)
        pts.append((x, s.top - c.rng.uniform(10, 40)))
        x += c.rng.uniform(20, 40)
    pts.append((s.x1 - 40, s.top + 4))
    L.poly(pts, peak)
    for (x1, y1), (x2, y2) in itertools.pairwise(pts):
        if y2 < y1 - 30:  # light the sunward slopes of the tall peaks
            L.poly([(x1, y1), (x2, y2), (x2 + 6, y2 + 20)], c.P["rim"], opacity=0.15)
        if winter and y2 < s.top - 70:
            L.poly([(x2 - 10, y2 + 16), (x2, y2), (x2 + 10, y2 + 16)], "#eef2f8")
    draw(L, c, s, "wild", style="wild")
    crystals(L, c, s)
    # Moss and long vines on the cliff, some flowering.
    moss = c.lit("#3f7a4a")
    for _ in range(26):
        x = c.rng.uniform(s.x0 + 30, s.x1 - 30)
        L.ellipse(x, s.ground(x) + c.rng.uniform(16, 60), c.rng.uniform(8, 18), c.rng.uniform(3, 6),
                  moss, opacity=0.8)
    for _ in range(16):
        x = c.rng.uniform(s.x0 + 50, s.x1 - 50)
        y = s.ground(x) + 14
        ln = c.rng.uniform(60, 140)
        L.path(f"M{x:.0f} {y:.0f}q{c.rng.uniform(-12, 12):.0f} {ln / 2:.0f} "
               f"{c.rng.uniform(-6, 6):.0f} {ln:.0f}", stroke=moss, stroke_width=1.6)
        if c.rng.random() < 0.5:
            col = c.rng.choice(("#ff9fd8", "#9fe6ff", "#ffe08a"))
            L.circle(x, y + ln, 2.4, col)
            if c.dark:
                c.glow(L, x, y + ln, 10, col, 0.7, class_="pulse")
    for x in (s.x0 + 70, s.cx + 160, s.x1 - 60):
        waterfall(L, c, s, x)
    L.ellipse(s.cx, RAIL_Y + 70, s.w * 0.6, 26, "#ffffff", opacity=0.18, filter=c.defs.blur(12))
    # Two rows of pines: a hazy back row and a darker front row.
    trees = min(80, 20 + c.w.stats.streak_days * 3)
    for row, (shade_by, hz) in enumerate(((0.75, 0.35), (1.0, 0.0))):
        for _ in range(trees // 2):
            x = s.x0 + 40 + (s.w - 80) * c.rng.random()
            h = c.rng.uniform(24, 44) if row == 0 else c.rng.uniform(32, 62)
            green = c.lit(c.rng.choice(("#24503e", "#2c5e48", "#1d4434")))
            _pine(L, x, s.ground(x) + (0 if row == 0 else 5), h,
                  c.haze(pal.shade(green, shade_by), hz), winter)
    _elder_tree(L, c, s)
    # A ruined arch and a broken tower near the cliff's edge, with glowing mushrooms.
    stone = c.lit("#9a9aa8")
    joint = pal.shade(stone, 0.75)
    ax = s.x0 + 150
    base = s.ground(ax) + 2
    # The arch, built of dressed blocks, its keystone gone and one side crumbling.
    L.path(f"M{ax} {base}v-46a24 24 0 0 1 20 -23.6l2 6a17 17 0 0 0 -13 16.6v47z", stone)
    L.path(f"M{ax + 48} {base}v-46a24 24 0 0 0 -20 -23.6l-1 7a17 17 0 0 1 12 16.6v46z", stone)
    L.path("".join(f"M{ax} {base - k * 9}h9M{ax + 39} {base - k * 9}h9" for k in range(1, 6)),
           stroke=joint, stroke_width=0.7)
    L.rect(ax - 3, base - 4, 54, 4, pal.shade(stone, 0.85))
    for bx, by in ((ax + 22, base - 2), (ax + 30, base - 3), (ax + 56, base - 2)):
        L.rect(bx, by - 3, 6, 4, pal.shade(stone, 0.9), transform=f"rotate(12 {bx} {by})")
    # A broken tower beside it, with a slit window.
    L.path(f"M{ax + 64} {base}V{base - 70}L{ax + 69} {base - 78}L{ax + 72} {base - 72}"
           f"L{ax + 75} {base - 81}L{ax + 78} {base - 70}V{base}Z", stone)
    L.path("".join(f"M{ax + 64} {base - k * 10}h14" for k in range(1, 7)), stroke=joint,
           stroke_width=0.7)
    L.rect(ax + 69.5, base - 52, 3, 9, "#0e1418", rx=1.5)
    L.rect(ax + 74, base - 70, 4, 70, "#000000", opacity=0.15)
    # Moss and ivy creeping over it all.
    for mx, my, r in ((ax + 3, base - 40, 5), (ax + 44, base - 30, 4), (ax + 66, base - 60, 4),
                      (ax + 20, base - 66, 3.5), (ax + 76, base - 24, 4)):
        L.ellipse(mx, my, r, r * 0.6, moss)
    L.path(f"M{ax + 2} {base - 10}q10 -14 2 -30M{ax + 66} {base}q6 -20 -1 -44",
           stroke=moss, stroke_width=2)
    if c.dark:
        c.glow(L, ax + 24, base - 30, 30, "#9fe6ff", 0.5, class_="pulse")
    holidays.wild(L, c, ax + 24, base - 92)
    _wildlife(L, c, s)
    for k in range(5):
        mx = ax - 20 + k * 9
        cap = "#7fe3ff" if k % 2 else "#c58bff"
        L.rect(mx - 0.8, base - 6, 1.6, 6, c.lit("#e8e0f0"))
        L.path(f"M{mx - 4} {base - 6}q4 -6 8 0z", cap)
        if c.dark:
            c.glow(L, mx, base - 7, 8, cap, 0.8, class_="pulse",
                   style=f"animation-delay:-{k * .4:.1f}s")
    if c.dark and 5 <= c.w.when.month <= 9:  # fireflies on warm nights
        for _ in range(16):
            x = c.rng.uniform(s.x0 + 40, s.x1 - 40)
            y = s.ground(x) - c.rng.uniform(10, 70)
            L.circle(x, y, 1.3, "#e6ff9a", class_="tw",
                     style=f"animation-delay:-{c.rng.uniform(0, 4):.1f}s")


# The Starport and the Sky Shrine float free in the open sky between stops: the Starport
# between the stadium and the Wildwood, the Shrine between the Wildwood and the Server Farm.
# The train crosses the bridges beneath them and their life plays out as it passes.
NEAR = (("starport", "STARPORT", (STADIUM_END + WILD.x0) / 2, 205, 150),
        ("shrine", "SKY SHRINE", (WILD.x1 + FIELDS.x0) / 2, 200, 140))


def locked_nearby(L: Layer, c: Ctx) -> None:
    """The Starport and the Sky Shrine, floating on their own above the bridges."""
    for key, name, cx, top, w in NEAR:
        s = Shape(cx, top, w, w * 0.8)
        g = Layer()
        wonder(g, c, key, s, f"near-{key}", None, name)
        locked = level(c) < UNLOCK[key]
        sign(g, cx, top - (26 if locked else 60),
             f"{name} · UNLOCKS AT LV {UNLOCK[key]}" if locked else name,
             "#ffe08a" if locked else "#9fe6ff")
        L.group(g, class_="bob", style=f"animation-duration:{5 + int(cx) % 3}s")


def _elder_tree(L: Layer, c: Ctx, s: Shape) -> None:
    """The Wildwood's Elder Tree: an ancient tree in the middle of the forest that grows
    taller with your streak, with a treehouse, lanterns hanging from its boughs, a rope
    swing, and spirit lights drifting round it after dark."""
    x = s.cx
    base = s.ground(x) + 5
    h = 120 + min(60, c.w.stats.streak_days * 3)
    bark, dark = c.lit("#6a4a3a"), c.lit("#4a3428")
    month = c.w.when.month
    leaf = c.lit("#2f7a4e")
    if month in (9, 10, 11):
        leaf = pal.mix(leaf, c.lit("#d9822b"), 0.45)
    top = base - h * 0.62
    # Roots flaring into the ground, a tapering trunk and three big boughs.
    L.path(f"M{x - 26} {base}Q{x - 12} {base - 10} {x - 9} {base - 30}L{x - 7} {top}"
           f"H{x + 7}L{x + 9} {base - 30}Q{x + 12} {base - 10} {x + 28} {base}Z", bark)
    L.path(f"M{x + 2} {base - 4}Q{x + 4} {base - 40} {x} {top + 6}", stroke=dark,
           stroke_width=1.4, opacity=0.6)
    boughs = ((-1, 0.55, 46), (1, 0.6, 52), (-1, 0.82, 34))
    for side, at, reach in boughs:
        y0 = base - h * at
        L.path(f"M{x} {y0}Q{x + side * reach * 0.5} {y0 - 14} {x + side * reach} {y0 - 22}",
               stroke=bark, stroke_width=5, stroke_linecap="round")
    # The crown: overlapping rounds, lit from above, with a faint glow of its own at night.
    cy = base - h * 0.86
    if c.dark:
        c.glow(L, x, cy, 110, "#5ff0c0", 0.35, class_="pulse")
    for dx, dy, r, k in ((-42, 8, 30, 0.85), (40, 6, 32, 0.9), (0, -10, 40, 1.0),
                         (-22, -26, 26, 0.95), (24, -24, 28, 1.05), (0, 14, 30, 0.8)):
        L.circle(x + dx, cy + dy, r, pal.shade(leaf, k))
    glint = pal.mix(leaf, c.lit("#9fe0a0"), 0.4)
    for dx, dy, r in ((-30, -30, 13), (-8, -40, 15), (-50, -4, 10), (16, -38, 10)):
        L.circle(x + dx, cy + dy, r, glint, opacity=0.8)
    L.path(f"M{x - 7} {base - 30}L{x - 6} {top}", stroke=c.P["rim"], stroke_width=1.6,
           opacity=0.4)
    if month in (12, 1, 2):
        for dx, dy, r in ((-22, -46, 14), (8, -48, 18), (32, -40, 12), (-46, -12, 10)):
            L.ellipse(x + dx, cy + dy, r, r * 0.45, c.lit("#eef2fb"))
    if month in (3, 4, 5):
        for k in range(14):
            L.circle(x - 50 + (k * 37) % 100, cy - 30 + (k * 23) % 50, 1.8, c.lit("#ffc9dc"))
    # The treehouse on the right bough, with a lit window and a rope ladder.
    tx, ty = x + 54, base - h * 0.6 - 24
    L.rect(tx - 14, ty, 28, 3, dark)
    L.rect(tx - 10, ty - 14, 20, 14, pal.mix(c.lit("#c08a5a"), "#c08a5a", 0.4))
    L.poly([(tx - 13, ty - 14), (tx, ty - 24), (tx + 13, ty - 14)],
           pal.mix(c.lit("#c9473f"), "#c9473f", 0.4))
    lit = c.P["lamps"]
    L.rect(tx - 3, ty - 10, 6, 5, "#ffd98a" if lit else c.lit("#bfe4f8"))
    if lit:
        c.glow(L, tx, ty - 8, 14, "#ffcf7a", 0.7)
    L.path("".join(f"M{tx + 8} {ty + 3 + k * 6}h5" for k in range(6)), stroke=c.lit("#c9b48a"),
           stroke_width=0.8)
    L.path(f"M{tx + 8} {ty + 3}v34M{tx + 13} {ty + 3}v34", stroke=c.lit("#c9b48a"),
           stroke_width=0.6)
    # A rope swing from the left bough, swaying.
    sx, sy = x - 40, base - h * 0.55 - 18
    swing = Layer()
    swing.path(f"M{sx - 4} {sy}v30M{sx + 4} {sy}v30", stroke=c.lit("#c9b48a"), stroke_width=0.6)
    swing.rect(sx - 6, sy + 30, 12, 2, c.lit("#8a5d42"))
    L.group(swing, class_="swing")
    # Lanterns hanging from the boughs.
    for k, (dx, dy) in enumerate(((-30, 4), (-12, 16), (14, 12), (34, 2), (-50, 10), (54, 8))):
        lx, ly = x + dx, cy + 26 + dy
        L.line(lx, ly - 8, lx, ly, c.lit("#3a3050"), 0.5)
        L.ellipse(lx, ly + 2.6, 2.4, 3, "#ffd27a" if lit else c.lit("#e8b440"))
        if lit:
            c.glow(L, lx, ly + 2.6, 9, "#ffb35a", 0.7, class_="flick",
                   style=f"animation-delay:-{k * 0.3:.1f}s")
    if c.dark:
        for k in range(8):
            L.circle(x - 60 + (k * 47) % 120, cy - 40 + (k * 31) % 90, 1.2, "#bff4ff",
                     class_="tw", style=f"animation-delay:-{k * 0.5:.1f}s")


# ---------------------------------------------------------------- life in the Wildwood

DEER_HEAD_UP = ("M5.6 -15.6L9 -25.4L12.8 -24.6L10 -13Z",
                "M9.4 -27C11 -28.6 14.4 -28 16.6 -25.4L16.4 -24.2C14 -24.4 11.6 -23.6 9.6 -24.4Z",
                "M10 -26.6l-3 -2.4l3.6 .2z", (13.2, -26))
DEER_GRAZING = ("M5.6 -14.6L10.4 -6.6L13.2 -8.4L9.8 -14Z",
                "M10.4 -7.2C11.6 -8.6 14.6 -6.8 15.8 -3.4L14.8 -2.8C13 -4 11.4 -4.6 10 -5.4Z",
                "M11 -7.4l-2.4 -2.4l3.4 .4z", (13.6, -5.8))
ANTLERS = ("M11 -27.6l-1.4 -6l-3 -2.4M9.9 -32.4l2.4 -2.6M12.6 -27.4l1.6 -6.4l3 -1.8"
           "M14 -32.6l-.4 -3")


def _deer(c: Ctx, coat: str, light: str, grazing: bool = False, antlers: str | None = None,
          spots: bool = False) -> Layer:
    """A deer in profile facing right, hooves on y=0."""
    g = Layer()
    neck, head, ear, (ex, ey) = DEER_GRAZING if grazing else DEER_HEAD_UP
    for x0, x1 in ((-7, -7.6), (-4.4, -4), (5, 5.4), (7.6, 8)):
        g.line(x0, -10, x1, 0, pal.shade(coat, 0.8), 1.3)
    g.ellipse(-10, -15, 1.6, 2.2, light)
    g.ellipse(0, -13, 10, 5.6, coat)
    g.ellipse(0, -10.4, 7, 2, light, opacity=0.7)
    if spots:
        g.path("M-4 -15h0M-1 -16h0M2 -15h0M-2.6 -13h0M1 -13.4h0", stroke=light,
               stroke_width=1.2, stroke_linecap="round")
    g.path(neck, coat)
    g.path(head, coat)
    g.path(ear, pal.shade(coat, 0.85))
    g.circle(ex, ey, 0.5, "#1a1622")
    if antlers:
        g.path(ANTLERS, stroke=antlers, stroke_width=1, stroke_linecap="round")
    return g


def _rabbit(c: Ctx) -> Layer:
    g = Layer()
    fur = pal.mix(c.lit("#c9b49a"), "#c9b49a", 0.45)
    g.ellipse(0, -2.6, 3, 2.4, fur)
    g.circle(2.6, -4.4, 1.7, fur)
    g.path("M2.4 -5.8l-.6 -4l1.2 .2l.4 3.8zM3.2 -5.8l.4 -3.8l1.1 .4l-.6 3.6z", fur)
    g.circle(-2.8, -3, 0.9, "#ffffff")
    g.circle(3.3, -4.6, 0.35, "#1a1622")
    return g


def _owl(c: Ctx) -> Layer:
    g = Layer()
    g.path("M-3 -7l-.6 -2.4l1.8 1.4zM3 -7l.6 -2.4l-1.8 1.4z", c.lit("#6a4a3a"))
    g.ellipse(0, -4, 3, 4, c.lit("#7a5a44"))
    g.ellipse(0, -5, 2.5, 2, c.lit("#c9a87a"))
    eye = "#ffd27a" if c.dark else "#e8b440"
    for dx in (-1.1, 1.1):
        g.circle(dx, -5.2, 0.8, eye)
        g.circle(dx, -5.2, 0.35, "#1a1622")
    if c.dark:
        c.glow(g, 0, -5.2, 5, "#ffd27a", 0.5)
    g.path("M0 -4.6l-.4 .8h.8z", c.lit("#e8873a"))
    return g


def _fairy(c: Ctx, col: str) -> str:
    g = Layer()
    if c.dark:
        c.glow(g, 0, 0, 9, col, 0.7)
    wings = Layer()
    wings.ellipse(-1.4, -1.6, 1.6, 2.4, "#ffffff", opacity=0.6)
    wings.ellipse(1.4, -1.6, 1.6, 2.4, "#ffffff", opacity=0.6)
    g.group(wings, class_="flap")
    g.circle(0, 0, 1.3, col)
    g.circle(0, 0, 0.6, "#ffffff")
    return g.svg()


def _wildlife(L: Layer, c: Ctx, s: Shape) -> None:
    """The Wildwood's creatures: a spirit stag with glowing antlers, a grazing doe and her
    fawn, rabbits that hop now and then, an owl on the treehouse roof, and fairies flitting
    round the Elder Tree and through the trees."""
    def place(g: Layer, x: float, scale: float = 1.0, left: bool = False, **a) -> None:
        sx = -scale if left else scale
        L.group(g, transform=f"translate({x:.0f} {s.ground(x) + 5:.1f}) scale({sx} {scale})", **a)

    # The spirit stag: pale, with antlers of light, glowing brighter at night.
    stag = Layer()
    if c.dark:
        c.glow(stag, 4, -20, 34, "#bff4ff", 0.55, class_="pulse")
    stag.add(_deer(c, pal.mix(c.lit("#eef6ff"), "#eef6ff", 0.6), "#ffffff", antlers="#9ff0ff"))
    for k, (dx, dy) in enumerate(((8, -38), (16, -36), (12, -42))):
        stag.circle(dx, dy, 0.8, "#bff4ff", class_="tw", style=f"animation-delay:-{k}s")
    place(stag, s.cx - 120, 1.5)
    # Animals keep some of their own colour after dark, so they do not vanish.
    coat = pal.mix(c.lit("#b07a4a"), "#b07a4a", 0.45)
    light = pal.mix(c.lit("#ecd2a8"), "#ecd2a8", 0.45)
    place(_deer(c, coat, light, grazing=True), s.cx + 140, 1.35, left=True)
    place(_deer(c, coat, light, spots=True), s.cx + 96, 0.85, left=True)
    for k, x in enumerate((s.cx - 230, s.cx + 210)):
        place(_rabbit(c), x, 1.7, left=k == 1, class_="hop",
              style=f"animation-delay:-{k * 1.7:.1f}s")
    # The owl sits on the treehouse roof (see _elder_tree for where the treehouse is).
    h = 120 + min(60, c.w.stats.streak_days * 3)
    base = s.ground(s.cx) + 5
    L.group(_owl(c), transform=f"translate({s.cx + 54:.0f} {base - h * 0.6 - 48:.1f}) scale(1.5)")
    # Fairies, each flitting round its own little loop.
    tree_y = base - h * 0.86
    spots = ((s.cx - 70, tree_y + 30), (s.cx + 60, tree_y + 10), (s.cx - 20, tree_y - 50),
             (s.cx + 90, tree_y + 60), (s.cx - 160, s.top - 20), (s.cx + 200, s.top - 30),
             (s.cx - 260, s.top - 10), (s.cx + 280, s.top - 16), (s.cx + 10, tree_y + 70))
    cols = ("#ffe08a", "#ff9fd8", "#9ff0ff", "#b6ff9a")
    for k, (x, y) in enumerate(spots):
        loop = f"M{x:.0f} {y:.0f}c12 -12 32 -4 26 8c-6 12 -32 8 -26 -8z"
        L.raw(f'<g><g transform="scale(1.5)">{_fairy(c, cols[k % 4])}</g>'
              f'<animateMotion dur="{5 + k % 4 * 1.3:.1f}s" repeatCount="indefinite" '
              f'begin="-{k * 0.9:.1f}s" path="{loop}"/></g>')


# ---------------------------------------------------------------- the west side: see serverfarm.py

# ---------------------------------------------------------------- skies behind each side

def backdrop(L: Layer, c: Ctx) -> None:
    """Distant scenery for each side, laid out so it slides past at parallax speed."""
    def at(k: int) -> float:  # where side k's backdrop sits so it is centred when the train is there
        return W / 2 + (0, 1150, 1950, 3050, PAN)[k] * BG_DEPTH

    # Town side: the Philly island far away.
    for k in (0, 4):  # and again as the lap comes back round to the town
        L.raw(f'<use href="#isl-philly" transform="translate({at(k) - 60:.0f} 150) scale(.42)" '
              f'opacity=".55"/>')
    # Stadium side: open sky and a few distant islands.
    for dx, y, r in ((-120, 210, 26), (90, 180, 18), (220, 240, 30)):
        col = c.haze(c.P["rock"][0], 0.6)
        L.ellipse(at(1) + dx, y, r, r * 0.22, col, opacity=0.6)
        L.path(f"M{at(1) + dx - r} {y}Q{at(1) + dx} {y + r * 1.5} {at(1) + dx + r} {y}Z", col,
               opacity=0.6)
    for k, (dx, y, col) in enumerate(((-160, 140, "#e2574c"), (40, 110, "#3d9bd1"),
                                      (180, 170, "#e8b440"))):
        b = Layer()
        bx = at(1) + dx
        b.ellipse(bx, y, 14, 17, c.lit(col))
        b.ellipse(bx, y, 5, 17, "#ffffff", opacity=0.3)
        b.line(bx - 6, y + 14, bx - 3, y + 24, "#5a4a3a", 0.7)
        b.line(bx + 6, y + 14, bx + 3, y + 24, "#5a4a3a", 0.7)
        b.rect(bx - 4, y + 24, 8, 5, c.lit("#8a5d42"))
        if c.P["lamps"]:
            c.glow(b, bx, y + 20, 10, "#ffb35a", 0.7)
        L.group(b, class_="drift", style=f"animation-delay:-{k * 9}s", opacity=0.85)
    # Wild side: night creeps in, with a nebula, a river of stars and a sky whale.
    x = at(2)
    L.rect(x - 520, 0, 1040, H, c.defs.linear("wildsky", [(0, "#0a0620", 0), (0.25, "#0a0620", 0.75),
                                                          (0.75, "#0a0620", 0.75), (1, "#0a0620", 0)],
                                              x2=1, y2=0))
    for k, col in enumerate(("#c04aff", "#3ad1ff", "#ff6ab4", "#7a6aff")):
        L.ellipse(x - 300 + k * 190, 140 + (k % 2) * 70, 170, 60, col, opacity=0.18,
                  filter=c.defs.blur(28))
    L.ellipse(x, 160, 420, 34, "#fff6e0", opacity=0.16, filter=c.defs.blur(10),
              transform=f"rotate(-12 {x:.0f} 160)")
    for _ in range(120):
        sx, sy = x + c.rng.uniform(-480, 480), c.rng.uniform(50, 380)
        L.circle(sx, sy, c.rng.choice((0.6, 0.8, 1.1)), "#ffffff", opacity=0.85)
    # The sky whale swimming left through the star river, and jellies rising below it.
    L.raw(f'<g opacity=".6"><g transform="scale(-.5 .5)">{creatures.whale(c, True).svg()}</g>'
          f'<animateMotion dur="40s" repeatCount="indefinite" '
          f'path="M{x + 260:.0f} 120Q{x:.0f} 90 {x - 300:.0f} 140"/></g>')
    creatures.jellies(L, c, ((x - 230, 350, 1.2), (x - 160, 372, 0.9), (x + 120, 360, 1.3),
                             (x + 190, 384, 0.8), (x + 40, 395, 1.0)))
    # West side: the sun going down over far mountains.
    x = at(3)
    # The sunset tint fades out at both ends, so no edge of it ever crosses the frame as a
    # line in the sky; the mountains taper down into the clouds for the same reason.
    L.rect(x - 520, 0, 1300, H, c.defs.linear("westsky", [
        (0, "#ff9a60", 0), (0.25, "#ff9a60", 0.35), (0.7, "#ff7a50", 0.45), (1, "#ff7a50", 0)],
        x2=1, y2=0))
    c.glow(L, x + 140, 330, 260, "#ffcf7a", 0.75)
    L.circle(x + 140, 330, 34, "#ffe6b0")
    L.poly([(x - 640, 420), (x - 500, 400), (x - 380, 300), (x - 260, 360), (x - 120, 280),
            (x + 20, 350), (x + 160, 290), (x + 320, 360), (x + 560, 330), (x + 720, 420)],
           c.haze(c.P["rock"][0], 0.55), opacity=0.8)
    # A cargo airship heading home into the sunset.
    L.raw(f'<g transform="translate({x - 150:.0f} 150) scale(.8)"><g class="drift">'
          f'{creatures.airship(c).svg()}</g></g>')


# ---------------------------------------------------------------- the track and the train

def _suspension(L: Layer, c: Ctx, a: float, b: float, y: float) -> None:
    """A suspension bridge: two towers, main cables sagging between them, hangers to the deck."""
    steel, cable = c.lit("#8a8fa8"), c.lit("#c9c4dc")
    t1, t2 = a + 14, b - 14
    top = y - 70
    L.rect(a, y, b - a, 3, steel)
    L.rect(a, y + 3, b - a, 2, "#000000", opacity=0.3)
    for tx in (t1, t2):
        L.rect(tx - 3, top, 6, y - top + 26, steel)
        for z in (top + 8, top + 30, y - 16):
            L.rect(tx - 5, z, 10, 2.4, steel)
        L.line(tx - 3, top, tx - 3, y + 26, c.P["rim"], 0.6, opacity=0.6)
        L.circle(tx, top - 2, 1.8, "#ff4d4d", class_="av")
    for start, end, sag in ((a, t1, top + 40), (t1, t2, y - 10), (t2, b, top + 40)):
        L.path(f"M{start} {y if start == a else top}Q{(start + end) / 2} {sag} {end} "
               f"{y if end == b else top}", stroke=cable, stroke_width=1.2)
    n = int((t2 - t1) // 7)
    for k in range(1, n):
        x = t1 + (t2 - t1) * k / n
        u = (x - t1) / (t2 - t1)
        cy = (1 - u) ** 2 * top + 2 * (1 - u) * u * (y - 10) + u ** 2 * top
        L.line(x, cy, x, y, cable, 0.5, opacity=0.8)
    if c.P["lamps"]:
        for k in range(1, 6):
            x = t1 + (t2 - t1) * k / 6
            L.circle(x, y - 3, 1.2, "#ffd27a")
            c.glow(L, x, y - 3, 6, "#ffd27a", 0.6)


def track(L: Layer, c: Ctx) -> None:
    """The railway all the way round: viaducts on the cliffs, steel bridges between.
    Drawn at the overview's size and then scaled up to match the enlarged islands."""
    y, s = RAIL_Y, SCALE
    g = Layer()
    _viaduct(g, c, (HOME_AT + 10) / s, (HOME_END - 10) / s, y)
    _suspension(g, c, (HOME_END - 10) / s, (STADIUM_AT + 10) / s, y)
    _viaduct(g, c, (STADIUM_AT + 10) / s, (STADIUM_END - 10) / s, y)
    _truss(g, c, (STADIUM_END - 10) / s, (WILD.x0 + 10) / s, y)
    _viaduct(g, c, (WILD.x0 + 10) / s, (WILD.x1 - 10) / s, y)
    _truss(g, c, (WILD.x1 - 10) / s, (FIELDS.x0 + 10) / s, y)
    _viaduct(g, c, (FIELDS.x0 + 10) / s, (FIELDS.x1 - 10) / s, y)
    _truss(g, c, (FIELDS.x1 - 10) / s, (PAN + HOME_AT + 10) / s, y)  # back to the town
    g.line(HOME_AT / s, y - 1, (PAN + HOME_AT) / s, y - 1, "#2a2230", 1.2)
    g.line(HOME_AT / s, y - 1.7, (PAN + HOME_AT) / s, y - 1.7, c.P["rim"], 0.5, opacity=0.5)
    # Signals where the line leaves each island for a bridge: green one way, red the other.
    for k, x in enumerate((HOME_END, STADIUM_AT, STADIUM_END, WILD.x0, WILD.x1, FIELDS.x0,
                           FIELDS.x1)):
        signal(g, c, x / s + (-6 if k % 2 == 0 else 6), y, green=k % 2 == 0)
    # A platform wherever the train stops: the town station under its canopy, where it waits
    # when the ride begins, and open halts with lamp posts on the way round, so the sky
    # above the train stays clear.
    length = train_length(cars_for(c))
    nose = _nose_x(length)
    for offset in (0, *(x - W / 2 for _, x in STOPS)):
        ahead = 44 if offset == 0 else 20  # room past the nose for the station master
        x0, x1 = (nose + offset - length * s - 20) / s, (nose + offset + ahead) / s
        g.rect(x0, y + 1, x1 - x0, 5, c.lit("#b8aa94"))
        if offset == 0:
            for x in (x0 + 8, (x0 + x1) / 2, x1 - 8):
                g.line(x, y + 1, x, y - 22, c.lit("#3a3050"), 1.4)
            g.poly([(x0 - 5, y - 22), (x1 + 5, y - 22), (x1, y - 28), (x0, y - 28)],
                   c.lit("#5a4a6a"))
            lamps = [(x, y - 20) for x in (x0 + 16, x1 - 16)]
        else:
            for x in (x0 + 4, x1 - 4):
                g.path(f"M{x} {y + 1}V{y - 24}h{3 if x < x1 - 10 else -3}",
                       stroke=c.lit("#3a3050"), stroke_width=1.2)
            lamps = [(x0 + 7, y - 23), (x1 - 7, y - 23)]
            holidays.platform(g, c, x0 + 4, x1 - 4, y - 24, y + 1)
        for lx, ly in lamps:
            if offset:
                g.rect(lx - 1.6, ly - 1, 3.2, 3, pal.WINDOW if c.P["lamps"] else c.lit("#c9b48a"))
            if c.P["lamps"]:
                c.glow(g, lx, ly, 14, "#ffd27a", 0.7)
    L.group(g, transform=TRACK_SPACE)
    sign(L, nose - length * s / 2, y - 56, "TOWN STATION", "#ffd27a")
    _station_master(L, c, nose + 32, y + 1)


def _station_master(L: Layer, c: Ctx, x: float, base: float) -> None:
    """The town's station master on the platform, waving the train off and back in."""
    L.line(x - 1.6, base, x - 1.6, base - 7, c.lit("#1f2a44"), 2)
    L.line(x + 1.6, base, x + 1.6, base - 7, c.lit("#1f2a44"), 2)
    L.rect(x - 4, base - 17, 8, 11, c.lit("#1f4673"), rx=2)
    L.line(x - 4, base - 12, x + 4, base - 12, c.lit("#f4c76a"), 0.9)
    L.circle(x, base - 20.5, 3.2, c.lit("#f2c9a8"))
    L.rect(x - 3.8, base - 25, 7.6, 2.6, c.lit("#112844"), rx=1)
    L.rect(x - 4.6, base - 22.8, 9.2, 1, c.lit("#112844"))
    arm = Layer()
    arm.path(f"M{x + 3.5} {base - 15}l5 -7", stroke=c.lit("#1f4673"), stroke_width=2,
             stroke_linecap="round")
    arm.circle(x + 8.8, base - 22.4, 1.5, c.lit("#f2c9a8"))
    L.group(arm, class_="wave")


def _nose_x(length: float) -> float:
    """Where the train's nose stays during the ride, so the whole train is centred."""
    return W / 2 + length * SCALE / 2


def train(c: Ctx) -> Layer:
    cars = cars_for(c)
    g = Layer()
    g.group(_train(c, RAIL_Y, cars, cargo(c.w.stats), moving=True),
            transform=f"translate({_nose_x(train_length(cars)):.0f} {RAIL_Y * (1 - SCALE):.1f}) "
                      f"scale({SCALE})")
    return g


def town_traffic(L: Layer, c: Ctx) -> None:
    """Sky taxis buzzing around the town as the train leaves the station."""
    routes = ((f"M{HOME_AT - 80} 230Q{HOME_AT + 300} 150 {HOME_END + 60} 210", 11, 0),
              (f"M{HOME_END + 40} 170Q{HOME_AT + 500} 110 {HOME_AT + 40} 160", 13, -5),
              (f"M{HOME_AT + 200} 120Q{HOME_AT + 600} 200 {STADIUM_AT + 200} 150", 15, -9))
    for (path, dur, begin), left in zip(routes, (False, True, False), strict=True):
        fly(L, sky_taxi(c, 1.4, left), path, dur, begin)


def far_side(L: Layer) -> None:
    """The far side of the loop, seen across the island: the same strip, small and mirrored,
    placed so the point opposite the train is centred. It drifts right as the world slides
    left, so whatever the train passes comes back round behind it."""
    x0 = W / 2 + FAR_K * (W / 2 + PAN / 2)
    y0 = FAR_RAIL_Y - RAIL_Y * FAR_K
    for n in (0, 1):
        L.raw(f'<use href="#ride-strip" transform="translate({x0 - n * FAR_K * PAN:.0f} '
              f'{y0:.0f}) scale({-FAR_K} {FAR_K})"/>')


def draw_world(c: Ctx) -> tuple[Layer, Layer, Layer, str]:
    """The ride's distant backdrop, the far side of the loop, the world strip, and the CSS
    for what happens at each station."""
    from . import stations  # imported here: stations needs the camera, which needs this module

    bg, far, world = Layer(), Layer(), Layer()
    backdrop(bg, c)
    far_side(far)
    for k in range(5):
        world.raw(f'<use href="#clouds" transform="translate({k * W - 120} -30)"/>')
    strip = Layer()
    strip.raw(f'<use href="#isl-home" transform="translate({HOME_T[0]:.1f} {HOME_T[1]:.1f}) '
              f'scale({SCALE})"/>')
    strip.raw(f'<use href="#isl-stadium" transform="translate({STADIUM_T[0]:.1f} {STADIUM_T[1]:.1f}) '
              f'scale({SCALE})"/>')
    town_traffic(strip, c)
    wild_side(strip, c)
    locked_nearby(strip, c)
    server_farm(strip, c, FIELDS)
    track(strip, c)
    css = stations.draw(strip, c)
    for x, text in SIDES:
        sign(strip, x, 506, text, "#ffffff", 9)
    world.group(strip, id="ride-strip")
    # The strip again a lap before and a lap after, so the track runs on unbroken: the
    # Server Farm and the bridge home sit left of the station, and the ride ends where it began.
    for lap in (-PAN, PAN):
        world.raw(f'<use href="#ride-strip" transform="translate({lap} 0)"/>')
    return bg, far, world, css

