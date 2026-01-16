from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from app.models.score import Score
from app.models.stats import Stats


@dataclass
class Achievement:
    file: str
    condition_func: Callable[[Score, int, Stats], bool]


class Registry:
    """Registry for achievement condition functions.

    Similar to FastAPI's APIRouter, allows modular definition of achievements
    that can be combined into a main registry.
    """

    def __init__(self) -> None:
        self._achievements: dict[str, Achievement] = {}

    def achievement(self, file: str) -> Callable[
        [Callable[[Score, int, Stats], bool]],
        Callable[[Score, int, Stats], bool],
    ]:
        """Decorator to register an achievement condition function.

        Args:
            file: Achievement file identifier (all other metadata loaded from DB)

        Returns:
            Decorator function that registers the achievement

        Example:
            registry = Registry()

            @registry.achievement(file="osu-skill-pass-1")
            def rising_star(score: Score, mode_vn: int, stats: Stats) -> bool:
                return (score.mods & 1 == 0) and 1 <= score.sr < 2 and mode_vn == 0
        """

        def decorator(
            func: Callable[[Score, int, Stats], bool],
        ) -> Callable[[Score, int, Stats], bool]:
            self._achievements[file] = Achievement(
                file=file,
                condition_func=func,
            )
            return func

        return decorator

    def include(self, other: Registry) -> None:
        """Include all achievements from another registry.

        Similar to FastAPI's router.include_router().

        Args:
            other: Another Registry to merge into this one
        """
        self._achievements.update(other._achievements)

    @property
    def achievements(self) -> dict[str, Achievement]:
        """Get all registered achievements."""
        return self._achievements
