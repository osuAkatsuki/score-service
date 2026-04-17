from __future__ import annotations

from app.constants.score_status import ScoreStatus
from app.usecases.score import calculate_status
from tests.unit.helpers import make_leaderboard_score
from tests.unit.helpers import make_score


def test_failed_when_not_passed_and_not_quit() -> None:
    score = make_score(passed=False, quit=False)
    assert calculate_status(score, previous_best=None) == ScoreStatus.FAILED


def test_quit_when_not_passed_and_quit() -> None:
    score = make_score(passed=False, quit=True)
    assert calculate_status(score, previous_best=None) == ScoreStatus.QUIT


def test_best_when_passed_with_no_previous_best() -> None:
    score = make_score(passed=True, pp=100.0, score=50_000)
    assert calculate_status(score, previous_best=None) == ScoreStatus.BEST


def test_best_when_pp_strictly_higher_than_previous() -> None:
    score = make_score(passed=True, pp=150.0, score=40_000)
    previous = make_leaderboard_score(pp=100.0, score=60_000)
    assert calculate_status(score, previous_best=previous) == ScoreStatus.BEST


def test_best_when_pp_equal_and_score_higher_spin_to_win() -> None:
    score = make_score(passed=True, pp=100.0, score=70_000)
    previous = make_leaderboard_score(pp=100.0, score=60_000)
    assert calculate_status(score, previous_best=previous) == ScoreStatus.BEST


def test_submitted_when_pp_lower_than_previous() -> None:
    score = make_score(passed=True, pp=80.0, score=90_000)
    previous = make_leaderboard_score(pp=100.0, score=60_000)
    assert calculate_status(score, previous_best=previous) == ScoreStatus.SUBMITTED


def test_submitted_when_pp_equal_and_score_lower() -> None:
    score = make_score(passed=True, pp=100.0, score=50_000)
    previous = make_leaderboard_score(pp=100.0, score=60_000)
    assert calculate_status(score, previous_best=previous) == ScoreStatus.SUBMITTED
