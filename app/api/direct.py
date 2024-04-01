from __future__ import annotations

import asyncio
from typing import Any
from typing import Optional
from urllib.parse import unquote_plus
from urllib.parse import urlparse

from fastapi import Depends
from fastapi import Path
from fastapi import Query
from fastapi import status
from fastapi.responses import RedirectResponse

import app.state
import app.usecases
import config
from app.adapters import amplitude
from app.constants.ranked_status import RankedStatus
from app.models.cheesegull import CheesegullBeatmapset
from app.models.user import User
from app.usecases.cheesegull import format_beatmapset_to_direct
from app.usecases.cheesegull import format_beatmapset_to_direct_card
from app.usecases.user import authenticate_user


async def osu_direct(
    user: User = Depends(authenticate_user(Query, "u", "h")),
    ranked_status: int = Query(..., alias="r", ge=0, le=8),
    query: str = Query(..., alias="q"),
    mode: int = Query(..., alias="m", ge=-1, le=3),
    page_num: int = Query(..., alias="p"),
):
    search_url = f"{config.DIRECT_URL}/search"

    params: dict[str, Any] = {"amount": 101, "offset": page_num}

    if unquote_plus(query) not in ("Newest", "Top Rated", "Most Played"):
        params["query"] = query

    if mode != -1:
        params["mode"] = mode

    if ranked_status != 4:
        params["status"] = RankedStatus.from_direct(ranked_status).osu_api

    try:
        response = await app.state.services.http_client.get(
            search_url,
            params=params,
            timeout=5,
        )
        if response.status_code != status.HTTP_200_OK:
            return b"-1\nFailed to retrieve data from the beatmap mirror."

        beatmapsets = [
            CheesegullBeatmapset.model_validate(beatmapset)
            for beatmapset in response.json()
        ]
    except asyncio.exceptions.TimeoutError:
        return b"-1\n3rd party beatmap mirror we depend on timed out. Their server is likely down."

    beatmapset_count = len(beatmapsets)

    osu_direct_response = [
        format_beatmapset_to_direct(beatmapset) for beatmapset in beatmapsets
    ]

    if config.AMPLITUDE_API_KEY:
        asyncio.create_task(
            amplitude.track(
                event_name="osudirect_search",
                user_id=str(user.id),
                device_id=None,
                event_properties={
                    "query": query,
                    "page_num": page_num,
                    "game_mode": (
                        amplitude.format_mode(mode) if mode != -1 else "All modes"
                    ),
                    "ranked_status": ranked_status,
                },
            ),
        )

    # direct will only ever ask for 100 beatmaps
    # but if it *should* fetch the next page then it wants a hint there's more beatmaps
    direct_beatmapset_count = 101 if beatmapset_count >= 100 else beatmapset_count
    beatmapset_count_line = f"{direct_beatmapset_count}\n"

    return (beatmapset_count_line + "\n".join(osu_direct_response)).encode()


async def beatmap_card(
    user: User = Depends(authenticate_user(Query, "u", "h")),
    map_set_id: Optional[int] = Query(None, alias="s"),
    map_id: Optional[int] = Query(None, alias="b"),
):
    if map_set_id is None and map_id is not None:
        bmap = await app.usecases.beatmap.fetch_by_id(map_id)
        if bmap is None:
            return

        map_set_id = bmap.set_id

    url = f"{config.DIRECT_URL}/s/{map_set_id}"
    response = await app.state.services.http_client.get(url, timeout=5)
    if response.status_code != 200:
        return

    beatmapset = CheesegullBeatmapset.model_validate(response.json())

    if config.AMPLITUDE_API_KEY:
        asyncio.create_task(
            amplitude.track(
                event_name="osudirect_card_view",
                user_id=str(user.id),
                device_id=None,
                event_properties={
                    "beatmapset_id": map_set_id,
                    "beatmap_id": map_id,
                },
            ),
        )

    return format_beatmapset_to_direct_card(beatmapset).encode()


async def download_map(set_id: str = Path(...)):
    parsed_url = urlparse(config.DIRECT_URL)

    return RedirectResponse(
        url=f"https://{parsed_url.netloc}/d/{set_id}",
        status_code=status.HTTP_301_MOVED_PERMANENTLY,
    )
