"""The README's buttons, the pages they open and the pictures drawn for them."""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from dataclasses import replace
from datetime import date, datetime
from pathlib import Path

import pytest

from sky_islands.buttons import BUTTONS, button_svg, write_buttons
from sky_islands.clock import PHILLY
from sky_islands.model import DEMO_STATS, world_at
from sky_islands.progress import level_info
from sky_islands.views import PREVIEW_LEVEL, TIMES, grown, moment, render_views
from sky_islands.wonders import DRAGON_STREAK

ROOT = Path(__file__).resolve().parents[1]
PAGES = [ROOT / "README.md", *sorted((ROOT / "views").glob("*.md"))]


@pytest.mark.parametrize("b", BUTTONS, ids=lambda b: b.key)
@pytest.mark.parametrize("active", [False, True])
def test_buttons_are_valid_svg(b, active):
    svg = button_svg(b, active)
    root = ET.fromstring(svg)
    assert root.tag.endswith("svg")
    assert b.label in svg
    assert ('class="shine"' in svg) is not active  # a pressed button does not shine


def test_committed_buttons_match_the_code(tmp_path):
    for path in write_buttons(tmp_path):
        committed = ROOT / "assets" / "buttons" / path.name
        assert committed.read_text(encoding="utf-8") == path.read_text(encoding="utf-8"), (
            f"{committed.name} is stale: run `python -m sky_islands buttons`")


@pytest.mark.parametrize("page", PAGES, ids=lambda p: p.name)
def test_every_button_link_and_image_exists(page):
    text = page.read_text(encoding="utf-8")
    for key in re.findall(r"blob/main/views/([\w-]+)\.md", text):
        assert (ROOT / "views" / f"{key}.md").exists(), key
    for src in re.findall(r'<img src="((?:\.\./)?assets/[^"]+)"', text):
        assert (page.parent / src).resolve().exists(), src


def test_each_view_page_shows_its_own_button_pressed():
    for page in sorted((ROOT / "views").glob("*.md")):
        pressed = re.findall(r"assets/buttons/([\w-]+)-active\.svg", page.read_text("utf-8"))
        assert pressed == [page.stem]


@pytest.mark.parametrize("month", range(1, 13))
@pytest.mark.parametrize("phase", TIMES)
def test_each_view_lands_in_its_time_of_day(month, phase):
    w = world_at(DEMO_STATS, moment(date(2026, month, 15), phase))
    assert w.phase == phase


def test_preview_is_fully_grown_but_keeps_higher_real_numbers():
    g = grown(DEMO_STATS)
    assert level_info(g.contributions_total).level >= PREVIEW_LEVEL
    assert g.streak_days >= DRAGON_STREAK
    assert g.repos == DEMO_STATS.repos
    assert grown(replace(DEMO_STATS, streak_days=40)).streak_days == 40


def test_render_views_writes_all_five(tmp_path):
    written = render_views(DEMO_STATS, datetime(2026, 11, 3, 12, tzinfo=PHILLY), tmp_path)
    assert sorted(p.name for p in written) == sorted(
        [f"{t}.svg" for t in TIMES] + [f"level-{PREVIEW_LEVEL}.svg"])
    for p in written:
        assert p.stat().st_size < 600_000
