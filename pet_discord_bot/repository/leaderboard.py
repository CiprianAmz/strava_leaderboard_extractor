import os

import schedule

from app.config.config import config
from tomita_discord_bot.vendors.firebase import FirebaseClient


class LeaderboardRepository:
    def __init__(self) -> None:
        self.firebase_client = FirebaseClient(
            db_url=config.get("firebase_url"),
            db_table="leaderboard",
            credential_path=os.getcwd() + "/../firebase_config.json"
        )

    def start_scheduler(self) -> None:
        schedule.every().second.do(self.fetch_scores)
        while True:
            schedule.run_pending()

    def fetch_scores(self):
        print("getting scores from firebase...")
        print(self.firebase_client.fetch_scores())
        return self.firebase_client.fetch_scores()
