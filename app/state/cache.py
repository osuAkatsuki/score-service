from __future__ import annotations

import logging

import app.state
from app.achievements import registry
from app.models.achievement import Achievement

logger = logging.getLogger(__name__)

ACHIEVEMENTS: list[Achievement] = []


async def init_cache() -> None:
    """Load achievements from decorator registry.

    Achievements are defined as type-safe Python functions with the
    @achievement decorator.
    """
    # Load achievement metadata from database to verify all are registered
    db_achievements = await app.state.services.database.fetch_all(
        "SELECT id, file, name, desc FROM less_achievements",
    )

    # Build achievements from registry
    for db_achievement in db_achievements:
        achievement_file = db_achievement["file"]

        # Look up the registered achievement condition function
        registered_achievement = registry.achievements.get(achievement_file)
        if registered_achievement is None:
            # Skip achievements not yet implemented in decorator system
            # (e.g., new achievements added to DB but not yet coded)
            logger.warning(
                "Achievement in database not found in registry",
                extra={
                    "achievement_id": db_achievement["id"],
                    "achievement_file": achievement_file,
                    "achievement_name": db_achievement["name"],
                },
            )
            continue

        # Use database values for id/name/desc (allows easy updates via DB)
        # but use registry function for condition (type-safe, no execution)
        ACHIEVEMENTS.append(
            Achievement(
                id=db_achievement["id"],
                file=achievement_file,
                name=db_achievement["name"],
                desc=db_achievement["desc"],
                cond=registered_achievement.condition_func,
            ),
        )
