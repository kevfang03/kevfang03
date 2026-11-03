"""Live Philadelphia weather: reading Open-Meteo and drawing the sky it describes."""

from __future__ import annotations

from datetime import datetime

import pytest

from sky_islands import forecast
from sky_islands.clock import PHILLY
from sky_islands.model import DEMO_STATS, demo_world, world_at
from sky_islands.render import render

SAMPLE = {
    "current": {"time": "2026-11-03T15:30", "temperature_2m": 69.5, "weather_code": 63},
    "daily": {"time": ["2026-11-03"], "sunrise": ["2026-11-03T06:31"],
              "sunset": ["2026-11-03T16:55"]},
}


@pytest.mark.parametrize(("code", "kind"), [(0, "clear"), (1, "clear"), (3, "cloudy"),
                                            (45, "fog"), (53, "rain"), (81, "rain"),
                                            (73, "snow"), (86, "snow"), (95, "storm")])
def test_weather_codes_fold_into_drawable_skies(code, kind):
    assert forecast.kind_for(code) == kind


def test_parse_reads_sky_temperature_and_real_sun_times():
    f = forecast.parse(SAMPLE)
    assert (f.kind, f.temp_f) == ("rain", 70)
    assert f.sunset == datetime(2026, 11, 3, 16, 55, tzinfo=PHILLY)


def test_a_failing_feed_means_a_clear_sky(capsys):
    def broken(url):
        raise TimeoutError

    assert forecast.fetch_forecast(broken) is None
    assert "clear sky" in capsys.readouterr().out


def test_world_uses_the_forecast_sun_times_and_weather():
    f = forecast.parse(SAMPLE)
    # 16:30 is golden hour with the real 16:55 sunset.
    w = world_at(DEMO_STATS, datetime(2026, 11, 3, 16, 30, tzinfo=PHILLY), f)
    assert (w.weather, w.temp_f, w.phase) == ("rain", 70, "golden")
    clear = world_at(DEMO_STATS, datetime(2026, 11, 3, 16, 30, tzinfo=PHILLY))
    assert (clear.weather, clear.temp_f) == ("clear", None)


@pytest.mark.parametrize(("kind", "marker"), [("rain", 'class="rain1"'),
                                              ("storm", 'class="flash"'),
                                              ("snow", 'class="snow1"'),
                                              ("fog", "drift")])
def test_each_weather_is_drawn(kind, marker):
    svg = render(demo_world("dusk", kind))
    assert marker in svg
    assert len(svg.encode()) < 600 * 1024


def test_clear_sky_draws_no_weather():
    svg = render(demo_world("dusk"))
    assert 'class="rain1"' not in svg and 'class="snow1"' not in svg
