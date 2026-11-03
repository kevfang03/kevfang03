"""Game rules: how GitHub activity turns into levels, building tiers, the current quest
and the train: how long it is and what its cargo wagon carries."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from .model import Repo, Stats

# XP needed to reach each level grows a little every level: 0, 50, 150, 300, 500, ...
XP_STEP = 25
# Commits on a repo's default branch needed for each building tier.
TIER_COMMITS = (0, 25, 100, 300)
ACTIVE_DAYS = 14  # recently pushed: lit windows and a smoking chimney
DORMANT_DAYS = 180  # untouched this long: vines grow over it
DOME_LEVEL = 4  # the glass-domed observation car joins the train
MAX_COACHES = 4
EVOLVE_LEVELS = (5, 10)  # your companion takes its second and third forms here

STYLE_BY_LANGUAGE = {
    "Python": "observatory", "Jupyter Notebook": "observatory",
    "JavaScript": "workshop", "TypeScript": "workshop", "HTML": "workshop", "CSS": "workshop",
    "Markdown": "bookshop", "TeX": "bookshop", "MDX": "bookshop",
    "C": "lab", "C++": "lab", "Rust": "lab", "Go": "lab", "Java": "lab", "C#": "lab",
    "Shell": "cottage", "PowerShell": "cottage", "Lua": "cottage", "Luau": "cottage",
}


def level_threshold(level: int) -> int:
    """Total XP needed to reach a level (level 1 is free)."""
    return XP_STEP * (level - 1) * level


def level_for(xp: int) -> int:
    level = 1
    while level_threshold(level + 1) <= xp:
        level += 1
    return level


@dataclass(frozen=True)
class Level:
    level: int
    xp: int
    floor: int  # XP where this level began
    next: int  # XP where the next level begins

    @property
    def fraction(self) -> float:
        return (self.xp - self.floor) / (self.next - self.floor)


def level_info(xp: int) -> Level:
    lv = level_for(max(0, xp))
    return Level(lv, xp, level_threshold(lv), level_threshold(lv + 1))


def tier_for(commits: int) -> int:
    """Building tier 1 to 4 from a repo's commit count."""
    return sum(1 for t in TIER_COMMITS if commits >= t)


def style_for(repo: Repo) -> str:
    return STYLE_BY_LANGUAGE.get(repo.language or "", "cottage")


def activity(repo: Repo, now: datetime) -> str:
    days = (now - repo.pushed_at).total_seconds() / 86400
    if days <= ACTIVE_DAYS:
        return "active"
    if days >= DORMANT_DAYS:
        return "dormant"
    return "quiet"


@dataclass(frozen=True)
class Quest:
    repo: Repo
    tier: int  # the tier being built
    remaining: int  # commits still needed
    floors_done: int
    floors_total: int


def current_quest(repos: tuple[Repo, ...]) -> Quest | None:
    """The most recently pushed repo is under construction toward its next tier."""
    if not repos:
        return None
    repo = max(repos, key=lambda r: r.pushed_at)
    tier = tier_for(repo.commits)
    if tier >= len(TIER_COMMITS):
        return None
    lo, hi = TIER_COMMITS[tier - 1], TIER_COMMITS[tier]
    total = 10
    done = round((repo.commits - lo) / (hi - lo) * total)
    return Quest(repo, tier + 1, hi - repo.commits, min(done, total - 1), total)


def consist(level: int) -> tuple[str, ...]:
    """The train's cars from the front: the engine, one passenger coach per two levels (up
    to four), the cargo wagon, and from DOME_LEVEL the glass-domed observation car."""
    coaches = min(MAX_COACHES, 1 + (max(1, level) - 1) // 2)
    cars = ("engine", *("coach",) * coaches, "cargo")
    return (*cars, "dome") if level >= DOME_LEVEL else cars


@dataclass(frozen=True)
class Cargo:
    """Loads on the cargo wagon, up to three of each."""

    wheat: int
    wood: int
    stone: int
    crystals: int


def cargo(stats: Stats) -> Cargo:
    """What the wagon carries: a sack of wheat per 4 contributions this week, a log per 2 days
    of streak this week, a stone block per 3 pull requests merged this year and a crystal per
    2 stars received. Any activity this week shows at least one sack or log."""
    week = stats.weekly[-1] if stats.weekly else 0
    stars = sum(r.stars for r in stats.repos)

    def loads(n: int) -> int:
        return max(0, min(3, n))

    return Cargo(loads(-(-week // 4)), loads(-(-min(7, stats.streak_days) // 2)),
                 loads(stats.merged_prs // 3), loads(stars // 2))
