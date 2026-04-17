from __future__ import annotations

from collections.abc import AsyncIterator
from collections.abc import Iterator

import pytest
import respx
from fastapi.testclient import TestClient

from app.state.services import Database


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
    # A *separate* Database instance, scoped to the test function. The app's
    # own pool (app.state.services.database) lives on the TestClient's event
    # loop and can't be shared across pytest-asyncio's per-test loops.
    # Uses the same app.state.services.Database wrapper as production so tests
    # exercise the read/write-split path the real code uses, with MySQL
    # autocommit making writes visible across connections immediately.
    import config

    read_dsn = (
        f"mysql+asyncmy://{config.READ_DB_USER}:{config.READ_DB_PASS}"
        f"@{config.READ_DB_HOST}:{config.READ_DB_PORT}/{config.READ_DB_NAME}"
    )
    write_dsn = (
        f"mysql+asyncmy://{config.WRITE_DB_USER}:{config.WRITE_DB_PASS}"
        f"@{config.WRITE_DB_HOST}:{config.WRITE_DB_PORT}/{config.WRITE_DB_NAME}"
    )
    database = Database(read_dsn=read_dsn, write_dsn=write_dsn)
    await database.connect()
    try:
        yield database
    finally:
        await database.disconnect()


# Tables mutated during score submission. Truncated between tests so each
# test starts from a clean slate without having to manage its own undo.
_MUTATED_TABLES: tuple[str, ...] = (
    "scores",
    "scores_first",
    "users",
    "user_stats",
    "beatmaps",
    "user_beatmaps",
    "users_achievements",
)


@pytest.fixture(autouse=True)
async def clean_db(db: Database) -> AsyncIterator[None]:
    await db.execute("SET FOREIGN_KEY_CHECKS = 0")
    for table in _MUTATED_TABLES:
        await db.execute(f"TRUNCATE TABLE {table}")
    await db.execute("SET FOREIGN_KEY_CHECKS = 1")
    yield


@pytest.fixture
def respx_mock() -> Iterator[respx.MockRouter]:
    # assert_all_called=False: individual tests stub only the endpoints they
    # care about; unreferenced stubs don't fail the test.
    with respx.mock(assert_all_called=False) as mock:
        yield mock
