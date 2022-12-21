from __future__ import annotations

from typing import TypedDict

import app.state
import config
from app.constants.mode import Mode


class PerformanceScore(TypedDict):
    beatmap_id: int
    mode: int
    mods: int
    max_combo: int
    accuracy: float
    miss_count: int


async def calculate_performances(
    scores: list[PerformanceScore],
) -> list[tuple[float, float]]:
    async with app.state.services.http.post(
        f"{config.PERFORMANCE_SERVICE_URL}/api/v1/calculate",
        json=scores,
    ) as resp:
        if resp.status != 200:
            return [(0.0, 0.0)] * len(scores)

        data = await resp.json()
        return [(result["pp"], result["stars"]) for result in data]


# TODO: split sr & pp calculations
async def calculate_performance(
    beatmap_id: int,
    mode: Mode,
    mods: int,
    max_combo: int,
    acc: float,
    nmiss: int,
) -> tuple[float, float]:
    async with app.state.services.http.post(
        f"{config.PERFORMANCE_SERVICE_URL}/api/v1/calculate",
        json=[
            {
                "beatmap_id": beatmap_id,
                "mode": mode.as_vn,
                "mods": mods,
                "max_combo": max_combo,
                "accuracy": acc,
                "miss_count": nmiss,
            },
        ],
    ) as resp:
        if resp.status != 200:
            return 0.0, 0.0

        data = (await resp.json())[0]
        return data["pp"], data["stars"]
