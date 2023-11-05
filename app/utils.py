from __future__ import annotations

import asyncio
import logging
import os

from tenacity import retry
from tenacity import wait_exponential
from tenacity.stop import stop_after_attempt

import app.state
import config
from app.reliability import retry_if_exception_network_related

def make_safe(username: str) -> str:
    return username.rstrip().lower().replace(" ", "_")


@retry(
    retry=retry_if_exception_network_related(),
    wait=wait_exponential(),
    stop=stop_after_attempt(10),
    reraise=True,
)
async def channel_message(channel: str, message: str) -> None:
    response = await app.state.services.http_client.get(
        "http://localhost:5001/api/v1/fokabotMessage",
        params={
            "to": channel,
            "msg": message,
            "k": config.FOKABOT_KEY,
        },
        timeout=2,
    )
    response.raise_for_status()


async def send_announcement_as_side_effect(message: str) -> None:
    try:
        asyncio.create_task(channel_message("#announce", message))
    except asyncio.TimeoutError:
        logging.warning(
            "Failed to send message to #announce, bancho-service is likely down",
        )


async def check_online(user_id: int) -> bool:
    key = f"bancho:tokens:ids:{user_id}"
    return await app.state.services.redis.exists(key)


def ts_to_utc_ticks(ts: int) -> int:
    """Converts a UNIX timestamp to a UTC ticks. Equivalent to the reverse of
    C#'s `DateTime.ToUniversalTime().Ticks`.
    """

    return int(ts * 1e7) + 0x89F7FF5F7B58000
