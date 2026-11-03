import xml.etree.ElementTree as ET
from dataclasses import replace
from datetime import datetime, timedelta

import pytest

from desk_scene.clock import PHILLY, fireworks_day, moon_phase, phase_for, season
from desk_scene.font import glyph, text_width
from desk_scene.growth import CONTRIBUTIONS_PER_FLOOR, LOTS, TOWER_FLOORS, tower_progress
from desk_scene.model import demo_state
from desk_scene.palette import PHASES, TEAMS, WEATHERS
from desk_scene.render import render

# README images over a few MB load slowly; keep every variant well under that.
MAX_BYTES = 1_000_000


@pytest.mark.parametrize("phase", PHASES)
@pytest.mark.parametrize("weather", WEATHERS)
def test_every_phase_and_weather_renders_valid_svg(phase, weather):
    svg = render(demo_state(phase, weather))
    root = ET.fromstring(svg)
    assert root.tag.endswith("svg")
    assert len(svg.encode()) < MAX_BYTES


@pytest.mark.parametrize("teams", [(t,) for t in TEAMS] + [tuple(TEAMS)])
def test_game_days_render_and_show_in_status(teams):
    svg = render(demo_state("night", "clear", teams))
    ET.fromstring(svg)


def test_same_day_draws_the_same_scene():
    assert render(demo_state("night")) == render(demo_state("night"))


def test_holiday_and_fireworks_days_render():
    ET.fromstring(render(demo_state("night", "snow", day=(2026, 12, 18))))
    svg = render(demo_state("night", day=(2026, 7, 4)))
    assert 'class="fw"' in svg


def test_moon_phase_matches_a_known_full_moon():
    full = datetime(2000, 1, 21, 4, 40, tzinfo=PHILLY)
    assert abs(moon_phase(full) - 0.5) < 0.03


def test_phase_boundaries():
    rise = datetime(2026, 11, 2, 6, 30, tzinfo=PHILLY)
    sets = datetime(2026, 11, 2, 17, 0, tzinfo=PHILLY)
    assert phase_for(rise - timedelta(minutes=50), rise, sets) == "night"
    assert phase_for(rise, rise, sets) == "dawn"
    assert phase_for(rise + timedelta(hours=3), rise, sets) == "day"
    assert phase_for(sets, rise, sets) == "dusk"
    assert phase_for(sets + timedelta(hours=1), rise, sets) == "night"


def test_seasons_and_fireworks():
    assert season(11) == "fall"
    assert season(1) == "winter"
    assert fireworks_day(datetime(2026, 7, 4).date())
    assert not fireworks_day(datetime(2026, 7, 5).date())


def test_towers_grow_with_contributions():
    per_tower = TOWER_FLOORS * CONTRIBUTIONS_PER_FLOOR
    assert tower_progress(0) == (0, 0)
    assert tower_progress(CONTRIBUTIONS_PER_FLOOR * 5) == (0, 5)
    assert tower_progress(per_tower + CONTRIBUTIONS_PER_FLOOR) == (1, 1)
    assert tower_progress(per_tower * 99) == (len(LOTS), 0)


@pytest.mark.parametrize("total", [0, 50, 400, 10_000])
def test_every_stage_of_the_skyline_renders(total):
    base = demo_state("night")
    stats = replace(base.stats, contributions_total=total)
    ET.fromstring(render(replace(base, stats=stats)))


def test_font_falls_back_and_measures():
    assert glyph("~") == glyph("?")
    assert glyph("a") == glyph("A")
    assert text_width("OK") == 7
    assert text_width("") == 0
