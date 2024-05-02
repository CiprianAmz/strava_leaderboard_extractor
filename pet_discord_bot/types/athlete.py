from dataclasses import dataclass


@dataclass
class Athlete:
    internal_id: str
    first_name: str
    last_name: str
    discord_id: str
