"""The camera: a looping ride around the island, written as plain CSS keyframes.

One loop: the whole archipelago with the train waiting at the station, a quick fade, then
the ride: the train holds the middle of the frame while one lap of the island slides past,
distant scenery slower than near (parallax), and the far side of the lap drifts the other
way behind the islands. On the way round the train eases into each station, waits a few
seconds while something happens there, and pulls out again. Another fade, and back to the
overview. With reduced motion turned on, nothing moves and the overview stays put.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from .context import W
from .ride import BG_DEPTH, FAR_K, PAN, STOPS

LOOP_S = 96  # seconds for one full loop

# Moments in the loop, as percentages.
FADE_IN = (12.0, 13.5, 15.0)  # start dimming, fully dark (cut to the ride), clear again
RIDE = (15.0, 90.0)  # the world slides past between these
FADE_OUT = (90.0, 92.0, 94.0)  # dim, fully dark (cut back to the overview), clear
DWELL_S = 4.0  # how long the train waits at each station


@dataclass(frozen=True)
class Stop:
    """One station on the ride: how far the world has slid when the train is there, and
    when in the loop (percent) the train arrives and leaves."""

    key: str
    offset: float
    arrive: float
    depart: float


def schedule() -> list[Stop]:
    """When the train reaches each station. Travel time is shared out by distance, so the
    train keeps the same average speed on every leg."""
    a, b = RIDE
    dwell = DWELL_S / LOOP_S * 100
    offsets = [x - W / 2 for _, x in STOPS]
    marks = [0.0, *offsets, float(PAN)]
    travel = (b - a) - dwell * len(STOPS)
    t, out = a, []
    for k, (key, _) in enumerate(STOPS):
        t += travel * (marks[k + 1] - marks[k]) / PAN
        out.append(Stop(key, offsets[k], t, t + dwell))
        t += dwell
    return out


def pct(p: float) -> str:
    """A keyframe percentage, short but exact enough for a 96-second loop."""
    return f"{p:.3f}".rstrip("0").rstrip(".") + "%"


def keyframes(name: str, stops: list[tuple[float, str]]) -> str:
    body = "".join(f"{pct(p)}{{{v}}}" for p, v in stops)
    return f"@keyframes {name}{{{body}}}"


def _show(name: str, during_ride: bool) -> str:
    on, off = ("opacity:1", "opacity:0") if during_ride else ("opacity:0", "opacity:1")
    return keyframes(name, [(0, off), (FADE_IN[1] - 0.05, off), (FADE_IN[1], on),
                            (FADE_OUT[1] - 0.05, on), (FADE_OUT[1], off), (100, off)])


def _legs(at: Callable[[float], str]) -> list[tuple[float, str]]:
    """Keyframes that ease from station to station and hold still at each one. `at(offset)`
    turns how far the world has slid into this layer's CSS."""
    ease = ";animation-timing-function:ease-in-out"
    frames = [(RIDE[0], at(0) + ease)]
    for s in schedule():
        frames += [(s.arrive, at(s.offset)), (s.depart, at(s.offset) + ease)]
    return [*frames, (RIDE[1], at(PAN))]


def _pan(name: str, distance: float) -> str:
    def at(offset: float) -> str:
        return f"transform:translateX({-distance * offset / PAN:.0f}px)"

    return keyframes(name, [
        (0, at(0)), *_legs(at),
        (FADE_OUT[1] - 0.05, at(PAN)), (FADE_OUT[1], at(0)), (100, at(0)),
    ])


def _trail() -> str:
    """The light streak behind the last car shows only while the train is moving."""
    frames = [(0, "opacity:1")]
    for s in schedule():
        frames += [(s.arrive - 0.6, "opacity:1"), (s.arrive, "opacity:0"),
                   (s.depart, "opacity:0"), (s.depart + 0.8, "opacity:1")]
    return keyframes("trail", [*frames, (100, "opacity:1")])


STOP_NAMES = {"stadium": "STADIUM", "wild": "THE WILDWOOD", "farm": "SERVER FARM"}


def board() -> list[tuple[str, list[tuple[float, float]]]]:
    """The departure board in the bottom bar: each message and the parts of the loop
    (percent from, to) when it shows, so it always names where the train is heading."""
    town = "TOWN STATION"
    out = [("THE CLOUDLINER › ALL ABOARD", [(0, FADE_IN[1]), (FADE_OUT[1], 100)]),
           (f"DEPARTING › {town}", [(FADE_IN[1], RIDE[0] + 1)])]
    t = RIDE[0] + 1
    for s in schedule():
        name = STOP_NAMES[s.key]
        out += [(f"NEXT STOP › {name}", [(t, s.arrive)]),
                (f"NOW AT › {name}", [(s.arrive, s.depart)])]
        t = s.depart
    out.append((f"NEXT STOP › {town}", [(t, FADE_OUT[1])]))
    return out


def _board_css() -> str:
    """Each message switches on and off at once (step-end holds a keyframe's value until
    the next one), so exactly one shows at any moment."""
    out = []
    for k, (_, spans) in enumerate(board()):
        frames = {0.0: "opacity:0"}
        for _, b in spans:
            frames[b] = "opacity:0"
        for a, _ in spans:
            frames[a] = "opacity:1"
        frames[100.0] = frames[0.0]
        out.append(keyframes(f"b{k}", sorted(frames.items())))
        # Without motion only the first message (the overview's) shows.
        hide = "opacity:0;" if k else ""
        out.append(f".b{k}{{{hide}animation:b{k} {LOOP_S}s step-end infinite}}")
    return "".join(out)


def css(timeline: tuple[float, float] | None = None) -> str:
    """CSS for the overview and ride layers, the fade and the timeline's progress marker."""
    out = [
        _show("over", during_ride=False), _show("ride", during_ride=True),
        _pan("ride-world", PAN), _pan("ride-bg", PAN * BG_DEPTH), _pan("ride-far", -PAN * FAR_K),
        _trail(),
        f".over{{animation:over {LOOP_S}s linear infinite}}",
        f".ride{{opacity:0;animation:ride {LOOP_S}s linear infinite}}",
        f".ride-world{{animation:ride-world {LOOP_S}s infinite}}",
        f".ride-bg{{animation:ride-bg {LOOP_S}s infinite}}",
        f".ride-far{{animation:ride-far {LOOP_S}s infinite}}",
        f".trail{{animation:trail {LOOP_S}s linear infinite}}",
        keyframes("fade", [
            (0, "opacity:0"), (FADE_IN[0], "opacity:0"), (FADE_IN[1], "opacity:1"),
            (FADE_IN[2], "opacity:0"), (FADE_OUT[0], "opacity:0"), (FADE_OUT[1], "opacity:1"),
            (FADE_OUT[2], "opacity:0"), (100, "opacity:0"),
        ]),
        f".fade{{opacity:0;animation:fade {LOOP_S}s linear infinite}}",
        _board_css(),
    ]
    if timeline:
        x0, x1 = timeline

        def at(offset: float) -> str:
            return f"transform:translateX({x0 + (x1 - x0) * offset / PAN:.0f}px)"

        out.append(keyframes("marker", [(0, at(0)), *_legs(at), (100, at(PAN))]))
        out.append(f".marker{{animation:marker {LOOP_S}s infinite}}")
    return "".join(out)
