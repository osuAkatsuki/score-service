from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel
from pydantic import Field


class CheesegullBeatmap(BaseModel):
    id: int = Field(..., alias="BeatmapID")
    beatmapset_id: int = Field(..., alias="ParentSetID")
    version: str = Field(..., alias="DiffName")
    checksum: str = Field(..., alias="FileMD5")
    mode: int = Field(..., alias="Mode")
    bpm: float = Field(..., alias="BPM")
    approach_rate: float = Field(..., alias="AR")
    overall_difficulty: float = Field(..., alias="OD")
    circle_size: float = Field(..., alias="CS")
    health_points: float = Field(..., alias="HP")
    total_length: int = Field(..., alias="TotalLength")
    hit_length: int = Field(..., alias="HitLength")
    play_count: int = Field(..., alias="Playcount")
    pass_count: int = Field(..., alias="Passcount")
    max_combo: int = Field(..., alias="MaxCombo")
    difficulty_rating: float = Field(..., alias="DifficultyRating")


class CheesegullBeatmapset(BaseModel):
    id: int = Field(..., alias="SetID")
    beatmaps: list[CheesegullBeatmap] = Field(..., alias="ChildrenBeatmaps")
    ranked_status: int = Field(..., alias="RankedStatus")
    approved_date: datetime = Field(..., alias="ApprovedDate")
    last_update: datetime = Field(..., alias="LastUpdate")
    last_checked: datetime = Field(..., alias="LastChecked")
    artist: str = Field(..., alias="Artist")
    title: str = Field(..., alias="Title")
    creator: str = Field(..., alias="Creator")
    source: str = Field(..., alias="Source")
    tags: str = Field(..., alias="Tags")
    has_video: bool = Field(..., alias="HasVideo")
    genre: int | None = Field(None, alias="Genre")
    language: int | None = Field(None, alias="Language")
    favourites: int = Field(..., alias="Favourites")
