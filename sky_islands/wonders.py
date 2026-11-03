"""The late-game islands and what flies past them.

The Starport docks starfighters, one parked for every few pull requests you merged. The
Sky Shrine has a torii gate, cherry blossoms and stone lanterns, and is guarded by the
sky dragon, which flies across the sky on days your streak is a week or longer. A
squadron of starfighters crosses the sky as the loop opens.

Islands are drawn in their own frame, 150 wide with the ground at y=0, and scaled to fit,
so the same drawing serves the small overview island and the bigger one on the ride.
"""

from __future__ import annotations

import math

from .context import Ctx
from .svg import Layer

DESIGN_W = 150  # islands are drawn this wide and scaled to fit
DRAGON_STREAK = 7  # the dragon flies on days your streak is at least this long
DRAGON_CROSSING = 0.14  # the share of the loop the dragon takes to cross the sky
SQUADRON_WINDOW = (0.02, 0.12)  # when the starfighters cross (during the overview)


def starfighter(c: Ctx, scale: float = 1.0, left: bool = False, haze: float = 0.0) -> str:
    """An original starfighter seen from the side, nose to the right (or left): a pale hull
    with an orange stripe, a glass canopy, swept wings and a glowing engine."""
    def tone(col: str) -> str:
        return c.haze(c.lit(col), haze)

    hull, belly, accent = tone("#dfe3ec"), tone("#9aa3b8"), tone("#ff8a3a")
    fin = tone("#5a6480")
    return (f'<g transform="scale({-scale if left else scale} {scale})">'
            '<ellipse cx="-17" cy="0" rx="5" ry="1.4" fill="#7fe3ff" opacity=".8" class="flick"/>'
            f'<path d="M-6 -3L-11 -8.5H-13L-10.5 -3Z" fill="{fin}"/>'
            f'<path d="M15 0L5 -3.2L-9 -3.6L-13 -2V2L-9 3L5 2.6Z" fill="{hull}"/>'
            f'<path d="M15 0L5 2.6L-9 3L-13 2V0.6H8Z" fill="{belly}"/>'
            f'<path d="M7 -2.6Q3 -6.4 -3 -3.4Z" fill="{tone("#7fd8ff")}"/>'
            f'<rect x="-9" y="-0.9" width="13" height="1" fill="{accent}"/>'
            f'<path d="M3 1.4L-8 8H-12L-6 1.4Z" fill="{fin}"/>'
            f'<path d="M3 1.4L-8 8H-9.5L-4 1.4Z" fill="{accent}" opacity=".8"/>'
            '<rect x="-14" y="-1.8" width="1.6" height="3.6" fill="#3a4258"/>'
            '<circle cx="-14.4" cy="0" r="1.4" fill="#bff4ff"/></g>')


def _foot(x: float, w: float) -> float:
    """How far the island's domed top has dropped below the flat build line at design x, so
    things near the edge can reach down to the ground instead of standing on air. Matches
    `Shape.ground`: 14 px at the edge, in design units."""
    return 14 * (x / (DESIGN_W / 2)) ** 4 * DESIGN_W / w


def _frame(L: Layer, cx: float, top: float, w: float, body: Layer) -> None:
    L.group(body, transform=f"translate({cx:.1f} {top:.1f}) scale({w / DESIGN_W:.3f})")


# ---------------------------------------------------------------- the Starport

