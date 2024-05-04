from dataclasses import dataclass


@dataclass
class AthleteStats:
    internal_id: str
    total_activities: int
    total_distance: float
    total_time: int
