"""Live stats: parsing GitHub's replies, without touching the network."""

from __future__ import annotations

from datetime import datetime

import pytest

from sky_islands import github
from sky_islands.clock import PHILLY
from sky_islands.model import world_at
from sky_islands.render import render

NOW = datetime(2026, 11, 3, 14, 0, tzinfo=PHILLY)


def _week(*counts: int, start: int = 1) -> dict:
    return {"contributionDays": [{"date": f"2026-10-{start + i:02d}", "contributionCount": c}
                                 for i, c in enumerate(counts)]}


def _repo(name: str, pushed: str, commits: int, headline: str = "", lang: str | None = "Python",
          stars: int = 0) -> dict:
    return {
        "name": name, "stargazerCount": stars, "pushedAt": pushed,
        "primaryLanguage": {"name": lang} if lang else None,
        "defaultBranchRef": {"target": {"history": {
            "totalCount": commits, "nodes": [{"messageHeadline": headline}] if headline else []}}},
    }


MAIN = {
    "user": {
        "login": "octocat",
        "createdAt": "2024-05-01T12:00:00Z",
        "year": {"contributionCalendar": {"totalContributions": 78}},
        "recent": {"contributionCalendar": {"weeks": [
            _week(1, 0, 2, 0, 0, 0, 3, start=1),
            _week(0, 4, 1, 2, 5, 1, 0, start=8),
        ]}},
        "repositories": {"nodes": [
            _repo("octocat", "2026-11-03T18:00:00Z", 900, "Redraw banner"),
            _repo("queue-auditor", "2026-11-02T20:00:00Z", 140, "Add DST-safe tests", stars=3),
            _repo("notes", "2026-09-01T10:00:00Z", 12, "Typo", lang=None),
            {"name": "empty", "stargazerCount": 0, "pushedAt": "2026-01-01T00:00:00Z",
             "primaryLanguage": None, "defaultBranchRef": None},
        ]},
    },
    "prs": {"issueCount": 7},
}
TOTALS = {"user": {"y2024": {"contributionCalendar": {"totalContributions": 40}},
                   "y2025": {"contributionCalendar": {"totalContributions": 120}},
                   "y2026": {"contributionCalendar": {"totalContributions": 78}}}}


def _fake_post(calls: list):
    def post(query: str, variables: dict) -> dict:
        calls.append((query, variables))
        return MAIN if len(calls) == 1 else TOTALS
    return post


def test_stats_from_replies():
    st = github.stats_from(MAIN, TOTALS)
    assert st.login == "octocat"
    assert st.contributions_total == 238
    assert st.contributions_year == 78
    assert st.merged_prs == 7
    assert st.weekly == (6, 13)
    # The last day (0 so far) does not break the streak; the day before it does end it.
    assert st.streak_days == 5


def test_profile_repo_is_left_out_and_latest_commit_comes_from_newest_repo():
    st = github.stats_from(MAIN, TOTALS)
    assert [r.name for r in st.repos] == ["queue-auditor", "notes", "empty"]
    assert st.latest_commit == "Add DST-safe tests"
    empty = st.repos[-1]
    assert empty.commits == 0 and empty.language is None
    assert st.repos[0].stars == 3


@pytest.mark.parametrize(("counts", "expected"), [
    ([1, 1, 1], 3),
    ([1, 1, 0], 2),       # nothing yet today: still a streak
    ([1, 0, 1], 1),
    ([0, 0, 0], 0),
    ([], 0),
])
def test_streak(counts, expected):
    days = [(f"2026-10-{i + 1:02d}", c) for i, c in enumerate(counts)]
    assert github.streak(days) == expected


def test_fetch_asks_for_every_year_since_the_account_was_made():
    calls: list = []
    st = github.fetch_stats("octocat", _fake_post(calls), NOW)
    assert st.contributions_total == 238
    first, second = calls
    assert first[1]["prs"] == "author:octocat is:pr is:merged merged:>=2026-01-01"
    assert first[1]["from"] == "2026-01-01T05:00:00Z"
    for year in (2024, 2025, 2026):
        assert f"y{year}:" in second[0]
    assert "y2023" not in second[0]


def test_missing_user_stops_cleanly():
    with pytest.raises(SystemExit):
        github.fetch_stats("nobody", lambda q, v: {"user": None, "prs": {"issueCount": 0}}, NOW)


def test_missing_token_stops_cleanly(monkeypatch):
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    monkeypatch.delenv("GH_TOKEN", raising=False)
    with pytest.raises(SystemExit):
        github.token_from_env()


@pytest.mark.parametrize(("hour", "phase"), [(3, "night"), (12, "day"), (16, "golden"),
                                             (17, "dusk"), (7, "dawn")])
def test_world_light_follows_the_real_clock(hour, phase):
    w = world_at(github.stats_from(MAIN, TOTALS), datetime(2026, 11, 3, hour, 0, tzinfo=PHILLY))
    assert w.phase == phase


def test_live_world_renders():
    svg = render(world_at(github.stats_from(MAIN, TOTALS), NOW))
    assert svg.startswith("<svg") and "octocat" in svg
    assert "queue-auditor" in svg
