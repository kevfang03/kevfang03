"""The sky railway: from a station on the Philly island, across a steel bridge, along a
slim ledge on the home island's cliff, and over a second bridge to the end of the line
on the stadium island. The camera follows the train along it (see camera.py)."""

from __future__ import annotations

from dataclasses import dataclass

from .context import Ctx
from .island import HOME, PHILLY, STADIUM
from .progress import Cargo, cargo, consist, level_info
from .svg import Layer

DROP = 46  # how far below the home island's ridge the track runs
CAR_W, GAP = 30, 2  # each car, and the gap between cars


@dataclass(frozen=True)
class Track:
    left: float  # buffer stop behind the station on the Philly island
    right: float  # buffer stop at the end of the line on the stadium island
    y: float
    viaduct: tuple[float, float]  # the stone section on the home island

    def start(self, length: float) -> float:
        """Where the nose of a train this long waits at the station."""
        return self.left + length + 8


def track() -> Track:
    return Track(left=PHILLY.x1 - 50, right=STADIUM.x0 + 26, y=HOME.top + DROP,
                 viaduct=(HOME.x0 + 14, HOME.x1 - 6))


def _buffer(L: Layer, c: Ctx, x: float, y: float, side: int) -> None:
    """A buffer stop where the line ends: a striped block with a red lamp."""
    bx = x - 3 if side > 0 else x - 1
    L.rect(bx, y - 7, 4, 7, c.lit("#3a3050"))
    L.rect(bx - 1, y - 6, 6, 3, c.lit("#e8e0f0"))
    L.rect(bx - 1, y - 6, 2, 3, c.lit("#c9473f"))
    L.circle(x, y - 9, 1.4, "#ff6a5a" if c.P["lamps"] else c.lit("#a84a40"))
    if c.P["lamps"]:
        c.glow(L, x, y - 9, 8, "#ff6a5a", 0.7, class_="blink")


def train_length(cars: tuple[str, ...]) -> float:
    return len(cars) * CAR_W + (len(cars) - 1) * GAP


def cars_for(c: Ctx) -> tuple[str, ...]:
    return consist(level_info(c.w.stats.contributions_total).level)


def _load(g: Layer, c: Ctx, kind: str, x: float, y: float) -> None:
    """One load on the cargo wagon, sitting on y."""
    if kind == "wheat":
        g.rect(x, y - 3.4, 5.6, 3.4, c.lit("#d9b46a"), rx=1.4)
        g.line(x + 2.8, y - 3.4, x + 2.8, y - 4.4, c.lit("#8a6a3a"), 0.7)
    elif kind == "wood":
        g.rect(x, y - 3, 5.6, 3, c.lit("#8a5a3a"), rx=1)
        g.circle(x + 5, y - 1.5, 1.4, c.lit("#d9a874"))
    elif kind == "stone":
        g.rect(x + 0.3, y - 3, 5, 3, c.lit("#a8a8b8"))
        g.line(x + 0.3, y - 3, x + 5.3, y - 3, "#ffffff", 0.6, opacity=0.6)
    else:
        g.poly([(x + 0.8, y), (x + 2.8, y - 4.2), (x + 4.8, y)], "#7fe3ff")
        g.poly([(x + 2.8, y - 4.2), (x + 4.8, y), (x + 2.8, y)], "#ffffff", opacity=0.35)


def _passengers(g: Layer, c: Ctx, x0: float, x1: float, top: float, seed: int) -> None:
    """Heads and shoulders in some of the windows, dark against daylight and warm at night."""
    sil = "#5a3a20" if c.P["lamps"] else "#16304f"
    x, k = x0, seed
    while x < x1 - 3:
        if k % 3 != 1:
            g.circle(x + 2.2, top + 4.4, 0.95, sil, opacity=0.6)
            g.rect(x + 1, top + 5.3, 2.4, 1.5, sil, rx=0.7, opacity=0.6)
        x += 4.4
        k += 1


def _hover_pods(g: Layer, c: Ctx, x0: float, x1: float, y: float, glow: str) -> None:
    """Two maglev pods under a car, glowing cyan underneath, with a soft halo on the rail."""
    g.ellipse((x0 + x1) / 2, y + 0.6, (x1 - x0) / 2, 2, glow)
    for px in (x0 + 7, x1 - 7):
        g.rect(px - 4.5, y - 3.4, 9, 2.6, "#0a1424", rx=1.3)
        g.rect(px - 3.6, y - 1.2, 7.2, 0.9, "#7fe3ff", rx=0.45, opacity=0.95)


