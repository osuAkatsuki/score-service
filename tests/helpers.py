from __future__ import annotations

from app.constants.mode import Mode
from app.constants.mods import Mods
from app.constants.score_status import ScoreStatus
from app.models.score import Score
from app.models.stats import Stats
from app.repositories.leaderboards import LeaderboardScore


def make_score(
    *,
    passed: bool = False,
    quit: bool = False,
    pp: float = 0.0,
    score: int = 0,
    mode: Mode = Mode.STD,
) -> Score:
    return Score(
        id=1,
        map_md5="a" * 32,
        user_id=1,
        mode=mode,
        mods=Mods(0),
        pp=pp,
        sr=0.0,
        score=score,
        max_combo=0,
        acc=0.0,
        n300=0,
        n100=0,
        n50=0,
        nmiss=0,
        ngeki=0,
        nkatu=0,
        passed=passed,
        quit=quit,
        full_combo=False,
        status=ScoreStatus.FAILED,
        time=0,
        time_elapsed=0,
        online_checksum=None,
    )


def make_stats() -> Stats:
    return Stats(
        user_id=1,
        mode=Mode.STD,
        ranked_score=0,
        total_score=0,
        pp=0.0,
        rank=0,
        country_rank=0,
        accuracy=0.0,
        playcount=0,
        playtime=0,
        max_combo=0,
        total_hits=0,
        replays_watched=0,
        xh_count=0,
        x_count=0,
        sh_count=0,
        s_count=0,
        a_count=0,
        b_count=0,
        c_count=0,
        d_count=0,
    )


def make_leaderboard_score(
    *,
    pp: float = 0.0,
    score: int = 0,
) -> LeaderboardScore:
    return LeaderboardScore(
        score_id=1,
        user_id=1,
        score=score,
        max_combo=0,
        full_combo=False,
        mods=0,
        count_300=0,
        count_100=0,
        count_50=0,
        count_geki=0,
        count_katu=0,
        count_miss=0,
        time=0,
        play_mode=0,
        completed=3,
        accuracy=0.0,
        pp=pp,
        checksum=None,
        patcher=False,
        pinned=False,
        score_rank=0,
        score_username="test",
    )


def make_score_tokens(
    *,
    beatmap_md5: str = "a" * 32,
    username: str = "tester",
    online_checksum: str = "c" * 32,
    n300: int = 100,
    n100: int = 0,
    n50: int = 0,
    ngeki: int = 0,
    nkatu: int = 0,
    nmiss: int = 0,
    score: int = 123456,
    max_combo: int = 100,
    full_combo: str = "True",
    grade: str = "S",
    mods: int = 0,
    passed: str = "True",
    mode: int = 0,
) -> list[str]:
    """Build a colon-split token list with the same positional layout the
    osu! client sends. Booleans are passed as the raw ``"True"``/``"False"``
    strings."""
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
