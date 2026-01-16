from __future__ import annotations

from app.achievements.registry import Registry
from app.constants.mode import Mode
from app.models.score import Score
from app.models.stats import Stats

registry = Registry()


@registry.achievement(file="osu-combo-500")
def combo_500(score: Score, mode_vn: int, stats: Stats) -> bool:
    return 500 <= score.max_combo and mode_vn == Mode.STD


@registry.achievement(file="osu-combo-750")
def combo_750(score: Score, mode_vn: int, stats: Stats) -> bool:
    return 750 <= score.max_combo and mode_vn == Mode.STD


@registry.achievement(file="osu-combo-1000")
def combo_1000(score: Score, mode_vn: int, stats: Stats) -> bool:
    return 1_000 <= score.max_combo and mode_vn == Mode.STD


@registry.achievement(file="osu-combo-2000")
def combo_2000(score: Score, mode_vn: int, stats: Stats) -> bool:
    return 2_000 <= score.max_combo and mode_vn == Mode.STD
