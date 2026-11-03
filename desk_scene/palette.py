"""Colour helpers and the fixed palettes the scene is drawn with."""

from __future__ import annotations

PHASES = ("dawn", "day", "dusk", "night")
WEATHERS = ("clear", "cloudy", "rain", "snow")


def _rgb(c: str) -> tuple[int, int, int]:
    c = c.lstrip("#")
    return int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16)


def _hex(r: float, g: float, b: float) -> str:
    return "#" + "".join(f"{max(0, min(255, round(v))):02x}" for v in (r, g, b))


def mix(a: str, b: str, t: float) -> str:
    """Blend colour a toward colour b by t (0 = a, 1 = b)."""
    ra, rb = _rgb(a), _rgb(b)
    return _hex(*(x + (y - x) * t for x, y in zip(ra, rb, strict=True)))


def shade(c: str, f: float) -> str:
    """Scale a colour's brightness by f."""
    return _hex(*(v * f for v in _rgb(c)))


# Light outside the window for each time of day. Sky lists run top to bottom.
OUTSIDE: dict[str, dict] = {
    "day": {
        "sky": ["#3f7fcf", "#5a95da", "#78aae3", "#98c0ec", "#bcd7f3"],
        "far": "#a7b7cb", "base": "#7b8ca5", "shade": "#63738b", "edge": "#c9d8e8",
        "glass": "#b6cbe0", "glass2": "#94adc6", "crown": "#c5ced8",
        "stone": "#d9c9a5", "stone_shade": "#b5a37f", "bronze": "#4a3f2e", "clock": "#efe6cc",
        "lit": [], "lit_ratio": 0.0,
        "water": ["#5a8fc0", "#4a7fb0", "#3d6d9c"],
        "cloud": ("#f4f7fb", "#d5dde8"),
    },
    "dawn": {
        "sky": ["#2e3166", "#5d4a80", "#a8678a", "#e3928a", "#f8c497"],
        "far": "#7a6a90", "base": "#5d5078", "shade": "#4b4064", "edge": "#c4a3b8",
        "glass": "#9a8fba", "glass2": "#7d72a0", "crown": "#d8b0b8",
        "stone": "#c4a088", "stone_shade": "#9f8070", "bronze": "#5a4636", "clock": "#f6e2c0",
        "lit": ["#ffd679"], "lit_ratio": 0.12,
        "water": ["#b88a8e", "#93708a", "#6d5270"],
        "cloud": ("#f2c0b0", "#c9909a"),
    },
    "dusk": {
        "sky": ["#1a1840", "#33285e", "#6a3570", "#b85068", "#ee8457"],
        "far": "#3a2d5a", "base": "#2c2550", "shade": "#211c40", "edge": "#7a5a8c",
        "glass": "#4c4480", "glass2": "#3d366d", "crown": "#ffe6c0",
        "stone": "#9a8078", "stone_shade": "#76606a", "bronze": "#5e4a40", "clock": "#fff1b0",
        "lit": ["#ffd679", "#ffe9a8"], "lit_ratio": 0.35,
        "water": ["#5a4278", "#433262", "#2c2348"],
        "cloud": ("#8a5a86", "#5e3f6e"),
    },
    "night": {
        "sky": ["#050a1a", "#08112a", "#0c1736", "#111f44", "#182a55"],
        "far": "#101a34", "base": "#141c36", "shade": "#0e1429", "edge": "#2a3a62",
        "glass": "#1c2848", "glass2": "#18223f", "crown": "#d6e6ff",
        # City Hall is floodlit at night, so its stone stays warm and bright.
        "stone": "#a8987a", "stone_shade": "#857759", "bronze": "#7a6648", "clock": "#fff1b0",
        "lit": ["#ffd679", "#ffe9a8", "#f2c45a"], "lit_ratio": 0.5,
        "water": ["#132244", "#0d1a36", "#081126"],
        "cloud": ("#26304d", "#1b2340"),
    },
}

# (tint colour, amount, brightness) applied to daytime colours for other phases.
_OUT_TINT = {
    "day": None,
    "dawn": ("#c07a8a", 0.3, 0.85),
    "dusk": ("#3e2f6b", 0.5, 0.62),
    "night": ("#0a1430", 0.68, 0.5),
}
# Indoors stays brighter than outdoors because the lamp and monitor are on.
_ROOM_TINT = {
    "day": None,
    "dawn": ("#c98a8a", 0.16, 0.9),
    "dusk": ("#4a3a6b", 0.28, 0.8),
    "night": ("#18203d", 0.42, 0.66),
}


def _tint(c: str, spec: tuple[str, float, float] | None) -> str:
    if spec is None:
        return c
    tint, amount, bright = spec
    return shade(mix(c, tint, amount), bright)


def outside(c: str, phase: str) -> str:
    """A daytime colour as it looks outside at the given time of day."""
    return _tint(c, _OUT_TINT[phase])


def room(c: str, phase: str) -> str:
    """A daytime colour as it looks inside the room at the given time of day."""
    return _tint(c, _ROOM_TINT[phase])


TEAMS: dict[str, dict[str, str]] = {
    "eagles": {
        "label": "EAGLES", "primary": "#004c54", "secondary": "#a5acaf",
        "light": "#2fd08a", "ball": "football", "cheer": "GO BIRDS",
    },
    "phillies": {
        "label": "PHILLIES", "primary": "#e81828", "secondary": "#002d72",
        "light": "#ff4a55", "ball": "baseball", "cheer": "GO PHILS",
    },
    "sixers": {
        "label": "SIXERS", "primary": "#006bb6", "secondary": "#ed174c",
        "light": "#3a9bff", "ball": "basketball", "cheer": "GO SIXERS",
    },
}

TREES = {
    "spring": ["#6fae4f", "#8cc46a", "#f2b8c8"],
    "summer": ["#3f7d3a", "#56984a", "#2f6230"],
    "fall": ["#d9822b", "#b8452a", "#e8b23a"],
    "winter": [],
}
GRASS = {"spring": "#62a046", "summer": "#4f8a3a", "fall": "#7a8a3a", "winter": "#7d7a5a"}

HOLIDAY_LIGHTS = ["#ff6b6b", "#ffd36b", "#6bd8ff", "#8aff8a"]
WARM_LIGHT = "#fff2c4"
