from __future__ import annotations

import logging

from starlette.config import Config
from starlette.datastructures import CommaSeparatedStrings

# Config reads from os.environ. Prod's .env is sourced into the shell by
# scripts/bootstrap.sh, tests load .env.test via python-dotenv — nothing
# relies on starlette's own .env lookup, which was only emitting a "Config
# file '.env' not found" warning on every import.
config = Config()

APP_HOST = config("APP_HOST")
APP_PORT = config("APP_PORT", cast=int)

LOG_LEVEL = config("LOG_LEVEL", cast=int, default=logging.WARNING)
CODE_HOTRELOAD = config("CODE_HOTRELOAD", cast=bool, default=False)

WRITE_DB_HOST = config("WRITE_DB_HOST")
WRITE_DB_PORT = config("WRITE_DB_PORT", cast=int)
WRITE_DB_USER = config("WRITE_DB_USER")
WRITE_DB_PASS = config("WRITE_DB_PASS")
WRITE_DB_NAME = config("WRITE_DB_NAME")

READ_DB_HOST = config("READ_DB_HOST")
READ_DB_PORT = config("READ_DB_PORT", cast=int)
READ_DB_USER = config("READ_DB_USER")
READ_DB_PASS = config("READ_DB_PASS")
READ_DB_NAME = config("READ_DB_NAME")

BEATMAPS_SERVICE_BASE_URL = config(
    "BEATMAPS_SERVICE_BASE_URL",
    default="https://beatmaps.akatsuki.gg",
)

ALLOW_CUSTOM_CLIENTS = config("ALLOW_CUSTOM_CLIENTS", cast=bool)

SRV_URL = config("SRV_URL", default="akatsuki.gg")

DISCORD_ADMIN_HOOK = config("DISCORD_ADMIN_HOOK")

BOT_USER_ID = config("BOT_USER_ID", cast=int)
FOKABOT_KEY = config("FOKABOT_KEY")

AWS_REGION = config("AWS_REGION", default=None)
AWS_ACCESS_KEY_ID = config("AWS_ACCESS_KEY_ID", default=None)
AWS_SECRET_ACCESS_KEY = config("AWS_SECRET_ACCESS_KEY", default=None)
AWS_ENDPOINT_URL = config("AWS_ENDPOINT_URL", default=None)
AWS_BUCKET_NAME = config("AWS_BUCKET_NAME", default=None)

AMQP_HOST = config("AMQP_HOST", default=None)
amqp_port = config("AMQP_PORT", default=None)  # optional int
if amqp_port:
    AMQP_PORT: int | None = int(amqp_port)
else:
    AMQP_PORT = None
AMQP_USER = config("AMQP_USER", default=None)
AMQP_PASS = config("AMQP_PASS", default=None)

BANCHO_SERVICE_URL = config("BANCHO_SERVICE_URL")

PERFORMANCE_SERVICE_URL = config("PERFORMANCE_SERVICE_URL")

REDIS_HOST = config("REDIS_HOST")
REDIS_PORT = config("REDIS_PORT", cast=int)
REDIS_USER = config("REDIS_USER")
REDIS_DB = config("REDIS_DB")
REDIS_PASS = config("REDIS_PASS")
REDIS_USE_SSL = config("REDIS_USE_SSL", cast=bool)

SCORE_SUBMISSION_ROUTING_KEYS: list[str] = list(
    config("SCORE_SUBMISSION_ROUTING_KEYS", cast=CommaSeparatedStrings),
)

LEADERBOARD_SIZE = config("LEADERBOARD_SIZE", cast=int, default=100)
