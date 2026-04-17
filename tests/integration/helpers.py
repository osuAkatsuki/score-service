from __future__ import annotations

import hashlib
import secrets
from base64 import b64encode
from typing import Any

import bcrypt
from py3rijndael import Pkcs7Padding
from py3rijndael import RijndaelCbc

from app.state.services import Database


def hash_password(plaintext: str) -> tuple[str, str]:
    # Client sends md5(plaintext); server stores bcrypt(md5(plaintext)).
    password_md5 = hashlib.md5(plaintext.encode()).hexdigest()
    password_bcrypt = bcrypt.hashpw(password_md5.encode(), bcrypt.gensalt()).decode()
    return password_md5, password_bcrypt


def rijndael_cipher(osu_version: str, iv: bytes) -> RijndaelCbc:
    return RijndaelCbc(
        key=f"osu!-scoreburgr---------{osu_version}".encode(),
        iv=iv,
        padding=Pkcs7Padding(32),
        block_size=32,
    )


def encrypt_score_payload(
    *,
    score_tokens: list[str],
    client_hash: str,
    osu_version: str,
) -> tuple[bytes, bytes, bytes]:
    """Build the three b64 blobs the client sends: score_data, iv, client_hash.

    Both the score tokens and the client hash are encrypted with the same IV,
    matching the osu! client's behavior.
    """
    iv = secrets.token_bytes(32)
    cipher = rijndael_cipher(osu_version, iv)
    score_data_b64 = b64encode(cipher.encrypt(":".join(score_tokens).encode()))
    client_hash_b64 = b64encode(cipher.encrypt(client_hash.encode()))
    iv_b64 = b64encode(iv)
    return score_data_b64, iv_b64, client_hash_b64


# Small but valid osu! replay header + zero-length data. The submission path
# only checks len(replay) >= 24; it doesn't parse the body.
DUMMY_REPLAY_BYTES: bytes = b"\x00" * 32


async def seed_user(
    db: Database,
    *,
    user_id: int = 1000,
    username: str = "tester",
    plaintext_password: str = "testpass",
    privileges: int = 3,  # USER_NORMAL | USER_PUBLIC
    country: str = "US",
) -> dict[str, Any]:
    password_md5, password_bcrypt = hash_password(plaintext_password)
    await db.execute(
        """
        INSERT INTO users (
            id, username, username_safe, password_md5, email, register_datetime,
            privileges, country
        ) VALUES (
            :id, :username, :username_safe, :password_bcrypt, :email, :register_datetime,
            :privileges, :country
        )
        """,
        {
            "id": user_id,
            "username": username,
            "username_safe": username.lower().replace(" ", "_"),
            "password_bcrypt": password_bcrypt,
            "email": f"{username}@test.local",
            "register_datetime": 0,
            "privileges": privileges,
            "country": country,
        },
    )
    # user_stats row is required — submit_score reads and updates it.
    await db.execute(
        "INSERT INTO user_stats (user_id, mode) VALUES (:user_id, 0)",
        {"user_id": user_id},
    )
    return {
        "user_id": user_id,
        "username": username,
        "plaintext_password": plaintext_password,
        "password_md5": password_md5,
    }


async def seed_beatmap(
    db: Database,
    *,
    beatmap_id: int = 1_000_000,
    beatmap_md5: str = "a" * 32,
    song_name: str = "Test Artist - Test Song [Test Diff]",
    file_name: str = "Test Artist - Test Song (Test Mapper) [Test Diff].osu",
    mode: int = 0,
    ranked: int = 2,  # RANKED
    max_combo: int = 1000,
    hit_length: int = 120,
) -> dict[str, Any]:
    await db.execute(
        """
        INSERT INTO beatmaps (
            beatmap_id, beatmapset_id, beatmap_md5, song_name, file_name,
            ar, od, mode, max_combo, hit_length, bpm, ranked, latest_update,
            ranked_status_freezed, playcount, passcount, rating,
            count_circles, count_sliders, count_spinners
        ) VALUES (
            :beatmap_id, :beatmapset_id, :beatmap_md5, :song_name, :file_name,
            9.0, 9.0, :mode, :max_combo, :hit_length, 180, :ranked, 0,
            0, 0, 0, 10.0,
            500, 500, 0
        )
        """,
        {
            "beatmap_id": beatmap_id,
            "beatmapset_id": beatmap_id + 1,
            "beatmap_md5": beatmap_md5,
            "song_name": song_name,
            "file_name": file_name,
            "mode": mode,
            "ranked": ranked,
            "max_combo": max_combo,
            "hit_length": hit_length,
        },
    )
    return {"beatmap_id": beatmap_id, "beatmap_md5": beatmap_md5}
