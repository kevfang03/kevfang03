"""Holidays through the year, each with its own decorations and a line in the header.

| Holiday | When | What appears |
|---|---|---|
| New Year's Day | Jan 1 | fireworks all day |
| Lunar New Year | its first week (dates listed to 2030) | a golden dragon, red lanterns, firecrackers after dark |
| Valentine's week | Feb 10 to 14 | hearts floating up from the town |
| Pi Day | Mar 14 | a hot-air balloon marked with pi |
| St. Patrick's Day | Mar 15 to 17 | a rainbow over the islands (by daylight) |
| Easter | Friday to Monday | painted eggs hidden in the grass, and in the Server Farm's wheat |
| Fourth of July | Jul 1 to 5 | bunting along the street and platforms, fireworks on the night of the 4th |
| Halloween | Oct 24 to 31 | jack-o'-lanterns, a pumpkin patch, bats, a ghost at the ruin, purple nights |
| Thanksgiving | Thursday to Sunday | a parade balloon over Philly on the day, pumpkins on the farm |
| Hanukkah | its eight nights (dates listed to 2030) | a menorah with that night's candles lit |
| Holiday lights | Dec 1 to Jan 1 | string lights on the street and platforms, lit trees |
| Christmas week | Dec 20 to 26 | the dragon in a Santa hat, a reindeer sleigh in place of the starfighters, presents |
| New Year's Eve | Dec 31 | fireworks after dark |

Every design here is original. Dates that follow the moon come from short tables; past
their last year those holidays simply skip.
"""

from __future__ import annotations

import itertools
from dataclasses import dataclass
from datetime import date, timedelta

from .clock import season
from .context import Ctx, H, W
from .island import Shape
from .svg import Layer, attrs

LUNAR_NEW_YEAR = {2026: date(2026, 2, 17), 2027: date(2027, 2, 6), 2028: date(2028, 1, 26),
                  2029: date(2029, 2, 13), 2030: date(2030, 2, 3)}
HANUKKAH = {2026: date(2026, 12, 4), 2027: date(2027, 12, 24), 2028: date(2028, 12, 12),
            2029: date(2029, 12, 1), 2030: date(2030, 12, 20)}  # the first candle's evening
FIREWORKS = {"newyear": ("#ffd27a", "#ffffff", "#ff6ab4"),
             "lunar": ("#ff4a3a", "#ffd27a", "#ff8a3a"),
             "july4": ("#ff4a55", "#ffffff", "#3a7bff"),
             "nye": ("#ffd27a", "#ffffff", "#ff6ab4")}
ALL_DAY = {"newyear"}  # fireworks by daylight too; the others wait for dusk

CSS = (
    "@keyframes float{0%{transform:translateY(0);opacity:0}15%{opacity:1}"
    "85%{opacity:1}100%{transform:translateY(-120px);opacity:0}}"
    ".float{animation:float 9s ease-in infinite}"
    "@keyframes bats{from{transform:translate(-120px,30px)}to{transform:translate(1100px,-20px)}}"
    ".bats{animation:bats 22s linear infinite}"
    "@keyframes sleigh{0%,55%{transform:translate(-200px,40px)}"
    "100%{transform:translate(1180px,-30px)}}.sleigh{animation:sleigh 24s linear infinite}"
    "@keyframes sway2{from{transform:rotate(-6deg)}to{transform:rotate(6deg)}}"
    ".swing{animation:sway2 2.6s ease-in-out infinite alternate;transform-box:fill-box;"
    "transform-origin:50% 0}"
)


@dataclass(frozen=True)
class Holiday:
    key: str
    headline: str
    night: int = 0  # Hanukkah's night


def easter(year: int) -> date:
    """Easter Sunday in the Gregorian calendar (the anonymous Gregorian algorithm)."""
    a, b, c = year % 19, year // 100, year % 100
    d, e = b // 4, b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = c // 4, c % 4
    m_ = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * m_) // 451
    month = (h + m_ - 7 * m + 114) // 31
    return date(year, month, (h + m_ - 7 * m + 114) % 31 + 1)


def thanksgiving(year: int) -> date:
    first = date(year, 11, 1)
    return first + timedelta(days=(3 - first.weekday()) % 7 + 21)


