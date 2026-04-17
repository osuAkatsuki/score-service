"""Composition-root container holding every shared service.

This is the beginning of the migration away from module-level globals on
:mod:`app.state.services`. New code should prefer receiving an
:class:`AppContainer` via ``Depends(get_container)`` instead of reaching
into ``app.state.services.X`` directly. The module globals remain in
place for backwards compatibility and reference the same object instances
as the container fields.
"""
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
class AppContainer:
    """Process-wide service container. One instance per running app."""

    database: Database
    redis: aioredis.Redis
    http_client: httpx.AsyncClient
    amqp: aio_pika.abc.AbstractConnection | None
    amqp_channel: aio_pika.abc.AbstractChannel | None
    s3_client: S3Client | None


def get_container(request: Request) -> AppContainer:
    """Return the :class:`AppContainer` attached to the running app."""
    container: AppContainer = request.app.state.container
    return container