def _body(c: Ctx, cars: tuple[str, ...], load: Cargo) -> Layer:
    """The Skyliner, nose at x=0: a streamlined navy maglev with brass trim, riding on glowing
    hover pods instead of wheels. Coaches join as you level up, with passengers in the
    windows; the cargo wagon carries this week's resources; the glass-domed observation car
    brings up the rear. After dark a soft headlight beam fades out ahead of it, and on the
    move it leaves a misty wake of cloud."""
    g = Layer()
    y = 0.0  # drawn on its rail at y=0 and placed by _train
    lamps = c.P["lamps"]
    length = train_length(cars)
    body = c.defs.linear("liner", [(0, c.lit("#3d74ad")), (0.45, c.lit("#1f4673")),
                                   (1, c.lit("#112844"))])
    roof, gold, skirt = c.lit("#e6edf6"), c.lit("#f4c76a"), c.lit("#0c1a30")
    brass = c.lit("#d9a441")
    glass = "#ffd98a" if lamps else c.lit("#b4dcf8")
    pod_glow = c.defs.radial("podglow", [(0, "#7fe3ff", 0.55), (1, "#7fe3ff", 0)])
    top, bot = y - 15, y - 3.4
    if lamps:
        g.ellipse(-length / 2, y + 2, length / 2 + 6, 3, "#ffcf7a", opacity=0.22)
    for k, kind in enumerate(cars):
        x0 = -(k + 1) * CAR_W - k * GAP
        x1 = x0 + CAR_W
        last = k == len(cars) - 1
        _hover_pods(g, c, x0, x1, y, pod_glow)
        if k:
            g.rect(x1, top + 3, GAP, bot - top - 5, skirt)
        win_x0, win_x1 = x0 + 3, x1 - 3
        if kind == "cargo":  # an open wagon with this week's loads stacked in it
            wy = top + 5
            g.rect(x0, wy, CAR_W, bot - wy, body, rx=2)
            sx = x0 + 2.2
            for name in ("wheat", "wood", "stone", "crystals"):
                for j in range(getattr(load, name)):
                    _load(g, c, name, sx, wy - j * 3.4)
                sx += 6.6
            if load.crystals and c.dark:
                c.glow(g, x0 + 23, wy - 3, 8, "#7fe3ff", 0.7, class_="pulse")
            g.line(x0, wy, x1, wy, brass, 1.2)
            g.line(x0 + 1, wy + 3.5, x1 - 1, wy + 3.5, gold, 0.9)
            if last:
                g.circle(x0 + 1.4, y - 7, 1, "#ff6a5a")
        else:
            if kind == "engine":  # a long swept nose with a brass-trimmed windscreen
                g.path(f"M{x0} {bot}V{top + 3}Q{x0} {top} {x0 + 3} {top}H{x1 - 9}"
                       f"Q{x1 - 1} {top + 0.5} {x1 + 7} {y - 9}Q{x1 + 13} {y - 6.5} {x1 + 13} "
                       f"{bot - 1}Q{x1 + 13} {bot} {x1 + 11} {bot}Z", body)
                g.path(f"M{x1 - 9} {top + 1.6}Q{x1 - 2} {top + 2} {x1 + 4} {y - 9.5}H{x1 - 9}Z",
                       "#0b1626")
                g.path(f"M{x1 - 9.5} {top + 1.2}Q{x1 - 2} {top + 1.6} {x1 + 4.6} {y - 9.4}",
                       stroke=brass, stroke_width=0.8)
                g.path(f"M{x1 - 7} {top + 2.4}Q{x1 - 2} {top + 3} {x1 + 1} {y - 10.5}",
                       stroke="#ffffff", stroke_width=0.7, opacity=0.5)
                # A swept brass fin on the roof and winged chevrons on the nose.
                g.path(f"M{x0 + 9} {top}l5 -4.5h3.4l-1.4 4.5z", brass)
                g.path(f"M{x1 + 3} {y - 6.4}l3.2 -1.8l3.2 1.8M{x1 + 4.4} {y - 4.8}l1.8 -1l1.8 1",
                       stroke=gold, stroke_width=0.9)
                g.circle(x1 + 11.2, y - 5.2, 1.5, "#fff6d0")
                if lamps:
                    beam = c.defs.linear("beam", [(0, "#fff3c4", 0.42), (0.35, "#fff3c4", 0.16),
                                                  (1, "#fff3c4", 0)], x2=1, y2=0)
                    g.path(f"M{x1 + 12} {y - 6.4}L{x1 + 150} {y - 19}V{y + 7}L{x1 + 12} {y - 4}Z",
                           beam, class_="flick", style="animation-duration:3.4s")
                    c.glow(g, x1 + 11.2, y - 5.2, 10, "#fff3c4", 0.95)
                win_x1 = x1 - 11
            elif kind == "dome":  # a rounded tail and a glass dome
                g.path(f"M{x1} {bot}V{top}H{x0 + 6}Q{x0 - 3} {top + 0.5} {x0 - 3} {y - 8}"
                       f"Q{x0 - 3} {bot} {x0 + 3} {bot}Z", body)
                g.path(f"M{x0 + 7} {top}A10 6 0 0 1 {x0 + 25} {top}Z", glass,
                       opacity=0.85 if lamps else 0.7)
                for dx in (11, 16, 21):
                    g.line(x0 + dx, top, x0 + dx, top - 4.6, brass, 0.5)
                g.path(f"M{x0 + 7} {top}A10 6 0 0 1 {x0 + 25} {top}", stroke=brass,
                       stroke_width=0.8)
                if lamps:
                    c.glow(g, x0 + 16, top - 2, 10, "#ffcf7a", 0.6)
                g.circle(x0 - 1.6, y - 7, 1, "#ff6a5a")
                win_x0 = x0 + 1
            else:
                g.rect(x0, top, CAR_W, bot - top, body, rx=3)
            rx0, rx1 = max(x0, win_x0 - 2), min(x1, win_x1 + 2)
            g.rect(rx0, top - 1.1, rx1 - rx0, 2.2, roof, rx=1.1)
            g.rect(win_x0, top + 3, win_x1 - win_x0, 3.8, glass, rx=1)
            if kind != "engine":
                _passengers(g, c, win_x0, win_x1, top, k)
            x = win_x0 + 4.4
            while x < win_x1 - 1:
                g.line(x, top + 3, x, top + 6.8, "#16304f", 0.6)
                x += 4.4
            if lamps:
                g.rect(win_x0, top + 3, win_x1 - win_x0, 3.8, "#ffcf7a", opacity=0.35,
                       filter=c.defs.blur(1.5))
            g.line(x0 + 1, top + 8.5, (x1 + 9 if kind == "engine" else x1 - 1), top + 8.5, gold,
                   0.9)
            g.line(x0 + 1, top + 9.9, x1 - 1, top + 9.9, brass, 0.4, opacity=0.8)
            g.line(x0 + 2, top + 0.9, x1 - 2, top + 0.9, c.P["rim"], 0.6, opacity=0.6)
        g.rect(x0 + 1.5, bot - 1.6, CAR_W - 3, 2.2, skirt, rx=1)
    return g


