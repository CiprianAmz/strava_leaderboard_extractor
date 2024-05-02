from typing import List

from pet_discord_bot.types.athlete import Athlete
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

    def fetch_all(self) -> List[Athlete]:
        return self.athletes

    def add(self, athlete: Athlete) -> None:
        self.athletes.append(athlete)
        self.client.upsert(db_table=self.db_table, internal_id=athlete.internal_id, data=athlete.__dict__)

    def get(self, internal_id: str) -> Athlete:
        return next((athlete for athlete in self.athletes if athlete.internal_id == internal_id), None)

    def get_by_name(self, first_name: str, last_name: str) -> Athlete or None:
        return next((athlete for athlete in self.athletes if
                     athlete.first_name == first_name and athlete.last_name == last_name), None)
