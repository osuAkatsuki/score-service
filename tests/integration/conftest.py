from __future__ import annotations

from collections.abc import AsyncIterator
from collections.abc import Iterator

import pytest
import respx
from fastapi.testclient import TestClient

import config
from app.state.services import Database
from app.state.services import dsn


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
