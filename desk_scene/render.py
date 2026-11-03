"""Put the layers together into one animated SVG."""

from __future__ import annotations

import random
from xml.sax.saxutils import escape

from . import outside
from . import room as room_layer
from .growth import tower_progress
from .model import SceneState
from .raster import Raster

W, H = outside.W, outside.H
SCALE = 4

# Animations are plain CSS, which GitHub keeps running in README images.
CSS = (
    "@keyframes blink{0%,50%{opacity:1}51%,100%{opacity:0}}"
    "@keyframes tw{0%,70%{opacity:1}71%,100%{opacity:.25}}"
    "@keyframes train{0%{transform:translateX(-170px)}55%,100%{transform:translateX(200px)}}"
    "@keyframes boat{from{transform:translateX(-20px)}to{transform:translateX(210px)}}"
    "@keyframes bird{from{transform:translate(-20px,0)}50%{transform:translate(90px,-4px)}"
    "to{transform:translate(200px,0)}}"
    "@keyframes rip{0%,60%{opacity:.9}61%,100%{opacity:0}}"
    "@keyframes rain{from{transform:translate(3px,-12px)}to{transform:translate(-3px,12px)}}"
    "@keyframes snow{0%{transform:translate(0,-12px);opacity:0}15%,85%{opacity:1}"
    "100%{transform:translate(4px,12px);opacity:0}}"
    "@keyframes fw{0%,30%{opacity:0}31%,55%{opacity:1}56%,100%{opacity:0}}"
    "@keyframes steam{0%{transform:translateY(0);opacity:0}30%{opacity:.8}"
    "100%{transform:translateY(-8px);opacity:0}}"
    "@keyframes ok{0%,15%{opacity:0}16%,95%{opacity:1}96%,100%{opacity:0}}"
    "@keyframes lid{0%,94%{opacity:0}95%,98%{opacity:1}99%,100%{opacity:0}}"
    ".tw{animation:tw 4s steps(1) infinite}.av{animation:blink 1.6s steps(1) infinite}"
    ".train{animation:train 16s linear infinite}.boat{animation:boat 48s linear infinite}"
    ".bird{animation:bird 28s linear infinite}.rip{animation:rip 3s steps(1) infinite}"
    ".rain{animation:rain .45s linear infinite}.snow{animation:snow 5s linear infinite}"
    ".fw{animation:fw 3.2s steps(1) infinite}.steam{animation:steam 3s ease-out infinite}"
    ".ok{animation:ok 9s steps(1) infinite}.cur{animation:blink 1s steps(1) infinite}"
    ".lid{animation:lid 6s steps(1) infinite}.xmas{animation:blink 1.2s steps(1) infinite}"
    "@keyframes plane{from{transform:translate(-10px,4px)}to{transform:translate(200px,-14px)}}"
    ".plane{animation:plane 50s linear infinite}"
    ".planeb{animation:plane 50s linear infinite,blink 1.1s steps(1) infinite}"
    "@keyframes carr{from{transform:translateX(-200px)}to{transform:translateX(200px)}}"
    "@keyframes carl{from{transform:translateX(200px)}to{transform:translateX(-200px)}}"
    "@keyframes jog{from{transform:translateX(-120px)}to{transform:translateX(200px)}}"
    "@keyframes sway{from{transform:translateX(-1px)}to{transform:translateX(1px)}}"
    ".carr{animation:carr 26s linear infinite}.carl{animation:carl 31s linear infinite}"
    ".jog{animation:jog 70s linear infinite}"
    ".sway{animation:sway 2.4s ease-in-out infinite alternate}"
    ".fa,.fb{animation:blink 1.2s steps(1) infinite}.fb{animation-delay:-.6s}"
    ".wa,.wb{animation:blink 1.6s steps(1) infinite}.wb{animation-delay:-.8s}"
    "@media (prefers-reduced-motion:reduce){*{animation:none!important}}"
)


def render(s: SceneState) -> str:
    """Draw the scene for one moment and return it as SVG text."""
    rng = random.Random(f"{s.seed}-{s.when.date().isoformat()}")
    ctx = outside.make_ctx(s, rng)
    g = (outside.GX0, outside.GY0, outside.GX1, outside.GY1)

    back = Raster(W, H)
    back.set_clip(*g)
    back_sprites = outside.draw_back(back, ctx)
    train = outside.train(ctx)
    bank = Raster(W, H)
    bank.set_clip(*g)
    traffic = outside.draw_bank(bank, ctx)
    front = Raster(W, H)
    front.set_clip(*g)
    front_sprites = outside.draw_front(front, bank, back, ctx)
    weather = outside.weather(ctx)

    room = Raster(W, H)
    room_sprites = room_layer.draw_room(room, s, rng)

    view = "".join([
        back.to_svg(),
        *(sp.to_svg() for sp in back_sprites),
        train.to_svg(),
        bank.to_svg(),
        *(sp.to_svg() for sp in traffic),
        front.to_svg(),
        *(sp.to_svg() for sp in front_sprites),
        *(sp.to_svg() for sp in weather),
        outside.glass_glints(ctx).to_svg(),
    ])
    inside = room.to_svg() + "".join(sp.to_svg() for sp in room_sprites)

    done, floors = tower_progress(s.stats.contributions_total)
    title = f"{s.stats.login}'s desk in Philadelphia"
    desc = (
        f"Pixel-art desk by a window over the Philadelphia skyline, {s.phase}, {s.weather}. "
        f"{s.stats.contributions_year} contributions this year, "
        f"{s.stats.streak_days}-day streak, {done} towers finished and "
        f"{floors} floors up on the next one."
    )
    gx0, gy0, gx1, gy1 = g
    sx, sy, sw, sh = room_layer.SCREEN
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W * SCALE} {H * SCALE}" '
        f'width="{W * SCALE}" height="{H * SCALE}" shape-rendering="crispEdges" role="img" '
        f'aria-labelledby="title desc">'
        f'<title id="title">{escape(title)}</title><desc id="desc">{escape(desc)}</desc>'
        f"<style>{CSS}{room_layer.typing_css(s)}</style>"
        f'<defs><clipPath id="glass"><rect x="{gx0}" y="{gy0}" width="{gx1 - gx0}" '
        f'height="{gy1 - gy0}"/></clipPath>'
        f'<clipPath id="screen"><rect x="{sx}" y="{sy}" width="{sw}" height="{sh}"/></clipPath>'
        f"</defs>"
        f'<g transform="scale({SCALE})"><g clip-path="url(#glass)">{view}</g>{inside}</g>'
        "</svg>"
    )
