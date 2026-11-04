"""What happens while the train waits at each station on the ride.

Every moment runs on the camera's loop clock, so it plays exactly while the train stands
there:

- **Stadium:** fireworks over the stands, or, while it is still locked, a glint on its
  padlock.
- **Wildwood:** sky jellies drifting up past the forest and its Elder Tree.
- **Server Farm:** a drone drops a crate into the cargo wagon.

A sign over each platform shows the number that builds that place.
"""

from __future__ import annotations

from . import creatures
from .camera import LOOP_S, Stop, keyframes, schedule
from .context import Ctx, W, sign
from .progress import level_threshold
from .rail import CAR_W, GAP, cars_for, train_length
from .ride import RAIL_Y, SCALE, STADIUM, STADIUM_T, _nose_x
from .svg import Layer
from .world import UNLOCK, level

SIGN_Y = RAIL_Y - 56  # station signs hang over the middle of the train, like the town's
GOLD = "#ffd27a"


def _moment(name: str, s: Stop, frames: list[tuple[float, str]], lead: float = 0.0,
            tail: float = 0.0, extra: str = "") -> str:
    """CSS for something that plays while the train waits at s. Each frame is (u, css), u
    running from 0 (`lead` seconds before the train arrives) to 1 (`tail` seconds after it
    leaves). Outside that window the first frame holds before it and the last after."""
    a = s.arrive - lead / LOOP_S * 100
    b = s.depart + tail / LOOP_S * 100
    body = [(0, frames[0][1]), *[(a + (b - a) * u, v) for u, v in frames], (100, frames[-1][1])]
    return keyframes(name, body) + f".{name}{{animation:{name} {LOOP_S}s linear infinite{extra}}}"


def _centre(s: Stop) -> float:
    """The strip's x under the middle of the screen while the train waits at s."""
    return W / 2 + s.offset


# ---------------------------------------------------------------- the stadium

def _burst(c: Ctx, col: str) -> str:
    """One firework, centred on 0,0: rays and sparks around a bright core. The drawing is
    kept once and each burst takes its colour from the copy that places it. An unfilled ring
    keeps its box centred, so it grows from the middle."""
    rays = "".join(f"M{10 * dx:.1f} {10 * dy:.1f}L{32 * dx:.1f} {32 * dy:.1f}"
                   for dx, dy in _spokes(16))
    sparks = "".join(f"M{37 * dx:.1f} {37 * dy:.1f}h0" for dx, dy in _spokes(16, 0.5))
    ref = c.defs.shape("burst", f'<circle r="39" fill="none"/>'
                       f'<path d="{rays}" stroke="currentColor" stroke-width="2" '
                       f'stroke-linecap="round"/>'
                       f'<path d="{sparks}" stroke="currentColor" stroke-width="4" '
                       f'stroke-linecap="round"/><circle r="4.5" fill="#fff6dc"/>')
    return f'<use href="{ref}" color="{col}"/>'


def _spokes(n: int, turn: float = 0.0) -> list[tuple[float, float]]:
    import math

    return [(math.cos(2 * math.pi * (k + turn) / n), math.sin(2 * math.pi * (k + turn) / n))
            for k in range(n)]


