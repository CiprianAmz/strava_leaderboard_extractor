import uuid
from datetime import datetime
from typing import List

from humanfriendly import format_timespan
from stravalib import Client

from pet_discord_bot.config.constants import strava_activity_to_emoji
from pet_discord_bot.repository.activity import ActivityRepository
from pet_discord_bot.repository.athlete import AthleteRepository
from pet_discord_bot.types.activity import Activity
from pet_discord_bot.utils.logs import tomi_logger
from strava_leaderboard_extractor.strava_config import StravaConfig


class TomitaStrava:
    @staticmethod
    def __replace_activity_type_name(activity_type: str) -> str:
        if activity_type == "Soccer":
            return "Football"
        return activity_type

    @staticmethod
    def __convert_str_date_to_datetime(str_date: str) -> datetime:
        return datetime.strptime(str_date, "%Y-%m-%d %H:%M")

    def __get_medal_for_idx(self, idx: int) -> str:
        if idx == 0:
            return "🥇"
        if idx == 1:
            return "🥈"
        if idx == 2:
            return "🥉"
        return "🎖️"

    def __compute_top_3(self, activities_list: List[Activity]) -> dict:
        athlete_stats_by_number_dict = {}
        athlete_stats_by_time_dict = {}
        athlete_stats_by_distance_dict = {}
        for activity in activities_list:
            athlete = self.athlete_repo.get(activity.athlete_id)
            if athlete is None:
                tomi_logger.warn(f"Athlete with ID {activity.athlete_id} not found in DB")
                tomi_logger.error(f"Activity {activity.name} will be skipped")
                continue

            if athlete.internal_id not in athlete_stats_by_number_dict:
                athlete_stats_by_number_dict.update({athlete.internal_id: 0})
            if athlete.internal_id not in athlete_stats_by_time_dict:
                athlete_stats_by_time_dict.update({athlete.internal_id: 0})
            if athlete.internal_id not in athlete_stats_by_distance_dict:
                athlete_stats_by_distance_dict.update({athlete.internal_id: 0})

            athlete_stats_by_number_dict[athlete.internal_id] += 1
            athlete_stats_by_time_dict[athlete.internal_id] += activity.time
            athlete_stats_by_distance_dict[athlete.internal_id] += activity.distance

        top_3_by_activities_list = sorted(athlete_stats_by_number_dict.items(), key=lambda item: item[1], reverse=True)[:3]
        top_3_by_time_list = sorted(athlete_stats_by_time_dict.items(), key=lambda item: item[1], reverse=True)[:3]
        top_3_by_distance_list = sorted(athlete_stats_by_distance_dict.items(), key=lambda item: item[1], reverse=True)[:3]

        return {
            "activities": top_3_by_activities_list,
            "time": top_3_by_time_list,
            "distance": top_3_by_distance_list,
        }

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
            time_str += f"{activity_emoji} {self.__replace_activity_type_name(key)}: {format_timespan(val)}\n"

        for key, val in sorted(activity_distance_dict.items(), key=lambda item: item[1], reverse=True):
            activity_emoji = strava_activity_to_emoji.get(key, "❓")
            distance_str += f"{activity_emoji} {self.__replace_activity_type_name(key)}: {"{:.2f}".format(val)} km\n"

        return {
            "count": count_str,
            "time": time_str,
            "distance": distance_str,
        }

    def compute_daily_stats(self) -> dict:
        daily_activities: List[Activity] = []
        for activity in self.activity_repo.fetch_all():
            if activity.date is not None:
                activity_date = self.__convert_str_date_to_datetime(activity.date)
                if activity_date.date() == datetime.now().date():
                    daily_activities.append(activity)

        result = self.__compute_top_3(daily_activities)

        count_str = ""
        time_str = ""
        distance_str = ""

        for idx, (key, val) in enumerate(result["activities"]):
            athlete = self.athlete_repo.get(key)
            count_str += f"*{self.__get_medal_for_idx(idx)} {athlete.first_name} {athlete.last_name}:* {val} activities\n"

        for idx, (key, val) in enumerate(result["time"]):
            athlete = self.athlete_repo.get(key)
            time_str += f"*{self.__get_medal_for_idx(idx)} {athlete.first_name} {athlete.last_name}:* {format_timespan(val)}\n"

        for idx, (key, val) in enumerate(result["distance"]):
            athlete = self.athlete_repo.get(key)
            distance_str += f"*{self.__get_medal_for_idx(idx)} {athlete.first_name} {athlete.last_name}:* {"{:.2f}".format(val)}km\n"

        return {
            "count": count_str,
            "time": time_str,
            "distance": distance_str,
        }

    def compute_monthly_stats(self) -> dict:
        monthly_activities: List[Activity] = []
        for activity in self.activity_repo.fetch_all():
            if activity.date is not None:
                activity_date = self.__convert_str_date_to_datetime(activity.date)
                if activity_date.month == datetime.now().month:
                    monthly_activities.append(activity)

        result = self.__compute_top_3(monthly_activities)

        count_str = ""
        time_str = ""
        distance_str = ""

        for idx, (key, val) in enumerate(result["activities"]):
            athlete = self.athlete_repo.get(key)
            count_str += f"*{self.__get_medal_for_idx(idx)} {athlete.first_name} {athlete.last_name}:* {val} activities\n"

        for idx, (key, val) in enumerate(result["time"]):
            athlete = self.athlete_repo.get(key)
            time_str += f"*{self.__get_medal_for_idx(idx)} {athlete.first_name} {athlete.last_name}:* {format_timespan(val)}\n"

        for idx, (key, val) in enumerate(result["distance"]):
            athlete = self.athlete_repo.get(key)
            distance_str += f"*{self.__get_medal_for_idx(idx)} {athlete.first_name} {athlete.last_name}:* {val} km\n"

        return {
            "count": count_str,
            "time": time_str,
            "distance": distance_str,
        }

    def compute_yearly_stats(self) -> dict:
        yearly_activities: List[Activity] = []
        for activity in self.activity_repo.fetch_all():
            if activity.date is not None:
                activity_date = self.__convert_str_date_to_datetime(activity.date)
                if activity_date.year == datetime.now().year:
                    yearly_activities.append(activity)

        result = self.__compute_top_3(yearly_activities)

        count_str = ""
        time_str = ""
        distance_str = ""

        for idx, (key, val) in enumerate(result["activities"]):
            athlete = self.athlete_repo.get(key)
            count_str += f"*{self.__get_medal_for_idx(idx)} {athlete.first_name} {athlete.last_name}:* {val} activities\n"

        for idx, (key, val) in enumerate(result["time"]):
            athlete = self.athlete_repo.get(key)
            time_str += f"*{self.__get_medal_for_idx(idx)} {athlete.first_name} {athlete.last_name}:* {format_timespan(val)}\n"

        for idx, (key, val) in enumerate(result["distance"]):
            athlete = self.athlete_repo.get(key)
            distance_str += f"*{self.__get_medal_for_idx(idx)} {athlete.first_name} {athlete.last_name}:* {"{:.2f}".format(val)}km\n"

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
                tomi_logger.error(f"Activity {activity.name} ({activity.athlete.firstname} "
                                  f"{activity.athlete.lastname}) will be skipped")
                continue

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
