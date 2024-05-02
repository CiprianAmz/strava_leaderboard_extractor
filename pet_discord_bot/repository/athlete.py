import os
from typing import List

from pet_discord_bot.utils.discord_config import load_discord_config_from_json
from pet_discord_bot.vendors.firebase import FirebaseClient


class AthleteRepository:
    def __init__(self) -> None:
        self.firebase_client = FirebaseClient(
            db_url=load_discord_config_from_json(
                os.path.join(os.path.dirname(__file__), '../../configs/discord_bot_config.json')
            ).firebase_url,
            db_table="athletes",
            credential_path=os.path.join(os.path.dirname(__file__), '../../configs/firebase_config.json')
        )
        self.athletes = self.firebase_client.fetch_all()

    def fetch_athletes(self) -> List[Athlete]:
        return self.athletes