def _stadium(L: Layer, c: Ctx, s: Stop, css: list[str]) -> None:
    x = _centre(s)
    total = c.w.stats.contributions_total
    if level(c) >= UNLOCK["stadium"]:
        cols = ("#ffd27a", "#ff6ab4", "#7fe3ff", "#9dff8a", "#ffffff")
        # Around and above the stadium's name sign, which sits over the middle at y 130.
        for k, (dx, y) in enumerate(((-170, 95), (150, 70), (-50, 50), (220, 150), (60, 105))):
            name = f"fw{k}"
            u = 0.04 + k * 0.15
            hidden = "transform:scale(.15);opacity:0"
            css.append(_moment(name, s, [(0, hidden), (u, hidden),
                                         (u + 0.02, "transform:scale(.35);opacity:1"),
                                         (u + 0.24, "transform:scale(1.2);opacity:0"),
                                         (1, "transform:scale(1.2);opacity:0")], tail=1.0,
                               extra=";transform-box:fill-box;transform-origin:center"))
            if c.P["lamps"]:
                c.glow(L, x + dx, y, 50, cols[k], 0.0, class_=name)
            L.raw(f'<g transform="translate({x + dx:.0f} {y})"><g class="{name}">'
                  f"{_burst(c, cols[k])}</g></g>")
        text = f"STADIUM STATION · {total:,} CONTRIBUTIONS"
    else:
        # The padlock sits just above the locked stadium's ridge.
        px = STADIUM_T[0] + STADIUM.cx * SCALE
        py = STADIUM_T[1] + (STADIUM.top - 10) * SCALE
        star = "M0 -9L1.6 -1.6L9 0L1.6 1.6L0 9L-1.6 1.6L-9 0L-1.6 -1.6Z"
        hidden = "transform:scale(0) rotate(0deg);opacity:0"
        css.append(_moment("glint", s, [(0, hidden), (0.15, hidden),
                                        (0.3, "transform:scale(1) rotate(45deg);opacity:1"),
                                        (0.45, hidden), (0.6, hidden),
                                        (0.75, "transform:scale(1.2) rotate(90deg);opacity:1"),
                                        (0.9, hidden), (1, hidden)],
                           extra=";transform-box:fill-box;transform-origin:center"))
        L.raw(f'<g transform="translate({px + 9:.0f} {py - 10:.0f})"><g class="glint">'
              f'<path d="{star}" fill="#fff6dc"/></g></g>')
        need = level_threshold(UNLOCK["stadium"]) - total
        text = f"STADIUM STATION · {need:,} CONTRIBUTIONS TO GO"
    sign(L, x, SIGN_Y, text, GOLD)


# ---------------------------------------------------------------- the Wildwood

def _wild(L: Layer, c: Ctx, s: Stop, css: list[str]) -> None:
    x = _centre(s)
    for k, (dx, y, size) in enumerate(((-300, 250, 1.1), (-180, 228, 0.8), (-60, 262, 1.3),
                                       (140, 236, 0.9), (290, 255, 1.2))):
        name = f"jr{k}"
        css.append(_moment(name, s, [(0, "transform:translateY(0px);opacity:0"),
                                     (0.12 + k * 0.03, "opacity:1"), (0.8, "opacity:1"),
                                     (1, "transform:translateY(-90px);opacity:0")],
                           lead=1.5, tail=1.5))
        L.raw(f'<g transform="translate({x + dx:.0f} {y})"><g class="{name}">'
              f"{creatures.jelly(c, size).svg()}</g></g>")
    n = c.w.stats.streak_days
    sign(L, x, SIGN_Y, f"WILDWOOD · STREAK {n} DAY{'' if n == 1 else 'S'}", GOLD)


# ---------------------------------------------------------------- passing the wonders

def _passing(L: Layer, c: Ctx, css: list[str]) -> None:
    """The Starport and the Shrine float between stops, so their moments play as the train
    passes under them: a starfighter lifts off on the way from the stadium to the Wildwood,
    and a gust of petals blows off the Shrine on the way on to the Server Farm."""
    from .ride import NEAR  # imported here: the ride module imports this one while drawing

    stops = {s.key: s for s in schedule()}

    def leg(a: str, b: str) -> Stop:
        d, r = stops[a].depart, stops[b].arrive
        return Stop("pass", 0, d + (r - d) * 0.25, d + (r - d) * 0.75)

    if level(c) >= UNLOCK["starport"]:
        s = leg("stadium", "wild")
        parked = "transform:translate(0px,0px);opacity:1"
        gone = "transform:translate(110px,-150px);opacity:0"
        css.append(keyframes("liftoff", [
            (0, parked), (s.arrive, parked + ";animation-timing-function:ease-in"),
            (s.depart, gone), (99.9, gone), (100, parked)]))
        css.append(f".ride .launch{{animation:liftoff {LOOP_S}s linear infinite}}")
    if level(c) >= UNLOCK["shrine"]:
        s = leg("wild", "farm")
        _, _, cx, top, w = NEAR[1]
        cols = ("#ffb7d0", "#ffc9dc", "#f49ac0", "#ffe0ea")
        for k in range(9):
            name = f"gust{k}"
            u = 0.05 + k * 0.06
            still = "transform:translate(0px,0px) rotate(0deg)"
            blown = "transform:translate(-150px,60px) rotate(260deg);opacity:0"
            css.append(_moment(name, s, [(0, still + ";opacity:0"), (u, still + ";opacity:1"),
                                         (u + 0.5, blown), (1, "opacity:0")],
                               extra=";transform-box:fill-box;transform-origin:center"))
            px = cx + (-50 if k % 2 else 52) * w / 150 + (k % 3) * 4
            py = top - 30 + (k * 7) % 16
            L.ellipse(px, py, 2.2, 1.3, cols[k % 4], class_=name)


