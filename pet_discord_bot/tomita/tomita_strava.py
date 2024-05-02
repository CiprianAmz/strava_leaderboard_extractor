import uuid
from datetime import datetime

from stravalib import Client

from configs.constants import strava_activity_to_emoji
from pet_discord_bot.repository.activity import ActivityRepository
from pet_discord_bot.repository.athlete import AthleteRepository
from pet_discord_bot.types.activity import Activity
from pet_discord_bot.utils.logs import tomi_logger
from strava_leaderboard_extractor.strava_config import StravaConfig


class TomitaStrava:
    def __replace_activity_type_name(self, activity_type: str) -> str:
        if activity_type == "Soccer":
            return "Football"
        return activity_type

    def __init__(self, config_json: StravaConfig, activity_repo: ActivityRepository, athlete_repo: AthleteRepository):
        self.strava_client = Client(access_token=config_json.access_token)
        self.club_activities = self.strava_client.get_club_activities(
            club_id=config_json.club_id,
            limit=3000,
        )
        self.activity_repo = activity_repo
        self.athlete_repo = athlete_repo

    def compute_overall_stats(self) -> dict:
        activity_dict = {}
        activity_time_dict = {}
        activity_distance_dict = {}
        for activity in self.activity_repo.fetch_all():
            if activity.type not in activity_dict:
                activity_dict.update({activity.type: 0})
            activity_dict[activity.type] += 1

            if activity.type not in activity_time_dict:
                activity_time_dict.update({activity.type: 0})
            activity_time_dict[activity.type] += activity.time

            if activity.type not in activity_distance_dict:
                activity_distance_dict.update({activity.type: 0})
            activity_distance_dict[activity.type] += activity.distance
        
        count_str = ""
        time_str = ""
        distance_str = ""
        
        for key, val in sorted(activity_dict.items(), key=lambda item: item[1], reverse=True):
            activity_emoji = strava_activity_to_emoji.get(key, "❓")
            count_str += f"{activity_emoji} {self.__replace_activity_type_name(key)}: {val} activities\n"

        for key, val in sorted(activity_time_dict.items(), key=lambda item: item[1], reverse=True):
            activity_emoji = strava_activity_to_emoji.get(key, "❓")
            time_str += f"{activity_emoji} {self.__replace_activity_type_name(key)}: {val}\n"

        for key, val in sorted(activity_distance_dict.items(), key=lambda item: item[1], reverse=True):
            activity_emoji = strava_activity_to_emoji.get(key, "❓")
            distance_str += f"{activity_emoji} {self.__replace_activity_type_name(key)}: {val} km\n"

        return {
            "count": count_str,
            "time": time_str,
            "distance": distance_str,
        }

    def sync_stats(self) -> int:
        activities_added = 0

        for activity in self.club_activities:
            athlete = self.athlete_repo.get_by_name(activity.athlete.firstname, activity.athlete.lastname)
            if athlete is None:
                tomi_logger.warn(f"Athlete {activity.athlete.firstname} {activity.athlete.lastname} not found in DB")
                tomi_logger.error(f"Activity {activity.name} will be skipped")
                continue
            else:
                tomi_logger.info(f"Athlete {athlete.first_name} {athlete.last_name} found for activity {activity.name}")

            new_activity = Activity(
                athlete_id=athlete.internal_id,
                date=None,
                distance=float("{:.2f}".format(activity.distance.num / 1000)),
                internal_id=str(uuid.uuid4()),
                name=activity.name,
                time=int(activity.moving_time.total_seconds()),
                type=activity.type,
            )
            existing_activity = self.activity_repo.get_by_time_and_distance(new_activity.time, new_activity.distance)
            if existing_activity is None:
                new_activity.date = datetime.now().strftime("%Y-%m-%d %H:%M")
                self.activity_repo.add(new_activity)
                activities_added += 1
            else:
                tomi_logger.info(
                    f"Activity {activity.name} from {athlete.first_name} {athlete.last_name} already exists in DB")

        return activities_added
