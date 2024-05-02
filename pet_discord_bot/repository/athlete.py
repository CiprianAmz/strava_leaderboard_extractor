import os
from typing import List

from pet_discord_bot.types.athlete import Athlete
from pet_discord_bot.utils.discord_config import load_discord_config_from_json
from pet_discord_bot.vendors.firebase import FirebaseClient


class AthleteRepository:
    def __init__(self, client: FirebaseClient) -> None:
        self.client = client
        self.db_table = "athletes"

        firebase_athletes = self.client.fetch_all(self.db_table)
        if firebase_athletes:
            self.athletes = [Athlete(**athlete) for athlete in firebase_athletes.values()]
        else:
            self.athletes = []

    def fetch_athletes(self) -> List[Athlete]:
        return self.athletes

    def add_athlete(self, athlete: Athlete) -> None:
        self.athletes.append(athlete)
        self.client.upsert(db_table=self.db_table, internal_id=athlete.internal_id, data=athlete.__dict__)
