"""Colours for each time of day, and helpers to blend them."""

from __future__ import annotations


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


# sky: top to horizon. haze: colour of distance. rim: light catching edges.
# light: (tint, amount, brightness) applied to daytime colours of things on the islands.
PHASE = {
    "dawn": {
        "sky": ["#232c62", "#4e4f8c", "#9c6f9c", "#e79a94", "#ffd2a4"],
        "sun": (200, 410, "#ffe2b0"), "haze": "#b896b8", "rim": "#ffc9a0",
        "rock": ("#6a5a8a", "#2c2446"), "grass": "#4f6e5e", "cloud": ("#8a6a92", "#ffd0b0"),
        "light": ("#c08ab0", 0.25, 0.85), "lit": 0.35, "stars": 30, "lamps": True,
    },
    "day": {
        "sky": ["#3f78cc", "#5f93dc", "#8fb4e8", "#bcd5f2", "#e6f0fa"],
        "sun": (840, 104, "#fff8e0"), "haze": "#bccde6", "rim": "#ffffff",
        "rock": ("#8c7c9c", "#4a3e62"), "grass": "#5c9e58", "cloud": ("#dfe7f3", "#ffffff"),
        "light": None, "lit": 0.0, "stars": 0, "lamps": False,
    },
    "golden": {
        "sky": ["#3c4a96", "#7466a6", "#c8848e", "#f2ac7a", "#ffd79c"],
        "sun": (700, 400, "#ffdc96"), "haze": "#e2a48e", "rim": "#ffc070",
        "rock": ("#7a5a7e", "#33244a"), "grass": "#5a7a4e", "cloud": ("#b87a86", "#ffd2a0"),
        "light": ("#ff9a60", 0.18, 0.95), "lit": 0.2, "stars": 0, "lamps": False,
    },
    "dusk": {
        "sky": ["#121640", "#2a2868", "#5a3a7c", "#ae527c", "#ec7c6e", "#f8ae72"],
        "sun": (520, 440, "#ffb27a"), "haze": "#8a5a8a", "rim": "#ffb070",
        "rock": ("#4e3570", "#1a1230"), "grass": "#2e4a52", "cloud": ("#7a4672", "#f7b088"),
        "light": ("#3e2f6b", 0.42, 0.72), "lit": 0.72, "stars": 110, "lamps": True,
    },
    "night": {
        "sky": ["#05071c", "#0c1134", "#171a48", "#262458", "#3a2e64"],
        "sun": None, "haze": "#3a3468", "rim": "#9fb4ec",
        "rock": ("#2e2650", "#0c0a1c"), "grass": "#1f3a3a", "cloud": ("#221c44", "#5a5490"),
        "light": ("#0a1430", 0.58, 0.55), "lit": 0.78, "stars": 170, "lamps": True,
    },
}


def lit_by(c: str, phase: str) -> str:
    """A daytime colour as it looks at the given time of day."""
    spec = PHASE[phase]["light"]
    if spec is None:
        return c
    tint, amount, bright = spec
    return shade(mix(c, tint, amount), bright)


WINDOW = "#ffcf7a"
LIGHTS = ("#ffd27a", "#ff9fb2", "#9fd8ff", "#b6ff9f")

TEAMS: dict[str, dict[str, str]] = {
    "eagles": {"label": "EAGLES", "primary": "#004c54", "secondary": "#a5acaf", "light": "#2fd08a"},
    "phillies": {"label": "PHILLIES", "primary": "#e81828", "secondary": "#002d72",
                 "light": "#ff4a55"},
    "sixers": {"label": "SIXERS", "primary": "#006bb6", "secondary": "#ed174c", "light": "#3a9bff"},
}
