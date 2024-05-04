import json
from typing import Optional
from dataclasses import dataclass


@dataclass
class BotConfig:
    access_token: str
    firebase_url: str


def load_bot_config_from_json(file_path: str) -> BotConfig:
    with open(file_path) as f:
        config_json = dict(json.load(f))
        return BotConfig(
            access_token=config_json["discord_access_token"],
            firebase_url=config_json["firebase_url"],
        )
