from __future__ import annotations

import app.state
from app.constants.mode import Mode
from app.constants.mods import Mods


async def get_pp_cap(mode: Mode, mods: Mods) -> int:
    prefix = ""
    if mode.relax:
        prefix += "relax_"
    elif mode.autopilot:
        prefix += "autopilot_"

    if mods & Mods.FLASHLIGHT:
        prefix += "flashlight_"

    pp_cap = await app.state.services.database.fetch_val(
        f"SELECT {prefix}pp FROM pp_limits WHERE gamemode = :mode",
        {"mode": mode.as_vn},
    )

    if not pp_cap:
        return 0  # xd

    return pp_cap
