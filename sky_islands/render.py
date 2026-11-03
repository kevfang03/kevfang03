"""Put the layers together into one animated SVG."""

from __future__ import annotations

import random
from xml.sax.saxutils import escape

from . import (
    camera,
    companion,
    creatures,
    events,
    holidays,
    hud,
    island,
    rail,
    ride,
    seasons,
    sky,
    stations,
    town,
    weather,
    wonders,
    world,
)
from .context import FONT, Ctx, H, W
from .model import World
from .progress import current_quest, level_info
from .svg import Defs, Layer

# Plain CSS and SMIL animations keep running when GitHub shows the SVG as a README image.
CSS = (
    "text{font-family:" + FONT + "}"
    "@keyframes blink{0%,50%{opacity:1}51%,100%{opacity:0}}"
    "@keyframes tw{0%,70%{opacity:1}71%,100%{opacity:.2}}"
    "@keyframes shoot{0%{transform:translate(0,0);opacity:0}1%{opacity:1}"
    "7%{transform:translate(-240px,110px);opacity:0}100%{opacity:0}}"
    "@keyframes flicker{0%,100%{opacity:.9}20%{opacity:.7}45%{opacity:1}70%{opacity:.8}}"
    "@keyframes fall{to{stroke-dashoffset:-48}}"
    "@keyframes sway{from{transform:translateX(-2px)}to{transform:translateX(2px)}}"
    "@keyframes bob{from{transform:translateY(-3px)}to{transform:translateY(3px)}}"
    "@keyframes smoke{0%{transform:translateY(0);opacity:0}30%{opacity:.5}"
    "100%{transform:translateY(-14px);opacity:0}}"
    "@keyframes spin{to{transform:rotate(360deg)}}"
    "@keyframes wake{from{transform:translateX(0) scale(.6);opacity:.5}"
    "to{transform:translateX(-28px) scale(1.5);opacity:0}}"
    ".wake{animation:wake 1.4s ease-out infinite;transform-box:fill-box;transform-origin:center}"
    "@keyframes wave{from{transform:rotate(-25deg)}to{transform:rotate(20deg)}}"
    ".wave{animation:wave .7s ease-in-out infinite alternate;transform-box:fill-box;"
    "transform-origin:0% 100%}"
    ".tw{animation:tw 4s steps(1) infinite}.av{animation:blink 1.6s steps(1) infinite}"
    ".shoot{animation:shoot 10s linear infinite}.flick{animation:flicker 2s ease-in-out infinite}"
    ".fall{animation:fall .8s linear infinite}.sway{animation:sway 2.4s ease-in-out infinite alternate}"
    ".bob{animation:bob 3s ease-in-out infinite alternate}.smoke{animation:smoke 3s ease-out infinite}"
    ".spin{animation:spin 7s linear infinite;transform-box:fill-box;transform-origin:center}"
    "@keyframes radar{0%,100%{transform:scaleX(1)}50%{transform:scaleX(.12)}}"
    ".radar{animation:radar 3.2s ease-in-out infinite;transform-box:fill-box;"
    "transform-origin:center}"
    ".fa,.fb{animation:blink 1.4s steps(1) infinite}.fb{animation-delay:-.7s}"
    "@keyframes flock{from{transform:translate(-80px,20px)}to{transform:translate(1040px,-30px)}}"
    ".flock{animation:flock 40s linear infinite}"
    "@keyframes pulse{from{opacity:.6}to{opacity:1}}.pulse{animation:pulse 3s ease-in-out infinite alternate}"
    "@keyframes drift{from{transform:translateX(-12px)}to{transform:translateX(12px)}}"
    ".drift{animation:drift 30s ease-in-out infinite alternate}"
    "@keyframes walk{from{transform:translateX(-18px)}to{transform:translateX(18px)}}"
    ".walk{animation:walk 16s ease-in-out infinite alternate}"
    "@keyframes launch{0%,55%{transform:translate(0,0);opacity:1}80%{opacity:1}"
    "100%{transform:translate(110px,-150px);opacity:0}}.launch{animation:launch 14s ease-in infinite}"
    "@keyframes petal{0%{transform:translate(0,0) rotate(0);opacity:0}15%{opacity:1}"
    "100%{transform:translate(-26px,40px) rotate(200deg);opacity:0}}"
    ".petal{animation:petal 7s linear infinite;transform-box:fill-box;transform-origin:center}"
    "@media (prefers-reduced-motion:reduce){*{animation:none!important}}"
)

def fireflies(L: Layer, c: Ctx, s: island.Shape) -> None:
    """Tiny drifting lights over the grass on warm nights, May to September."""
    if not c.dark or not 5 <= c.w.when.month <= 9:
        return
    for _ in range(22):
        x = c.rng.uniform(s.x0 + 30, s.x1 - 30)
        y = s.ground(x) - c.rng.uniform(4, 60)
        L.circle(x, y, 1.3, "#e6ff9a", class_="tw", style=f"animation-delay:-{c.rng.uniform(0, 4):.1f}s")
        c.glow(L, x, y, 5, "#e6ff9a", 0.5)


def _with_labels(c: Ctx, draw) -> Layer:
    """Draw one island with its own labels, so a copy of it carries them along."""
    g, labels = Layer(), []
    draw(g, c, labels)
    hud.labels(g, labels)
    return g


