import uuid
from datetime import datetime
from uuid import uuid4

from humanfriendly import format_timespan
from stravalib import Client

from configs.constants import strava_activity_to_emoji
from pet_discord_bot.repository.activity import ActivityRepository
from pet_discord_bot.repository.athlete import AthleteRepository
from pet_discord_bot.types.activity import Activity
from pet_discord_bot.utils.logs import tomi_logger
from strava_leaderboard_extractor.strava_config import StravaConfig


class TomitaStrava:
    def __init__(self, config_json: StravaConfig, activity_repo: ActivityRepository, athlete_repo: AthleteRepository):
        self.strava_client = Client(access_token=config_json.access_token)
        self.club_activities = self.strava_client.get_club_activities(
            club_id=config_json.club_id,
            limit=3000,
        )
        self.activity_repo = activity_repo
        self.athlete_repo = athlete_repo

    def print_stats(self):
        activity_type_dict = {}
        activity_type_time_dict = {}
        activity_type_distance_dict = {}

        for activity in self.club_activities:
            if activity.type not in activity_type_dict:
                activity_type_dict.update({activity.type: 0})

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
            else:
                tomi_logger.info(f"Activity {activity.name} from {athlete.first_name} {athlete.last_name} already exists in DB")
            activity_type_dict[activity.type] += 1

            if activity.type not in activity_type_time_dict:
                activity_type_time_dict.update({activity.type: 0})

            activity_type_time_dict[activity.type] += activity.moving_time.total_seconds()

            if activity.type not in activity_type_distance_dict:
                activity_type_distance_dict.update({activity.type: 0})

            activity_type_distance_dict[activity.type] += activity.distance

        result_time = ""
        result_count = ""
        result_distance = ""

        for key, val in sorted(activity_type_dict.items(), key=lambda item: item[1], reverse=True):
            activity_emoji = strava_activity_to_emoji.get(key, "❓")
            result_count += f"{activity_emoji} {key}: {val} activities\n"

        for key, val in sorted(activity_type_time_dict.items(), key=lambda item: item[1], reverse=True):
            activity_emoji = strava_activity_to_emoji.get(key, "❓")
            result_time += f"{activity_emoji} {key}: {format_timespan(val)}\n"

        for key, val in sorted(activity_type_distance_dict.items(), key=lambda item: item[1], reverse=True):
            if val.num > 0.0:
                activity_emoji = strava_activity_to_emoji.get(key, "❓")
                distance_in_km = val.num // 1000
                result_distance += f"{activity_emoji} {key}: {distance_in_km} km\n"

        return {
            "time": result_time,
            "count": result_count,
            "distance": result_distance,
        }