def starport(L: Layer, c: Ctx, cx: float, top: float, w: float, ships: int,
             haze: float = 0.0) -> None:
    """A landing pad on pylons, a ribbed hangar with a ship nosing out, fuel tanks and a
    control tower with a radar dish; parked ships, and one taking off now and then."""
    def tone(col: str) -> str:
        return c.haze(c.lit(col), haze)

    lamps = c.P["lamps"]
    g = Layer()
    steel, dark = tone("#8a90a8"), tone("#3a3f56")

    def foot(x: float) -> float:
        return _foot(x, w)

    # Control tower on a concrete footing, with a turning radar and a red beacon on its cab.
    base = foot(-62)
    g.rect(-62, -58, 8, 58 + base, tone("#c9cede"))
    g.rect(-55.5, -58, 1.5, 58 + base, "#000000", opacity=0.15)
    g.rect(-65, base - 2.5, 14, 3, tone("#8a8490"), rx=1)
    g.rect(-66, -66, 16, 9, tone("#5a6480"), rx=2)
    g.rect(-64, -63.5, 12, 3.5, "#7fe3ff" if lamps else tone("#bfe4f8"))
    g.line(-62, -66, -62, -75, dark, 1)
    g.circle(-62, -76, 1.4, "#ff5a4a", class_="av")
    g.line(-55, -66, -55, -71, dark, 1.2)
    radar = Layer()
    radar.rect(-61, -73.5, 12, 2.4, tone("#e6eaf2"), rx=1.2)
    radar.rect(-61, -73.5, 12, 1, "#ffffff", opacity=0.5, rx=0.5)
    g.group(radar, class_="radar")
    # Fuel tanks.
    for x in (-44, -35):
        g.rect(x, -16, 8, 16 + foot(x), tone("#e8e4dc"), rx=4)
        g.rect(x, -10, 8, 2, tone("#ff8a3a"))
    # Hangar: a ribbed half-cylinder with its door open.
    g.path("M-26 0V-14A22 18 0 0 1 18 -14V0Z", tone("#a8b0c4"))
    for k in range(1, 6):
        x = -26 + k * 7.3
        g.line(x, 0, x, -14 - 16 * math.sin(math.pi * k / 6), dark, 0.6, opacity=0.5)
    g.path("M-16 0V-12A12 10 0 0 1 8 -12V0Z", "#ffe6a8" if lamps else tone("#2a2f44"))
    if lamps:
        c.glow(g, -4, -6, 22, "#ffcf7a", 0.5)
    g.raw(f'<g transform="translate(2 -5)">{starfighter(c, 0.55, haze=haze)}</g>')
    # The landing pad, raised on pylons, with lights round its edge.
    g.rect(24, -12, 46, 3, steel)
    g.path(f"M30 -9L34 {foot(34):.1f}M64 -9L60 {foot(60):.1f}", stroke=dark, stroke_width=1.6)
    g.ellipse(47, -12.5, 14, 2, "none", stroke=tone("#f2c230"), stroke_width=0.8,
              stroke_dasharray="2 2")
    for k, x in enumerate(range(26, 70, 7)):
        g.circle(x, -12, 0.9, "#7fe3ff" if k % 2 else "#ffd27a", class_="fa" if k % 2 else "fb")
    # Parked ships, and one that lifts off the pad every so often.
    for k in range(min(ships, 3)):
        g.raw(f'<g transform="translate({-40 + k * 26} 4)">{starfighter(c, 0.5, k % 2 == 1, haze)}'
              "</g>")
    # Cargo crates, antennas on the hangar roof, a holo sign over the pad, a shuttle parked in
    # front and a pilot in an orange flight suit.
    for k, (x, y, col) in enumerate(((-30, -5, "#e8873a"), (-24, -5, "#8a90a8"),
                                     (-27, -10, "#e8b440"))):
        g.rect(x, y, 6, 5, tone(col))
        g.path(f"M{x} {y}l6 5M{x + 6} {y}l-6 5", stroke=dark, stroke_width=0.4, opacity=0.6)
    for x, h in ((-14, 12), (-9, 8)):
        roof = -14 - 18 * math.sqrt(1 - ((x + 4) / 22) ** 2)
        g.line(x, roof + 1, x, roof - h, dark, 0.8)
        g.line(x - 2, roof - h * 0.7, x + 2, roof - h * 0.7, dark, 0.6)
    g.circle(-14, -14 - 18 * math.sqrt(1 - (10 / 22) ** 2) - 12.6, 0.9, "#ff5a4a", class_="av")
    g.line(36, -12, 36, -32, dark, 0.8)
    g.rect(28, -42, 18, 10, "#7fe3ff", opacity=0.25 if lamps else 0.18, rx=1)
    g.rect(28, -42, 18, 10, "none", stroke="#7fe3ff", stroke_width=0.6, opacity=0.8)
    g.path("M31 -37l3 -2.5l3 2.5M37 -37l3 -2.5l3 2.5", stroke="#bff4ff", stroke_width=0.7,
           class_="pulse")
    shuttle, belly = tone("#e8e4dc"), tone("#9aa3b8")
    g.path("M30 4Q30 -5 40 -5H46Q52 -5 52 1V4Z", shuttle)
    g.path("M30 4Q30 1 36 1H52V4Z", belly)
    g.rect(42, -3.5, 6, 3, "#7fd8ff")
    g.rect(28, -2, 3, 5, dark)
    g.circle(28, 0.5, 1.2, "#7fe3ff", class_="flick")
    g.circle(20, -6, 1.6, tone("#f2c9a8"))
    g.rect(18.6, -4.4, 2.8, 4.4, tone("#ff8a3a"), rx=0.8)
    g.path("M18.4 -6.4a1.8 1.8 0 0 1 3.2 -0.6", stroke="#ffffff", stroke_width=0.7)
    lift = Layer()
    lift.raw(starfighter(c, 0.7, haze=haze))
    g.raw(f'<g transform="translate(47 -18)"><g class="launch">{lift.svg()}</g></g>')
    _frame(L, cx, top, w, g)


