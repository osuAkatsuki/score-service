from __future__ import annotations

from app.achievements.registry import AchievementRegistry
from app.constants.mode import Mode
from app.constants.ranked_status import RankedStatus
from app.models.score import Score
from app.models.stats import Stats
from app.utils.score_utils import calculate_grade

registry = AchievementRegistry()


@registry.achievement(file="all-secret-bunny")
def dont_let_bunny_distract(score: Score, mode_vn: int, stats: Stats) -> bool:
    """PFC Chatmonchy - Make Up! Make Up! (any difficulty)"""
    # TODO: Requires beatmap lookup to check artist/title
    # Would need to fetch beatmap data from beatmaps-service
    return False


@registry.achievement(file="all-secret-sranker")
def s_ranker(score: Score, mode_vn: int, stats: Stats) -> bool:
    """Get five S (or SS) ranks on different maps within 24 hours"""
    # TODO: Requires tracking recent scores within time window
    # Would need to query database for user's scores in last 24h
    return False


@registry.achievement(file="all-secret-improved")
def most_improved(score: Score, mode_vn: int, stats: Stats) -> bool:
    """Get a D rank, then achieve an A+ on same map within 24 hours"""
    # TODO: Requires tracking score history per beatmap with timestamps
    # Would need to query previous scores on same beatmap
    return False


@registry.achievement(file="osu-secret-dancer")
def nonstop_dancer(score: Score, mode_vn: int, stats: Stats) -> bool:
    """Pass Yoko Ishida - paraparaMAX I with over 3,000,000 score (osu!std)"""
    # TODO: Requires beatmap lookup to check artist/title
    # Would need to fetch beatmap data from beatmaps-service
    return False


@registry.achievement(file="all-secret-consolation")
def consolation_prize(score: Score, mode_vn: int, stats: Stats) -> bool:
    """Get a D rank on any map with a play above 100,000 score"""
    if not score.passed or score.score < 100_000:
        return False

    grade = calculate_grade(
        vanilla_mode=mode_vn,
        mods=score.mods.value,
        acc=score.acc,
        n300=score.n300,
        n100=score.n100,
        n50=score.n50,
        nmiss=score.nmiss,
    )
    return grade == "D"


@registry.achievement(file="all-secret-challenge")
def challenge_accepted(score: Score, mode_vn: int, stats: Stats) -> bool:
    """Pass any approved map with an A rank or higher"""
    # TODO: Requires beatmap ranked status lookup
    # Would need to fetch beatmap data to check if approved
    # For now, return False as we can't verify approved status during score submission
    return False


@registry.achievement(file="all-secret-stumbler")
def stumbler(score: Score, mode_vn: int, stats: Stats) -> bool:
    """PFC any map with less than 85% accuracy"""
    return score.full_combo and score.acc < 85.0


@registry.achievement(file="all-secret-jackpot")
def jackpot(score: Score, mode_vn: int, stats: Stats) -> bool:
    """Pass a map where every digit of score is identical (e.g., 7,777,777)"""
    if not score.passed:
        return False

    # Convert score to string and check if all digits are the same
    score_str = str(score.score)
    if len(score_str) < 2:
        return False

    first_digit = score_str[0]
    return all(digit == first_digit for digit in score_str)


@registry.achievement(file="all-secret-quickdraw")
def quick_draw(score: Score, mode_vn: int, stats: Stats) -> bool:
    """Be the first to submit a score on any ranked/qualified map"""
    # TODO: Requires checking if this is the first score on the beatmap
    # Would need to query database for existing scores on this map
    return False


@registry.achievement(file="all-secret-obsessed")
def obsessed(score: Score, mode_vn: int, stats: Stats) -> bool:
    """Retry a map 100+ times and pass within 24 hours"""
    # TODO: Requires tracking retry count and time window
    # Would need to count failed attempts on same beatmap in last 24h
    return False


@registry.achievement(file="all-secret-nonstop")
def nonstop(score: Score, mode_vn: int, stats: Stats) -> bool:
    """PFC any map with drain time 8:41 or longer (521 seconds)"""
    # TODO: Requires beatmap drain time lookup
    # Would need to fetch beatmap data from beatmaps-service
    # time_elapsed could be used but it's not currently stored in DB
    return False


@registry.achievement(file="all-secret-jackofalltrades")
def jack_of_all_trades(score: Score, mode_vn: int, stats: Stats) -> bool:
    """Reach 5,000+ playcount in all four gamemodes"""
    # TODO: Requires fetching playcount across all modes
    # Stats object only contains current mode data
    # Would need to query user_stats for all 4 modes
    return False


@registry.achievement(file="mania-secret-twin")
def twin_perspectives(score: Score, mode_vn: int, stats: Stats) -> bool:
    """Pass any ranked mania map with 100 combo or more"""
    # TODO: Requires beatmap ranked status check (RANKED or APPROVED only, not LOVED/QUALIFIED)
    # unlock_achievements() doesn't receive Beatmap object, only Score and Stats
    # Current call site checks beatmap.has_leaderboard which includes LOVED/QUALIFIED
    # Need to either:
    #   1. Add Beatmap parameter to unlock_achievements (breaking change to all achievements)
    #   2. Add ranked_status field to Score object
    #   3. Filter at call site before checking achievements
    return False
