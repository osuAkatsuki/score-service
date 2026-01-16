from __future__ import annotations

from app.achievements.registry import Registry
from app.constants.mode import Mode
from app.constants.mods import Mods
from app.models.score import Score
from app.models.stats import Stats

registry = Registry()


@registry.achievement(file="osu-skill-pass-1")
def rising_star(score: Score, mode_vn: int, stats: Stats) -> bool:
    return (score.mods & Mods.NOFAIL == 0) and 1 <= score.sr < 2 and mode_vn == Mode.STD


@registry.achievement(file="osu-skill-pass-2")
def constellation_prize(score: Score, mode_vn: int, stats: Stats) -> bool:
    return (score.mods & Mods.NOFAIL == 0) and 2 <= score.sr < 3 and mode_vn == Mode.STD


@registry.achievement(file="osu-skill-pass-3")
def building_confidence(score: Score, mode_vn: int, stats: Stats) -> bool:
    return (score.mods & Mods.NOFAIL == 0) and 3 <= score.sr < 4 and mode_vn == Mode.STD


@registry.achievement(file="osu-skill-pass-4")
def insanity_approaches(score: Score, mode_vn: int, stats: Stats) -> bool:
    return (score.mods & Mods.NOFAIL == 0) and 4 <= score.sr < 5 and mode_vn == Mode.STD


@registry.achievement(file="osu-skill-pass-5")
def these_clarion_skies(score: Score, mode_vn: int, stats: Stats) -> bool:
    return (score.mods & Mods.NOFAIL == 0) and 5 <= score.sr < 6 and mode_vn == Mode.STD


@registry.achievement(file="osu-skill-pass-6")
def above_and_beyond(score: Score, mode_vn: int, stats: Stats) -> bool:
    return (score.mods & Mods.NOFAIL == 0) and 6 <= score.sr < 7 and mode_vn == Mode.STD


@registry.achievement(file="osu-skill-pass-7")
def supremacy(score: Score, mode_vn: int, stats: Stats) -> bool:
    return (score.mods & Mods.NOFAIL == 0) and 7 <= score.sr < 8 and mode_vn == Mode.STD


@registry.achievement(file="osu-skill-pass-8")
def absolution(score: Score, mode_vn: int, stats: Stats) -> bool:
    return (score.mods & Mods.NOFAIL == 0) and 8 <= score.sr < 9 and mode_vn == Mode.STD


@registry.achievement(file="osu-skill-pass-9")
def event_horizon(score: Score, mode_vn: int, stats: Stats) -> bool:
    return (
        (score.mods & Mods.NOFAIL == 0) and 9 <= score.sr < 10 and mode_vn == Mode.STD
    )


@registry.achievement(file="osu-skill-pass-10")
def phantasm(score: Score, mode_vn: int, stats: Stats) -> bool:
    return (
        (score.mods & Mods.NOFAIL == 0) and 10 <= score.sr < 11 and mode_vn == Mode.STD
    )


@registry.achievement(file="osu-skill-fc-1")
def totality(score: Score, mode_vn: int, stats: Stats) -> bool:
    return score.full_combo and 1 <= score.sr < 2 and mode_vn == Mode.STD


@registry.achievement(file="osu-skill-fc-2")
def business_as_usual(score: Score, mode_vn: int, stats: Stats) -> bool:
    return score.full_combo and 2 <= score.sr < 3 and mode_vn == Mode.STD


@registry.achievement(file="osu-skill-fc-3")
def building_steam(score: Score, mode_vn: int, stats: Stats) -> bool:
    return score.full_combo and 3 <= score.sr < 4 and mode_vn == Mode.STD


@registry.achievement(file="osu-skill-fc-4")
def moving_forward(score: Score, mode_vn: int, stats: Stats) -> bool:
    return score.full_combo and 4 <= score.sr < 5 and mode_vn == Mode.STD


@registry.achievement(file="osu-skill-fc-5")
def paradigm_shift(score: Score, mode_vn: int, stats: Stats) -> bool:
    return score.full_combo and 5 <= score.sr < 6 and mode_vn == Mode.STD


@registry.achievement(file="osu-skill-fc-6")
def anguish_quelled(score: Score, mode_vn: int, stats: Stats) -> bool:
    return score.full_combo and 6 <= score.sr < 7 and mode_vn == Mode.STD


@registry.achievement(file="osu-skill-fc-7")
def never_give_up(score: Score, mode_vn: int, stats: Stats) -> bool:
    return score.full_combo and 7 <= score.sr < 8 and mode_vn == Mode.STD


@registry.achievement(file="osu-skill-fc-8")
def aberration(score: Score, mode_vn: int, stats: Stats) -> bool:
    return score.full_combo and 8 <= score.sr < 9 and mode_vn == Mode.STD


@registry.achievement(file="osu-skill-fc-9")
def chosen(score: Score, mode_vn: int, stats: Stats) -> bool:
    return score.full_combo and 9 <= score.sr < 10 and mode_vn == Mode.STD


@registry.achievement(file="osu-skill-fc-10")
def unfathomable(score: Score, mode_vn: int, stats: Stats) -> bool:
    return score.full_combo and 10 <= score.sr < 11 and mode_vn == Mode.STD
