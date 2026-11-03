"""Rare and dated sky events: repeatable per hour, and only when they make sense."""

from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timedelta

from sky_islands import events
from sky_islands.clock import PHILLY
from sky_islands.model import demo_world
from sky_islands.render import render


def _at(phase: str, day: tuple[int, int, int], weather: str = "clear", hour: int | None = None):
    w = demo_world(phase, weather, day=day)
    return replace(w, when=w.when.replace(hour=hour)) if hour is not None else w


def test_each_hour_rolls_the_same_every_time():
    w = _at("night", (2026, 11, 2))
    assert events.roll(w) == events.roll(w)


def test_golden_dragon_is_rare_but_happens():
    start = datetime(2026, 1, 1, tzinfo=PHILLY)
    w = demo_world("day")
    hits = sum(events.roll(replace(w, when=start + timedelta(hours=h))).shiny
               for h in range(24 * 365))
    assert 15 < hits < 90  # about 1 in 200 of 8,760 hours


def test_aurora_only_on_clear_winter_nights():
    start = datetime(2027, 1, 1, 23, tzinfo=PHILLY)
    winter = [events.roll(replace(_at("night", (2027, 1, 1)), when=start + timedelta(days=d)))
              for d in range(60)]
    assert any(e.aurora for e in winter)
    summer = [events.roll(replace(_at("night", (2026, 7, 1)),
                                  when=datetime(2026, 7, 1, 23, tzinfo=PHILLY) + timedelta(days=d)))
              for d in range(60)]
    assert not any(e.aurora for e in summer)
    assert not events.roll(_at("day", (2027, 1, 5))).aurora


def test_meteor_showers_on_their_peak_nights_with_a_clear_sky():
    assert events.roll(_at("night", (2026, 8, 12))).meteors == "PERSEIDS"
    assert events.roll(_at("night", (2026, 12, 14))).meteors == "GEMINIDS"
    assert events.roll(_at("night", (2026, 12, 14), "rain")).meteors is None
    assert events.roll(_at("night", (2026, 10, 14))).meteors is None


def test_big_moon_only_when_full():
    day = datetime(2026, 11, 1, 23, tzinfo=PHILLY)
    w = demo_world("night")
    seen = {abs(replace(w, when=day + timedelta(days=d)).moon - 0.5) < events.FULL_MOON:
            events.roll(replace(w, when=day + timedelta(days=d))).big_moon for d in range(30)}
    assert seen.get(True) is True and seen.get(False) is False


def test_fireworks_for_holidays_after_dark_and_for_yesterdays_win():
    july4 = events.roll(_at("night", (2026, 7, 4)))
    assert july4.fireworks and "FOURTH OF JULY" in july4.headline()
    assert not events.roll(_at("day", (2026, 7, 4))).fireworks
    win = events.roll(replace(_at("day", (2026, 11, 3)), wins=("sixers",)))
    assert win.fireworks and win.headline() == "SIXERS WON LAST NIGHT · VICTORY FIREWORKS"


def test_rarest_event_takes_the_header():
    e = events.Events(shiny=True, aurora=True, big_moon=True)
    assert "GOLDEN DRAGON" in e.headline()
    assert events.Events().headline() is None


def test_events_are_drawn(monkeypatch):
    every = events.Events(shiny=True, aurora=True, comet=True, meteors="GEMINIDS",
                          big_moon=True, fireworks=("#ffffff",), reason="TEST FIREWORKS")
    monkeypatch.setattr(events, "roll", lambda w: every)
    w = demo_world("night")
    svg = render(replace(w, stats=replace(w.stats, streak_days=0)))
    for marker in ('class="aurora"', 'id="comet"', 'class="pop"', "GOLDEN DRAGON",
                   "#f2c046"):
        assert marker in svg, marker
    assert len(svg.encode()) < 600 * 1024
