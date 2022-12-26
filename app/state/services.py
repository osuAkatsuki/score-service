from __future__ import annotations

from typing import Any
from typing import Mapping
from typing import TYPE_CHECKING

import aio_pika
import aiohttp
import aioredis
import databases
from sqlalchemy.sql import ClauseElement

if TYPE_CHECKING:
    from types_aiobotocore_s3.client import S3Client

import config


s3_client: S3Client
http: aiohttp.ClientSession

amqp: aio_pika.RobustConnection
amqp_channel: aio_pika.RobustChannel


class Database:
    def __init__(self, read_dsn: str, write_dsn: str) -> None:
        self.read_database = databases.Database(read_dsn)
        self.write_database = databases.Database(write_dsn)

    async def connect(self) -> None:
        await self.read_database.connect()
        await self.write_database.connect()

    async def disconnect(self) -> None:
        await self.read_database.disconnect()
        await self.write_database.disconnect()

    async def fetch_all(
        self,
        query: ClauseElement | str,
        values: dict | None = None,
    ) -> list[Mapping]:
        rows = await self.read_database.fetch_all(query, values)  # type: ignore
        return [row._mapping for row in rows]

    async def fetch_one(
        self,
        query: ClauseElement | str,
        values: dict | None = None,
    ) -> Mapping | None:
        row = await self.read_database.fetch_one(query, values)  # type: ignore
        if row is None:
            return None

        return row._mapping

    async def fetch_val(
        self,
        query: ClauseElement | str,
        values: dict | None = None,
        column: Any = 0,
    ) -> Any:
        val = await self.read_database.fetch_val(query, values, column)  # type: ignore
        return val

    async def execute(
        self,
        query: ClauseElement | str,
        values: dict | None = None,
    ) -> Any:
        result = await self.write_database.execute(query, values)  # type: ignore
        return result

    async def execute_many(
        self,
        query: ClauseElement | str,
        values: list,
    ) -> None:
        await self.write_database.execute_many(query, values)


def sql_dsn(driver: str, host: str, port: int, username: str, password: str, db: str) -> str:
    return f"{driver}://{username}:{password}@{host}:{port}/{db}"


database = Database(
    read_dsn = sql_dsn(
        driver="mysql+asyncmy",
        host=config.READ_DB_HOST,
        port=config.READ_DB_PORT,
        username=config.READ_DB_USER,
        password=config.READ_DB_PASS,
        db=config.READ_DB_NAME,
    ),
    write_dsn = sql_dsn(
        driver="mysql+asyncmy",
        host=config.WRITE_DB_HOST,
        port=config.WRITE_DB_PORT,
        username=config.WRITE_DB_USER,
        password=config.WRITE_DB_PASS,
        db=config.WRITE_DB_NAME,
    ),
)

def redis_dsn(host: str, port: int, username: str | None, password: str | None, db: int | None) -> str:
    if username is None and password is None:
        base =  f"redis://{host}:{port}/{db}"
    else:
        base = f"redis://{username}:{password}@{host}:{port}/{db}"

    return f"{base}/{db}" if db else base

redis: aioredis.Redis = aioredis.from_url(
    url=redis_dsn(
        host=config.REDIS_HOST,
        port=config.REDIS_PORT,
        username=config.REDIS_USER,
        password=config.REDIS_PASS,
        # db=config.REDIS_DB,
    ),
)
