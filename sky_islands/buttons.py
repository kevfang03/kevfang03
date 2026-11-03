"""Small game-style buttons for the README: a navy plate in a notched gold frame standing on a
ledge, an icon tile on the left and a shine that sweeps across now and then. The button for
the page you are on is drawn pressed, in gold.

GitHub shows README images without scripts, so each button is a picture inside a link.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .context import FONT
from .svg import Layer

H = 40
LEDGE = 4
NOTCH = 5
ICON = 26


@dataclass(frozen=True)
class Button:
    key: str
    label: str
    width: int
    tile: tuple[str, str]  # icon tile gradient, top to bottom


BUTTONS = (
    Button("dawn", "DAWN", 124, ("#b84a7a", "#f29a5a")),
    Button("day", "DAY", 124, ("#6cc4ff", "#3a8ee0")),
    Button("dusk", "DUSK", 124, ("#ff8a5c", "#7a4ab0")),
    Button("night", "NIGHT", 124, ("#3a3a8a", "#141438")),
    Button("level-10", "LV 10 PREVIEW", 184, ("#ffe08a", "#e8a030")),
)


def _plate(w: float, h: float, n: float = NOTCH) -> str:
    """An outline with the corners cut off, like a game menu frame."""
    return (f"M{n} 0H{w - n}L{w} {n}V{h - n}L{w - n} {h}H{n}L0 {h - n}V{n}Z")


def _icon(g: Layer, key: str, x: float, y: float) -> None:
    """A tiny picture for each button, drawn inside a 26 px tile at (x, y)."""
    cx, cy = x + ICON / 2, y + ICON / 2
    sun, white = "#fff2b0", "#ffffff"
    if key == "dawn":
        g.path(f"M{cx - 7} {cy + 4}a7 7 0 0 1 14 0z", sun)
        for dx, dy in ((-9, -1), (-5, -6), (0, -8), (5, -6), (9, -1)):
            g.line(cx + dx * 0.8, cy + 4 + dy * 0.8 - 1, cx + dx, cy + 4 + dy - 1, sun, 1.2,
                   stroke_linecap="round")
        g.line(x + 4, cy + 5, x + ICON - 4, cy + 5, white, 1.2, stroke_linecap="round")
    elif key == "day":
        g.circle(cx, cy, 5, sun)
        for k in range(8):
            dx, dy = [(1, 0), (0.7, 0.7), (0, 1), (-0.7, 0.7), (-1, 0), (-0.7, -0.7), (0, -1),
                      (0.7, -0.7)][k]
            g.line(cx + dx * 7, cy + dy * 7, cx + dx * 9.5, cy + dy * 9.5, sun, 1.3,
                   stroke_linecap="round")
    elif key == "dusk":
        g.circle(cx, cy + 3, 6, "#ffd27a")
        g.rect(x + 2, cy + 3, ICON - 4, 9, "#7a4ab0")
        for k, w in enumerate((14, 10, 6)):
            g.line(cx - w / 2, cy + 6 + k * 2.5, cx + w / 2, cy + 6 + k * 2.5, "#ffb27a", 1,
                   stroke_linecap="round")
    elif key == "night":
        g.path(f"M{cx + 2} {cy - 7}a7 7 0 1 0 5 12a6 6 0 0 1 -5 -12z", "#fff3c4")
        g.path(f"M{cx + 6} {cy - 7}l1 2.2l2.2 1l-2.2 1l-1 2.2l-1 -2.2l-2.2 -1l2.2 -1z", white,
               class_="tw")
    else:
        # A small floating island with a crystal sparkle.
        g.path(f"M{cx - 9} {cy}h18l-6 7l-3 4l-3 -4z", "#8a6a4a")
        g.ellipse(cx, cy, 9.5, 2.6, "#5cbf6a")
        g.rect(cx - 2, cy - 7, 4, 6, "#ffffff")
        g.path(f"M{cx - 3} {cy - 7}l3 -3l3 3z", "#e0452f")
        g.path(f"M{cx + 7} {cy - 9}l0.9 2l2 0.9l-2 0.9l-0.9 2l-0.9 -2l-2 -0.9l2 -0.9z",
               "#bff4ff", class_="tw")


def button_svg(b: Button, active: bool = False) -> str:
    """One button as a standalone SVG."""
    w, h = b.width, H
    drop = LEDGE if active else 0  # a pressed button sinks onto its ledge
    face_top, face_bot = ("#ffe08a", "#e8b440") if active else ("#2c2560", "#17123a")
    text = "#1a1430" if active else "#ffffff"
    g = Layer()
    g.path(_plate(w, h), "#0a0a20", transform=f"translate(0 {LEDGE})")
    g.path(_plate(w, h), "url(#face)", stroke="#e8b440", stroke_width=2,
           transform=f"translate(0 {drop})")
    inner = Layer()
    inner.line(NOTCH + 2, 3.5, w - NOTCH - 2, 3.5, "#ffffff", 1, opacity=0.25)
    tx, ty = 7, (h - ICON) / 2
    inner.path(f"M{tx + 3} {ty}h{ICON - 6}l3 3v{ICON - 6}l-3 3h{-(ICON - 6)}l-3 -3v{-(ICON - 6)}z",
               "url(#tile)", stroke="#0a0a20", stroke_width=1, stroke_opacity=0.5)
    _icon(inner, b.key, tx, ty)
    label_x = tx + ICON + (w - tx - ICON) / 2
    inner.text(label_x, h / 2 + 4, b.label, 11.5, text, text_anchor="middle", font_weight="800",
               letter_spacing=2)
    if not active:
        inner.rect(-30, -4, 16, h + 8, "url(#shine)", class_="shine",
                   transform="skewX(-20)")
    g.group(inner, transform=f"translate(0 {drop})", clip_path="url(#plate)")
    style = (
        f"text{{font-family:{FONT}}}"
        f".shine{{animation:shine 6s ease-in-out infinite}}"
        f"@keyframes shine{{0%,70%{{transform:skewX(-20deg) translateX(0)}}"
        f"100%{{transform:skewX(-20deg) translateX({w + 60}px)}}}}"
        ".tw{animation:tw 2.4s ease-in-out infinite}"
        "@keyframes tw{0%,100%{opacity:1}50%{opacity:.35}}"
        "@media (prefers-reduced-motion:reduce){*{animation:none!important}}"
    )
    defs = (
        f'<linearGradient id="face" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{face_top}"/><stop offset="1" stop-color="{face_bot}"/>'
        f'</linearGradient>'
        f'<linearGradient id="tile" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{b.tile[0]}"/><stop offset="1" stop-color="{b.tile[1]}"/>'
        f'</linearGradient>'
        '<linearGradient id="shine" x1="0" y1="0" x2="1" y2="0">'
        '<stop offset="0" stop-color="#ffffff" stop-opacity="0"/>'
        '<stop offset=".5" stop-color="#ffffff" stop-opacity=".28"/>'
        '<stop offset="1" stop-color="#ffffff" stop-opacity="0"/></linearGradient>'
        f'<clipPath id="plate"><path d="{_plate(w, h)}"/></clipPath>'
    )
    total_h = h + LEDGE
    title = f"{b.label.title()} (this page)" if active else b.label.title()
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="-1 -1 {w + 2} {total_h + 2}" '
            f'width="{w + 2}" height="{total_h + 2}" role="img" aria-label="{title}">'
            f"<title>{title}</title><style>{style}</style><defs>{defs}</defs>{g.svg()}</svg>")


def write_buttons(out: Path) -> list[Path]:
    """Every button, plain and pressed, into `out`."""
    out.mkdir(parents=True, exist_ok=True)
    written = []
    for b in BUTTONS:
        for active in (False, True):
            path = out / f"{b.key}{'-active' if active else ''}.svg"
            path.write_text(button_svg(b, active), encoding="utf-8")
            written.append(path)
    return written
