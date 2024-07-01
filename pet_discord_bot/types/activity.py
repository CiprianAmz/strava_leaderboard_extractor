from dataclasses import dataclass


@dataclass
class Activity:
    athlete_id: str
    date: str | None
    distance: float  # in kilometers
    internal_id: str  # UUID
    speed: float
    error: str | None
    name: str
    time: int  # in seconds
    type: str
