from dataclasses import dataclass


@dataclass
class Activity:
    athlete_id: str
    activity_id: str
    activity_name: str
    time: int  # in seconds
    distance: float  # in kilometers
    date: str
