from __future__ import annotations

import osu_orz
import pytest

import app.state.services
from app.adapters import s3
from app.usecases import replays


@pytest.fixture
def stored(monkeypatch: pytest.MonkeyPatch) -> dict[str, bytes]:
    objects: dict[str, bytes] = {}

    async def download(file_name: str, folder: str) -> bytes | None:
        return objects.get(f"{folder}/{file_name}")

    monkeypatch.setattr(app.state.services, "s3_client", object(), raising=False)
    monkeypatch.setattr(s3, "download", download)
    return objects


async def test_osr_is_preferred_over_orz(stored: dict[str, bytes]) -> None:
    stored["replays/1.osr"] = b"osr"
    stored["replays-orz/1.orz"] = b"not read"
    assert await replays.download_replay(1) == b"osr"


async def test_orz_is_decompressed_when_osr_is_missing(
    stored: dict[str, bytes],
) -> None:
    stored["replays-orz/1.orz"] = osu_orz.compress(b"replay", mode=osu_orz.Mode.OSU)
    assert await replays.download_replay(1) == b"replay"


async def test_none_when_neither_exists(stored: dict[str, bytes]) -> None:
    assert await replays.download_replay(1) is None
