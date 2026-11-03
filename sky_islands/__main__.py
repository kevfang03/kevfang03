"""Command line: draw demo worlds or a review gallery.

    python -m sky_islands demo --phase night
    python -m sky_islands gallery --out preview/islands
    python -m sky_islands live --login octocat --out dist/sky-islands.svg

The live command reads public stats from GitHub and needs GITHUB_TOKEN (or GH_TOKEN) set.
"""

from __future__ import annotations

import argparse
import html
from dataclasses import replace
from datetime import datetime
from pathlib import Path

from .clock import PHASES, PHILLY
from .github import fetch_stats, poster, token_from_env
from .model import DEMO_STATS, demo_world, world_at
from .render import render

# (label, phase, weather, total contributions, date) for the review gallery.
GALLERY = [
    ("Dusk", "dusk", "clear", None, (2026, 11, 2)),
    ("Night, Eagles game", "night", "clear", None, (2026, 11, 2), "eagles"),
    ("Night", "night", "clear", None, (2026, 11, 2)),
    ("Day", "day", "clear", None, (2026, 11, 2)),
    ("Golden hour", "golden", "clear", None, (2026, 11, 2)),
    ("Dawn, spring", "dawn", "clear", None, (2026, 4, 20)),
    ("Night, new account (12 contributions)", "night", "clear", 12, (2026, 11, 2)),
    ("Day, summer, veteran (2,400 contributions)", "day", "clear", 2400, (2026, 7, 10)),
]


def _date(value: str) -> tuple[int, int, int]:
    y, m, d = (int(p) for p in value.split("-"))
    return y, m, d


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="sky_islands", description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    d = sub.add_parser("demo", help="draw one world from placeholder data")
    d.add_argument("--phase", choices=PHASES, default="dusk")
    d.add_argument("--date", type=_date, default=(2026, 11, 2), help="YYYY-MM-DD")
    d.add_argument("--out", type=Path, default=Path("preview/islands/world.svg"))
    g = sub.add_parser("gallery", help="draw a set of demo worlds and an index page")
    g.add_argument("--out", type=Path, default=Path("preview/islands"))
    live = sub.add_parser("live", help="draw the world from an account's live GitHub stats")
    live.add_argument("--login", required=True, help="GitHub account name")
    live.add_argument("--out", type=Path, default=Path("dist/sky-islands.svg"))
    args = p.parse_args(argv)

    if args.cmd == "live":
        now = datetime.now(PHILLY)
        stats = fetch_stats(args.login, poster(token_from_env()), now)
        world = world_at(stats, now)
        args.out.parent.mkdir(parents=True, exist_ok=True)
        svg = render(world)
        args.out.write_text(svg, encoding="utf-8")
        print(f"wrote {args.out} ({len(svg) // 1024} KB) at {world.phase}: "
              f"{stats.contributions_total} contributions, {stats.streak_days}-day streak, "
              f"{len(stats.repos)} repos")
        return 0

    if args.cmd == "demo":
        args.out.parent.mkdir(parents=True, exist_ok=True)
        svg = render(demo_world(args.phase, day=args.date))
        args.out.write_text(svg, encoding="utf-8")
        print(f"wrote {args.out} ({len(svg) // 1024} KB)")
        return 0

    args.out.mkdir(parents=True, exist_ok=True)
    cards = []
    for i, (label, phase, weather, total, day, *game) in enumerate(GALLERY):
        stats = DEMO_STATS if total is None else replace(DEMO_STATS, contributions_total=total)
        svg = render(demo_world(phase, weather, stats, day, game[0] if game else None))
        name = f"world-{i:02d}.svg"
        (args.out / name).write_text(svg, encoding="utf-8")
        cards.append(f'<figure><img src="{name}" alt="{html.escape(label)}">'
                     f"<figcaption>{html.escape(label)} · {len(svg) // 1024} KB</figcaption></figure>")
    page = ("<!doctype html><meta charset='utf-8'><title>Sky islands gallery</title>"
            "<style>body{background:#0d1117;color:#c9d1d9;font:14px system-ui;margin:24px auto;"
            "max-width:1000px}figure{margin:0 0 28px}img{width:100%;display:block;border-radius:14px}"
            "figcaption{margin-top:6px}</style>" + "".join(cards))
    (args.out / "index.html").write_text(page, encoding="utf-8")
    print(f"wrote {len(cards)} worlds to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