def on(day: date) -> list[Holiday]:
    """Every holiday on this date, the one the header should name first. Each one lasts as
    long as people celebrate it: a day for Pi Day, a weekend for Easter, a week for
    Halloween and Christmas, a month of lights in December."""
    md, y = (day.month, day.day), day.year
    out: list[Holiday] = []

    def add(key: str, line: str, night: int = 0) -> None:
        out.append(Holiday(key, line, night))

    if day.month == 12 and 20 <= day.day <= 26:
        add("christmas", {24: "CHRISTMAS EVE · SANTA'S SLEIGH IS OUT",
                          25: "MERRY CHRISTMAS"}.get(day.day, "CHRISTMAS WEEK"))
    lunar = LUNAR_NEW_YEAR.get(y)
    if lunar and 0 <= (day - lunar).days < 7:
        add("lunar", "LUNAR NEW YEAR · THE GOLDEN DRAGON FLIES" if day == lunar
            else "LUNAR NEW YEAR WEEK · THE GOLDEN DRAGON FLIES")
    start = HANUKKAH.get(y) or HANUKKAH.get(y - 1)
    if start and 0 <= (day - start).days < 8:
        n = (day - start).days + 1
        add("hanukkah", f"HANUKKAH · NIGHT {n}", n)
    if md == (12, 31):
        add("nye", "NEW YEAR'S EVE")
    elif md == (1, 1):
        add("newyear", "HAPPY NEW YEAR")
    if day.month == 2 and 10 <= day.day <= 14:
        add("valentine", "VALENTINE'S DAY" if day.day == 14 else "VALENTINE'S WEEK")
    if md == (3, 14):
        add("pi", "PI DAY · 3.14159…")
    if day.month == 3 and 15 <= day.day <= 17:
        add("stpatrick", "ST. PATRICK'S DAY · LOOK FOR THE RAINBOW" if day.day == 17
            else "ST. PATRICK'S WEEKEND · LOOK FOR THE RAINBOW")
    sunday = easter(y)
    if -2 <= (day - sunday).days <= 1:
        add("easter", "EASTER · AN EGG HUNT IN THE TOWN" if day == sunday
            else "EASTER WEEKEND · AN EGG HUNT IN THE TOWN")
    if day.month == 7 and day.day <= 5:
        add("july4", "FOURTH OF JULY" if day.day == 4 else "FOURTH OF JULY WEEK")
    if day.month == 10 and day.day >= 24:
        add("halloween", "HAPPY HALLOWEEN" if day.day == 31 else "SPOOKY SEASON · HALLOWEEN WEEK")
    turkey = thanksgiving(y)
    if 0 <= (day - turkey).days <= 3:
        add("thanksgiving", "HAPPY THANKSGIVING · A PARADE OVER PHILLY" if day == turkey
            else "THANKSGIVING WEEKEND")
    if (day.month == 12 and day.day != 31) or md == (1, 1):
        add("lights", "HOLIDAY LIGHTS IN THE TOWN")
    return out


def sleigh(c: Ctx) -> str:
    """Santa's sleigh behind four reindeer, the lead one with a glowing red nose. Faces
    right, the sleigh at 0,0."""
    g = Layer()
    deer = c.lit("#8a5a3a")
    for k in range(4):
        x = 46 + k * 22
        g.path(f"M{x} 0q1 -6 9 -5h4l3 -6l1 1l-2 5l3 -4l1 1l-3 5q3 1 2 4h-3l-2 -2h-3"
               f"l-3 4l2 6h-2l-3 -5l-3 5h-2l2 -6q-4 1 -4 -3z", deer)
    g.path("M14 2Q60 -6 112 -3", stroke="#c9a24a", stroke_width=0.7)
    g.path("M-20 -10H6Q12 -10 12 -2Q12 8 2 8H-22Q-28 8 -28 0Q-28 -6 -24 -6Z", "#c0352e")
    g.path("M-30 12H14Q20 12 22 8", stroke="#e8b440", stroke_width=1.6)
    g.path("M-20 -10H6", stroke="#e8b440", stroke_width=1.2)
    g.rect(-20, -20, 12, 10, "#2f8a4a", rx=2)
    g.rect(-9, -17, 8, 7, "#3a7bd0", rx=1.5)
    g.circle(-4, -18, 4, "#d8342a")
    g.circle(-4, -21, 3, "#f2c9a8")
    g.path("M-7 -22Q-4 -28 0 -23Z", "#d8342a")
    g.circle(0, -23, 1.2, "#ffffff")
    g.path("M-7 -19.5Q-4 -15 -1 -19.5", "#ffffff")
    nose_x = 46 + 3 * 22 + 21
    if c.dark:
        c.glow(g, nose_x, -1, 9, "#ff4a3a", 0.9)
    g.circle(nose_x, -1, 1.6, "#ff4a3a")
    return g.svg()


