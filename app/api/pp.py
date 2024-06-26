from __future__ import annotations

import logging

from fastapi import Query
from fastapi import Response
from fastapi import status
from fastapi.responses import ORJSONResponse

import app.usecases
from app.constants.mode import Mode
from app.constants.mods import Mods
from app.usecases.performance import PerformanceScore

COMMON_PP_PERCENTAGES = (
    100.0,
    99.0,
    98.0,
    95.0,
)


async def calculate_pp(
    beatmap_id: int = Query(..., alias="b"),
    mods_arg: int = Query(0, alias="m"),
    mode_arg: int = Query(0, alias="g", ge=0, le=3),
    acc: float | None = Query(None, alias="a"),
    combo: int = Query(0, alias="max_combo"),
) -> Response:
    mods = Mods(mods_arg)
    mode = Mode.from_lb(mode_arg, mods_arg)

    beatmap = await app.usecases.akatsuki_beatmaps.fetch_by_id(beatmap_id)
    if not beatmap:
        return ORJSONResponse(
            content={"message": "Invalid/non-existent beatmap id."},
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    combo = combo if combo else beatmap.max_combo

    star_rating = 0.0
    pp_result: list[float] | float = 0.0
    if acc is None:
        performance_requests: list[PerformanceScore] = [
            {
                "beatmap_id": beatmap.id,
                "beatmap_md5": beatmap.md5,
                "mode": mode.as_vn,
                "mods": mods,
                "max_combo": combo,
                "accuracy": accuracy,
                "miss_count": 0,
            }
            for accuracy in COMMON_PP_PERCENTAGES
        ]

        performance_results = await app.usecases.performance.calculate_performances(
            performance_requests,
        )  # [(pp, stars)]

        pp_result = [pp for pp, stars in performance_results]

        # fetching first SR as they are all the same
        star_rating = performance_results[0][1]
    else:
        pp_result, star_rating = await app.usecases.performance.calculate_performance(
            beatmap_id=beatmap.id,
            beatmap_md5=beatmap.md5,
            mode=mode,
            mods=mods,
            max_combo=combo,
            accuracy=acc,
            miss_count=0,
        )

    logging.info(f"Handled PP calculation API request for {beatmap.song_name}!")

    return ORJSONResponse(
        {
            "status": 200,
            "message": "ok",
            "song_name": beatmap.song_name,
            "pp": pp_result,
            "length": beatmap.hit_length,
            "stars": star_rating,  # TODO is this wrong for common values?
            "ar": beatmap.ar,
            "bpm": beatmap.bpm,
        },
    )