def _home(c: Ctx, home: island.Shape) -> Layer:
    g = Layer()
    island.hanging_lanterns(g, c, home)
    island.draw(g, c, home, "rock-home", style="town")
    island.crystals(g, c, home)
    labels = town.draw(g, c, home)
    fireflies(g, c, home)
    seasons.butterflies(g, c, home)
    seasons.fallers(g, c, home)
    hud.labels(g, labels)
    return g


def render(w: World) -> str:
    """Draw the world for one moment and return it as SVG text."""
    defs = Defs()
    c = Ctx(w, random.Random(f"{w.seed}-{w.when.date().isoformat()}"), defs)
    home = island.HOME

    L = Layer()
    # Fixed backdrop: the sky barely changes as the camera moves.
    sky.sky(L, c)
    ev = events.roll(w)
    sky.stars(L, c)
    if ev.meteors:
        events.meteors(L, c)
    if ev.aurora:
        events.aurora(L, c)
    sky.sun_or_moon(L, c, ev.big_moon)
    if ev.comet:
        events.comet(L, c)
    hs = holidays.keys(c)
    holidays.sky(L, c, hs)
    labels: list = []
    # The overview: the whole archipelago, as the loop opens and closes.
    far = Layer()
    sky.sky_clouds(far, c)
    island.far_islands(far, c)
    creatures.whales(far, c)
    sky.birds(far, c)
    world.locked_islands(far, c, labels)
    if ev.fireworks:
        events.fireworks(far, c, ev.fireworks)
    creatures.jellies(far, c)
    holidays.far(far, c, hs)
    near = Layer()
    world.flying_cars(near, c)
    near.group(_with_labels(c, world.philly), id="isl-philly")
    holidays.near(near, c, hs)
    near.group(_with_labels(c, world.stadium), id="isl-stadium")
    near.group(_home(c, home), id="isl-home")
    world.rope_bridge(near, c, island.PHILLY, home)
    rail.draw(near, c)
    island.drifting_rocks(near, c, world.DRIFTING)
    clouds = Layer()
    sky.cloud_sea(clouds, c)
    near.group(clouds, id="clouds")
    hud.labels(near, labels)
    over = Layer()
    over.add(far)
    over.add(near)
    L.group(over, class_="over")
    # The ride: one lap around the island, revealed after the first fade.
    bg, far, strip, station_css = ride.draw_world(c)
    trip = Layer()
    trip.group(bg, class_="ride-bg")
    # Only the half of the loop across the island shows; it fades out towards the sides.
    fade = defs.linear("farfade", [(0.12, "#ffffff", 0), (0.36, "#ffffff", 1),
                                   (0.64, "#ffffff", 1), (0.88, "#ffffff", 0)], x2=1, y2=0)
    across = Layer()
    across.group(far, class_="ride-far")
    trip.group(across, opacity=0.5,
               mask=defs.mask("farmask", f'<rect width="{W}" height="{H}" fill="{fade}"/>'))
    trip.group(strip, class_="ride-world")
    crate, drone, delivery_css = stations.delivery(c)
    trip.add(crate)
    trip.add(ride.train(c))
    trip.add(drone)
    L.group(trip, class_="ride")
    # Things that cross the whole sky, whatever the camera is doing.
    wonders.squadron(L, c, holidays.sleigh(c) if "christmas" in hs else None)
    skin = "lunar" if "lunar" in hs else "christmas" if "christmas" in hs else None
    wonders.dragon_flight(L, c, ev.shiny, skin)
    holidays.flyers(L, c, hs)
    holidays.night_tint(L, c)
    weather.overlay(L, c)
    L.rect(0, 0, W, H, defs.radial("vignette", [(0.55, "#000000", 0), (1, "#000000", 0.38)],
                                   r=0.75))
    L.rect(0, 0, W, H, "#05040f", class_="fade")
    hud.header(L, c, ev.headline())
    marker_span = hud.timeline(L, c)
    L.rect(0, 0, W, H, "#808080", filter=defs.grain(), opacity=0.06)
    card = defs.clip("card", f'<rect width="{W}" height="{H}" rx="14"/>')

    st = w.stats
    lv = level_info(st.contributions_total)
    quest = current_quest(st.repos)
    title = f"{st.login}'s sky islands"
    desc = (
        f"A floating world that grows with {st.login}'s GitHub activity, shown at {w.phase}. "
        f"Level {lv.level} with {st.contributions_total} contributions; "
        f"{len(st.repos)} repositories stand as buildings: "
        + ", ".join(r.name for r in st.repos[:8])
        + (f". Now building {quest.repo.name}, {quest.remaining} commits from its next tier."
           if quest else ".")
        + f" Your companion, {companion.NAMES[companion.stage(lv.level) - 1]}, waits on the HQ roof."
    )
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
        f'role="img" aria-labelledby="title desc">'
        f'<title id="title">{escape(title)}</title><desc id="desc">{escape(desc)}</desc>'
        f"<style>{CSS}{creatures.css()}{camera.css(marker_span)}{station_css}{delivery_css}{weather.CSS}{events.CSS}{seasons.CSS}{holidays.CSS}{hud.MOBILE_CSS}"
        f"</style>{defs.svg()}"
        f'<g clip-path="{card}">{L.svg()}</g></svg>'
    )