def fireworks(day: date, phase: str) -> tuple[str, ...]:
    """Fireworks colours if a holiday has fireworks at this time of day, else none."""
    after_dark = phase in ("dusk", "night")
    for h in on(day):
        if h.key == "july4" and day.day != 4:
            continue
        if h.key in FIREWORKS and (after_dark or h.key in ALL_DAY):
            return FIREWORKS[h.key]
    return ()


def keys(c: Ctx) -> set[str]:
    return {h.key for h in on(c.w.when.date())}


# ---------------------------------------------------------------- in the sky

def _heart(x: float, y: float, r: float, col: str) -> str:
    return (f'<path d="M{x} {y + r}C{x - 2 * r} {y - 0.2 * r} {x - r} {y - 1.6 * r} {x} '
            f'{y - 0.6 * r}C{x + r} {y - 1.6 * r} {x + 2 * r} {y - 0.2 * r} {x} {y + r}Z" '
            f'fill="{col}"/>')


def _balloon(c: Ctx, x: float, y: float, envelope: str, mark: str) -> Layer:
    g = Layer()
    g.ellipse(x, y, 16, 19, c.lit(envelope))
    g.ellipse(x - 5, y - 6, 4, 7, "#ffffff", opacity=0.25)
    g.text(x, y + 5, mark, 15, "#ffffff", text_anchor="middle", font_weight="800")
    g.line(x - 8, y + 15, x - 4, y + 26, c.lit("#5a4a3a"), 0.7)
    g.line(x + 8, y + 15, x + 4, y + 26, c.lit("#5a4a3a"), 0.7)
    g.rect(x - 5, y + 26, 10, 6, c.lit("#8a5d42"), rx=1)
    return g


def _turkey(c: Ctx, x: float, y: float) -> Layer:
    """A round parade balloon of a cheerful turkey, held down by lines to the skyline."""
    g = Layer()
    for k, col in enumerate(("#e2574c", "#e8b440", "#e8873a", "#c0552e", "#e8b440")):
        g.ellipse(x - 24 + k * 12, y - 16 - (2 - abs(k - 2)) * 4, 7, 16, c.lit(col),
                  transform=f"rotate({(k - 2) * 22} {x - 24 + k * 12} {y - 4})")
    g.ellipse(x, y, 20, 17, c.lit("#8a5a3a"))
    g.circle(x + 15, y - 12, 9, c.lit("#9a6a44"))
    g.circle(x + 18, y - 14, 1.6, "#1a1622")
    g.path(f"M{x + 23} {y - 12}l6 2l-6 2z", c.lit("#e8b440"))
    g.path(f"M{x + 22} {y - 9}q3 4 0 7", stroke=c.lit("#e2574c"), stroke_width=2)
    for dx in (-10, 10):
        g.line(x + dx, y + 16, x + dx * 1.6, y + 64, c.lit("#3a3050"), 0.6, opacity=0.8)
    return g


def sky(L: Layer, c: Ctx, hs: set[str]) -> None:
    """Holiday things in the fixed sky behind the islands."""
    if "stpatrick" in hs and not c.dark:
        for k, col in enumerate(("#ff5a5a", "#ffa23a", "#ffe45a", "#5fd06a", "#4aa8ff",
                                 "#8a6aff")):
            r = 330 - k * 9
            L.path(f"M{480 - r} 330A{r} {r * 0.62} 0 0 1 {480 + r} 330", stroke=col,
                   stroke_width=9, opacity=0.32)


