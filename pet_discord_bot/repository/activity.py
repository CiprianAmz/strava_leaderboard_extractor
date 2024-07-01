from pet_discord_bot.types.activity import Activity
from pet_discord_bot.vendors.firebase import FirebaseClient


class ActivityRepository:
    def __init__(self, client: FirebaseClient) -> None:
        self.client = client
        self.db_table = "activities"

        firebase_activities = self.client.fetch_all(self.db_table)
        if firebase_activities:
            self.activities = [Activity(speed=0.0, error=None, **activity) for activity in firebase_activities.values()]
        else:
            self.activities = []

    def fetch_all(self) -> list[Activity]:
        return self.activities

    def add(self, activity: Activity) -> None:
        self.activities.append(activity)
        self.client.upsert(db_table=self.db_table, internal_id=activity.internal_id, data=activity.__dict__)

    def get_by_time_and_distance(self, time: int, distance: float) -> Activity or None:
        for activity in self.activities:
            if activity.time == time and round(activity.distance, 1) == round(distance, 1):
                return activity
        return None
