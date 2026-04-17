from __future__ import annotations

from typing import Annotated
from typing import Any

from pydantic import BaseModel
from pydantic import BeforeValidator
from pydantic import ConfigDict


def _parse_bool_str(value: Any) -> bool:
    if isinstance(value, str):
        if value == "True":
            return True
        if value == "False":
            return False
    raise ValueError(f"expected 'True' or 'False', got {value!r}")


BoolStr = Annotated[bool, BeforeValidator(_parse_bool_str)]


class DecryptedScoreData(BaseModel):
    """Decrypted score data submitted by the osu! client.

    Input is the colon-separated list produced by
    :func:`app.api.score_sub.decrypt_score_data`. Position is load-bearing.
    """

    model_config = ConfigDict(frozen=True)

    beatmap_md5: str
    username: str
    online_checksum: str
    n300: int
    n100: int
    n50: int
    ngeki: int
    nkatu: int
    nmiss: int
    score: int
    max_combo: int
    full_combo: BoolStr
    grade: str
    mods: int
    passed: BoolStr
    mode: int

    @classmethod
    def from_tokens(cls, tokens: list[str]) -> DecryptedScoreData:
        if len(tokens) < 16:
            raise ValueError(
                f"expected at least 16 score data tokens, got {len(tokens)}",
            )
        return cls.model_validate(
            {
                "beatmap_md5": tokens[0],
                "username": tokens[1].rstrip(),
                "online_checksum": tokens[2],
                "n300": tokens[3],
                "n100": tokens[4],
                "n50": tokens[5],
                "ngeki": tokens[6],
                "nkatu": tokens[7],
                "nmiss": tokens[8],
                "score": tokens[9],
                "max_combo": tokens[10],
                "full_combo": tokens[11],
                "grade": tokens[12],
                "mods": tokens[13],
                "passed": tokens[14],
                "mode": tokens[15],
            },
        )
