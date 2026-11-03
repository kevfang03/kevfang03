"""Command line: draw demo scenes or a review gallery.

    python -m desk_scene demo --phase night --weather rain --teams eagles
    python -m desk_scene gallery --out preview
"""

from __future__ import annotations

import argparse
import html
from pathlib import Path

from .model import demo_state
from .palette import PHASES, TEAMS, WEATHERS
from .vector.render import render

# (label, phase, weather, teams, date) for the review gallery.
GALLERY = [
    ("Night, clear", "night", "clear", (), (2026, 11, 2)),
    ("Night, rain, Eagles game", "night", "rain", ("eagles",), (2026, 11, 2)),
    ("Day, clear, Phillies game", "day", "clear", ("phillies",), (2026, 9, 12)),
    ("Dusk, snow, Sixers game", "dusk", "snow", ("sixers",), (2026, 1, 20)),
    ("Dawn, clear", "dawn", "clear", (), (2026, 5, 6)),
    ("Night, Eagles and Sixers games", "night", "clear", ("eagles", "sixers"), (2026, 11, 2)),
    ("Day, cloudy", "day", "cloudy", (), (2026, 11, 2)),
    ("Night, snow, December", "night", "snow", (), (2026, 12, 18)),
    ("Night, July 4th", "night", "clear", (), (2026, 7, 4)),
]


def _teams(value: str) -> tuple[str, ...]:
    teams = tuple(t.strip().lower() for t in value.split(",") if t.strip())
    for t in teams:
        if t not in TEAMS:
            raise argparse.ArgumentTypeError(f"unknown team {t!r}; pick from {', '.join(TEAMS)}")
    return teams


def _date(value: str) -> tuple[int, int, int]:
    y, m, d = (int(p) for p in value.split("-"))
    return y, m, d


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="desk_scene", description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="cmd", required=True)

    d = sub.add_parser("demo", help="draw one scene from placeholder data")
    d.add_argument("--phase", choices=PHASES, default="night")
    d.add_argument("--weather", choices=WEATHERS, default="clear")
    d.add_argument("--teams", type=_teams, default=(), help="comma-separated, e.g. eagles,sixers")
    d.add_argument("--date", type=_date, default=(2026, 11, 2), help="YYYY-MM-DD")
    d.add_argument("--out", type=Path, default=Path("preview/scene.svg"))

    g = sub.add_parser("gallery", help="draw a set of demo scenes and an index page")
    g.add_argument("--out", type=Path, default=Path("preview"))

    args = p.parse_args(argv)
    if args.cmd == "demo":
        args.out.parent.mkdir(parents=True, exist_ok=True)
        svg = render(demo_state(args.phase, args.weather, args.teams, args.date))
        args.out.write_text(svg, encoding="utf-8")
        print(f"wrote {args.out} ({len(svg) // 1024} KB)")
        return 0

    args.out.mkdir(parents=True, exist_ok=True)
    cards = []
    for i, (label, phase, weather, teams, day) in enumerate(GALLERY):
        name = f"scene-{i:02d}.svg"
        svg = render(demo_state(phase, weather, teams, day))
        (args.out / name).write_text(svg, encoding="utf-8")
        cards.append(
            f'<figure><img src="{name}" alt="{html.escape(label)}">'
            f"<figcaption>{html.escape(label)} · {len(svg) // 1024} KB</figcaption></figure>"
        )
    page = (
        "<!doctype html><meta charset='utf-8'><title>Desk scene gallery</title>"
        "<style>body{background:#0d1117;color:#c9d1d9;font:14px system-ui;margin:24px}"
        "figure{margin:0 0 28px}img{width:100%;max-width:1280px;display:block}"
        "figcaption{margin-top:6px}</style>"
        + "".join(cards)
    )
    (args.out / "index.html").write_text(page, encoding="utf-8")
    print(f"wrote {len(cards)} scenes to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
