from __future__ import annotations

import logging
from typing import Optional
import hashlib

from fastapi import Query
from fastapi import status
from fastapi.responses import ORJSONResponse

import app.state.services
import config
import app.usecases
from app.constants.mode import Mode
from app.constants.mods import Mods
from app.usecases.performance import PerformanceScore

COMMON_PP_PERCENTAGES = (
    100.0,
    99.0,
    98.0,
    97.0,
    96.0,
    95.0,
    90.0,
)


async def calculate_pp(
    beatmap_id: int = Query(..., alias="b"),
    mods_arg: int = Query(0, alias="m"),
    mode_arg: int = Query(0, alias="g", ge=0, le=3),
    acc: Optional[float] = Query(None, alias="a"),
    combo: int = Query(0, alias="max_combo"),
):
    mods = Mods(mods_arg)
    mode = Mode.from_lb(mode_arg, mods_arg)

    use_common_pp_percentages = acc is None

    beatmap = await app.usecases.beatmap.id_from_api(beatmap_id, should_save=False)
    if not beatmap:
        return ORJSONResponse(
            content={"message": "Invalid/non-existent beatmap id."},
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    combo = combo if combo else beatmap.max_combo

    # make sure beatmap file exists on s3
    try:
        s3_response = await app.state.services.s3_client.get_object(
            Bucket=config.AWS_BUCKET_NAME,
            Key=f"beatmaps/{beatmap.id}.osu",
        )
    except Exception as exc: # TODO: more specific err
        print("Exc type", exc)
        beatmap_file_found = False
    else:
        # file was found on s3; make sure it's up to date
        response_body = await s3_response["Body"].read()
        is_up_to_date = hashlib.md5(response_body).hexdigest() == beatmap.md5

        if is_up_to_date:
            beatmap_file_found = True
        else:
            # not up to date - fetch from osu!api
            async with app.state.services.http.get(
                f"https://old.ppy.sh/osu/{beatmap.id}",
            ) as response:
                if response.status != 200:
                    beatmap_file_found = False
                else:
                    try:
                        await app.state.services.s3_client.put_object(
                            Bucket=config.AWS_BUCKET_NAME,
                            Key=f"beatmaps/{beatmap.id}.osu",
                            Body=await response.read(),
                        )
                    except Exception as exc:
                        print("Exc type", exc)
                        beatmap_file_found = False
                    else:
                        beatmap_file_found = True

    if not beatmap_file_found:
        return ORJSONResponse(
            content={"message": "Invalid/non-existent beatmap id."},
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    star_rating = pp_result = 0.0
    if use_common_pp_percentages:
        pp_requests: list[PerformanceScore] = [
            {
                "beatmap_id": beatmap.id,
                "mode": mode.as_vn,
                "mods": mods,
                "max_combo": combo,
                "accuracy": accuracy,
                "miss_count": 0,
            }
            for accuracy in COMMON_PP_PERCENTAGES
        ]

        pp_result = [
            pp
            for pp, _ in await app.usecases.performance.calculate_performances(
                pp_requests,
            )
        ]
    else:
        pp_result, star_rating = await app.usecases.performance.calculate_performance(
            beatmap.id,
            mode,
            mods,
            combo,
            acc,
            0,  # miss count
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
