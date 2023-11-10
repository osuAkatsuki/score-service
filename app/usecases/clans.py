from __future__ import annotations

import app.state


async def get_clan(user_id: int) -> str:
    clan_tag = await app.state.services.database.fetch_val(
        "SELECT tag FROM users LEFT JOIN clans ON users.clan_id = clans.id WHERE users.id = :id",
        {"id": user_id},
    )

    if not clan_tag:
        # i know this is bad, i'm just replicating old behaviour
        return ""

    return clan_tag
