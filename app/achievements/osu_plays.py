from __future__ import annotations

from app.achievements.registry import Registry
from app.constants.mode import Mode
from app.models.score import Score
from app.models.stats import Stats

registry = Registry()


@registry.achievement(file="osu-plays-5000")
def plays_5000(score: Score, mode_vn: int, stats: Stats) -> bool:
    return 5_000 <= stats.playcount and mode_vn == Mode.STD


@registry.achievement(file="osu-plays-15000")
def plays_15000(score: Score, mode_vn: int, stats: Stats) -> bool:
    return 15_000 <= stats.playcount and mode_vn == Mode.STD


@registry.achievement(file="osu-plays-25000")
def plays_25000(score: Score, mode_vn: int, stats: Stats) -> bool:
    return 25_000 <= stats.playcount and mode_vn == Mode.STD


@registry.achievement(file="osu-plays-50000")
def plays_50000(score: Score, mode_vn: int, stats: Stats) -> bool:
    return 50_000 <= stats.playcount and mode_vn == Mode.STD
