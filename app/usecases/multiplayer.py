from __future__ import annotations

import logging
from dataclasses import dataclass

import app.state.services
from app.adapters import bancho_service
from app.utils.score_utils import calculate_accuracy


@dataclass
class MatchDetails:
    match_name: str
    match_id: int
    slot_id: int
    game_id: int
    team: int


async def get_player_match_details(user_id: int) -> MatchDetails | None:
    match_status = await bancho_service.get_player_match_details(user_id)
    if match_status is None:
        return None

    return MatchDetails(
        match_name=match_status.match_name,
        match_id=match_status.match_id,
        slot_id=match_status.slot_id,
        game_id=match_status.game_id,
        team=match_status.team,
    )


async def insert_match_game_score(
    match_id: int,
    game_id: int,
    user_id: int,
    mode: int,
    count_300: int,
    count_100: int,
    count_50: int,
    count_miss: int,
    count_geki: int,
    count_katu: int,
    score: int,
    max_combo: int,
    mods: int,
    passed: bool,
    team: int,
    *,
    beatmap_id: int,
    submitted_at: int,
    map_hit_length: int,
) -> None:
    accuracy = calculate_accuracy(
        n300=count_300,
        n100=count_100,
        n50=count_50,
        ngeki=count_geki,
        nkatu=count_katu,
        nmiss=count_miss,
        vanilla_mode=mode,
    )
    query = """
    INSERT INTO match_game_scores
        (id, match_id, game_id, user_id, mode, count_300, count_100, count_50, count_miss,
         count_geki, count_katu, score, accuracy, max_combo, mods, passed, team, timestamp)
    SELECT NULL, :match_id, :game_id, :user_id, :mode, :count_300, :count_100, :count_50, :count_miss,
           :count_geki, :count_katu, :score, :accuracy, :max_combo, :mods, :passed, :team, NOW()
      FROM match_games AS game
     WHERE game.id = :game_id
       AND game.match_id = :match_id
       AND game.beatmap_id = :beatmap_id
       AND MOD(game.mode, 4) = :mode
       AND TIMESTAMPDIFF(SECOND, game.start_time, FROM_UNIXTIME(:submitted_at))
           BETWEEN 0 AND :max_elapsed
       AND (game.end_time IS NULL OR
            FROM_UNIXTIME(:submitted_at) <= TIMESTAMPADD(SECOND, 120, game.end_time))
    """
    params = {
        "match_id": match_id,
        "game_id": game_id,
        "user_id": user_id,
        "mode": mode,
        "count_300": count_300,
        "count_100": count_100,
        "count_50": count_50,
        "count_miss": count_miss,
        "count_geki": count_geki,
        "count_katu": count_katu,
        "score": score,
        "accuracy": accuracy,
        "max_combo": max_combo,
        "mods": mods,
        "passed": passed,
        "team": team,
        "beatmap_id": beatmap_id,
        "submitted_at": submitted_at,
        # Allow time for loading, breaks, slower mods, and client upload retries.
        "max_elapsed": map_hit_length * 2 + 300,
    }
    try:
        await app.state.services.database.execute(query, params)
    except Exception:
        logging.exception("Failed to insert match game score", extra=params)
