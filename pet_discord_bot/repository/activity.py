import schedule

from pet_discord_bot.vendors.firebase import FirebaseClient


class ActivityRepository:
    def __init__(self, client: FirebaseClient) -> None:
        self.client = client
        self.db_table = "activities"

    def start_scheduler(self) -> None:
        schedule.every().second.do(self.fetch_scores)
        while True:
            schedule.run_pending()

    def fetch_scores(self):
        print("getting scores from firebase...")
        print(self.client.fetch_all(self.db_table))
        return self.client.fetch_all(self.db_table)
