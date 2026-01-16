from __future__ import annotations

from app.achievements.registry import Registry
from app.constants.mode import Mode
from app.constants.mods import Mods
from app.models.score import Score
from app.models.stats import Stats

registry = Registry()


@registry.achievement(file="taiko-skill-pass-1")
def my_first_don(score: Score, mode_vn: int, stats: Stats) -> bool:
    return (
        (score.mods & Mods.NOFAIL == 0) and 1 <= score.sr < 2 and mode_vn == Mode.TAIKO
    )


@registry.achievement(file="taiko-skill-pass-2")
def katsu_katsu_katsu(score: Score, mode_vn: int, stats: Stats) -> bool:
    return (
        (score.mods & Mods.NOFAIL == 0) and 2 <= score.sr < 3 and mode_vn == Mode.TAIKO
    )


@registry.achievement(file="taiko-skill-pass-3")
def not_even_trying(score: Score, mode_vn: int, stats: Stats) -> bool:
    return (
        (score.mods & Mods.NOFAIL == 0) and 3 <= score.sr < 4 and mode_vn == Mode.TAIKO
    )


@registry.achievement(file="taiko-skill-pass-4")
def face_your_demons(score: Score, mode_vn: int, stats: Stats) -> bool:
    return (
        (score.mods & Mods.NOFAIL == 0) and 4 <= score.sr < 5 and mode_vn == Mode.TAIKO
    )


@registry.achievement(file="taiko-skill-pass-5")
def the_demon_within(score: Score, mode_vn: int, stats: Stats) -> bool:
    return (
        (score.mods & Mods.NOFAIL == 0) and 5 <= score.sr < 6 and mode_vn == Mode.TAIKO
    )


@registry.achievement(file="taiko-skill-pass-6")
def drumbreaker(score: Score, mode_vn: int, stats: Stats) -> bool:
    return (
        (score.mods & Mods.NOFAIL == 0) and 6 <= score.sr < 7 and mode_vn == Mode.TAIKO
    )


@registry.achievement(file="taiko-skill-pass-7")
def the_godfather(score: Score, mode_vn: int, stats: Stats) -> bool:
    return (
        (score.mods & Mods.NOFAIL == 0) and 7 <= score.sr < 8 and mode_vn == Mode.TAIKO
    )


@registry.achievement(file="taiko-skill-pass-8")
def rhythm_incarnate(score: Score, mode_vn: int, stats: Stats) -> bool:
    return (
        (score.mods & Mods.NOFAIL == 0) and 8 <= score.sr < 9 and mode_vn == Mode.TAIKO
    )


@registry.achievement(file="taiko-skill-fc-1")
def keeping_time(score: Score, mode_vn: int, stats: Stats) -> bool:
    return score.full_combo and 1 <= score.sr < 2 and mode_vn == Mode.TAIKO


@registry.achievement(file="taiko-skill-fc-2")
def to_your_own_beat(score: Score, mode_vn: int, stats: Stats) -> bool:
    return score.full_combo and 2 <= score.sr < 3 and mode_vn == Mode.TAIKO


@registry.achievement(file="taiko-skill-fc-3")
def big_drums(score: Score, mode_vn: int, stats: Stats) -> bool:
    return score.full_combo and 3 <= score.sr < 4 and mode_vn == Mode.TAIKO


@registry.achievement(file="taiko-skill-fc-4")
def adversity_overcome(score: Score, mode_vn: int, stats: Stats) -> bool:
    return score.full_combo and 4 <= score.sr < 5 and mode_vn == Mode.TAIKO


@registry.achievement(file="taiko-skill-fc-5")
def demonslayer(score: Score, mode_vn: int, stats: Stats) -> bool:
    return score.full_combo and 5 <= score.sr < 6 and mode_vn == Mode.TAIKO


@registry.achievement(file="taiko-skill-fc-6")
def rhythms_call(score: Score, mode_vn: int, stats: Stats) -> bool:
    return score.full_combo and 6 <= score.sr < 7 and mode_vn == Mode.TAIKO


@registry.achievement(file="taiko-skill-fc-7")
def time_everlasting(score: Score, mode_vn: int, stats: Stats) -> bool:
    return score.full_combo and 7 <= score.sr < 8 and mode_vn == Mode.TAIKO


@registry.achievement(file="taiko-skill-fc-8")
def the_drummers_throne(score: Score, mode_vn: int, stats: Stats) -> bool:
    return score.full_combo and 8 <= score.sr < 9 and mode_vn == Mode.TAIKO


@registry.achievement(file="taiko-hits-30000")
def hits_30000(score: Score, mode_vn: int, stats: Stats) -> bool:
    return 30_000 <= stats.total_hits and mode_vn == Mode.TAIKO


@registry.achievement(file="taiko-hits-300000")
def hits_300000(score: Score, mode_vn: int, stats: Stats) -> bool:
    return 300_000 <= stats.total_hits and mode_vn == Mode.TAIKO


@registry.achievement(file="taiko-hits-3000000")
def hits_3000000(score: Score, mode_vn: int, stats: Stats) -> bool:
    return 3_000_000 <= stats.total_hits and mode_vn == Mode.TAIKO
