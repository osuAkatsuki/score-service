from __future__ import annotations

import os
from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

# Point the app at the docker-compose.test.yml services (or whatever TEST_*
# values CI supplies). Defaults match docker-compose.test.yml so
# `docker compose -f docker-compose.test.yml up -d && pytest -m integration`
# works out of the box.
_INTEGRATION_ENV: dict[str, str] = {
    "WRITE_DB_HOST": os.environ.get("TEST_DB_HOST", "127.0.0.1"),
    "WRITE_DB_PORT": os.environ.get("TEST_DB_PORT", "3307"),
    "WRITE_DB_USER": os.environ.get("TEST_DB_USER", "test"),
    "WRITE_DB_PASS": os.environ.get("TEST_DB_PASS", "test"),
    "WRITE_DB_NAME": os.environ.get("TEST_DB_NAME", "score_service_test"),
    "READ_DB_HOST": os.environ.get("TEST_DB_HOST", "127.0.0.1"),
    "READ_DB_PORT": os.environ.get("TEST_DB_PORT", "3307"),
    "READ_DB_USER": os.environ.get("TEST_DB_USER", "test"),
    "READ_DB_PASS": os.environ.get("TEST_DB_PASS", "test"),
    "READ_DB_NAME": os.environ.get("TEST_DB_NAME", "score_service_test"),
    "REDIS_HOST": os.environ.get("TEST_REDIS_HOST", "127.0.0.1"),
    "REDIS_PORT": os.environ.get("TEST_REDIS_PORT", "6380"),
    "REDIS_USER": "default",
    "REDIS_PASS": "",
    "REDIS_DB": "0",
    "REDIS_USE_SSL": "false",
}
for _key, _value in _INTEGRATION_ENV.items():
    os.environ[_key] = _value


def pytest_collection_modifyitems(
    config: pytest.Config,
    items: list[pytest.Item],
) -> None:
    """Auto-mark every test under tests/integration/ with `integration`."""
    for item in items:
        if "tests/integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)


@pytest.fixture(scope="session")
def client() -> Iterator[TestClient]:
    # Import after env overrides above so config.py reads the right values.
    from app.init_api import asgi_app

    with TestClient(asgi_app) as test_client:
        yield test_client
