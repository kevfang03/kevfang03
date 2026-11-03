"""Live numbers from GitHub's GraphQL API.

Only public data is read: the contribution calendar, public repositories that the account
owns, merged pull requests and stars. The token comes from the environment (the Actions
GITHUB_TOKEN is enough) and is never printed.
"""

from __future__ import annotations

import json
import os
import urllib.request
from collections.abc import Callable
from datetime import UTC, datetime

from .clock import PHILLY
from .model import Repo, Stats

API = "https://api.github.com/graphql"
MAX_REPOS = 30

Post = Callable[[str, dict], dict]

_MAIN = """
query($login: String!, $from: DateTime!, $to: DateTime!, $prs: String!, $repos: Int!) {
  user(login: $login) {
    login
    createdAt
    year: contributionsCollection(from: $from, to: $to) {
      contributionCalendar { totalContributions }
    }
    recent: contributionsCollection {
      contributionCalendar { weeks { contributionDays { date contributionCount } } }
    }
    repositories(first: $repos, privacy: PUBLIC, isFork: false, ownerAffiliations: OWNER,
                 orderBy: {field: PUSHED_AT, direction: DESC}) {
      nodes {
        name
        stargazerCount
        pushedAt
        primaryLanguage { name }
        defaultBranchRef {
          target { ... on Commit { history(first: 1) { totalCount nodes { messageHeadline } } } }
        }
      }
    }
  }
  prs: search(query: $prs, type: ISSUE) { issueCount }
}
"""


def token_from_env() -> str:
    """The API token from GITHUB_TOKEN or GH_TOKEN."""
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if not token:
        raise SystemExit("Set GITHUB_TOKEN (or GH_TOKEN) to read live GitHub stats.")
    return token


def poster(token: str) -> Post:
    """A function that sends one GraphQL query and returns its data."""

    def post(query: str, variables: dict) -> dict:
        body = json.dumps({"query": query, "variables": variables}).encode()
        req = urllib.request.Request(API, body, {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "sky-islands",
        })
        with urllib.request.urlopen(req, timeout=30) as resp:
            reply = json.load(resp)
        if reply.get("errors"):
            raise RuntimeError("GitHub API: " + "; ".join(e.get("message", "?")
                                                         for e in reply["errors"]))
        return reply["data"]

    return post


def _iso(when: datetime) -> str:
    return when.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def _parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value)


def _all_time_query(first_year: int, now: datetime) -> str:
    """One query with a contributions total per calendar year (the API allows a year at most
    per collection)."""
    parts = []
    for year in range(first_year, now.year + 1):
        start = datetime(year, 1, 1, tzinfo=UTC)
        end = now if year == now.year else datetime(year, 12, 31, 23, 59, 59, tzinfo=UTC)
        parts.append(f'y{year}: contributionsCollection(from: "{_iso(start)}", '
                     f'to: "{_iso(end)}") {{ contributionCalendar {{ totalContributions }} }}')
    return ("query($login: String!) { user(login: $login) { " + " ".join(parts) + " } }")


def _days(user: dict) -> list[tuple[str, int]]:
    weeks = user["recent"]["contributionCalendar"]["weeks"]
    return [(d["date"], d["contributionCount"]) for w in weeks for d in w["contributionDays"]]


def streak(days: list[tuple[str, int]]) -> int:
    """Days in a row with a contribution, ending today. Today only breaks the streak once it
    is over, so a day with nothing yet is skipped."""
    days = sorted(days)
    if days and days[-1][1] == 0:
        days = days[:-1]
    run = 0
    for _, count in reversed(days):
        if count == 0:
            break
        run += 1
    return run


def weekly(user: dict) -> tuple[int, ...]:
    """Contributions per calendar week, oldest first, ending with this week."""
    weeks = user["recent"]["contributionCalendar"]["weeks"]
    return tuple(sum(d["contributionCount"] for d in w["contributionDays"]) for w in weeks)


def repos(user: dict) -> tuple[tuple[Repo, ...], str]:
    """Public repos as buildings, and the headline of the latest commit among them.

    The profile repo (named after the account) is left out: the hourly redraw pushes to it,
    so it would always look like the newest project."""
    out, latest = [], ""
    for node in user["repositories"]["nodes"]:
        if node["name"].lower() == user["login"].lower():
            continue
        history = ((node.get("defaultBranchRef") or {}).get("target") or {}).get("history") or {}
        lang = (node.get("primaryLanguage") or {}).get("name")
        out.append(Repo(node["name"], lang, history.get("totalCount", 0),
                        _parse_time(node["pushedAt"]), node["stargazerCount"]))
        if not latest and history.get("nodes"):
            latest = history["nodes"][0]["messageHeadline"]
    return tuple(out), latest


def stats_from(main: dict, totals: dict) -> Stats:
    """Turn the two API replies into the numbers the world is built from."""
    user = main["user"]
    found, latest = repos(user)
    return Stats(
        login=user["login"],
        contributions_total=sum(y["contributionCalendar"]["totalContributions"]
                                for y in totals["user"].values()),
        contributions_year=user["year"]["contributionCalendar"]["totalContributions"],
        streak_days=streak(_days(user)),
        repos=found,
        latest_commit=latest,
        weekly=weekly(user),
        merged_prs=main["prs"]["issueCount"],
    )


def fetch_stats(login: str, post: Post, now: datetime | None = None) -> Stats:
    """Read one account's public stats. Contributions and merged pull requests "this year"
    count from January 1 in Philadelphia."""
    now = now or datetime.now(PHILLY)
    jan1 = datetime(now.year, 1, 1, tzinfo=PHILLY)
    main = post(_MAIN, {
        "login": login, "from": _iso(jan1), "to": _iso(now), "repos": MAX_REPOS,
        "prs": f"author:{login} is:pr is:merged merged:>={jan1:%Y-%m-%d}",
    })
    if not main.get("user"):
        raise SystemExit(f"No GitHub user named {login!r}.")
    first_year = _parse_time(main["user"]["createdAt"]).year
    totals = post(_all_time_query(first_year, now.astimezone(UTC)), {"login": login})
    return stats_from(main, totals)