def far(L: Layer, c: Ctx, hs: set[str]) -> None:
    """Holiday things floating among the islands (the overview)."""
    if "valentine" in hs:
        for k, (x, y, r, col) in enumerate(((300, 250, 4, "#ff6a9a"), (420, 230, 3, "#ffb7d0"),
                                            (560, 245, 5, "#ff4a7a"), (690, 235, 3.5, "#ffb7d0"),
                                            (480, 260, 3, "#ff6a9a"), (620, 270, 4, "#ff4a7a"))):
            L.raw(f'<g class="float" style="animation-delay:-{k * 1.5}s">'
                  f"{_heart(x, y, r, col)}</g>")
    if "pi" in hs:
        L.group(_balloon(c, 640, 120, "#3d5bb0", "π"), class_="bob",
                style="animation-duration:4s")


def near(L: Layer, c: Ctx, hs: set[str]) -> None:
    """Holiday things in front of the Philly skyline."""
    if "thanksgiving" in hs and c.w.when.date() == thanksgiving(c.w.when.year):
        L.group(_turkey(c, 205, 104), class_="bob", style="animation-duration:5s")


def flyers(L: Layer, c: Ctx, hs: set[str]) -> None:
    """Things crossing the whole frame: bats at Halloween, the sleigh on Christmas Eve."""
    if "halloween" in hs:
        bats = Layer()
        for k, (dx, dy) in enumerate(((0, 0), (22, -12), (40, 6), (14, 16), (58, -4))):
            bats.path(f"M{dx} {dy}q-4 -5 -9 -3q3 1 2 4q-2 -2 -5 0q4 1 5 4q3 -3 7 -3"
                      f"q4 0 7 3q1 -3 5 -4q-3 -2 -5 0q-1 -3 2 -4q-5 -2 -9 3z",
                      "#5a3a78" if c.dark else "#1a1222",
                      class_="flap", style=f"animation-delay:-{k * 0.05:.2f}s")
        g = Layer()
        g.group(bats, transform="translate(0 110) scale(1.6)")
        L.group(g, class_="bats")


# ---------------------------------------------------------------- in the town

def _use(L: Layer, ref: str, x: float, y: float, **a) -> None:
    """Place a kept shape at x, y. An animated one (a class) goes inside a translated group,
    so its own box sits at 0,0 and a swing turns about its hook, not about a far point."""
    if a:
        L.raw(f'<g transform="translate({x:.1f} {y:.1f})"><use href="{ref}"{attrs(a)}/></g>')
    else:
        L.el("use", href=ref, x=round(x, 1), y=round(y, 1))


def _dots(L: Layer, c: Ctx, by_colour: dict[str, list[tuple[float, float]]],
          twinkle: bool = True) -> None:
    """Bulbs as round-capped zero-length strokes, one path per colour, and one soft glow
    path per colour after dark."""
    for k, (col, spots) in enumerate(by_colour.items()):
        d = "".join(f"M{x:.1f} {y:.1f}h0" for x, y in spots)
        if c.P["lamps"]:
            L.path(d, stroke=col, stroke_width=6, stroke_linecap="round", opacity=0.35,
                   filter=c.defs.blur(1.5))
        L.path(d, stroke=col, stroke_width=2.4, stroke_linecap="round",
               class_="tw" if twinkle and k % 2 else None,
               style=f"animation-delay:-{k}s" if twinkle and k % 2 else None)


def _sag(a: tuple[float, float], b: tuple[float, float], u: float, sag: float) -> tuple[float, float]:
    (x0, y0), (x1, y1) = a, b
    my = max(y0, y1) + sag
    return ((1 - u) ** 2 * x0 + 2 * (1 - u) * u * (x0 + x1) / 2 + u * u * x1,
            (1 - u) ** 2 * y0 + 2 * (1 - u) * u * my + u * u * y1)


def _wires(L: Layer, pairs: list, sag: float) -> None:
    L.path("".join(f"M{a[0]:.1f} {a[1]:.1f}Q{(a[0] + b[0]) / 2:.1f} {max(a[1], b[1]) + sag:.1f} "
                   f"{b[0]:.1f} {b[1]:.1f}" for a, b in pairs), stroke="#2a2230", stroke_width=0.5)


