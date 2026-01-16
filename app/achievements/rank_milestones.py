from __future__ import annotations

from app.achievements.registry import AchievementRegistry
from app.constants.mode import Mode
from app.models.score import Score
from app.models.stats import Stats

registry = AchievementRegistry()


@registry.achievement(file="osu-rank-50000")
def std_rank_50k(score: Score, mode_vn: int, stats: Stats) -> bool:
    return stats.rank <= 50_000 and mode_vn == Mode.STD


@registry.achievement(file="osu-rank-10000")
def std_rank_10k(score: Score, mode_vn: int, stats: Stats) -> bool:
    return stats.rank <= 10_000 and mode_vn == Mode.STD


@registry.achievement(file="osu-rank-5000")
def std_rank_5k(score: Score, mode_vn: int, stats: Stats) -> bool:
    return stats.rank <= 5_000 and mode_vn == Mode.STD


@registry.achievement(file="osu-rank-1000")
def std_rank_1k(score: Score, mode_vn: int, stats: Stats) -> bool:
    return stats.rank <= 1_000 and mode_vn == Mode.STD


@registry.achievement(file="taiko-rank-50000")
def taiko_rank_50k(score: Score, mode_vn: int, stats: Stats) -> bool:
    return stats.rank <= 50_000 and mode_vn == Mode.TAIKO


@registry.achievement(file="taiko-rank-10000")
def taiko_rank_10k(score: Score, mode_vn: int, stats: Stats) -> bool:
    return stats.rank <= 10_000 and mode_vn == Mode.TAIKO


@registry.achievement(file="taiko-rank-5000")
def taiko_rank_5k(score: Score, mode_vn: int, stats: Stats) -> bool:
    return stats.rank <= 5_000 and mode_vn == Mode.TAIKO


@registry.achievement(file="taiko-rank-1000")
def taiko_rank_1k(score: Score, mode_vn: int, stats: Stats) -> bool:
    return stats.rank <= 1_000 and mode_vn == Mode.TAIKO


@registry.achievement(file="fruits-rank-50000")
def catch_rank_50k(score: Score, mode_vn: int, stats: Stats) -> bool:
    return stats.rank <= 50_000 and mode_vn == Mode.CATCH


@registry.achievement(file="fruits-rank-10000")
def catch_rank_10k(score: Score, mode_vn: int, stats: Stats) -> bool:
    return stats.rank <= 10_000 and mode_vn == Mode.CATCH


@registry.achievement(file="fruits-rank-5000")
def catch_rank_5k(score: Score, mode_vn: int, stats: Stats) -> bool:
    return stats.rank <= 5_000 and mode_vn == Mode.CATCH


@registry.achievement(file="fruits-rank-1000")
def catch_rank_1k(score: Score, mode_vn: int, stats: Stats) -> bool:
    return stats.rank <= 1_000 and mode_vn == Mode.CATCH


@registry.achievement(file="mania-rank-50000")
def mania_rank_50k(score: Score, mode_vn: int, stats: Stats) -> bool:
    return stats.rank <= 50_000 and mode_vn == Mode.MANIA


@registry.achievement(file="mania-rank-10000")
def mania_rank_10k(score: Score, mode_vn: int, stats: Stats) -> bool:
    return stats.rank <= 10_000 and mode_vn == Mode.MANIA


@registry.achievement(file="mania-rank-5000")
def mania_rank_5k(score: Score, mode_vn: int, stats: Stats) -> bool:
    return stats.rank <= 5_000 and mode_vn == Mode.MANIA


@registry.achievement(file="mania-rank-1000")
def mania_rank_1k(score: Score, mode_vn: int, stats: Stats) -> bool:
    return stats.rank <= 1_000 and mode_vn == Mode.MANIA
