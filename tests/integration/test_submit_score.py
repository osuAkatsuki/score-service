from __future__ import annotations

from base64 import b64encode

import httpx
import pytest
import respx
from databases import Database
from fastapi.testclient import TestClient

from tests.integration.helpers import DUMMY_REPLAY_BYTES
from tests.integration.helpers import encrypt_score_payload
from tests.integration.helpers import seed_beatmap
from tests.integration.helpers import seed_user

OSU_VERSION = "20210103"


async def test_happy_path_score_submission(
    client: TestClient,
    db: Database,
    respx_mock: respx.MockRouter,
) -> None:
    user = await seed_user(db)
    beatmap = await seed_beatmap(db)

    # Beatmaps service: the app looks up the beatmap by md5 over HTTP.
    respx_mock.get(
        "http://beatmaps.test/api/akatsuki/v1/beatmaps/lookup",
    ).mock(
        return_value=httpx.Response(
            200,
            json={
                "beatmap_id": beatmap["beatmap_id"],
                "beatmapset_id": beatmap["beatmap_id"] + 1,
                "beatmap_md5": beatmap["beatmap_md5"],
                "song_name": "Test Artist - Test Song [Test Diff]",
                "file_name": "test.osu",
                "ar": 9.0,
                "od": 9.0,
                "mode": 0,
                "max_combo": 1000,
                "hit_length": 120,
                "bpm": 180,
                "ranked": 2,
                "latest_update": 0,
                "ranked_status_freezed": 0,
                "playcount": 0,
                "passcount": 0,
                "rating": 10.0,
                "rankedby": None,
                "bancho_ranked_status": None,
                "count_circles": 500,
                "count_sliders": 500,
                "count_spinners": 0,
            },
        ),
    )

    # Performance service: return fixed pp/stars so the test stays deterministic.
    respx_mock.post("http://performance.test/api/v1/calculate").mock(
        return_value=httpx.Response(200, json=[{"pp": 123.4, "stars": 6.5}]),
    )

    # Bancho service: no multiplayer match for this user, and first-place chat
    # announce is swallowed as a 200.
    respx_mock.get("http://bancho.test/api/v1/playerMatchDetails").mock(
        return_value=httpx.Response(200, json={"message": "no match"}),
    )
    respx_mock.get("http://bancho.test/api/v1/fokabotMessage").mock(
        return_value=httpx.Response(200),
    )

    # Build the 16-token score payload in the exact positional shape the
    # osu! client serializes.
    score_tokens = [
        beatmap["beatmap_md5"],
        user["username"],
        "a" * 32,  # online checksum
        "100",  # n300
        "2",  # n100
        "1",  # n50
        "0",  # ngeki
        "0",  # nkatu
        "0",  # nmiss
        "123456",  # score
        "500",  # max_combo
        "True",  # full_combo
        "S",  # grade
        "0",  # mods
        "True",  # passed
        "0",  # mode
    ]
    score_data_b64, iv_b64, client_hash_b64 = encrypt_score_payload(
        score_tokens=score_tokens,
        client_hash=":".join(["0" * 32] * 5),
        osu_version=OSU_VERSION,
    )

    response = client.post(
        "/web/osu-submit-modular-selector.php",
        headers={"user-agent": "osu!"},
        data={
            "x": "0",
            "ft": "0",
            "fs": b64encode(b"visual-settings").decode(),
            "bmk": beatmap["beatmap_md5"],
            "sbk": "",
            "iv": iv_b64.decode(),
            "c1": "abc-unique-id",
            "st": "0",
            "pass": user["password_md5"],
            "osuver": OSU_VERSION,
            "s": client_hash_b64.decode(),
        },
        files=[
            # A plain form value (filename=None) under the key "score".
            ("score", (None, score_data_b64, "text/plain")),
            # And a file upload under the same key, matching what the
            # osu! client uploads as the replay.
            (
                "score",
                ("replay.osr", DUMMY_REPLAY_BYTES, "application/octet-stream"),
            ),
        ],
    )

    assert response.status_code == 200
    body = response.content
    assert b"chartId:beatmap" in body, body
    assert b"chartId:overall" in body, body
    assert f"onlineScoreId:".encode() in body

    # The score was persisted with the expected raw score value.
    score_row = await db.fetch_one(
        "SELECT score, pp, play_mode, completed FROM scores WHERE userid = :uid",
        {"uid": user["user_id"]},
    )
    assert score_row is not None
    assert score_row["score"] == 123456
    assert score_row["pp"] == pytest.approx(123.4, abs=1e-3)
    assert score_row["play_mode"] == 0
    assert score_row["completed"] == 3  # ScoreStatus.BEST

    # Stats were bumped.
    stats_row = await db.fetch_one(
        "SELECT playcount, total_score FROM user_stats WHERE user_id = :uid AND mode = 0",
        {"uid": user["user_id"]},
    )
    assert stats_row is not None
    assert stats_row["playcount"] == 1
    assert stats_row["total_score"] == 123456