def _posts(s: Shape, span: tuple[float, float]) -> list[tuple[float, float]]:
    """The tops of the street lamps, where strands and bunting hang from."""
    out, x = [], span[0] - 10
    while x < span[1] + 20:
        out.append((x, s.ground(x) + 4 - 17))
        x += 34
    return out


def _jack(c: Ctx) -> str:
    """A jack-o'-lantern sitting on 0,0, its face lit after dark."""
    face = "#ffd27a" if c.P["lamps"] else "#3a2010"
    g = Layer()
    if c.P["lamps"]:
        c.glow(g, 0, -3, 9, "#ffb35a", 0.6, class_="flick")
    g.ellipse(0, -3, 4.2, 3.4, c.lit("#e8873a"))
    g.path("M-1.4 -3.4V-0.2M1.4 -3.4V-0.2", stroke=c.lit("#c0652a"), stroke_width=0.5)
    g.rect(-0.5, -7.6, 1, 1.6, c.lit("#3a6a3a"))
    g.path("M-2.4 -4l1 -1.4l1 1.4zM0.4 -4l1 -1.4l1 1.4zM-2.2 -2.2q2.2 1.6 4.4 0z", face)
    return c.defs.shape(f"jack-{c.phase}", g.svg())


def _lantern(c: Ctx) -> str:
    """A red paper lantern hanging from 0,0."""
    g = Layer()
    if c.P["lamps"]:
        c.glow(g, 0, 7, 10, "#ff6a3a", 0.7)
    g.line(0, 0, 0, 3, "#2a2230", 0.5)
    g.ellipse(0, 7, 3.2, 4, "#e2302a")
    g.rect(-2, 2.8, 4, 1, c.lit("#e8b440"))
    g.rect(-2, 10.4, 4, 1, c.lit("#e8b440"))
    g.line(0, 11.4, 0, 14, c.lit("#e8b440"), 0.6)
    return c.defs.shape(f"lantern-{c.phase}", g.svg())


def _egg(L: Layer, x: float, y: float, col: str, band: str) -> None:
    L.ellipse(x, y, 1.8, 2.4, col)
    L.path(f"M{x - 1.7:.1f} {y}h3.4", stroke=band, stroke_width=0.6)


def _tree(L: Layer, c: Ctx, x: float, base: float) -> None:
    """A tall decorated tree with a star on top."""
    L.rect(x - 1.5, base - 5, 3, 5, c.lit("#5a3f2e"))
    for k, (w, y) in enumerate(((13, 5), (10, 15), (7, 24))):
        L.poly([(x - w, base - y), (x, base - y - 14), (x + w, base - y)],
               c.lit("#1f6a3e" if k % 2 else "#24784a"))
    baubles: dict[str, list[tuple[float, float]]] = {}
    for k, (dx, dy) in enumerate(((-6, 8), (5, 11), (-3, 17), (4, 21), (0, 28), (-8, 6),
                                  (8, 7), (-2, 12))):
        baubles.setdefault(("#ff4a3a", "#ffd27a", "#4aa8ff", "#ff6ab4")[k % 4], []).append(
            (x + dx, base - dy))
    _dots(L, c, baubles)
    L.path(f"M{x} {base - 42}l1.4 3.2l3.4 .3l-2.6 2.2l.8 3.3l-3 -1.8l-3 1.8l.8 -3.3"
           f"l-2.6 -2.2l3.4 -.3z", "#ffd27a")
    if c.P["lamps"]:
        c.glow(L, x, base - 38, 12, "#ffd27a", 0.8)


def _menorah(L: Layer, c: Ctx, x: float, base: float, lit: int) -> None:
    """A menorah: eight candles and the raised helper candle in the middle; tonight's are lit."""
    gold = c.lit("#e8b440")
    L.rect(x - 1, base - 12, 2, 12, gold)
    L.rect(x - 4, base - 1.5, 8, 1.5, gold)
    L.path(f"M{x - 12} {base - 13}q12 9 24 0", stroke=gold, stroke_width=1.2)
    slots = [x - 12, x - 9, x - 6, x - 3, x + 3, x + 6, x + 9, x + 12]
    for k, cx in enumerate([*slots, x]):
        top = base - (19 if k == 8 else 16)
        L.rect(cx - 0.6, top, 1.2, 3, "#f2f2f8")
        if k == 8 or k >= 8 - lit:  # lit from right to left, newest first
            L.ellipse(cx, top - 1.2, 0.8, 1.3, "#ffd27a", class_="flick")
            if c.P["lamps"]:
                c.glow(L, cx, top - 1.2, 4, "#ffb35a", 0.7)


