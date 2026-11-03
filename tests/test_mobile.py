"""At phone width the banner hides its small print and enlarges the title and level."""

from __future__ import annotations

import re

from sky_islands import hud
from sky_islands.model import demo_world
from sky_islands.render import render


def test_phone_layout_rules_are_in_the_image():
    svg = render(demo_world("dusk"))
    assert hud.MOBILE_CSS in svg
    for cls in ("title", "lvl"):
        assert f'class="{cls}"' in svg


def test_every_label_and_the_fine_print_can_hide():
    svg = render(demo_world("dusk"))
    # Each sign is a dark pill with its text; every one sits inside a "fine" group.
    pills = len(re.findall(r'fill="#120e24" opacity="0?\.78"', svg))
    assert pills and svg.count('class="fine"') >= pills
    assert re.search(r'<text[^>]*class="fine"[^>]*>LAST 26 WEEKS', svg)
