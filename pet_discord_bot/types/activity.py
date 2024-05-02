from dataclasses import dataclass


@dataclass
class Activity:
    athlete_id: str
    date: str | None
    distance: float  # in kilometers
    internal_id: str # UUID
    name: str
    time: int  # in seconds
    type: str
