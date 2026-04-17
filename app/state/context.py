from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import aio_pika
import httpx
import redis.asyncio as aioredis
from fastapi import Request

from app.state.services import Database

if TYPE_CHECKING:
    from types_aiobotocore_s3.client import S3Client


@dataclass
class AppContext:
    """Process-wide service context. One instance per running app."""

    database: Database
    redis: aioredis.Redis
    http_client: httpx.AsyncClient
    amqp: aio_pika.abc.AbstractConnection | None
    amqp_channel: aio_pika.abc.AbstractChannel | None
    s3_client: S3Client | None


def get_context(request: Request) -> AppContext:
    """Return the :class:`AppContext` attached to the running app."""
    context: AppContext = request.app.state.context
    return context
