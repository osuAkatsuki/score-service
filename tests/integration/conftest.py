from __future__ import annotations

from collections.abc import AsyncIterator
from collections.abc import Iterator
from typing import Any

import httpx
import pytest
import respx
from fastapi.testclient import TestClient

import config
from app.state.services import Database
from app.state.services import dsn
from tests.integration.helpers import seed_beatmap
from tests.integration.helpers import seed_pp_limits
from tests.integration.helpers import seed_user
from tests.integration.helpers import seed_user_stats


@pytest.fixture(scope="session")
def client() -> Iterator[TestClient]:
    # Imported here, not at module level, so the root conftest's
    # load_dotenv(".env.test") runs first and populates the env vars
    # config.py reads.
    from app.init_api import asgi_app

    with TestClient(asgi_app) as test_client:
        yield test_client


@pytest.fixture
async def db(client: TestClient) -> AsyncIterator[Database]:
    # Dedicated test-owned Database, separate from app.state.services.database.
    # Seeds, TRUNCATE cleanup, and assertions go through this connection; the
    # app keeps its own pool for the HTTP request under test. Keeping them
    # separate is the usual pattern for Django/SQLAlchemy-style test suites —
    # DDL and fixture state live with the harness, request state with the
    # app. MySQL autocommit makes writes visible across both immediately.
    database = Database(
        read_dsn=dsn(
            dialect="mysql",
            driver="asyncmy",
            username=config.READ_DB_USER,
            password=config.READ_DB_PASS,
            host=config.READ_DB_HOST,
            port=config.READ_DB_PORT,
            database=config.READ_DB_NAME,
        ),
        write_dsn=dsn(
            dialect="mysql",
            driver="asyncmy",
            username=config.WRITE_DB_USER,
            password=config.WRITE_DB_PASS,
            host=config.WRITE_DB_HOST,
            port=config.WRITE_DB_PORT,
            database=config.WRITE_DB_NAME,
        ),
    )
    await database.connect()
    try:
        yield database
    finally:
        await database.disconnect()


# Tables excluded from per-test cleanup. The schema_migrations table is
# populated by go-migrate when the container brings up the DB; the rest
# are DB-local infra, not app data.
_CLEAN_DB_EXCLUDED_TABLES: frozenset[str] = frozenset(
    {"akatsuki_schema_migrations"},
)


@pytest.fixture(autouse=True)
async def clean_db(db: Database) -> AsyncIterator[None]:
    rows = await db.fetch_all(
        """
        SELECT table_name FROM information_schema.tables
         WHERE table_schema = DATABASE() AND table_type = 'BASE TABLE'
        """,
    )
    tables = [
        row["TABLE_NAME"]
        for row in rows
        if row["TABLE_NAME"] not in _CLEAN_DB_EXCLUDED_TABLES
    ]

    await db.execute("SET FOREIGN_KEY_CHECKS = 0")
    for table in tables:
        await db.execute(f"TRUNCATE TABLE `{table}`")
    await db.execute("SET FOREIGN_KEY_CHECKS = 1")
    yield


@pytest.fixture
def respx_mock() -> Iterator[respx.MockRouter]:
    # assert_all_called=False: individual tests stub only the endpoints they
    # care about; unreferenced stubs don't fail the test.
    with respx.mock(assert_all_called=False) as mock:
        yield mock


@pytest.fixture(autouse=True)
async def pp_limits(db: Database) -> None:
    # Production has pp_limits seeded; tests need it too or every score
    # submission > 0 pp trips the pp-cap restrict guard.
    await seed_pp_limits(db)


@pytest.fixture
async def user(db: Database) -> dict[str, Any]:
    seeded = await seed_user(db)
    await seed_user_stats(db, user_id=seeded["user_id"])
    return seeded


@pytest.fixture
async def beatmap(db: Database) -> dict[str, Any]:
    return await seed_beatmap(db)


@pytest.fixture
def external_service_stubs(
    respx_mock: respx.MockRouter,
    beatmap: dict[str, Any],
) -> dict[str, respx.Route]:
    """Default stubs for the three services submit_score calls into.

    Tests use the returned dict to assert that a given route was or was not
    hit (e.g. bancho fokabot-message for first-place announces / restricts).
    """
    beatmaps_route = respx_mock.get(
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
    performance_route = respx_mock.post(
        "http://performance.test/api/v1/calculate",
    ).mock(
        return_value=httpx.Response(200, json=[{"pp": 123.4, "stars": 6.5}]),
    )
    match_details_route = respx_mock.get(
        "http://bancho.test/api/v1/playerMatchDetails",
    ).mock(
        return_value=httpx.Response(200, json={"message": "no match"}),
    )
    fokabot_route = respx_mock.get(
        "http://bancho.test/api/v1/fokabotMessage",
    ).mock(
        return_value=httpx.Response(200),
    )
    return {
        "beatmaps": beatmaps_route,
        "performance": performance_route,
        "match_details": match_details_route,
        "fokabot": fokabot_route,
    }
