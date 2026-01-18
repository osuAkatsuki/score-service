from __future__ import annotations

from app.achievements.registry import AchievementRegistry
from app.constants.mode import Mode
from app.constants.mods import Mods
from app.models.score import Score
from app.models.stats import Stats

registry = AchievementRegistry()


# ====================
# Skill Pass Achievements
# ====================


@registry.achievement(file="fruits-skill-pass-1")
def catch_skill_pass_1(score: Score, mode_vn: int, stats: Stats) -> bool:
    return (
        (score.mods & Mods.NOFAIL == 0) and 1 <= score.sr < 2 and mode_vn == Mode.CATCH
    )


@registry.achievement(file="fruits-skill-pass-2")
def catch_skill_pass_2(score: Score, mode_vn: int, stats: Stats) -> bool:
    return (
        (score.mods & Mods.NOFAIL == 0) and 2 <= score.sr < 3 and mode_vn == Mode.CATCH
    )


@registry.achievement(file="fruits-skill-pass-3")
def catch_skill_pass_3(score: Score, mode_vn: int, stats: Stats) -> bool:
    return (
        (score.mods & Mods.NOFAIL == 0) and 3 <= score.sr < 4 and mode_vn == Mode.CATCH
    )


@registry.achievement(file="fruits-skill-pass-4")
def catch_skill_pass_4(score: Score, mode_vn: int, stats: Stats) -> bool:
    return (
        (score.mods & Mods.NOFAIL == 0) and 4 <= score.sr < 5 and mode_vn == Mode.CATCH
    )


@registry.achievement(file="fruits-skill-pass-5")
def catch_skill_pass_5(score: Score, mode_vn: int, stats: Stats) -> bool:
    return (
        (score.mods & Mods.NOFAIL == 0) and 5 <= score.sr < 6 and mode_vn == Mode.CATCH
    )


@registry.achievement(file="fruits-skill-pass-6")
def catch_skill_pass_6(score: Score, mode_vn: int, stats: Stats) -> bool:
    return (
        (score.mods & Mods.NOFAIL == 0) and 6 <= score.sr < 7 and mode_vn == Mode.CATCH
    )


@registry.achievement(file="fruits-skill-pass-7")
def catch_skill_pass_7(score: Score, mode_vn: int, stats: Stats) -> bool:
    return (
        (score.mods & Mods.NOFAIL == 0) and 7 <= score.sr < 8 and mode_vn == Mode.CATCH
    )


@registry.achievement(file="fruits-skill-pass-8")
def catch_skill_pass_8(score: Score, mode_vn: int, stats: Stats) -> bool:
    return (
        (score.mods & Mods.NOFAIL == 0) and 8 <= score.sr < 9 and mode_vn == Mode.CATCH
    )


# ====================
# Skill FC Achievements
# ====================


@registry.achievement(file="fruits-skill-fc-1")
def catch_skill_fc_1(score: Score, mode_vn: int, stats: Stats) -> bool:
    return score.full_combo and 1 <= score.sr < 2 and mode_vn == Mode.CATCH


@registry.achievement(file="fruits-skill-fc-2")
def catch_skill_fc_2(score: Score, mode_vn: int, stats: Stats) -> bool:
    return score.full_combo and 2 <= score.sr < 3 and mode_vn == Mode.CATCH


@registry.achievement(file="fruits-skill-fc-3")
def catch_skill_fc_3(score: Score, mode_vn: int, stats: Stats) -> bool:
    return score.full_combo and 3 <= score.sr < 4 and mode_vn == Mode.CATCH


@registry.achievement(file="fruits-skill-fc-4")
def catch_skill_fc_4(score: Score, mode_vn: int, stats: Stats) -> bool:
    return score.full_combo and 4 <= score.sr < 5 and mode_vn == Mode.CATCH


@registry.achievement(file="fruits-skill-fc-5")
def catch_skill_fc_5(score: Score, mode_vn: int, stats: Stats) -> bool:
    return score.full_combo and 5 <= score.sr < 6 and mode_vn == Mode.CATCH


@registry.achievement(file="fruits-skill-fc-6")
def catch_skill_fc_6(score: Score, mode_vn: int, stats: Stats) -> bool:
    return score.full_combo and 6 <= score.sr < 7 and mode_vn == Mode.CATCH


@registry.achievement(file="fruits-skill-fc-7")
def catch_skill_fc_7(score: Score, mode_vn: int, stats: Stats) -> bool:
    return score.full_combo and 7 <= score.sr < 8 and mode_vn == Mode.CATCH


@registry.achievement(file="fruits-skill-fc-8")
def catch_skill_fc_8(score: Score, mode_vn: int, stats: Stats) -> bool:
    return score.full_combo and 8 <= score.sr < 9 and mode_vn == Mode.CATCH


# ====================
# Hit Count Achievements
# ====================


@registry.achievement(file="fruits-hits-20000")
def fruits_hits_20000(score: Score, mode_vn: int, stats: Stats) -> bool:
    return 20_000 <= stats.total_hits and mode_vn == Mode.CATCH


@registry.achievement(file="fruits-hits-200000")
def fruits_hits_200000(score: Score, mode_vn: int, stats: Stats) -> bool:
    return 200_000 <= stats.total_hits and mode_vn == Mode.CATCH


@registry.achievement(file="fruits-hits-2000000")
def fruits_hits_2000000(score: Score, mode_vn: int, stats: Stats) -> bool:
    return 2_000_000 <= stats.total_hits and mode_vn == Mode.CATCH


@registry.achievement(file="fruits-hits-20000000")
def fruits_hits_20000000(score: Score, mode_vn: int, stats: Stats) -> bool:
    return 20_000_000 <= stats.total_hits and mode_vn == Mode.CATCH


# ====================
# Rank Achievements
# ====================


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
