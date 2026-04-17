from __future__ import annotations

from typing import Any

import pytest
import respx
from fastapi.testclient import TestClient

from app.state.services import Database
from tests.integration.helpers import build_score_tokens
from tests.integration.helpers import submit_score_request


async def test_happy_path_score_submission(
    client: TestClient,
    db: Database,
    user: dict[str, Any],
    beatmap: dict[str, Any],
    external_service_stubs: dict[str, respx.Route],
) -> None:
    response = submit_score_request(
        client,
        password_md5=user["password_md5"],
        score_tokens=build_score_tokens(
            beatmap_md5=beatmap["beatmap_md5"],
            username=user["username"],
        ),
    )

    assert response.status_code == 200
    body = response.content
    assert b"chartId:beatmap" in body, body
    assert b"chartId:overall" in body, body
    assert b"onlineScoreId:" in body, body

    score_row = await db.fetch_one(
        "SELECT score, pp, play_mode, completed FROM scores WHERE userid = :uid",
        {"uid": user["user_id"]},
    )
    assert score_row is not None
    assert score_row["score"] == 123_456
    assert score_row["pp"] == pytest.approx(123.4, abs=1e-3)
    assert score_row["play_mode"] == 0
    assert score_row["completed"] == 3  # ScoreStatus.BEST

    stats_row = await db.fetch_one(
        "SELECT playcount, total_score FROM user_stats WHERE user_id = :uid AND mode = 0",
        {"uid": user["user_id"]},
    )
    assert stats_row is not None
    assert stats_row["playcount"] == 1
    assert stats_row["total_score"] == 123_456


async def test_duplicate_checksum_rejected(
    client: TestClient,
    db: Database,
    user: dict[str, Any],
    beatmap: dict[str, Any],
    external_service_stubs: dict[str, respx.Route],
) -> None:
    # Seed a score that already owns the online_checksum the submission will
    # use; the handler's uniqueness guard should reject the second attempt.
    duplicate_checksum = "c" * 32
    await db.execute(
        """
        INSERT INTO scores (
            beatmap_md5, userid, score, play_mode, completed, checksum
        ) VALUES (
            :md5, :uid, :score, 0, 3, :checksum
        )
        """,
        {
            "md5": beatmap["beatmap_md5"],
            "uid": user["user_id"],
            "score": 50_000,
            "checksum": duplicate_checksum,
        },
    )

    response = submit_score_request(
        client,
        password_md5=user["password_md5"],
        score_tokens=build_score_tokens(
            beatmap_md5=beatmap["beatmap_md5"],
            username=user["username"],
            online_checksum=duplicate_checksum,
        ),
    )

    assert response.status_code == 200
    assert response.content == b"error: no"

    # The pre-existing row is still the only one.
    count = await db.fetch_val(
        "SELECT COUNT(*) FROM scores WHERE userid = :uid",
        {"uid": user["user_id"]},
    )
    assert count == 1


async def test_failed_score_records_failed_status(
    client: TestClient,
    db: Database,
    user: dict[str, Any],
    beatmap: dict[str, Any],
    external_service_stubs: dict[str, respx.Route],
) -> None:
    response = submit_score_request(
        client,
        password_md5=user["password_md5"],
        score_tokens=build_score_tokens(
            beatmap_md5=beatmap["beatmap_md5"],
            username=user["username"],
            passed="False",
        ),
    )

    assert response.status_code == 200

    score_row = await db.fetch_one(
        "SELECT completed FROM scores WHERE userid = :uid",
        {"uid": user["user_id"]},
    )
    assert score_row is not None
    assert score_row["completed"] == 1  # ScoreStatus.FAILED

    # Ranked score is only bumped for passed BEST scores on ranked maps.
    stats_row = await db.fetch_one(
        "SELECT ranked_score, playcount FROM user_stats WHERE user_id = :uid AND mode = 0",
        {"uid": user["user_id"]},
    )
    assert stats_row is not None
    assert stats_row["ranked_score"] == 0
    # Playcount still bumps on any submission.
    assert stats_row["playcount"] == 1


async def test_bad_user_agent_restricts_user(
    client: TestClient,
    db: Database,
    user: dict[str, Any],
    beatmap: dict[str, Any],
    external_service_stubs: dict[str, respx.Route],
) -> None:
    # user.privileges starts at 3 (USER_NORMAL | USER_PUBLIC); after restrict
    # the USER_PUBLIC bit (1) is cleared, leaving 2.
    response = submit_score_request(
        client,
        password_md5=user["password_md5"],
        score_tokens=build_score_tokens(
            beatmap_md5=beatmap["beatmap_md5"],
            username=user["username"],
        ),
        user_agent="python-httpx/0.0.0",
    )

    assert response.status_code == 200

    updated = await db.fetch_one(
        "SELECT privileges, ban_datetime FROM users WHERE id = :uid",
        {"uid": user["user_id"]},
    )
    assert updated is not None
    assert updated["privileges"] & 1 == 0, "USER_PUBLIC bit should be cleared"
    assert updated["ban_datetime"] != 0


async def test_first_place_inserts_scores_first_row(
    client: TestClient,
    db: Database,
    user: dict[str, Any],
    beatmap: dict[str, Any],
    external_service_stubs: dict[str, respx.Route],
) -> None:
    # With no prior scores on the map, the submitted score becomes #1 and
    # the handler writes to scores_first. The chat announce is scheduled as
    # a background job; we don't assert on it here because it runs outside
    # the request lifecycle.
    response = submit_score_request(
        client,
        password_md5=user["password_md5"],
        score_tokens=build_score_tokens(
            beatmap_md5=beatmap["beatmap_md5"],
            username=user["username"],
        ),
    )

    assert response.status_code == 200

    first_row = await db.fetch_one(
        """
        SELECT userid, scoreid, mode, rx
          FROM scores_first
         WHERE beatmap_md5 = :md5
        """,
        {"md5": beatmap["beatmap_md5"]},
    )
    assert first_row is not None
    assert first_row["userid"] == user["user_id"]
    assert first_row["mode"] == 0
    assert first_row["rx"] == 0