LIGHTS = ("#ff4a3a", "#ffd27a", "#4aa8ff", "#5fd06a", "#ff6ab4")


def _lights(L: Layer, c: Ctx, pairs: list, per: int, sag: float) -> None:
    _wires(L, pairs, sag)
    bulbs: dict[str, list[tuple[float, float]]] = {}
    for a, b in pairs:
        for k in range(1, per + 1):
            x, y = _sag(a, b, k / (per + 1), sag)
            bulbs.setdefault(LIGHTS[k % len(LIGHTS)], []).append((x, y + 1))
    _dots(L, c, bulbs)


def _bunting(L: Layer, pairs: list, per: int, sag: float) -> None:
    _wires(L, pairs, sag)
    flags: dict[str, list[str]] = {}
    for a, b in pairs:
        for k in range(1, per + 1):
            x, y = _sag(a, b, k / (per + 1), sag)
            flags.setdefault(("#e2302a", "#ffffff", "#3a5bd0")[k % 3], []).append(
                f"M{x - 2.4:.1f} {y:.1f}h4.8l-2.4 4z")
    for col, d in flags.items():
        L.path("".join(d), col)


def _lanterns(L: Layer, c: Ctx, pairs: list, us: tuple[float, ...], sag: float) -> None:
    _wires(L, pairs, sag)
    ref = _lantern(c)
    for a, b in pairs:
        for u in us:
            x, y = _sag(a, b, u, sag)
            _use(L, ref, x, y, class_="swing")


def _presents(L: Layer, c: Ctx, x: float, base: float) -> None:
    """Wrapped presents with ribbons, piled at the foot of a tree."""
    for dx, w, h, box, ribbon in ((-11, 6, 5, "#c0352e", "#ffd27a"), (-5, 5, 4, "#3a7bd0", "#ffffff"),
                                  (6, 6, 6, "#2f8a4a", "#ff4a3a"), (12, 4, 3.5, "#ffd27a", "#c0352e")):
        L.rect(x + dx - w / 2, base - h, w, h, c.lit(box), rx=0.6)
        L.path(f"M{x + dx:.1f} {base - h:.1f}v{h}M{x + dx - w / 2:.1f} {base - h / 2:.1f}h{w}",
               stroke=c.lit(ribbon), stroke_width=0.8)


def _ghost(c: Ctx) -> Layer:
    """A small friendly ghost."""
    g = Layer()
    if c.dark:
        c.glow(g, 0, 0, 16, "#dff0ff", 0.4)
    g.path("M-7 8V-2a7 7 0 0 1 14 0V8l-2.4 -2.4l-2.3 2.4l-2.3 -2.4l-2.3 2.4l-2.3 -2.4z",
           "#f4f2ff", opacity=0.85)
    g.circle(-2.4, -1.5, 1, "#2a2440")
    g.circle(2.4, -1.5, 1, "#2a2440")
    g.ellipse(0, 2.4, 1.4, 1.8, "#2a2440")
    return g


def snowman(L: Layer, c: Ctx, x: float, base: float) -> None:
    """A snowman in a top hat and red scarf."""
    snow = c.lit("#f4f6fc")
    L.circle(x, base - 6, 6.5, snow)
    L.circle(x, base - 16, 4.8, snow)
    L.circle(x, base - 23.5, 3.6, snow)
    L.path(f"M{x - 4} {base - 20.5}h8", stroke=c.lit("#c0352e"), stroke_width=1.6)
    L.path(f"M{x} {base - 23.5}l4 1l-4 0.8z", c.lit("#e8873a"))
    L.rect(x - 3.4, base - 30.5, 6.8, 4.2, c.lit("#1f1a2a"))
    L.rect(x - 4.8, base - 26.8, 9.6, 1, c.lit("#1f1a2a"))
    L.path(f"M{x - 5} {base - 16}l-6 -5M{x + 5} {base - 16}l6 -5", stroke=c.lit("#5a3f2e"),
           stroke_width=0.9)


