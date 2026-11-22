from __future__ import annotations

import pytest

from app.state import services
from app.state.services import Database
from app.usecases.multiplayer import insert_match_game_score


async def test_game_score_matches_the_beatmap_and_submission_window(
    db: Database,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(services, "database", db)
    submitted_at = await db.fetch_val("SELECT UNIX_TIMESTAMP()")
    match_id = 24
    game_id = await db.execute(
        """
        INSERT INTO match_games (match_id, beatmap_id, mode, scoring_type, team_type, start_time)
        VALUES (:match_id, 17, 0, 0, 0, FROM_UNIXTIME(:started_at))
        """,
        {"match_id": match_id, "started_at": submitted_at - 60},
    )
    for user_id, beatmap_id, submitted in [
        (1, 17, submitted_at),
        (2, 18, submitted_at),
        (3, 17, submitted_at + 1200),
    ]:
        await insert_match_game_score(
            match_id=match_id,
            game_id=game_id,
            user_id=user_id,
            mode=0,
            count_300=100,
            count_100=0,
            count_50=0,
            count_miss=0,
            count_geki=0,
            count_katu=0,
            score=10_000,
            max_combo=100,
            mods=0,
            passed=True,
            team=0,
            beatmap_id=beatmap_id,
            submitted_at=submitted,
            map_hit_length=60,
        )

    rows = await db.fetch_all("SELECT user_id FROM match_game_scores")
    assert rows == [{"user_id": 1}]
