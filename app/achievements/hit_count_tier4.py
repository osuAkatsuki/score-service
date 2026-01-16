from __future__ import annotations

from app.achievements.registry import AchievementRegistry
from app.constants.mode import Mode
from app.models.score import Score
from app.models.stats import Stats

registry = AchievementRegistry()


@registry.achievement(file="taiko-hits-30000000")
def taiko_hits_30m(score: Score, mode_vn: int, stats: Stats) -> bool:
    return 30_000_000 <= stats.total_hits and mode_vn == Mode.TAIKO


@registry.achievement(file="fruits-hits-20000000")
def fruits_hits_20m(score: Score, mode_vn: int, stats: Stats) -> bool:
    return 20_000_000 <= stats.total_hits and mode_vn == Mode.CATCH


@registry.achievement(file="mania-hits-40000000")
def mania_hits_40m(score: Score, mode_vn: int, stats: Stats) -> bool:
    return 40_000_000 <= stats.total_hits and mode_vn == Mode.MANIA
