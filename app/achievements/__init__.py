from __future__ import annotations

from app.achievements import catch
from app.achievements import mania
from app.achievements import mod_introductions
from app.achievements import osu_combo
from app.achievements import osu_plays
from app.achievements import osu_skill
from app.achievements import taiko
from app.achievements.registry import Registry

# Create main registry and explicitly include all sub-registries
registry = Registry()
registry.include(osu_skill.registry)
registry.include(osu_combo.registry)
registry.include(osu_plays.registry)
registry.include(taiko.registry)
registry.include(catch.registry)
registry.include(mania.registry)
registry.include(mod_introductions.registry)
