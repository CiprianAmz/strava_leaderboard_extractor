import os

import schedule

from app.config.config import config
from app.vendors.firebase import FirebaseClient


class RepositoryLeaderboard:
    def __init__(self):
        self.firebase_client = FirebaseClient(
            db_url=config.get("firebase_url"),
            credential_path=os.getcwd() + "/../firebase.json"
        )

    def start_scheduler(self):
        schedule.every().second.do(self.fetch_scores)
        while True:
            schedule.run_pending()

    def fetch_scores(self):
        print("getting scores from firebase...")
        print(self.firebase_client.fetch_scores())
        return self.firebase_client.fetch_scores()
