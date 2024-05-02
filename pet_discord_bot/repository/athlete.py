import os
from typing import List

from app.config.config import config
from types.athlete import Athlete
from tomita_discord_bot.vendors.firebase import FirebaseClient


class AthleteRepository:
    def __init__(self) -> None:
        self.firebase_client = FirebaseClient(
            db_url=config.get("firebase_url"),
            db_table="athletes",
            credential_path=os.getcwd() + "/../firebase_config.json"
        )
        self.athletes = self.firebase_client.fetch_athletes()

    def fetch_athletes(self) -> List[Athlete]:
        return self.athletes
