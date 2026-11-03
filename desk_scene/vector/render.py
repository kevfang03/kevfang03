"""Put the vector scene together into one animated SVG."""

from __future__ import annotations

import random
from xml.sax.saxutils import escape

from ..growth import tower_progress
from ..model import SceneState
from . import city, hud, room, sky
from .layout import FONT, GX0, GX1, GY0, GY1, Ctx, H, W
from .svg import Defs, Layer

# Plain CSS animations keep running when GitHub shows the SVG as a README image.
CSS = (
    "text{font-family:" + FONT + "}"
    "@keyframes blink{0%,50%{opacity:1}51%,100%{opacity:0}}"
    "@keyframes tw{0%,70%{opacity:1}71%,100%{opacity:.2}}"
    "@keyframes drift{from{transform:translateX(-14px)}to{transform:translateX(14px)}}"
    "@keyframes plane{from{transform:translate(0,120px)}to{transform:translate(640px,96px)}}"
    "@keyframes bird{from{transform:translate(10px,170px)}50%{transform:translate(320px,160px)}"
    "to{transform:translate(640px,172px)}}"
    "@keyframes boat{from{transform:translateX(-10px)}to{transform:translateX(640px)}}"
    "@keyframes rip{0%,60%{opacity:1}61%,100%{opacity:0}}"
    "@keyframes rain{from{transform:translate(4px,-20px)}to{transform:translate(-4px,20px)}}"
    "@keyframes snow{0%{transform:translate(0,-18px);opacity:0}15%,85%{opacity:1}"
    "100%{transform:translate(6px,18px);opacity:0}}"
    "@keyframes fw{0%,30%{opacity:0}31%,55%{opacity:1}56%,100%{opacity:0}}"
    "@keyframes steam{0%{transform:translateY(0);opacity:0}30%{opacity:.7}"
    "100%{transform:translateY(-10px);opacity:0}}"
    "@keyframes ok{0%,15%{opacity:0}16%,95%{opacity:1}96%,100%{opacity:0}}"
    "@keyframes lid{0%,94%{opacity:0}95%,98%{opacity:1}99%,100%{opacity:0}}"
    "@keyframes sway{from{transform:translateX(-1.5px)}to{transform:translateX(1.5px)}}"
    "@keyframes wag{from{transform:rotate(-5deg)}to{transform:rotate(7deg)}}"
    ".tw{animation:tw 4s steps(1) infinite}.av{animation:blink 1.6s steps(1) infinite}"
    ".cloud{animation:drift 40s ease-in-out infinite alternate}"
    ".plane{animation:plane 55s linear infinite}.bird{animation:bird 30s linear infinite}"
    ".boat{animation:boat 60s linear infinite}.rip{animation:rip 3s steps(1) infinite}"
    ".rain{animation:rain .5s linear infinite}.snow{animation:snow 6s linear infinite}"
    ".fw{animation:fw 3.2s steps(1) infinite}.steam{animation:steam 3s ease-out infinite}"
    ".ok{animation:ok 9s steps(1) infinite}.cur{animation:blink 1s steps(1) infinite}"
    ".lid{animation:lid 6s steps(1) infinite}"
    ".sway{animation:sway 2.4s ease-in-out infinite alternate}"
    ".tail{animation:wag 2.6s ease-in-out infinite alternate}"
    ".fa,.fb{animation:blink 1.4s steps(1) infinite}.fb{animation-delay:-.7s}"
    "@media (prefers-reduced-motion:reduce){*{animation:none!important}}"
)


def render(s: SceneState) -> str:
    """Draw the scene for one moment and return it as SVG text."""
    rng = random.Random(f"{s.seed}-{s.when.date().isoformat()}")
    defs = Defs()
    c = Ctx(s, rng, defs)

    view = Layer()
    sky.sky(view, c)
    sky.sun_or_moon(view, c)
    sky.stars(view, c)
    sky.clouds(view, c)
    sky.fireworks(view, c)
    sky.plane(view, c)
    sky.birds(view, c)
    outside, tags = city.draw(c)
    view.add(outside)
    sky.weather(view, c)
    sky.glass_glints(view, c)
    glass = defs.clip("glass", f'<rect x="{GX0}" y="{GY0}" width="{GX1 - GX0}" '
                               f'height="{GY1 - GY0}"/>')

    body = Layer()
    body.group(view, clip_path=glass)
    labels = Layer()
    hud.tags(labels, tags)
    body.add(labels)
    body.add(room.draw(c))
    hud.header(body, c)
    hud.footer(body, c)
    card = defs.clip("card", f'<rect width="{W}" height="{H}" rx="12"/>')

    done, floors = tower_progress(s.stats.contributions_total)
    title = f"{s.stats.login}'s desk in Philadelphia"
    desc = (
        f"A desk by a window over the Philadelphia skyline, {s.phase}, {s.weather}. "
        f"{s.stats.contributions_year} contributions this year, "
        f"{s.stats.streak_days}-day streak, {done} towers built and "
        f"{floors} floors up on the next one."
    )
    if c.games:
        desc += " Game day: " + ", ".join(hud.game_text(g) for g in c.games) + "."
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" '
        f'height="{H}" role="img" aria-labelledby="title desc">'
        f'<title id="title">{escape(title)}</title><desc id="desc">{escape(desc)}</desc>'
        f"<style>{CSS}{room.typing_css(c)}{room.TAIL_ORIGIN}</style>"
        f"{defs.svg()}"
        f'<g clip-path="{card}">{body.svg()}</g>'
        "</svg>"
    )
