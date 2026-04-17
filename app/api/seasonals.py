from __future__ import annotations

from fastapi import Depends
from fastapi import Response
from fastapi.responses import ORJSONResponse

from app.state.container import AppContainer
from app.state.container import get_container


async def get_seasonals(
    container: AppContainer = Depends(get_container),
) -> Response:
    db_seasonals = await container.database.fetch_all(
        "SELECT url FROM seasonal_bg WHERE enabled = 1",
    )

    return ORJSONResponse([seasonal["url"] for seasonal in db_seasonals])
