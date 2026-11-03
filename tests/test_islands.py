import xml.etree.ElementTree as ET
from dataclasses import replace
from datetime import datetime, timedelta
from itertools import pairwise

import pytest

from sky_islands.clock import PHASES, PHILLY, phase_for
from sky_islands.hud import LABEL_STEP, place
from sky_islands.island import HOME
from sky_islands.model import DEMO_STATS, Repo, demo_world
from sky_islands.progress import (
    current_quest,
    level_for,
    level_info,
    level_threshold,
    style_for,
    tier_for,
)
from sky_islands.render import render
from sky_islands.town import Label, plan

# README images over a few MB load slowly; keep every variant well under that.
MAX_BYTES = 600_000
NOW = datetime(2026, 11, 2, 12, tzinfo=PHILLY)


def _repos(n: int) -> tuple[Repo, ...]:
    return tuple(Repo(f"repo-{i}", "Python" if i % 2 else "Go", 5 + i * 17, NOW - timedelta(days=i))
                 for i in range(n))


@pytest.mark.parametrize("phase", PHASES)
def test_every_phase_renders_valid_svg(phase):
    svg = render(demo_world(phase))
    assert ET.fromstring(svg).tag.endswith("svg")
    assert len(svg.encode()) < MAX_BYTES


def test_same_moment_draws_the_same_world():
    assert render(demo_world("night")) == render(demo_world("night"))


@pytest.mark.parametrize("n", [0, 1, 6, 40])
def test_any_number_of_repos_renders(n):
    stats = replace(DEMO_STATS, repos=_repos(n))
    ET.fromstring(render(demo_world("dusk", stats=stats)))


@pytest.mark.parametrize("n", [0, 3, 6, 12, 40])
def test_buildings_never_overlap_and_stay_on_the_island(n):
    town = plan(_repos(n), 4, HOME)
    lo, hi = town.span
    plots = sorted(town.plots, key=lambda p: p.x)
    for a, b in pairwise(plots):
        assert a.x + a.w <= b.x
    for p in plots:
        if p.kind == "repo":
            assert lo <= p.x and p.x + p.w <= hi
    assert len(plots) - 1 + town.overflow == n


def test_labels_never_overlap():
    labels = [Label(400 + k * 6, 200, f"label-{k}", "#fff") for k in range(8)]
    placed = place(labels)
    for i, (a, ya) in enumerate(placed):
        for b, yb in placed[i + 1:]:
            if abs(a.x - b.x) < 60:
                assert abs(ya - yb) >= LABEL_STEP


def test_levels_grow_with_xp():
    assert level_threshold(1) == 0
    assert level_for(0) == 1
    assert level_for(49) == 1
    assert level_for(50) == 2
    assert level_for(300) == 4
    info = level_info(300)
    assert (info.floor, info.next) == (300, 500)
    assert 0 <= info.fraction < 1


def test_tiers_and_styles():
    assert [tier_for(n) for n in (0, 24, 25, 100, 299, 300, 5000)] == [1, 1, 2, 3, 3, 4, 4]
    assert style_for(Repo("a", "Python", 1, NOW)) == "observatory"
    assert style_for(Repo("a", "Haskell", 1, NOW)) == "cottage"
    assert style_for(Repo("a", None, 1, NOW)) == "cottage"


def test_quest_is_the_most_recent_repo():
    q = current_quest(DEMO_STATS.repos)
    assert q.repo.name == "ops-suite"
    assert q.tier == 4 and q.remaining == 300 - 186
    assert current_quest(()) is None
    assert current_quest((Repo("done", "Go", 999, NOW),)) is None


def test_phase_boundaries():
    rise = datetime(2026, 11, 2, 6, 50, tzinfo=PHILLY)
    sets = datetime(2026, 11, 2, 16, 45, tzinfo=PHILLY)
    m = timedelta(minutes=1)
    assert phase_for(rise - 60 * m, rise, sets) == "night"
    assert phase_for(rise, rise, sets) == "dawn"
    assert phase_for(rise + 3 * 60 * m, rise, sets) == "day"
    assert phase_for(sets - 60 * m, rise, sets) == "golden"
    assert phase_for(sets, rise, sets) == "dusk"
    assert phase_for(sets + 60 * m, rise, sets) == "night"


def test_motion_can_be_turned_off():
    assert "prefers-reduced-motion" in render(demo_world("night"))


def test_islands_unlock_with_level():
    low = render(demo_world("dusk", stats=replace(DEMO_STATS, contributions_total=12)))
    assert "PHILLY ISLAND · UNLOCKS AT LV 3" in low
    assert "STADIUM · UNLOCKS AT LV 4" in low
    high = render(demo_world("dusk"))
    assert "PHILLY ISLAND · UNLOCKS" not in high
    assert "STARPORT · UNLOCKS AT LV 6" in high
    assert "SKY SHRINE · UNLOCKS AT LV 8" in high