# ---------------------------------------------------------------- the Sky Shrine

PETALS = ("#ffb7d0", "#ffc9dc", "#f49ac0", "#ffe0ea")


def _sakura(g: Layer, c: Ctx, x: float, h: float, tone, haze: float, foot: float = 0) -> None:
    trunk = tone("#4a2e2a")
    g.path(f"M{x} {foot:.1f}V0q-2 {-h * 0.4:.0f} 2 {-h * 0.7:.0f}M{x + 1} {-h * 0.45:.0f}"
           f"q6 -4 10 -10M{x + 1} {-h * 0.55:.0f}q-6 -3 -9 -9", stroke=trunk, stroke_width=1.6,
           stroke_linecap="round")
    for _ in range(9):
        g.circle(x + c.rng.uniform(-12, 13), -h * c.rng.uniform(0.62, 0.95), c.rng.uniform(4, 7),
                 c.haze(c.lit(c.rng.choice(PETALS)), haze))
    for k in range(4):
        g.ellipse(x + c.rng.uniform(-8, 10), -h * c.rng.uniform(0.4, 0.7), 1.2, 0.7,
                  c.haze(c.lit("#ffc9dc"), haze), class_="petal",
                  style=f"animation-delay:-{k * 1.7:.1f}s")


def shrine(L: Layer, c: Ctx, cx: float, top: float, w: float, haze: float = 0.0) -> None:
    """A torii gate at the top of stone steps, a small shrine hall with sweeping eaves,
    stone lanterns that glow at night and cherry trees shedding petals."""
    def tone(col: str) -> str:
        return c.haze(c.lit(col), haze)

    lamps = c.P["lamps"]
    g = Layer()
    _sakura(g, c, -55, 46, tone, haze, _foot(-55, w))
    # Bamboo behind the hall.
    for k, x in enumerate((36, 40, 44, 47)):
        stalk = tone("#5aa05a" if k % 2 else "#4a8a4a")
        g.line(x, 0, x + 1, -50 - k * 4, stalk, 1.6)
        for y in range(-10, -46 - k * 4, -9):
            g.line(x - 0.6, y, x + 1.6, y, tone("#3a6a3a"), 0.6)
            g.path(f"M{x + 1} {y - 2}q5 -1 8 2q-5 0 -8 -2z", tone("#6ab86a"))
    # Shrine hall.
    wood, plaster, roof = tone("#8a3a2a"), tone("#f2ead8"), tone("#3a3a4e")
    g.rect(4, -24, 40, 24, plaster)
    for x in (4, 18, 30, 42):
        g.rect(x, -24, 2.4, 24, wood)
    g.rect(4, -24, 40, 2.4, wood)
    g.rect(19, -14, 10, 14, "#ffcf7a" if lamps else tone("#5a3a2a"))
    # A solid hipped roof with upturned eaves, tile ribs, a ridge cap and gold ridge ends.
    g.path("M-7 -28Q1 -23 8 -25L15 -37H33L40 -25Q47 -23 55 -28L49 -21.5H-1Z", roof)
    for x in (12, 18, 24, 30, 36):
        g.line(x, -36, x + (x - 24) * 0.45, -23, tone("#4e4e66"), 0.7)
    g.path("M-7 -28Q1 -23 8 -25L15 -37", stroke=c.P["rim"], stroke_width=0.9, opacity=0.7)
    g.path("M-1 -21.5H49", stroke=tone("#24242f"), stroke_width=1.2)
    g.rect(13, -39.5, 22, 2.8, tone("#2a2a3a"), rx=1)
    for x in (12, 34):
        g.path(f"M{x} -39l1 -3.4l1.6 3.4z", tone("#e8b440"))
    if lamps:
        c.glow(g, 24, -8, 20, "#ffcf7a", 0.6)
    # Steps and the torii gate in front.
    for k in range(3):
        g.rect(-30 + k * 2, -2 - k * 1.5, 22 - k * 4, 2, tone("#b8b0a4"))
    red, black = tone("#e0452f"), tone("#1f1a22")
    g.rect(-30, -34, 3, 34, red)
    g.rect(-13, -34, 3, 34, red)
    g.rect(-33, -28, 26, 2.6, red)
    g.path("M-38 -36Q-20 -33 -2 -36L-1 -39Q-20 -36 -39 -39Z", black)
    g.rect(-36, -36, 32, 2.4, red)
    g.rect(-22, -34, 4, 6, black)
    for x in (-31, -14):
        g.rect(x - 0.5, -3, 4, 3, black)
    # Stone lanterns.
    for x in (-42, 50):
        stone = tone("#a8a4b0")
        g.rect(x - 1.5, -10, 3, 10 + _foot(x, w), stone)
        g.rect(x - 3.5, _foot(x, w) - 2, 7, 2, tone("#8a8490"))
        g.rect(x - 4, -16, 8, 6, stone)
        g.path(f"M{x - 6} -16l6 -4l6 4z", stone)
        g.rect(x - 2, -15, 4, 3.6, "#ffcf7a" if lamps else tone("#5a5560"))
        if lamps:
            c.glow(g, x, -13, 10, "#ffb35a", 0.8, class_="flick")
    # The sacred rope on the gate, with paper streamers.
    g.path("M-30 -26Q-20 -22 -10 -26", stroke=tone("#d9c08a"), stroke_width=1.6)
    for x in (-25, -20, -15):
        g.path(f"M{x} -24l1 2l-1.6 1.4l1.6 1.6", stroke="#ffffff", stroke_width=0.7, fill="none")
    # Two stone fox guardians with red bibs.
    for x, flip in ((-36, 1), (-5, -1)):
        fox = tone("#c9c4cc")
        g.rect(x - 3, -4, 6, 4, tone("#8a8490"))
        g.path(f"M{x - 2.4} -4q0 -6 {2.4 * flip:.1f} -8q2 3 0 8z", fox)
        g.path(f"M{x + 0.4 * flip:.1f} -12l{-1 * flip} -3l{2 * flip} 1.6z", fox)
        g.path(f"M{x - 2.4} -4q-3 -1 -2 -5", stroke=fox, stroke_width=1.4, fill="none")
        g.path(f"M{x - 1.6} -9.4h3l-1.5 2z", tone("#e0452f"))
    # A small koi pond in front of the hall.
    g.ellipse(24, 0.6, 14, 2.6, tone("#5aa0c8"))
    g.ellipse(24, 0.2, 12, 1.6, tone("#8ac8e8"), opacity=0.6)
    for k, x in enumerate((18, 26, 31)):
        g.ellipse(x, 0.6, 1.8, 0.7, tone("#ff8a3a" if k != 1 else "#ffffff"))
    g.ellipse(21, 0.4, 2.2, 0.8, tone("#5cbf6a"))
    # A bronze bell at the door, and a rack of wooden prayer plaques.
    g.line(24, -21.5, 24, -19, tone("#d9c08a"), 0.6)
    g.path("M22 -19q2 -3 4 0v2h-4z", tone("#c9973a"))
    for k in range(3):
        g.rect(-2 + k * 3.4, -11, 3, 2.4, tone("#d9b47a"))
    g.line(-3, -8.4, 8, -8.4, tone("#5a3a2a"), 0.8)
    g.line(-2, -8.4, -2, 0, tone("#5a3a2a"), 0.6)
    g.line(7.4, -8.4, 7.4, 0, tone("#5a3a2a"), 0.6)
    _sakura(g, c, 58, 40, tone, haze, _foot(58, w))
    _frame(L, cx, top, w, g)


