"""Background creatures and the fixes that keep models on the ground."""

from __future__ import annotations

import re

import pytest

from sky_islands import creatures
from sky_islands.island import Shape
from sky_islands.model import demo_world
from sky_islands.render import render
from sky_islands.wonders import DESIGN_W, _foot


@pytest.fixture(scope="module")
def night() -> str:
    return render(demo_world("night"))


def test_whales_jellies_and_airship_are_drawn(night):
    assert 'class="glide"' in night
    assert night.count('class="rise"') >= len(creatures.JELLIES)
    assert 'class="fluke"' in night
    assert "@keyframes glide" in night


def test_whale_glide_only_jumps_while_the_ride_hides_it():
    """Between 92% and 13.5% (through the wrap) the overview shows, so the glide must move
    smoothly there: the 0% and 100% frames match and sit on the line between start and end."""
    css = creatures.css()
    frames = dict(re.findall(r"([\d.]+)%\{transform:translate\(([-\d.]+)px", css))
    assert frames["0"] == frames["100"]
    sx, ex = 0, creatures.WHALE_TO[0] - creatures.WHALE_FROM[0]
    assert sx < float(frames["0"]) < ex
    assert float(frames["13.5"]) == ex and float(frames["92"]) == sx


def test_glowing_spots_only_at_night():
    day = render(demo_world("day"))
    assert "#9ff0ff" not in day.split("ride-bg")[0]


@pytest.mark.parametrize("w", [90, 100, 150])
def test_foot_matches_the_island_ground(w):
    """Things near a wonder's edge reach down exactly as far as the island's top has dropped."""
    s = Shape(cx=0, top=0, w=w, depth=80)
    scale = w / DESIGN_W
    for x in (-70, -40, 0, 30, 62):
        assert _foot(x, w) * scale == pytest.approx(s.ground(x * scale) - s.top)
