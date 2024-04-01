from app.models.cheesegull import CheesegullBeatmap
from app.models.cheesegull import CheesegullBeatmapset

def format_beatmapset_to_direct(beatmapset: CheesegullBeatmapset) -> str:
    # TODO: replace some of the placeholder values

    difficulty_sorted_beatmapsets = sorted(
        beatmapset.beatmaps,
        key=lambda x: x.difficulty_rating,
    )
    formatted_beatmaps = ",".join(format_beatmap_to_direct(beatmap) for beatmap in difficulty_sorted_beatmapsets)

    return (
        f"{beatmapset.id}.osz|{beatmapset.artist}|{beatmapset.title}|{beatmapset.creator}|"
        f"{beatmapset.ranked_status}|10.0|{beatmapset.last_update}|{beatmapset.id}|"
        f"0|{beatmapset.has_video}|0|0|0|{formatted_beatmaps}"
    )

def format_beatmap_to_direct(beatmap: CheesegullBeatmap) -> str:
    return (
        f"[{beatmap.difficulty_rating:.2f}⭐] {beatmap.version} "
        f"{{cs: {beatmap.circle_size} / od: {beatmap.overall_difficulty} / ar: {beatmap.approach_rate} / hp: {beatmap.health_points}}}@{beatmap.mode}"
    )

def format_beatmapset_to_direct_card(beatmapset: CheesegullBeatmapset) -> str:
    # TODO: replace some of the placeholder values

    return (
        f"{beatmapset.id}.osz|{beatmapset.artist}|{beatmapset.title}|{beatmapset.creator}|"
        f"{beatmapset.ranked_status}|10.0|{beatmapset.last_update}|{beatmapset.id}|"
        "0|0|0|0|0"
    )
