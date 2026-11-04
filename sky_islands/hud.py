"""The header across the top and the labels pinned over the world."""

from __future__ import annotations

from datetime import datetime

from . import palette as pal
from .context import HEADER_H, STRIP_Y, Ctx, H, W, sign, sign_width
from .progress import level_info
from .svg import Layer
from .town import Label

LABEL_SIZE = 7.5
LABEL_STEP = 13


def clock_text(t: datetime) -> str:
    return f"{t.hour % 12 or 12}:{t.minute:02d} {'AM' if t.hour < 12 else 'PM'}"


def game_text(g) -> str:
    label = pal.TEAMS[g.team]["label"]
    where = "vs" if g.home else "@"
    if g.result:
        when = f" · {g.result}"
    else:
        when = f" · {clock_text(g.start)}" if g.start else ""
    return f"{label} {where} {g.opponent}{when}"


def place(labels: list[Label]) -> list[tuple[Label, float]]:
    """Give each label a height so that no two overlap, raising later ones as needed."""
    placed: list[tuple[float, float, float]] = []  # x0, x1, y
    out = []
    for lb in sorted(labels, key=lambda lb: lb.y, reverse=True):
        half = sign_width(lb.text, LABEL_SIZE) / 2 + 3
        y = lb.y
        while any(abs(y - py) < LABEL_STEP and lb.x - half < px1 and lb.x + half > px0
                  for px0, px1, py in placed):
            y -= LABEL_STEP
        y = max(y, HEADER_H + 14)
        placed.append((lb.x - half, lb.x + half, y))
        out.append((lb, y))
    return out


def labels(L: Layer, items: list[Label]) -> None:
    for lb, y in place(items):
        x = min(max(lb.x, sign_width(lb.text) / 2 + 6), W - sign_width(lb.text) / 2 - 6)
        sign(L, x, y, lb.text, lb.color, LABEL_SIZE, leader=max(0.0, lb.y - y))


# Shown at phone width the banner is about a third of its size, so its small print would be
# a few pixels tall. An SVG's media queries see the size it is drawn at, so this applies
# only there.
MOBILE_CSS = (
    "@media (max-width:600px){.fine{display:none}"
    ".title{transform:scale(1.8);transform-origin:22px 26px}"
    f".lvl{{transform:scale(1.7);transform-origin:{W - 22}px 23px}}"
    ".headline{transform:translate(0,8px) scale(1.6);transform-origin:22px 42px}}"
)


def header(L: Layer, c: Ctx, headline: str | None = None) -> None:
    """The title, level and stats; a rare or dated event takes the tagline's place."""
    st = c.w.stats
    lv = level_info(st.contributions_total)
    L.rect(0, 0, W, HEADER_H + 10, c.defs.linear(
        "header", [(0, "#0a0a20", 0.82), (0.75, "#0a0a20", 0.5), (1, "#0a0a20", 0)]))
    # At phone width (see MOBILE_CSS) the title, level and any event line grow and the
    # fine print hides.
    title = Layer()
    title.text(22, 26, f"{st.login.upper()} · SKY ISLANDS", 13, "#ffffff", font_weight="800",
               letter_spacing=2)
    L.group(title, class_="title")
    if headline:
        line = Layer()
        line.text(22, 42, headline, 8.5, "#ffd27a", font_weight="700", class_="pulse")
        L.group(line, class_="headline")
    else:
        L.text(22, 42, "each repo is a building · commits upgrade it · contributions are XP",
               8.5, "#d6cfee", class_="fine")
    bar_x, bar_w = W - 196, 120
    lvl = Layer()
    lvl.rect(bar_x - 40, 15, 34, 16, "#e8b440", rx=8)
    lvl.text(bar_x - 23, 26.5, f"LV {lv.level}", 8.5, "#1a1430", text_anchor="middle",
             font_weight="800")
    lvl.rect(bar_x, 19, bar_w, 8, "#ffffff", opacity=0.18, rx=4)
    lvl.rect(bar_x, 19, max(4.0, bar_w * lv.fraction), 8, "#3fb950", rx=4)
    lvl.text(W - 22, 26.5, f"{lv.xp:,}/{lv.next:,} XP", 8.5, "#ffffff", text_anchor="end",
             font_weight="700")
    L.group(lvl, class_="lvl")
    weather = c.w.weather.capitalize()
    temp = f" {c.w.temp_f}°F" if c.w.temp_f is not None else ""
    L.text(W - 22, 42, f"{st.streak_days}-day streak · {len(st.repos)} repos · "
                       f"{st.contributions_year} this year · Philly {clock_text(c.w.when)} · "
                       f"{weather}{temp}", 8.5, "#d6cfee", text_anchor="end", class_="fine")


def _heat(n: int, peak: int) -> str:
    if n <= 0:
        return "#2a2f3a"
    t = n / max(peak, 1)
    return "#0e6b33" if t < 0.25 else "#1f9a46" if t < 0.5 else "#2fc35a" if t < 0.75 else "#5ff07e"


