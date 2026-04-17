"""Pytest-wide fixtures and environment setup.

Populates required env vars with dummy values *before* any application
module is imported so that importing :mod:`config` (starlette Config)
does not raise a ``KeyError``. Tests that need a real running service
layer should be marked accordingly and are not run in this file's
default suite.
"""

from __future__ import annotations

import os

_DEFAULT_TEST_ENV: dict[str, str] = {
    "APP_HOST": "127.0.0.1",
    "APP_PORT": "8080",
    "WRITE_DB_HOST": "localhost",
    "WRITE_DB_PORT": "3306",
    "WRITE_DB_USER": "test",
    "WRITE_DB_PASS": "test",
    "WRITE_DB_NAME": "test",
    "READ_DB_HOST": "localhost",
    "READ_DB_PORT": "3306",
    "READ_DB_USER": "test",
    "READ_DB_PASS": "test",
    "READ_DB_NAME": "test",
    "ALLOW_CUSTOM_CLIENTS": "false",
    "DISCORD_ADMIN_HOOK": "",
    "BOT_USER_ID": "999",
    "FOKABOT_KEY": "test",
    "BANCHO_SERVICE_URL": "http://localhost:5000",
    "PERFORMANCE_SERVICE_URL": "http://localhost:5001",
    "REDIS_HOST": "localhost",
    "REDIS_PORT": "6379",
    "REDIS_USER": "default",
    "REDIS_DB": "0",
    "REDIS_PASS": "",
    "REDIS_USE_SSL": "false",
    "SCORE_SUBMISSION_ROUTING_KEYS": "",
}

for _key, _value in _DEFAULT_TEST_ENV.items():
    os.environ.setdefault(_key, _value)
