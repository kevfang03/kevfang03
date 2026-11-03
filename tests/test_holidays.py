"""Holidays through the year and what each season adds."""

from __future__ import annotations

import re
from dataclasses import replace
from datetime import date

import pytest

from sky_islands import events, holidays
from sky_islands.model import demo_world
from sky_islands.render import render
from sky_islands.views import grown


def _keys(y: int, m: int, d: int) -> list[str]:
    return [h.key for h in holidays.on(date(y, m, d))]


def test_moving_dates():
    assert holidays.easter(2026) == date(2026, 4, 5)
    assert holidays.easter(2027) == date(2027, 3, 28)
    assert holidays.easter(2028) == date(2028, 4, 16)
    assert holidays.thanksgiving(2026) == date(2026, 11, 26)
    assert holidays.thanksgiving(2027) == date(2027, 11, 25)


@pytest.mark.parametrize(("day", "key"), [
    ((2026, 10, 27), "halloween"), ((2027, 2, 12), "valentine"), ((2026, 7, 2), "july4"),
    ((2027, 3, 26), "easter"), ((2027, 3, 29), "easter"), ((2026, 11, 28), "thanksgiving"),
    ((2027, 2, 10), "lunar"), ((2026, 12, 22), "christmas"), ((2026, 12, 5), "lights"),
    ((2027, 1, 1), "lights"), ((2028, 12, 15), "hanukkah"), ((2027, 3, 16), "stpatrick"),
])
def test_each_holiday_lasts_as_long_as_it_is_celebrated(day, key):
    assert key in _keys(*day)


def test_ordinary_days_have_no_holiday():
    assert _keys(2026, 11, 3) == [] and _keys(2027, 5, 20) == []


def test_header_names_the_day_itself_and_the_rest_of_the_week():
    assert holidays.on(date(2026, 10, 31))[0].headline == "HAPPY HALLOWEEN"
    assert "WEEK" in holidays.on(date(2026, 10, 27))[0].headline
    assert holidays.on(date(2026, 12, 25))[0].headline == "MERRY CHRISTMAS"
    assert holidays.on(date(2028, 12, 15))[0].headline == "HANUKKAH · NIGHT 4"


def test_fireworks_only_on_the_night():
    assert holidays.fireworks(date(2026, 7, 4), "night")
    assert not holidays.fireworks(date(2026, 7, 2), "night")
    assert not holidays.fireworks(date(2026, 7, 4), "day")
    assert holidays.fireworks(date(2027, 1, 1), "day")  # New Year's Day, all day
    e = events.roll(demo_world("night", day=(2026, 7, 4)))
    assert e.fireworks and e.headline().startswith("FOURTH OF JULY")


def test_christmas_brings_the_hat_the_sleigh_and_presents():
    svg = render(demo_world("night", day=(2026, 12, 24)))
    assert 'fill="#d8342a"' in svg  # the dragon's Santa hat (it flies for Christmas)
    assert "#2f8a4a" in svg  # a present
    assert svg.count("#ff4a3a") >= 1  # the lead reindeer's nose


def test_lunar_new_year_brings_the_golden_dragon_and_lanterns():
    svg = render(demo_world("night", day=(2027, 2, 6)))
    assert "#f2b632" in svg and "#fff6dc" in svg  # gold body and the pearl
    # Swinging lanterns sit in their own translated group, so they swing about the hook.
    assert re.search(r'<g transform="translate\([\d.]+ [\d.]+\)"><use href="#lantern-night" '
                     r'class="swing"/></g>', svg)


def test_halloween_week_decorates_the_map():
    svg = render(demo_world("night", day=(2026, 10, 28)))
    assert 'class="bats"' in svg and "#jack-night" in svg and "#f4f2ff" in svg


@pytest.mark.parametrize(("day", "marker"), [
    ((2027, 4, 20), 'class="drop"'), ((2026, 10, 10), 'class="drop"'),
    ((2027, 7, 10), 'class="flap"'), ((2027, 1, 20), 'stroke-width="5"'),
])
def test_each_season_adds_something(day, marker):
    phase = "day"
    assert marker in render(demo_world(phase, day=day))


@pytest.mark.parametrize(("phase", "day"), [("night", (2027, 2, 6)), ("night", (2026, 12, 24)),
                                            ("dusk", (2028, 12, 15)), ("night", (2026, 10, 31))])
def test_a_fully_grown_world_stays_under_the_size_limit_on_holidays(phase, day):
    w = demo_world(phase, "storm", day=day)
    assert len(render(replace(w, stats=grown(w.stats))).encode()) < 600 * 1024


def test_sunset_backdrop_fades_out_so_no_edge_crosses_the_sky():
    svg = render(demo_world("golden"))
    west = re.search(r'<linearGradient id="westsky".*?</linearGradient>', svg).group(0)
    assert west.endswith('stop-opacity="0"/></linearGradient>')


def test_seasonal_fallers_are_few_and_never_fill_the_frame():
    svg = render(demo_world("day", day=(2026, 10, 10)))
    assert svg.count('class="drop"') == 9
    assert "petals1" not in svg
