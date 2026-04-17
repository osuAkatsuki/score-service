from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.models.decrypted_score_data import DecryptedScoreData
from tests.unit.helpers import make_score_tokens


def test_parses_well_formed_tokens() -> None:
    tokens = make_score_tokens(
        username="cmyui",
        n300=100,
        n100=2,
        n50=1,
        score=123_456,
        max_combo=500,
        mods=64,
        passed="True",
        mode=0,
    )
    data = DecryptedScoreData.from_tokens(tokens)
    assert data.username == "cmyui"
    assert data.n300 == 100
    assert data.n100 == 2
    assert data.n50 == 1
    assert data.score == 123_456
    assert data.max_combo == 500
    assert data.mods == 64
    assert data.passed is True
    assert data.mode == 0


def test_rejects_short_token_list() -> None:
    with pytest.raises(ValueError, match="at least 16"):
        DecryptedScoreData.from_tokens(["only", "three", "tokens"])


def test_rejects_invalid_boolean_token() -> None:
    tokens = make_score_tokens(full_combo="maybe")
    with pytest.raises(ValidationError):
        DecryptedScoreData.from_tokens(tokens)


def test_rejects_non_numeric_score() -> None:
    tokens = make_score_tokens()
    tokens[9] = "not-a-number"
    with pytest.raises(ValidationError):
        DecryptedScoreData.from_tokens(tokens)


def test_trims_supporter_pace_suffix_from_username() -> None:
    tokens = make_score_tokens(username="supporter ")
    data = DecryptedScoreData.from_tokens(tokens)
    assert data.username == "supporter"


def test_frozen_model_cannot_be_mutated() -> None:
    tokens = make_score_tokens()
    data = DecryptedScoreData.from_tokens(tokens)
    with pytest.raises(ValidationError):
        data.score = 999_999  # type: ignore[misc]
