from __future__ import annotations

import asyncio

import osu_orz

import app.state.services
from app.adapters import s3


async def save_replay(score_id: int, replay_data: bytes) -> None:
    if app.state.services.s3_client is not None:
        await s3.upload(replay_data, file_name=f"{score_id}.osr", folder="replays")
        return


async def download_replay(score_id: int) -> bytes | None:
    replay_data = None

    if app.state.services.s3_client is not None:
        replay_data = await s3.download(file_name=f"{score_id}.osr", folder="replays")
        if replay_data is not None:
            return replay_data

        # Replays converted to ORZ may no longer have an .osr copy.
        orz_data = await s3.download(file_name=f"{score_id}.orz", folder="replays-orz")
        if orz_data is not None:
            replay_data = await asyncio.to_thread(osu_orz.decompress, orz_data)

    return replay_data
