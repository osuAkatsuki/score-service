from __future__ import annotations

from app.achievements import catch
from app.achievements import hit_count_tier4
from app.achievements import hush_hush
from app.achievements import mania
from app.achievements import mod_introductions
from app.achievements import osu_combo
from app.achievements import osu_plays
from app.achievements import osu_skill
from app.achievements import rank_milestones
from app.achievements import taiko
from app.achievements.registry import AchievementRegistry

# Create main registry and explicitly include all sub-registries
registry = AchievementRegistry()
registry.include(osu_skill.registry)
registry.include(osu_combo.registry)
registry.include(osu_plays.registry)
registry.include(taiko.registry)
registry.include(catch.registry)
registry.include(mania.registry)
registry.include(mod_introductions.registry)
registry.include(hit_count_tier4.registry)
registry.include(rank_milestones.registry)
registry.include(hush_hush.registry)

__all__ = [
    "registry",
    "AchievementRegistry",
]
