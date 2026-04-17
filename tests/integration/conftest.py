from __future__ import annotations

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient


def pytest_collection_modifyitems(
    config: pytest.Config,
    items: list[pytest.Item],
) -> None:
    # Auto-mark every test under tests/integration/ with `integration`.
    for item in items:
        if "tests/integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)


@pytest.fixture(scope="session")
def client() -> Iterator[TestClient]:
    # Imported here, not at module level, so the root conftest's
    # load_dotenv(".env.test") runs first and populates the env vars
    # config.py reads.
    from app.init_api import asgi_app

    with TestClient(asgi_app) as test_client:
        yield test_client
