from __future__ import annotations

from app.achievements.registry import AchievementRegistry
from app.constants.mods import Mods
from app.models.score import Score
from app.models.stats import Stats

registry = AchievementRegistry()


@registry.achievement(file="all-intro-suddendeath")
def intro_sudden_death(score: Score, mode_vn: int, stats: Stats) -> bool:
    return (score.mods & Mods.SUDDENDEATH != 0) and score.passed


@registry.achievement(file="all-intro-perfect")
def intro_perfect(score: Score, mode_vn: int, stats: Stats) -> bool:
    return (score.mods & Mods.PERFECT != 0) and score.passed


@registry.achievement(file="all-intro-hardrock")
def intro_hardrock(score: Score, mode_vn: int, stats: Stats) -> bool:
    return (score.mods & Mods.HARDROCK != 0) and score.passed


@registry.achievement(file="all-intro-doubletime")
def intro_doubletime(score: Score, mode_vn: int, stats: Stats) -> bool:
    return (score.mods & Mods.DOUBLETIME != 0) and score.passed


@registry.achievement(file="all-intro-nightcore")
def intro_nightcore(score: Score, mode_vn: int, stats: Stats) -> bool:
    return (score.mods & Mods.NIGHTCORE != 0) and score.passed


@registry.achievement(file="all-intro-hidden")
def intro_hidden(score: Score, mode_vn: int, stats: Stats) -> bool:
    return (score.mods & Mods.HIDDEN != 0) and score.passed


@registry.achievement(file="all-intro-flashlight")
def intro_flashlight(score: Score, mode_vn: int, stats: Stats) -> bool:
    return (score.mods & Mods.FLASHLIGHT != 0) and score.passed


@registry.achievement(file="all-intro-easy")
def intro_easy(score: Score, mode_vn: int, stats: Stats) -> bool:
    return (score.mods & Mods.EASY != 0) and score.passed


@registry.achievement(file="all-intro-nofail")
def intro_nofail(score: Score, mode_vn: int, stats: Stats) -> bool:
    return (score.mods & Mods.NOFAIL != 0) and score.passed


@registry.achievement(file="all-intro-halftime")
def intro_halftime(score: Score, mode_vn: int, stats: Stats) -> bool:
    return (score.mods & Mods.HALFTIME != 0) and score.passed


@registry.achievement(file="all-intro-spunout")
def intro_spunout(score: Score, mode_vn: int, stats: Stats) -> bool:
    return (score.mods & Mods.SPUNOUT != 0) and score.passed