# ---------------------------------------------------------------- the sky dragon

def _timing(window: tuple[float, float]) -> str:
    """Move along the path once per loop, between the two fractions of it in `window`."""
    from .camera import LOOP_S  # imported here: the camera module imports the ride, which needs us

    a, b = window
    return (f'dur="{LOOP_S}s" repeatCount="indefinite" calcMode="linear" '
            f'keyPoints="0;0;1;1" keyTimes="0;{a};{b};1"')


def dragon_window() -> tuple[float, float]:
    """When in the loop the dragon crosses: centred on the train's stop at the wild side,
    so it flies over while the train stands still."""
    # Imported here: the camera module imports the ride, which needs this module.
    from .camera import schedule

    wild = next(s for s in schedule() if s.key == "wild")
    mid = (wild.arrive + wild.depart) / 200
    return mid - DRAGON_CROSSING / 2, mid + DRAGON_CROSSING / 2


def dragon_flight(L: Layer, c: Ctx, shiny: bool = False) -> None:
    """The sky dragon: a long emerald serpent with gold bands, fins and whiskers, weaving
    across the sky. Its body is a chain of segments that follow the head along one path.
    The rare golden one flies whatever the streak."""
    if c.w.stats.streak_days < DRAGON_STREAK and not shiny:
        return
    path = ("M-200 170C-60 90 60 240 200 150S420 70 560 160S800 250 960 140"
            "S1140 90 1260 150")
    body, belly, gold, fin = "#2fae6e", "#c8ecb0", "#f2c46d", "#1f7a4e"
    if c.dark:
        body, belly, fin = "#279a62", "#a8d8a0", "#1a6a44"
    if shiny:
        body, belly, gold, fin = "#f2c046", "#fff3c4", "#ffffff", "#c8902a"
    n, lag = 24, 0.11
    parts = []
    for k in range(n, 0, -1):
        r = 7.2 * (1 - 0.62 * k / n)
        # Long ovals, lined up with the direction of flight, overlap into one smooth body.
        seg = f'<ellipse rx="10" ry="{r:.1f}" fill="{body}"/>'
        seg += f'<ellipse cy="{r * 0.5:.1f}" rx="9.5" ry="{r * 0.42:.1f}" fill="{belly}"/>'
        if k % 3 == 0:
            seg += (f'<path d="M0 {-r:.1f}V{r * 0.2:.1f}" stroke="{gold}" stroke-width="1.4" '
                    'opacity=".9"/>')
        if k % 2 == 0:
            seg += (f'<path d="M-3 {-r + 0.5:.1f}L1 {-r - 5:.1f}L3 {-r + 0.5:.1f}Z" '
                    f'fill="{fin}"/>')
        if k == n:
            seg += (f'<path d="M-2 0L-14 -7L-10 0L-14 7Z" fill="{fin}"/>'
                    f'<path d="M-6 0L-14 -7" stroke="{gold}" stroke-width=".8"/>')
        parts.append((k, seg))
    head = (f'<path d="M-6 -6Q8 -8 16 -3L20 0Q12 5 -4 6Z" fill="{body}"/>'
            f'<path d="M2 3Q12 4 20 0Q14 7 0 6Z" fill="{belly}"/>'
            f'<path d="M0 -6Q-6 -15 -15 -15" stroke="{gold}" stroke-width="2" fill="none" '
            'stroke-linecap="round"/>'
            f'<path d="M5 -6Q0 -13 -7 -15" stroke="{gold}" stroke-width="1.4" fill="none" '
            'stroke-linecap="round"/>'
            f'<path d="M-6 -4L-12 -10L-9 -2L-14 -4L-7 2Z" fill="{fin}"/>'
            f'<path d="M18 1Q8 10 -10 12M17 -1Q6 -10 -8 -9" stroke="{gold}" stroke-width=".8" '
            'fill="none"/>'
            '<circle cx="9" cy="-2.6" r="1.8" fill="#fff3a0"/>'
            '<circle cx="9.4" cy="-2.6" r=".8" fill="#1a1622"/>')
    if c.dark or shiny:
        head = '<circle cx="9" cy="-2.6" r="8" fill="#fff3a0" opacity=".25"/>' + head
    # Each segment trails the head by `lag` seconds. Begin times are negative so every
    # segment is already on its (off-screen) path when the image loads.
    timing = _timing(dragon_window())
    out = []
    for k, seg in [*parts, (0, head)]:
        out.append(f'<g>{seg}<animateMotion {timing} begin="{(k - n) * lag:.2f}s" '
                   f'rotate="auto" path="{path}"/></g>')
    L.raw("".join(out))


def squadron(L: Layer, c: Ctx) -> None:
    """Three starfighters crossing the sky in formation, engines glowing."""
    path = "M-120 120C200 90 500 70 1150 40"
    timing = _timing(SQUADRON_WINDOW)
    for k, (dx, dy, lag) in enumerate(((0, 0, 0.0), (-34, 14, 0.25), (-34, -16, 0.4))):
        ship = starfighter(c, 1.3 - k * 0.15)
        L.raw(f'<g><g transform="translate({dx} {dy})">{ship}</g>'
              f'<animateMotion {timing} begin="{lag - 1:.2f}s" path="{path}"/></g>')


def ship_count(merged_prs: int) -> int:
    """Ships parked at the Starport: one per 3 merged pull requests, up to three."""
    return max(1, min(3, merged_prs // 3))