def test_game_day_lights_up_the_stadium():
    assert "GAME DAY · EAGLES vs DAL · 8:20 PM" in render(demo_world("night", game="eagles"))
    assert "NO GAME TODAY" in render(demo_world("night"))


def test_timeline_shows_recent_weeks():
    svg = render(demo_world("day"))
    assert "LAST 26 WEEKS" in svg and "PEAK 21" in svg


def test_ride_goes_round_the_island_and_starts_on_the_overview():
    from sky_islands import camera, ride

    css = camera.css((150, 650))
    for name in ("over", "ride", "ride-world", "ride-bg", "fade", "marker"):
        assert f"@keyframes {name}" in css
    # The overview shows at the start and end of the loop; the ride is hidden by default,
    # so a still frame (or reduced motion) shows the overview.
    assert ".ride{opacity:0;" in css
    assert f"translateX({-ride.PAN}px)" in css
    svg = render(demo_world("dusk"))
    for side in ("FRONT · THE TOWN", "EAST · STADIUM BRIDGE", "NORTH · THE WILD SIDE",
                 "WEST · THE SERVER FARM"):
        assert side in svg
    assert 'href="#isl-home"' in svg and 'id="isl-home"' in svg


def test_ride_loops_back_to_the_town():
    """The strip repeats a lap either side, so the track never breaks off and the ride ends
    where it began, and the far side of
    the loop is shown behind the islands drifting the other way."""
    from sky_islands import ride

    svg = render(demo_world("day"))
    assert 'id="ride-strip"' in svg
    assert f'<use href="#ride-strip" transform="translate({ride.PAN} 0)"/>' in svg
    assert f'<use href="#ride-strip" transform="translate({-ride.PAN} 0)"/>' in svg
    assert svg.count('href="#ride-strip"') == 4  # a lap either side plus two far-side copies
    assert "@keyframes ride-far" in svg and f"translateX({round(ride.PAN * ride.FAR_K)}px)" in svg


def test_train_grows_with_level():
    from sky_islands.progress import DOME_LEVEL, MAX_COACHES, consist

    assert consist(1) == ("engine", "coach", "cargo")
    assert consist(DOME_LEVEL)[-1] == "dome"
    lengths = [len(consist(lv)) for lv in range(1, 30)]
    assert lengths == sorted(lengths)  # never shrinks as you level up
    assert consist(99).count("coach") == MAX_COACHES


def test_cargo_loads_follow_activity_and_stay_capped():
    from sky_islands.progress import cargo

    idle = replace(DEMO_STATS, weekly=(0,), streak_days=0, merged_prs=0, repos=())
    assert cargo(idle) == cargo(idle).__class__(0, 0, 0, 0)
    busy = replace(DEMO_STATS, weekly=(1,), streak_days=1)
    assert cargo(busy).wheat == 1 and cargo(busy).wood == 1  # any activity shows
    huge = replace(DEMO_STATS, weekly=(500,), streak_days=400, merged_prs=900)
    load = cargo(huge)
    assert max(load.wheat, load.wood, load.stone, load.crystals) <= 3


def test_dragon_flies_only_on_a_long_streak():
    from sky_islands.wonders import DRAGON_STREAK

    long_streak = render(demo_world("dusk", stats=replace(DEMO_STATS, streak_days=DRAGON_STREAK)))
    short = render(demo_world("dusk", stats=replace(DEMO_STATS, streak_days=DRAGON_STREAK - 1)))
    assert long_streak.count('rotate="auto"') > short.count('rotate="auto"')


def test_wonders_open_at_their_levels():
    veteran = render(demo_world("day", stats=replace(DEMO_STATS, contributions_total=2400)))
    assert "STARPORT · UNLOCKS" not in veteran and "SKY SHRINE · UNLOCKS" not in veteran
    assert ">STARPORT<" in veteran and ">SKY SHRINE<" in veteran


def test_companion_evolves_with_level():
    from sky_islands.companion import stage
    from sky_islands.progress import EVOLVE_LEVELS

    first, second = EVOLVE_LEVELS
    assert stage(1) == 1 and stage(first - 1) == 1
    assert stage(first) == 2 and stage(second - 1) == 2
    assert stage(second) == 3 and stage(99) == 3


def test_server_farm_racks_follow_this_years_contributions():
    from sky_islands.serverfarm import MAX_RACKS, RACKS_PER, rack_count

    assert rack_count(0) == 3  # a few racks are always there
    assert rack_count(RACKS_PER * 8) == 8
    assert rack_count(10**6) == MAX_RACKS
