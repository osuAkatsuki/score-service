from __future__ import annotations

from app.achievements import catch
from app.achievements import hush_hush
from app.achievements import mania
from app.achievements import mod_introductions
from app.achievements import osu
from app.achievements import taiko
from app.achievements.registry import AchievementRegistry

# Create main registry and explicitly include all sub-registries
registry = AchievementRegistry()
registry.include(osu.registry)
registry.include(taiko.registry)
registry.include(catch.registry)
registry.include(mania.registry)
registry.include(mod_introductions.registry)
registry.include(hush_hush.registry)

__all__ = [
    "registry",
    "AchievementRegistry",
]