def town(L: Layer, c: Ctx, s: Shape, span: tuple[float, float]) -> None:
    """Decorations along the main street, drawn after the buildings and lamps."""
    hs = keys(c)
    if season(c.w.when.month) == "winter":
        snowman(L, c, s.x0 + 70, s.ground(s.x0 + 70) + 4)
    if not hs:
        return
    posts = _posts(s, span)
    pairs = list(itertools.pairwise(posts))
    if "lights" in hs:
        _lights(L, c, pairs, 6, 12)
        x = span[1] + 18
        _tree(L, c, x, s.ground(x) + 3)
        if "christmas" in hs:
            _presents(L, c, x, s.ground(x) + 4)
    if "hanukkah" in hs:
        night = next(h.night for h in on(c.w.when.date()) if h.key == "hanukkah")
        x = span[1] - 4
        _menorah(L, c, x, s.ground(x) + 3, night)
    if "july4" in hs:
        _bunting(L, pairs, 5, 8)
    if "lunar" in hs:
        _lanterns(L, c, pairs, (0.33, 0.67), 8)
    if "halloween" in hs:
        ref = _jack(c)
        for x, _ in posts:
            _use(L, ref, x + 5, s.ground(x + 5) + 4)
    if "easter" in hs:
        _eggs(L, s, s.x0 + 70, s.x1 - 70, 14)


def _eggs(L: Layer, s: Shape, x0: float, x1: float, n: int) -> None:
    cols = (("#ffb7d0", "#ffffff"), ("#9fd8ff", "#ffe27a"), ("#ffe27a", "#b07aff"),
            ("#b6f0a0", "#ff9fb8"))
    for k in range(n):
        x = x0 + (x1 - x0) * ((k * 37) % 100) / 100
        _egg(L, x, s.ground(x) + 6 + (k % 3), *cols[k % 4])


def platform(L: Layer, c: Ctx, a: float, b: float, top: float, base: float) -> None:
    """The same decorations on a ride station's platform, strung between its two lamps."""
    hs = keys(c)
    pairs = [((a, top), (b, top))]
    if "lights" in hs:
        _lights(L, c, pairs, 12, 9)
    if "july4" in hs:
        _bunting(L, pairs, 10, 7)
    if "lunar" in hs:
        _lanterns(L, c, pairs, (0.25, 0.5, 0.75), 7)
    if "halloween" in hs:
        ref = _jack(c)
        for x in (a + 6, b - 6):
            _use(L, ref, x, base)


def farm(L: Layer, c: Ctx, s: Shape, x0: float, x1: float) -> None:
    """The Server Farm's old wheat patch: pumpkins for Halloween and Thanksgiving, eggs at
    Easter, and a snowman (with a lit tree and presents in December) in winter."""
    hs = keys(c)
    if hs & {"halloween", "thanksgiving"}:
        ref = _jack(c)
        for k in range(6):
            x = x0 + 6 + (x1 - x0 - 12) * k / 5
            _use(L, ref, x, s.ground(x) + 3 + (k % 2) * 2)
    if "easter" in hs:
        _eggs(L, s, x0, x1, 8)
    if season(c.w.when.month) == "winter":
        snowman(L, c, x0 - 12, s.ground(x0 - 12) + 3)
    if "lights" in hs:
        x = x0 + 14
        _tree(L, c, x, s.ground(x) + 2)
        if "christmas" in hs:
            _presents(L, c, x, s.ground(x) + 3)


def wild(L: Layer, c: Ctx, x: float, y: float) -> None:
    """A ghost haunting the ruined arch on the wild side in Halloween week."""
    if "halloween" in keys(c):
        g = Layer()
        g.group(_ghost(c), class_="bob", style="animation-duration:2.2s")
        L.group(g, transform=f"translate({x:.0f} {y:.0f}) scale(1.4)")


def night_tint(L: Layer, c: Ctx) -> None:
    """Halloween nights turn a little purple."""
    if "halloween" in keys(c) and c.dark:
        L.rect(0, 0, W, H, "#6a2a9a", opacity=0.12)
