from __future__ import annotations

from fastapi import Depends
from fastapi import Response
from fastapi.responses import ORJSONResponse

from app.state.context import AppContext
from app.state.context import get_context


async def get_seasonals(
    context: AppContext = Depends(get_context),
) -> Response:
    db_seasonals = await context.database.fetch_all(
        "SELECT url FROM seasonal_bg WHERE enabled = 1",
    )

    return ORJSONResponse([seasonal["url"] for seasonal in db_seasonals])