def _train(c: Ctx, y: float, cars: tuple[str, ...], load: Cargo, moving: bool = False) -> Layer:
    """The Skyliner on a rail at height y. It is drawn once and reused by the overview and
    the ride, which keeps the file small; on the move a light streak and a misty wake of
    cloud trail the last car."""
    ref = c.defs.shape("skyliner", _body(c, cars, load).svg())
    g = Layer()
    if moving:
        length, top = train_length(cars), y - 15
        wake = Layer()
        wake.rect(-length - 90, top + 3, 90, 7, c.defs.linear(
            "trail", [(0, "#ffffff", 0), (1, "#fff6dc", 0.3 if c.P["lamps"] else 0.22)],
            x2=1, y2=0), rx=3.5)
        for k in range(3):
            wake.circle(-length - 6 - k * 9, y - 3 - k, 3 + k, "#ffffff", opacity=0.35,
                        class_="wake", style=f"animation-delay:-{k * 0.45:.2f}s")
        g.group(wake, class_="trail")
    g.el("use", href=ref, y=y)
    return g


def signal(L: Layer, c: Ctx, x: float, y: float, green: bool) -> None:
    """A signal post beside the track: a dark head with a red and a green lamp, one lit."""
    post = c.lit("#3a3050")
    L.line(x, y, x, y - 20, post, 1)
    L.rect(x - 2.4, y - 28, 4.8, 9, post, rx=1.6)
    for k, col in enumerate(("#ff5a4a", "#5cf08a")):
        on = (k == 1) == green
        L.circle(x, y - 25.6 + k * 4.2, 1.3, col if on else "#2a2238")
        if on and c.P["lamps"]:
            c.glow(L, x, y - 25.6 + k * 4.2, 8, col, 0.8)