# ---------------------------------------------------------------- the Server Farm

def _farm(L: Layer, c: Ctx, s: Stop) -> None:
    year = c.w.stats.contributions_year
    sign(L, _centre(s), SIGN_Y, f"SERVER FARM · {year:,} CONTRIBUTIONS THIS YEAR", GOLD)


def delivery(c: Ctx) -> tuple[Layer, Layer, str]:
    """A drone flies a crate down to the cargo wagon while the train waits at the Server
    Farm and lets it drop in. Drawn in screen space with the train; returns the crate
    (behind the train, so it falls into the wagon), the drone (in front) and their CSS."""
    s = next(st for st in schedule() if st.key == "farm")
    cars = cars_for(c)
    ci = cars.index("cargo")
    nose = _nose_x(train_length(cars))
    x = nose + (-(ci + 1) * CAR_W - ci * GAP + CAR_W / 2) * SCALE
    y = RAIL_Y - 10 * SCALE - 52  # hovering above the wagon's rim

    away, over = "translate(170px,-200px)", "translate(0px,0px)"
    gone = "translate(-160px,-210px)"
    drone_css = _moment("dlv", s, [
        (0, f"transform:{away};opacity:0"), (0.06, f"transform:{away};opacity:1"),
        (0.42, f"transform:{over}"), (0.58, f"transform:{over}"),
        (0.94, f"transform:{gone};opacity:1"), (1, f"transform:{gone};opacity:0")],
        lead=1.0, tail=1.5)
    crate_css = _moment("crate", s, [
        (0, f"transform:{away};opacity:0"), (0.06, f"transform:{away};opacity:1"),
        (0.42, f"transform:{over}"),
        (0.5, f"transform:{over};animation-timing-function:ease-in"),
        (0.57, "transform:translate(0px,34px);opacity:1"),
        (0.58, "transform:translate(0px,34px);opacity:0"), (1, "opacity:0")],
        lead=1.0, tail=1.5)

    # Both are drawn around 0,0 at the train's scale, then placed over the wagon.
    place = f"translate({x:.1f} {y:.1f}) scale({SCALE})"
    crate = Layer()
    crate.rect(-5, 9, 10, 8, c.lit("#b07a4a"), rx=1)
    crate.path("M-5 9l10 8M5 9l-10 8", stroke=c.lit("#7a5236"), stroke_width=0.8)
    crate.line(0, 4, 0, 9, c.lit("#5a6480"), 0.6)
    behind = Layer()
    behind.raw(f'<g class="crate"><g transform="{place}">{crate.svg()}</g></g>')

    # A pale drone with an orange stripe, so it reads against the dusk and the night.
    d = Layer()
    if c.dark:
        c.glow(d, 0, 0, 16, "#bff4ff", 0.35)
    for dx in (-10, 10):
        d.line(dx * 0.5, -1, dx, -5, c.lit("#3a4058"), 1.2)
        d.rect(dx - 0.8, -6, 1.6, 2, c.lit("#3a4058"))
        d.ellipse(dx, -6.4, 6, 1.2, c.lit("#eef2f8"), opacity=0.9)
    d.rect(-7, -2.5, 14, 6, c.lit("#dfe3ec"), rx=2.5)
    d.rect(-7, 0, 14, 1.2, c.lit("#ff8a3a"))
    d.circle(4.5, -0.6, 1, "#7fe3ff", class_="av")
    front = Layer()
    front.raw(f'<g class="dlv"><g transform="{place}">{d.svg()}</g></g>')
    return behind, front, drone_css + crate_css


# ---------------------------------------------------------------- all of them

def draw(L: Layer, c: Ctx) -> str:
    """Draw every station's moment and sign into the ride's world strip; returns their CSS."""
    css: list[str] = []
    for s in schedule():
        if s.key == "stadium":
            _stadium(L, c, s, css)
        elif s.key == "wild":
            _wild(L, c, s, css)
        else:
            _farm(L, c, s)
    _passing(L, c, css)
    return "".join(css)
