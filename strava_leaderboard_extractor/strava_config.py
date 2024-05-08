import json
from typing import Optional
from dataclasses import dataclass


@dataclass
class StravaConfig:
    access_token: str
    activities_limit: Optional[int]
    client_id: int
    client_secret: str
    club_id: int
    refresh_token: str


def load_strava_config_from_json(file_path: str) -> StravaConfig:
    with open(file_path) as f:
        config_json = dict(json.load(f))
        return StravaConfig(
            access_token=config_json["strava_access_token"],
            activities_limit=config_json.get("activities_limit", None),
            client_id=int(config_json["strava_client_id"]),
            client_secret=config_json["strava_client_secret"],
            club_id=int(config_json["strava_club_id"]),
            refresh_token=config_json.get("strava_refresh_token", None),
        )
