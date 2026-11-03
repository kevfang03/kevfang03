import xml.etree.ElementTree as ET
from dataclasses import replace

import pytest

from desk_scene.model import demo_state
from desk_scene.palette import PHASES, TEAMS, WEATHERS
from desk_scene.vector.render import render

# README images over a few MB load slowly; keep every variant well under that.
MAX_BYTES = 600_000


@pytest.mark.parametrize("phase", PHASES)
@pytest.mark.parametrize("weather", WEATHERS)
def test_every_phase_and_weather_renders_valid_svg(phase, weather):
    svg = render(demo_state(phase, weather))
    root = ET.fromstring(svg)
    assert root.tag.endswith("svg")
    assert len(svg.encode()) < MAX_BYTES


@pytest.mark.parametrize("teams", [(t,) for t in TEAMS] + [tuple(TEAMS)])
def test_game_days_show_a_chip_per_team(teams):
    svg = render(demo_state("night", "clear", teams))
    ET.fromstring(svg)
    for t in teams:
        assert TEAMS[t]["label"] in svg


def test_eagles_game_shows_opponent_and_time():
    svg = render(demo_state("day", "clear", ("eagles",)))
    assert "EAGLES vs DAL · 8:20 PM" in svg


def test_labels_explain_the_scene():
    svg = render(demo_state("night"))
    for text in ("BOATHOUSE ROW", "TOWER 1 · BUILT", "BUILDING ops-suite", "1 floor = 8"):
        assert text in svg


def test_same_day_draws_the_same_scene():
    assert render(demo_state("night")) == render(demo_state("night"))


def test_holiday_and_fireworks_days_render():
    ET.fromstring(render(demo_state("night", "snow", day=(2026, 12, 18))))
    assert 'class="fw"' in render(demo_state("night", day=(2026, 7, 4)))


@pytest.mark.parametrize("total", [0, 50, 400, 10_000])
def test_every_stage_of_the_skyline_renders(total):
    base = demo_state("night")
    stats = replace(base.stats, contributions_total=total)
    svg = render(replace(base, stats=stats))
    ET.fromstring(svg)
    if total >= 10_000:
        assert "SKYLINE COMPLETE" in svg


def test_motion_can_be_turned_off():
    assert "prefers-reduced-motion" in render(demo_state("night"))
