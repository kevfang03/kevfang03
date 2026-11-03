"""The header and footer around the scene, and the labels that explain what is what."""

from __future__ import annotations

from datetime import datetime
from xml.sax.saxutils import escape

from .. import palette as pal
from ..growth import CONTRIBUTIONS_PER_FLOOR, LOTS, TOWER_FLOORS, tower_progress
from ..model import Game
from .city import Tag
from .layout import FOOTER_Y, GX0, GX1, HEADER_H, UI, Ctx, H, W
from .svg import Layer, Rects, attrs

CHAR = 0.6  # monospace glyph width as a share of the font size
PHASE_CHIP = {"dawn": "#b0577a", "day": "#1f6feb", "dusk": "#8a4fd8", "night": "#3b45a8"}


def clock_text(t: datetime) -> str:
    return f"{t.hour % 12 or 12}:{t.minute:02d} {'AM' if t.hour < 12 else 'PM'}"


def rich(L: Layer, x: float, y: float, parts: list[tuple[str, str, bool]], size: float,
         **a) -> None:
    """One line of text made of differently coloured pieces."""
    spans = "".join(
        f'<tspan fill="{col}"{" font-weight=\"700\"" if bold else ""}>{escape(s)}</tspan>'
        for s, col, bold in parts
    )
    L.raw(f"<text{attrs({'x': x, 'y': y, 'font_size': size, **a})}>{spans}</text>")


def _chip(L: Layer, x: float, y: float, text: str, bg: str, fg: str = "#ffffff",
          edge: str | None = None, size: float = 9) -> float:
    w = len(text) * size * CHAR + 14
    L.rect(x, y - size - 3, w, size + 8, bg, rx=(size + 8) / 2, stroke=edge,
           stroke_width=1 if edge else None)
    L.text(x + 7, y + 1, text, size, fg, font_weight="700", letter_spacing=0.3)
    return w


def game_text(g: Game, short: bool = False) -> str:
    label = pal.TEAMS[g.team]["label"]
    where = "vs" if g.home else "@"
    when = clock_text(g.start) if g.start else ""
    if short:
        return f"{label} {when}".strip()
    opp = f" {where} {g.opponent}" if g.opponent else ""
    return f"{label}{opp} · {when}" if when else f"{label}{opp}"


def header(L: Layer, c: Ctx) -> None:
    L.rect(0, 0, W, HEADER_H, UI["bg"])
    L.rect(0, HEADER_H - 1, W, 1, UI["line"])
    title = f"{c.s.stats.login.upper()} · PHILADELPHIA"
    L.text(20, 29, title, 15, UI["text"], font_weight="800", letter_spacing=1.5)
    x = 20 + len(title) * (15 * CHAR + 1.5) + 12
    x += _chip(L, x, 26, f"{c.phase.upper()} · {clock_text(c.s.when)}",
               PHASE_CHIP[c.phase]) + 6
    games = c.games
    for g in games:
        team = pal.TEAMS[g.team]
        x += _chip(L, x, 26, game_text(g, short=len(games) > 1), team["primary"], "#ffffff",
                   team["light"]) + 6
    legend = (f"1 floor = {CONTRIBUTIONS_PER_FLOOR} contributions · 1 lit boathouse = 1 repo · "
              "the city lights up on game days")
    L.text(20, 50, legend, 9, UI["muted"])

    st = c.s.stats
    done, floors = tower_progress(st.contributions_total)
    rich(L, W - 20, 27, [
        (f"{st.contributions_total:,}", UI["text"], True), (" CONTRIBUTIONS · ", UI["muted"], False),
        (str(done), UI["text"], True),
        (f" TOWER{'S' if done != 1 else ''} BUILT", UI["muted"], False),
    ], 10.5, text_anchor="end")
    if done >= len(LOTS):
        L.text(W - 20, 48, "SKYLINE COMPLETE", 9, UI["green"], text_anchor="end", font_weight="700")
        return
    bar_w, bx = 94, W - 20 - 94
    L.rect(bx, 42, bar_w, 6, "#21262d", rx=3)
    L.rect(bx, 42, max(3, bar_w * floors / TOWER_FLOORS), 6, UI["green"], rx=3)
    rich(L, bx - 8, 48, [(f"TOWER {done + 1} ", UI["muted"], False),
                         (f"{floors}/{TOWER_FLOORS} FLOORS", UI["text"], True)],
         9, text_anchor="end")


def _heat(n: int) -> str:
    if n <= 0:
        return "#161b22"
    if n <= 2:
        return "#0e4429"
    if n <= 4:
        return "#006d32"
    if n <= 7:
        return "#26a641"
    return "#39d353"


def footer(L: Layer, c: Ctx) -> None:
    L.rect(0, FOOTER_Y, W, H - FOOTER_Y, UI["bg"])
    L.rect(0, FOOTER_Y, W, 1, UI["line"])
    cal = c.s.stats.calendar[-182:]
    cells = Rects()
    today = (c.s.when.weekday() + 1) % 7  # Sunday is row 0, like GitHub's graph
    weeks = 26
    for i, n in enumerate(cal):
        ago = len(cal) - 1 - i
        col = weeks - 1 - (ago + 6 - today) // 7
        row = (today - ago) % 7
        if col >= 0:
            cells.add(20 + col * 9, FOOTER_Y + 11 + row * 9, 7, 7, _heat(n))
    L.add(cells)

    st = c.s.stats
    x, size = 272, 10.5
    rich(L, x, FOOTER_Y + 24, [
        (str(st.contributions_year), UI["green"], True), (" contributions this year   ", UI["muted"], False),
        (str(st.streak_days), UI["gold"], True), ("-day streak   ", UI["muted"], False),
        (str(st.repo_count), UI["blue"], True), (" repos   ", UI["muted"], False),
        (st.top_language, UI["text"], True),
    ], size)
    rich(L, x, FOOTER_Y + 44, [
        ("latest commit ", UI["muted"], False), (st.latest_commit, UI["text"], False),
        ("   building ", UI["muted"], False), (st.now_building, UI["blue"], True),
    ], size)
    weather = c.s.weather.capitalize()
    temp = f", {c.s.temp_f}°F" if c.s.temp_f is not None else ""
    parts = [("Philadelphia ", UI["muted"], False),
             (f"{clock_text(c.s.when)} · {weather}{temp}", UI["text"], False)]
    for g in c.games:
        parts += [("  ·  ", UI["muted"], False),
                  (game_text(g), pal.TEAMS[g.team]["light"], True)]
    rich(L, x, FOOTER_Y + 64, parts, size)


def tags(L: Layer, items: list[Tag]) -> None:
    for t in items:
        size = 7.6
        w = len(t.text) * size * CHAR + 10
        x = min(max(t.x - w / 2, GX0 + 4), GX1 - 4 - w)
        L.line(t.x, t.y + 3, t.x, t.y + 11, t.color, 0.8, stroke_dasharray="1.5 1.5")
        L.rect(x, t.y - 9, w, 13, UI["bg"], opacity=0.86, rx=3, stroke=t.color, stroke_width=0.8)
        L.text(x + 5, t.y + 0.5, t.text, size, t.color, font_weight="700")
