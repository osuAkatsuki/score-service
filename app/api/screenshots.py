from __future__ import annotations

import logging
import random
import string

from fastapi import Depends
from fastapi import File
from fastapi import Form
from fastapi import Header
from fastapi import UploadFile

import app.state
import app.utils
import config
from app.models.user import User
from app.usecases.user import authenticate_user

UPLOAD_INTERVAL = 10
SIZE_LIMIT = 500_000
ERR_RESP = "https://akatsuki.pw/" # TODO: is this right?
MAX_NAME_LENGTH = 8


async def is_ratelimit(ip: str) -> bool:
    """Checks if an IP is ratelimited from taking screenshots. If not,
    it establishes the limit in Redis."""

    key = "less:ss_limit:" + ip
    if await app.state.services.redis.get(key):
        return True

    await app.state.services.redis.setex(key, UPLOAD_INTERVAL, 1)
    return False


FILENAME_CHARSET = string.ascii_letters + string.digits


def gen_rand_str(len: int) -> str:
    return "".join(random.choice(FILENAME_CHARSET) for _ in range(len))


async def upload_screenshot(
    user: User = Depends(authenticate_user(Form, "u", "p")),
    screenshot_file: UploadFile = File(..., alias="ss"),
    user_agent: str = Header(...),
    x_real_ip: str = Header(...),
):
    if not await app.utils.check_online(user.id):
        logging.error(f"{user} tried to upload a screenshot while offline")
        return ERR_RESP

    if user_agent != "osu!":
        logging.error(f"{user} tried to upload a screenshot using a bot")
        return ERR_RESP

    if await is_ratelimit(x_real_ip):
        logging.error(f"{user} tried to upload a screenshot while ratelimited")
        return ERR_RESP

    content = await screenshot_file.read()
    if len(content) > SIZE_LIMIT:
        return ERR_RESP

    if content[6:10] in (b"JFIF", b"Exif"):
        ext = "jpeg"
    elif content.startswith(b"\211PNG\r\n\032\n"):
        ext = "png"
    else:
        logging.error(f"{user} tried to upload unknown extension file")
        return ERR_RESP

    while True:
        file_name = f"{gen_rand_str(MAX_NAME_LENGTH)}.{ext}"

        # check if file already exists on s3
        try:
            await app.state.services.s3_client.get_object(
                Bucket=config.AWS_BUCKET_NAME,
                Key=f"screenshots/{file_name}",
            )
        except Exception as exc: # TODO: more specific err
            print("Exc type", exc)
            screenshot_file_found = False
        else:
            screenshot_file_found = True

        if not screenshot_file_found:
            break

    # TODO: ideally we should do exponential backoff retries here incase s3 is down,
    # but the osu! client will probably freak out if we don't send a response back in a timely matter :(
    try:
        await app.state.services.s3_client.put_object(
            Bucket=config.AWS_BUCKET_NAME,
            Key=f"screenshots/{file_name}",
            Body=content,
        )
    except Exception as exc:
        print("Exc type", exc)
        return ERR_RESP

    logging.info(f"{user} has uploaded screenshot {file_name}")
    return file_name
