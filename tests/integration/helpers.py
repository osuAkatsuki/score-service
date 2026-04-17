from __future__ import annotations

import hashlib
import secrets
from base64 import b64encode
from typing import Any

import bcrypt
import httpx
from fastapi.testclient import TestClient
from py3rijndael import Pkcs7Padding
from py3rijndael import RijndaelCbc

from app.state.services import Database

SUBMIT_SCORE_PATH = "/web/osu-submit-modular-selector.php"
DEFAULT_OSU_VERSION = "20210103"


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
    username_safe: str | None = None,
    plaintext_password: str = "testpass",
    email: str | None = None,
    register_datetime: int = 0,
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
            "username_safe": (
                username_safe
                if username_safe is not None
                else username.lower().replace(" ", "_")
            ),
            "password_bcrypt": password_bcrypt,
            "email": email if email is not None else f"{username}@test.local",
            "register_datetime": register_datetime,
            "privileges": privileges,
            "country": country,
        },
    )
    return {
        "user_id": user_id,
        "username": username,
        "plaintext_password": plaintext_password,
        "password_md5": password_md5,
    }


async def seed_pp_limits(
    db: Database,
    *,
    pp_cap: int = 30_000,
) -> None:
    """Populate pp_limits with a high cap for every vanilla game mode.

    Without a row, app.usecases.pp_cap.get_pp_cap returns 0, which makes every
    non-whitelisted score submission above 0 pp trip the pp-cap restrict
    path. Production seeds real values; tests use a cap big enough that no
    default test submission hits it, unless a test overrides to something
    lower.

    pp_limits.gamemode is an AUTO_INCREMENT column, so inserting literal 0
    requires ``NO_AUTO_VALUE_ON_ZERO`` in sql_mode. We set it on a single
    held connection for the duration of the inserts rather than relying on
    the server default — server sql_mode is an infra concern we don't want
    tests to assume.
    """
    async with db.write_database.connection() as conn:
        await conn.execute("SET SESSION sql_mode = 'NO_AUTO_VALUE_ON_ZERO'")
        for mode in (0, 1, 2, 3):
            await conn.execute(
                """
                INSERT INTO pp_limits (
                    gamemode, pp, relax_pp, flashlight_pp,
                    relax_flashlight_pp, autopilot_pp, autopilot_flashlight_pp
                ) VALUES (
                    :gamemode, :cap, :cap, :cap, :cap, :cap, :cap
                )
                """,
                {"gamemode": mode, "cap": pp_cap},
            )


async def seed_user_stats(
    db: Database,
    *,
    user_id: int,
    mode: int = 0,
) -> None:
    # submit_score reads and updates user_stats; any test covering score
    # submission needs a row for the (user_id, mode) pair it exercises.
    await db.execute(
        "INSERT INTO user_stats (user_id, mode) VALUES (:user_id, :mode)",
        {"user_id": user_id, "mode": mode},
    )


def build_score_tokens(
    *,
    beatmap_md5: str,
    username: str,
    online_checksum: str = "c" * 32,
    n300: int = 100,
    n100: int = 2,
    n50: int = 1,
    ngeki: int = 0,
    nkatu: int = 0,
    nmiss: int = 0,
    score: int = 123_456,
    max_combo: int = 500,
    full_combo: str = "True",
    grade: str = "S",
    mods: int = 0,
    passed: str = "True",
    mode: int = 0,
) -> list[str]:
    """Build the 16-token score payload in the positional shape the
    osu! client serializes before encrypting."""
    return [
        beatmap_md5,
        username,
        online_checksum,
        str(n300),
        str(n100),
        str(n50),
        str(ngeki),
        str(nkatu),
        str(nmiss),
        str(score),
        str(max_combo),
        full_combo,
        grade,
        str(mods),
        passed,
        str(mode),
    ]


def submit_score_request(
    client: TestClient,
    *,
    password_md5: str,
    score_tokens: list[str],
    user_agent: str = "osu!",
    osu_version: str = DEFAULT_OSU_VERSION,
    client_hash: str | None = None,
    replay_bytes: bytes = DUMMY_REPLAY_BYTES,
) -> httpx.Response:
    """Encrypt the tokens and POST the submit-modular-selector multipart.

    Mirrors what the osu! client sends: score and client-hash are encrypted
    with the same IV; the `score` multipart key has two parts — the
    encrypted score string and the replay file upload.
    """
    score_data_b64, iv_b64, client_hash_b64 = encrypt_score_payload(
        score_tokens=score_tokens,
        client_hash=client_hash or ":".join(["0" * 32] * 5),
        osu_version=osu_version,
    )
    return client.post(
        SUBMIT_SCORE_PATH,
        headers={"user-agent": user_agent},
        data={
            "x": "0",
            "ft": "0",
            "fs": b64encode(b"visual-settings").decode(),
            "bmk": score_tokens[0],
            "sbk": "",
            "iv": iv_b64.decode(),
            "c1": "abc-unique-id",
            "st": "0",
            "pass": password_md5,
            "osuver": osu_version,
            "s": client_hash_b64.decode(),
        },
        files=[
            ("score", (None, score_data_b64, "text/plain")),
            ("score", ("replay.osr", replay_bytes, "application/octet-stream")),
        ],
    )


async def seed_beatmap(
    db: Database,
    *,
    beatmap_id: int = 1_000_000,
    beatmapset_id: int | None = None,
    beatmap_md5: str = "a" * 32,
    song_name: str = "Test Artist - Test Song [Test Diff]",
    file_name: str = "Test Artist - Test Song (Test Mapper) [Test Diff].osu",
    ar: float = 9.0,
    od: float = 9.0,
    mode: int = 0,
    max_combo: int = 1000,
    hit_length: int = 120,
    bpm: int = 180,
    ranked: int = 2,  # RANKED
    latest_update: int = 0,
    ranked_status_freezed: int = 0,
    playcount: int = 0,
    passcount: int = 0,
    rating: float = 10.0,
    count_circles: int = 500,
    count_sliders: int = 500,
    count_spinners: int = 0,
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
            :ar, :od, :mode, :max_combo, :hit_length, :bpm, :ranked, :latest_update,
            :ranked_status_freezed, :playcount, :passcount, :rating,
            :count_circles, :count_sliders, :count_spinners
        )
        """,
        {
            "beatmap_id": beatmap_id,
            "beatmapset_id": (
                beatmapset_id if beatmapset_id is not None else beatmap_id + 1
            ),
            "beatmap_md5": beatmap_md5,
            "song_name": song_name,
            "file_name": file_name,
            "ar": ar,
            "od": od,
            "mode": mode,
            "max_combo": max_combo,
            "hit_length": hit_length,
            "bpm": bpm,
            "ranked": ranked,
            "latest_update": latest_update,
            "ranked_status_freezed": ranked_status_freezed,
            "playcount": playcount,
            "passcount": passcount,
            "rating": rating,
            "count_circles": count_circles,
            "count_sliders": count_sliders,
            "count_spinners": count_spinners,
        },
    )
    return {"beatmap_id": beatmap_id, "beatmap_md5": beatmap_md5}