def timeline(L: Layer, c: Ctx, board: list[str] = ()) -> tuple[float, float] | None:
    """The last 26 weeks as a route map: one stop per week, bigger and brighter when busier,
    with a little Cloudliner riding it and a departure board naming the next stop.
    Returns where the ride's progress marker travels, if there is a route to travel."""
    st = c.w.stats
    weeks = st.weekly[-26:]
    L.rect(0, STRIP_Y, W, H - STRIP_Y, "#0a0a1c", opacity=0.92)
    L.line(0, STRIP_Y, W, STRIP_Y, "#ffffff", 0.6, opacity=0.12)
    mid = STRIP_Y + (H - STRIP_Y) / 2 + 1
    L.text(20, mid - 3, "LAST 26 WEEKS", 8, "#d6cfee", font_weight="700", letter_spacing=1,
           class_="fine")
    L.text(20, mid + 9, f"{sum(weeks)} contributions", 8, "#8b86a8", class_="fine")
    if weeks:
        x0, x1 = 150, 650
        L.line(x0, mid, x1, mid, "#3a3658", 3, stroke_linecap="round")
        peak = max(weeks)
        step = (x1 - x0) / max(len(weeks) - 1, 1)
        for i, n in enumerate(weeks):
            x = x0 + i * step
            r = 2.2 + 3.2 * (n / max(peak, 1)) ** 0.5
            L.circle(x, mid, r, _heat(n, peak))
            if n == peak:
                L.text(x, mid - 9, f"PEAK {n}", 7, "#5ff07e", text_anchor="middle",
                       font_weight="700", class_="fine")
        now = x0 + (len(weeks) - 1) * step
        L.circle(now, mid, 8, "none", stroke="#ffd27a", stroke_width=1.4, class_="flick")
        L.text(now + 12, mid + 3, "NOW", 7.5, "#ffd27a", font_weight="700", class_="fine")
        L.group(_mini_liner(mid), class_="marker", transform=f"translate({now:.0f} 0)")
    # The departure board: one message per part of the loop, switched by the camera's CSS.
    b = Layer()
    for k, text in enumerate(board):
        b.text(W - 20, mid - 3, text, 8, "#ffd27a", text_anchor="end", font_weight="700",
               letter_spacing=0.6, class_=f"b{k}")
    L.group(b, class_="fine")
    L.text(W - 20, mid + 9, _last_push(c), 8, "#8b86a8", text_anchor="end", class_="fine")
    return (x0, now) if weeks else None


def _mini_liner(mid: float) -> Layer:
    """The Cloudliner in miniature, nose at x=0 and wheels on the route line: an ivory
    locomotive and one coach with a sky-blue band and a lit headlamp."""
    m = Layer()
    top, base = mid - 10, mid - 2.5
    m.rect(-31, top + 1, 14, base - top - 1, "#efe9dc", rx=1.5)  # coach
    m.path(f"M-16 {top}h9q6 0 7 {base - top}h-16z", "#efe9dc")  # locomotive and nose
    m.path(f"M-30 {top + 2.6}h12M-15 {top + 2.6}h7", stroke="#2b4a6e", stroke_width=1.8)
    m.path(f"M-31 {base - 2.4}h31", stroke="#5fb4e8", stroke_width=1.3)  # the cloud band
    m.path(f"M-28 {base + 1}h0M-20 {base + 1}h0M-13 {base + 1}h0M-4 {base + 1}h0",
           stroke="#1a1430", stroke_width=2.4, stroke_linecap="round")  # wheels
    m.circle(-0.6, base - 1.4, 2.6, "#ffe9a8", opacity=0.35)
    m.circle(-0.6, base - 1.4, 0.9, "#fff6d8")
    return m


def _ago(then: datetime, now: datetime) -> str:
    mins = max(0, int((now - then).total_seconds() // 60))
    if mins < 60:
        return "just now" if mins < 2 else f"{mins}m ago"
    if mins < 48 * 60:
        return f"{mins // 60}h ago"
    return f"{mins // 1440}d ago"


def _last_push(c: Ctx) -> str:
    """Pull requests and stars when there are any, and which repo was pushed to last."""
    st = c.w.stats
    bits = []
    if st.merged_prs:
        bits.append(f"{st.merged_prs} PR{'s' if st.merged_prs != 1 else ''} merged")
    stars = sum(r.stars for r in st.repos)
    if stars:
        bits.append(f"{stars} star{'s' if stars != 1 else ''}")
    if st.repos:
        r = max(st.repos, key=lambda r: r.pushed_at)
        name = r.name if len(r.name) <= 24 else r.name[:23] + "…"
        bits.append(f"last push {name} · {_ago(r.pushed_at, c.w.when)}")
    return " · ".join(bits)