def _truss(L: Layer, c: Ctx, x1: float, x2: float, y: float) -> None:
    steel = c.lit("#8a8fa8")
    L.rect(x1, y, x2 - x1, 3, steel)
    L.line(x1, y - 14, x2, y - 14, steel, 1.6)
    n = max(2, int((x2 - x1) // 10))
    for k in range(n + 1):
        x = x1 + (x2 - x1) * k / n
        L.line(x, y, x, y - 14, steel, 0.8)
        if k < n:
            nx = x1 + (x2 - x1) * (k + 1) / n
            L.line(x, y, nx, y - 14, steel, 0.8)
    L.line(x1, y - 14, x2, y - 14, c.P["rim"], 0.6, opacity=0.6)


def _viaduct(L: Layer, c: Ctx, a: float, b: float, y: float) -> None:
    """The track along a cliff: a slim deck on iron brackets, with lanterns every so often."""
    iron = c.lit("#4a4258")
    L.rect(a, y + 3, b - a, 3, "#000000", opacity=0.22)
    x = a + 12
    while x < b - 6:
        L.path(f"M{x} {y + 3}L{x - 8} {y + 13}M{x} {y + 3}V{y + 12}", stroke=iron,
               stroke_width=1.1)
        L.circle(x - 8, y + 13, 1, c.lit("#6a6278"))
        x += 30
    L.rect(a, y, b - a, 3.2, c.lit("#5a4e62"))
    L.line(a, y + 0.6, b, y + 0.6, c.lit("#8a6a52"), 2.2, stroke_dasharray="1.4 2.6")
    L.line(a, y, b, y, c.P["rim"], 0.8, opacity=0.6)
    x = a + 40
    while x < b - 20:
        L.line(x, y, x, y - 16, iron, 0.9)
        L.rect(x - 1.6, y - 19, 3.2, 3.4, "#ffd27a" if c.P["lamps"] else c.lit("#9a8a6a"))
        if c.P["lamps"]:
            c.glow(L, x, y - 17, 10, "#ffb35a", 0.7, class_="flick")
        x += 96


def _station(L: Layer, c: Ctx, t: Track, length: float) -> None:
    """A platform with a canopy where the train waits on the Philly island."""
    x0, x1 = t.left + 6, t.start(length) + 4
    roof = c.lit("#5a4a6a")
    L.rect(x0, t.y + 1, x1 - x0, 5, c.lit("#b8aa94"))
    for x in (x0 + 8, (x0 + x1) / 2, x1 - 8):
        L.line(x, t.y + 1, x, t.y - 22, c.lit("#3a3050"), 1.4)
    L.poly([(x0 - 4, t.y - 22), (x1 + 4, t.y - 22), (x1, t.y - 28), (x0, t.y - 28)], roof)
    L.line(x0 - 4, t.y - 22, x1 + 4, t.y - 22, c.P["rim"], 0.8, opacity=0.8)
    if c.P["lamps"]:
        for x in (x0 + 20, x1 - 20):
            c.glow(L, x, t.y - 20, 14, "#ffd27a", 0.7)


def draw(L: Layer, c: Ctx) -> None:
    t = track()
    a, b = t.viaduct
    _truss(L, c, t.left, a, t.y)
    _viaduct(L, c, a, b, t.y)
    _truss(L, c, b, t.right + 4, t.y)
    cars = cars_for(c)
    _station(L, c, t, train_length(cars))
    L.line(t.left, t.y - 1, t.right, t.y - 1, "#2a2230", 1.2)
    clip = c.defs.clip("rail", f'<rect x="{t.left:.0f}" y="{t.y - 40:.0f}" '
                               f'width="{t.right - t.left:.0f}" height="60"/>')
    moving = Layer()
    moving.group(_train(c, t.y, cars, cargo(c.w.stats)),
                 transform=f"translate({t.start(train_length(cars)):.0f} 0)")
    L.group(moving, clip_path=clip)
    _buffer(L, c, t.left, t.y, -1)
    _buffer(L, c, t.right, t.y, 1)
