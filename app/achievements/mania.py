from __future__ import annotations

from app.achievements.registry import AchievementRegistry
from app.constants.mode import Mode
from app.constants.mods import Mods
from app.models.score import Score
from app.models.stats import Stats

registry = AchievementRegistry()


@registry.achievement(file="mania-skill-pass-1")
def mania_skill_pass_1(score: Score, mode_vn: int, stats: Stats) -> bool:
    return (
        (score.mods & Mods.NOFAIL == 0) and 1 <= score.sr < 2 and mode_vn == Mode.MANIA
    )


@registry.achievement(file="mania-skill-pass-2")
def mania_skill_pass_2(score: Score, mode_vn: int, stats: Stats) -> bool:
    return (
        (score.mods & Mods.NOFAIL == 0) and 2 <= score.sr < 3 and mode_vn == Mode.MANIA
    )


@registry.achievement(file="mania-skill-pass-3")
def mania_skill_pass_3(score: Score, mode_vn: int, stats: Stats) -> bool:
    return (
        (score.mods & Mods.NOFAIL == 0) and 3 <= score.sr < 4 and mode_vn == Mode.MANIA
    )


@registry.achievement(file="mania-skill-pass-4")
def mania_skill_pass_4(score: Score, mode_vn: int, stats: Stats) -> bool:
    return (
        (score.mods & Mods.NOFAIL == 0) and 4 <= score.sr < 5 and mode_vn == Mode.MANIA
    )


@registry.achievement(file="mania-skill-pass-5")
def mania_skill_pass_5(score: Score, mode_vn: int, stats: Stats) -> bool:
    return (
        (score.mods & Mods.NOFAIL == 0) and 5 <= score.sr < 6 and mode_vn == Mode.MANIA
    )


@registry.achievement(file="mania-skill-pass-6")
def mania_skill_pass_6(score: Score, mode_vn: int, stats: Stats) -> bool:
    return (
        (score.mods & Mods.NOFAIL == 0) and 6 <= score.sr < 7 and mode_vn == Mode.MANIA
    )


@registry.achievement(file="mania-skill-pass-7")
def mania_skill_pass_7(score: Score, mode_vn: int, stats: Stats) -> bool:
    return (
        (score.mods & Mods.NOFAIL == 0) and 7 <= score.sr < 8 and mode_vn == Mode.MANIA
    )


@registry.achievement(file="mania-skill-pass-8")
def mania_skill_pass_8(score: Score, mode_vn: int, stats: Stats) -> bool:
    return (
        (score.mods & Mods.NOFAIL == 0) and 8 <= score.sr < 9 and mode_vn == Mode.MANIA
    )


@registry.achievement(file="mania-skill-fc-1")
def mania_skill_fc_1(score: Score, mode_vn: int, stats: Stats) -> bool:
    return score.full_combo and 1 <= score.sr < 2 and mode_vn == Mode.MANIA


@registry.achievement(file="mania-skill-fc-2")
def mania_skill_fc_2(score: Score, mode_vn: int, stats: Stats) -> bool:
    return score.full_combo and 2 <= score.sr < 3 and mode_vn == Mode.MANIA


@registry.achievement(file="mania-skill-fc-3")
def mania_skill_fc_3(score: Score, mode_vn: int, stats: Stats) -> bool:
    return score.full_combo and 3 <= score.sr < 4 and mode_vn == Mode.MANIA


@registry.achievement(file="mania-skill-fc-4")
def mania_skill_fc_4(score: Score, mode_vn: int, stats: Stats) -> bool:
    return score.full_combo and 4 <= score.sr < 5 and mode_vn == Mode.MANIA


@registry.achievement(file="mania-skill-fc-5")
def mania_skill_fc_5(score: Score, mode_vn: int, stats: Stats) -> bool:
    return score.full_combo and 5 <= score.sr < 6 and mode_vn == Mode.MANIA


@registry.achievement(file="mania-skill-fc-6")
def mania_skill_fc_6(score: Score, mode_vn: int, stats: Stats) -> bool:
    return score.full_combo and 6 <= score.sr < 7 and mode_vn == Mode.MANIA


@registry.achievement(file="mania-skill-fc-7")
def mania_skill_fc_7(score: Score, mode_vn: int, stats: Stats) -> bool:
    return score.full_combo and 7 <= score.sr < 8 and mode_vn == Mode.MANIA


@registry.achievement(file="mania-skill-fc-8")
def mania_skill_fc_8(score: Score, mode_vn: int, stats: Stats) -> bool:
    return score.full_combo and 8 <= score.sr < 9 and mode_vn == Mode.MANIA


@registry.achievement(file="mania-hits-40000")
def mania_hits_40000(score: Score, mode_vn: int, stats: Stats) -> bool:
    return 40_000 <= stats.total_hits and mode_vn == Mode.MANIA


@registry.achievement(file="mania-hits-400000")
def mania_hits_400000(score: Score, mode_vn: int, stats: Stats) -> bool:
    return 400_000 <= stats.total_hits and mode_vn == Mode.MANIA


@registry.achievement(file="mania-hits-4000000")
def mania_hits_4000000(score: Score, mode_vn: int, stats: Stats) -> bool:
    return 4_000_000 <= stats.total_hits and mode_vn == Mode.MANIA


@registry.achievement(file="mania-hits-40000000")
def mania_hits_40000000(score: Score, mode_vn: int, stats: Stats) -> bool:
    return 40_000_000 <= stats.total_hits and mode_vn == Mode.MANIA
