"""The train stops at each station on the ride, and something happens while it waits."""

from __future__ import annotations

import re
from dataclasses import replace

import pytest

from sky_islands import camera, wonders
from sky_islands.model import demo_world
from sky_islands.render import render
from sky_islands.ride import PAN
from sky_islands.views import grown


@pytest.fixture(scope="module")
def low() -> str:
    """A level 2 account: the stadium, Starport and Shrine are still locked."""
    w = demo_world("dusk")
    return render(replace(w, stats=replace(w.stats, contributions_total=92, streak_days=3)))


@pytest.fixture(scope="module")
def high() -> str:
    w = demo_world("night")
    return render(replace(w, stats=grown(w.stats)))


def test_stops_are_in_order_inside_the_ride_and_last_the_dwell():
    stops = camera.schedule()
    assert [s.key for s in stops] == ["stadium", "wild", "farm"]
    dwell = camera.DWELL_S / camera.LOOP_S * 100
    last = camera.RIDE[0]
    for s in stops:
        assert last < s.arrive < s.depart < camera.RIDE[1]
        assert s.depart - s.arrive == pytest.approx(dwell)
        last = s.depart
    assert 0 < stops[0].offset < stops[1].offset < stops[2].offset < PAN


def test_the_world_holds_still_while_the_train_waits():
    css = camera.css()
    frames = re.search(r"@keyframes ride-world\{(.*?)\}\}", css).group(1)
    for s in camera.schedule():
        held = f"translateX({-s.offset:.0f}px)"
        assert frames.count(held) == 2, s.key  # the same place on arrival and on leaving
    assert f"translateX({-PAN}px)" in frames


def test_locked_stadium_shows_how_far_to_go(low):
    assert "CONTRIBUTIONS TO GO" in low
    assert 'class="glint"' in low
    assert 'class="fw0"' not in low
    assert ".ride .launch" not in low  # no Starport yet, so nothing lifts off
    assert "WILD SIDE · STREAK 3 DAYS" in low


def test_open_stations_have_their_moments(high):
    assert 'class="fw0"' in high and "@keyframes fw0" in high
    assert ".ride .launch{animation:liftoff" in high
    assert 'class="gust0"' in high
    assert "CONTRIBUTIONS THIS YEAR" in high


def test_drone_drops_a_crate_into_the_wagon(low):
    assert 'class="dlv"' in low and 'class="crate"' in low
    # The crate is drawn before the train so it falls in behind the wagon's side.
    ride = low[low.index('class="ride"'):]
    assert ride.index('class="crate"') < ride.index('class="trail"') < ride.index('class="dlv"')


def test_the_dragon_crosses_while_the_train_waits_at_the_wild_side():
    a, b = wonders.dragon_window()
    wild = next(s for s in camera.schedule() if s.key == "wild")
    assert a * 100 < wild.arrive and wild.depart < b * 100


def test_town_station_master_waves(low):
    assert 'class="wave"' in low and "@keyframes wave" in low
