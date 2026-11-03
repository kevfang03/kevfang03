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


def header(L: Layer, c: Ctx) -> None:
    st = c.w.stats
    lv = level_info(st.contributions_total)
    L.rect(0, 0, W, HEADER_H + 10, c.defs.linear(
        "header", [(0, "#0a0a20", 0.82), (0.75, "#0a0a20", 0.5), (1, "#0a0a20", 0)]))
    L.text(22, 26, f"{st.login.upper()} · SKY ISLANDS", 13, "#ffffff", font_weight="800",
           letter_spacing=2)
    L.text(22, 42, "each repo is a building · commits upgrade it · contributions are XP", 8.5,
           "#d6cfee")
    bar_x, bar_w = W - 196, 120
    L.rect(bar_x - 40, 15, 34, 16, "#e8b440", rx=8)
    L.text(bar_x - 23, 26.5, f"LV {lv.level}", 8.5, "#1a1430", text_anchor="middle",
           font_weight="800")
    L.rect(bar_x, 19, bar_w, 8, "#ffffff", opacity=0.18, rx=4)
    L.rect(bar_x, 19, max(4.0, bar_w * lv.fraction), 8, "#3fb950", rx=4)
    L.text(W - 22, 26.5, f"{lv.xp:,}/{lv.next:,} XP", 8.5, "#ffffff", text_anchor="end",
           font_weight="700")
    weather = c.w.weather.capitalize()
    temp = f" {c.w.temp_f}°F" if c.w.temp_f is not None else ""
    L.text(W - 22, 42, f"{st.streak_days}-day streak · {len(st.repos)} repos · "
                       f"{st.contributions_year} this year · Philly {clock_text(c.w.when)} · "
                       f"{weather}{temp}", 8.5, "#d6cfee", text_anchor="end")


def _heat(n: int, peak: int) -> str:
    if n <= 0:
        return "#2a2f3a"
    t = n / max(peak, 1)
    return "#0e6b33" if t < 0.25 else "#1f9a46" if t < 0.5 else "#2fc35a" if t < 0.75 else "#5ff07e"


def timeline(L: Layer, c: Ctx) -> tuple[float, float] | None:
    """The last 26 weeks as a route map: one stop per week, bigger and brighter when busier.
    Returns where the ride's progress marker travels, if there is a route to travel."""
    st = c.w.stats
    weeks = st.weekly[-26:]
    L.rect(0, STRIP_Y, W, H - STRIP_Y, "#0a0a1c", opacity=0.92)
    L.line(0, STRIP_Y, W, STRIP_Y, "#ffffff", 0.6, opacity=0.12)
    mid = STRIP_Y + (H - STRIP_Y) / 2 + 1
    L.text(20, mid - 3, "LAST 26 WEEKS", 8, "#d6cfee", font_weight="700", letter_spacing=1)
    L.text(20, mid + 9, f"{sum(weeks)} contributions", 8, "#8b86a8")
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
                L.text(x, mid - 9, f"PEAK {n}", 7, "#5ff07e", text_anchor="middle", font_weight="700")
        now = x0 + (len(weeks) - 1) * step
        L.circle(now, mid, 8, "none", stroke="#ffd27a", stroke_width=1.4, class_="flick")
        L.text(now + 12, mid + 3, "NOW", 7.5, "#ffd27a", font_weight="700")
        # A little train that rides along the route while the camera follows the real one.
        m = Layer()
        m.rect(-14, mid - 15, 14, 6, "#efe6f2", rx=2)
        m.path(f"M0 {mid - 15}q5 1 6 6h-6z", "#c9473f")
        m.rect(-11, mid - 14, 8, 2, "#ffd98a")
        L.group(m, class_="marker", transform=f"translate({now:.0f} 0)")
    L.text(W - 20, mid - 3, f"{st.merged_prs} PRs merged · {sum(r.stars for r in st.repos)} stars",
           8, "#d6cfee", text_anchor="end", font_weight="700")
    commit = st.latest_commit if len(st.latest_commit) <= 34 else st.latest_commit[:33] + "…"
    L.text(W - 20, mid + 9, f"latest: {commit}", 8, "#8b86a8", text_anchor="end")
    return (x0, now) if weeks else None
