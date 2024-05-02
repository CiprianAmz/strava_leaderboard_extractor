import json
from typing import Optional
from dataclasses import dataclass

@dataclass
class StravaConfig():
    access_token:str
    club_id:str
    activities_limit:Optional[int]

def load_strava_config_from_json(file_path: str) -> StravaConfig:
    with open(file_path) as f:
        config_json = dict(json.load(f))
        return StravaConfig(
            access_token=config_json["strava_access_token"],
            club_id=config_json["strava_club_id"],
            activities_limit=config_json.get("activities_limit", None),
        )
