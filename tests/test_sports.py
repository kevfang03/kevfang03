"""Philadelphia game days from ESPN's public scoreboards."""

from __future__ import annotations

from datetime import date

from sky_islands import hud, sports


def _board(state: str, philly_home: bool, ours: str, theirs: str, we_won: bool,
           when: str = "2026-11-02T01:20Z") -> dict:
    us = {"homeAway": "home" if philly_home else "away", "team": {"abbreviation": "PHI"},
          "score": ours, "winner": we_won}
    them = {"homeAway": "away" if philly_home else "home", "team": {"abbreviation": "WSH"},
            "score": theirs, "winner": not we_won}
    other = {"date": when, "status": {"type": {"state": "pre"}},
             "competitions": [{"competitors": [
                 {"homeAway": "home", "team": {"abbreviation": "DAL"}},
                 {"homeAway": "away", "team": {"abbreviation": "NYG"}}]}]}
    ours_event = {"date": when, "status": {"type": {"state": state}},
                  "competitions": [{"competitors": [them, us]}]}
    return {"events": [other, ours_event]}


def test_finds_the_philly_game_and_its_result():
    g = sports.parse_game("eagles", _board("post", False, "10", "27", False))
    assert (g.team, g.opponent, g.home, g.result) == ("eagles", "WSH", False, "L 10-27")
    assert g.start.hour == 20  # 01:20 UTC is 8:20 PM the evening before in Philadelphia (EST)
    assert hud.game_text(g) == "EAGLES @ WSH · L 10-27"


def test_upcoming_game_shows_its_start_time():
    g = sports.parse_game("eagles", _board("pre", True, "0", "0", False))
    assert g.result is None and hud.game_text(g) == "EAGLES vs WSH · 8:20 PM"


def test_no_game_today():
    assert sports.parse_game("sixers", {"events": []}) is None


def test_wins_are_only_finished_games_philly_won():
    assert sports.won(_board("post", True, "24", "17", True))
    assert not sports.won(_board("post", True, "17", "24", False))
    assert not sports.won(_board("in", True, "24", "17", True))


def test_fetch_games_reads_today_and_yesterday_and_skips_a_failing_league(capsys):
    asked = []

    def get(url):
        asked.append(url)
        if "baseball" in url:
            raise TimeoutError
        if "football" in url and "20261103" in url:
            return _board("pre", True, "0", "0", False, "2026-11-04T01:15Z")
        if "football" in url:
            return _board("post", True, "24", "17", True)
        return {"events": []}

    games, wins = sports.fetch_games(date(2026, 11, 3), get)
    assert [g.team for g in games] == ["eagles"] and wins == ("eagles",)
    assert "phillies scores unavailable" in capsys.readouterr().out
    assert any("dates=20261102" in u for u in asked)
