"""The camera: a looping ride around the island, written as plain CSS keyframes.

One loop: the whole archipelago with the train waiting at the station, a quick fade, then
the ride: the train holds the middle of the frame while one lap of the island slides past,
distant scenery slower than near (parallax), and the far side of the lap drifts the other
way behind the islands. Another fade, and back to the overview.
With reduced motion turned on, nothing moves and the overview stays put.
"""

from __future__ import annotations

from .ride import BG_DEPTH, FAR_K, PAN

LOOP_S = 84  # seconds for one full loop

# Moments in the loop, as percentages.
FADE_IN = (12.0, 13.5, 15.0)  # start dimming, fully dark (cut to the ride), clear again
RIDE = (15.0, 90.0)  # the world slides past between these
FADE_OUT = (90.0, 92.0, 94.0)  # dim, fully dark (cut back to the overview), clear


def _keyframes(name: str, stops: list[tuple[float, str]]) -> str:
    body = "".join(f"{p:g}%{{{v}}}" for p, v in stops)
    return f"@keyframes {name}{{{body}}}"


def _show(name: str, during_ride: bool) -> str:
    on, off = ("opacity:1", "opacity:0") if during_ride else ("opacity:0", "opacity:1")
    return _keyframes(name, [(0, off), (FADE_IN[1] - 0.05, off), (FADE_IN[1], on),
                             (FADE_OUT[1] - 0.05, on), (FADE_OUT[1], off), (100, off)])


def _pan(name: str, distance: float) -> str:
    a, b = RIDE
    return _keyframes(name, [
        (0, "transform:translateX(0px)"),
        (a, "transform:translateX(0px);animation-timing-function:ease-in-out"),
        (b, f"transform:translateX({-distance:.0f}px)"),
        (FADE_OUT[1] - 0.05, f"transform:translateX({-distance:.0f}px)"),
        (FADE_OUT[1], "transform:translateX(0px)"), (100, "transform:translateX(0px)"),
    ])


def css(timeline: tuple[float, float] | None = None) -> str:
    """CSS for the overview and ride layers, the fade and the timeline's progress marker."""
    out = [
        _show("over", during_ride=False), _show("ride", during_ride=True),
        _pan("ride-world", PAN), _pan("ride-bg", PAN * BG_DEPTH), _pan("ride-far", -PAN * FAR_K),
        f".over{{animation:over {LOOP_S}s linear infinite}}",
        f".ride{{opacity:0;animation:ride {LOOP_S}s linear infinite}}",
        f".ride-world{{animation:ride-world {LOOP_S}s infinite}}",
        f".ride-bg{{animation:ride-bg {LOOP_S}s infinite}}",
        f".ride-far{{animation:ride-far {LOOP_S}s infinite}}",
        _keyframes("fade", [
            (0, "opacity:0"), (FADE_IN[0], "opacity:0"), (FADE_IN[1], "opacity:1"),
            (FADE_IN[2], "opacity:0"), (FADE_OUT[0], "opacity:0"), (FADE_OUT[1], "opacity:1"),
            (FADE_OUT[2], "opacity:0"), (100, "opacity:0"),
        ]),
        f".fade{{opacity:0;animation:fade {LOOP_S}s linear infinite}}",
    ]
    if timeline:
        x0, x1 = timeline
        a, b = RIDE
        out.append(_keyframes("marker", [
            (0, f"transform:translateX({x0:.0f}px)"),
            (a, f"transform:translateX({x0:.0f}px);animation-timing-function:ease-in-out"),
            (b, f"transform:translateX({x1:.0f}px)"), (100, f"transform:translateX({x1:.0f}px)"),
        ]))
        out.append(f".marker{{animation:marker {LOOP_S}s infinite}}")
    return "".join(out)
