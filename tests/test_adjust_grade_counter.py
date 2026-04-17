from __future__ import annotations

import pytest

from app.usecases.stats import adjust_grade_counter
from tests.helpers import make_stats


@pytest.mark.parametrize(
    ("grade", "attr"),
    [
        ("XH", "xh_count"),
        ("X", "x_count"),
        ("SH", "sh_count"),
        ("S", "s_count"),
        ("A", "a_count"),
        ("B", "b_count"),
        ("C", "c_count"),
        ("D", "d_count"),
    ],
)
def test_increments_grade_counter(grade: str, attr: str) -> None:
    stats = make_stats()
    adjust_grade_counter(stats, grade, +1)
    assert getattr(stats, attr) == 1


@pytest.mark.parametrize(
    ("grade", "attr"),
    [
        ("XH", "xh_count"),
        ("X", "x_count"),
        ("SH", "sh_count"),
        ("S", "s_count"),
        ("A", "a_count"),
        ("B", "b_count"),
        ("C", "c_count"),
        ("D", "d_count"),
    ],
)
def test_decrements_grade_counter(grade: str, attr: str) -> None:
    stats = make_stats()
    setattr(stats, attr, 5)
    adjust_grade_counter(stats, grade, -1)
    assert getattr(stats, attr) == 4


def test_ignores_unknown_grade() -> None:
    stats = make_stats()
    adjust_grade_counter(stats, "Z", +1)
    assert stats.xh_count == 0
    assert stats.x_count == 0
    assert stats.sh_count == 0
    assert stats.s_count == 0
    assert stats.a_count == 0
    assert stats.b_count == 0
    assert stats.c_count == 0
    assert stats.d_count == 0


def test_only_adjusts_the_matched_counter() -> None:
    stats = make_stats()
    adjust_grade_counter(stats, "A", +1)
    assert stats.a_count == 1
    assert stats.xh_count == 0
    assert stats.x_count == 0
    assert stats.sh_count == 0
    assert stats.s_count == 0
    assert stats.b_count == 0
    assert stats.c_count == 0
    assert stats.d_count == 0
