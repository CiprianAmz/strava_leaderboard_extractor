import time
import uuid
from datetime import datetime
from typing import List

from humanfriendly import format_timespan
from stravalib import Client

from pet_discord_bot.config.constants import strava_activity_to_emoji, time_unit_to_short
from pet_discord_bot.repository.activity import ActivityRepository
from pet_discord_bot.repository.athlete import AthleteRepository
from pet_discord_bot.types.activity import Activity
from pet_discord_bot.types.strava_access import StravaAccess
from pet_discord_bot.utils.logs import tomi_logger
from strava_leaderboard_extractor.strava_config import StravaConfig


class TomitaStrava:

    def __init__(self, config_json: StravaConfig, activity_repo: ActivityRepository, athlete_repo: AthleteRepository):
        self.strava_client = Client(access_token=config_json.access_token)
        self.strava_config = config_json
        self.strava_access = StravaAccess(
            access_token=config_json.access_token,
            refresh_token=config_json.refresh_token,
            expires_at=int(time.time())
        )
        self.club_activities = self.strava_client.get_club_activities(
            club_id=config_json.club_id,
            limit=3000,
        )
        self.activity_repo = activity_repo
        self.athlete_repo = athlete_repo

    @staticmethod
    def __replace_activity_type_name(activity_type: str) -> str:
        if activity_type == "Soccer":
            return "Football"
        return activity_type

    @staticmethod
    def __convert_str_date_to_datetime(str_date: str) -> datetime:
        return datetime.strptime(str_date, "%Y-%m-%d %H:%M")

    @staticmethod
    def __get_medal_for_idx(idx: int) -> str:
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
                tomi_logger.error(f"Athlete with ID {activity.athlete_id} not found in DB "
                                  f"- skipping activity {activity.name}")
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

        top_3_by_activities_list = sorted(athlete_stats_by_number_dict.items(), key=lambda item: item[1], reverse=True)[
                                   :3]
        top_3_by_time_list = sorted(athlete_stats_by_time_dict.items(), key=lambda item: item[1], reverse=True)[:3]
        top_3_by_distance_list = sorted(athlete_stats_by_distance_dict.items(), key=lambda item: item[1], reverse=True)[
                                 :3]

        return {
            "activities": top_3_by_activities_list,
            "time": top_3_by_time_list,
            "distance": top_3_by_distance_list,
        }

    def __compute_activities_str(self, activities_list) -> str:
        activities_str = ""
        for idx, (key, val) in enumerate(activities_list):
            athlete = self.athlete_repo.get(key)
            activities_str += (f"**{self.__get_medal_for_idx(idx)} {athlete.first_name} {athlete.last_name}:"
                               f"** {self.__replace_activity_type_name(val)}\n")
        return activities_str

    def __compute_time_str(self, activities_list: List[Activity]) -> str:
        time_str = ""
        for idx, (key, val) in enumerate(activities_list):
            athlete = self.athlete_repo.get(key)
            time_str += (f"**{self.__get_medal_for_idx(idx)} {athlete.first_name} {athlete.last_name}:** "
                         f"{self.convert_seconds_to_human_readable(val)}\n")
        return time_str

    def __compute_distance_str(self, activities_list: List[Activity]) -> str:
        distance_str = ""
        for idx, (key, val) in enumerate(activities_list):
            athlete = self.athlete_repo.get(key)
            distance_str += f"**{self.__get_medal_for_idx(idx)} {athlete.first_name} {athlete.last_name}:** {'{:.1f}'.format(val)} km\n"
        return distance_str

    @staticmethod
    def convert_seconds_to_human_readable(seconds: int) -> str:
        formatted_time = format_timespan(seconds)
        for key, val in time_unit_to_short.items():
            formatted_time = formatted_time.replace(key, val)
        formatted_time = formatted_time.replace(" and ", " ")
        formatted_time = formatted_time.replace(", ", " ")
        return formatted_time

    def compute_athlete_stats(self, firstname: str, lastname: str) -> dict:
        athlete = self.athlete_repo.get_by_name(firstname, lastname)
        if athlete is None:
            return {
                "found": False
            }

        athlete_activities = [activity for activity in self.activity_repo.fetch_all() if
                              activity.athlete_id == athlete.internal_id]
        result = self.__compute_top_3(athlete_activities)
        return {
            "found": True,
            "count": result["activities"][0][1],
            "time": self.convert_seconds_to_human_readable(result["time"][0][1]),
            "distance": "{:.1f} km".format(result["distance"][0][1]),
        }

    def refresh_access_token(self) -> None:
        access_info = self.strava_client.refresh_access_token(
            client_id=self.strava_config.client_id,
            client_secret=self.strava_config.client_secret,
            refresh_token=self.strava_config.refresh_token,
        )
        self.strava_access = StravaAccess(
            access_token=access_info["access_token"],
            refresh_token=access_info["refresh_token"],
            expires_at=access_info["expires_at"],
        )
        self.strava_client = Client(access_token=access_info["access_token"])
        tomi_logger.info("Access token refreshed successfully")

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
            time_str += (f"{activity_emoji} {self.__replace_activity_type_name(key)}: "
                         f"{self.convert_seconds_to_human_readable(val)}\n")

        for key, val in sorted(activity_distance_dict.items(), key=lambda item: item[1], reverse=True):
            activity_emoji = strava_activity_to_emoji.get(key, "❓")
            distance_str += f"{activity_emoji} {self.__replace_activity_type_name(key)}: {'{:.1f}'.format(val)} km\n"

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

        return {
            "count": self.__compute_activities_str(result["activities"]),
            "time": self.__compute_time_str(result["time"]),
            "distance": self.__compute_distance_str(result["distance"]),
        }

    def compute_weekly_stats(self) -> dict:
        weekly_activities: List[Activity] = []
        for activity in self.activity_repo.fetch_all():
            if activity.date is not None:
                activity_date = self.__convert_str_date_to_datetime(activity.date)
                if activity_date.isocalendar()[1] == datetime.now().isocalendar()[1]:
                    weekly_activities.append(activity)

        result = self.__compute_top_3(weekly_activities)

        return {
            "count": self.__compute_activities_str(result["activities"]),
            "time": self.__compute_time_str(result["time"]),
            "distance": self.__compute_distance_str(result["distance"]),
        }

    def compute_monthly_stats(self) -> dict:
        monthly_activities: List[Activity] = []
        for activity in self.activity_repo.fetch_all():
            if activity.date is not None:
                activity_date = self.__convert_str_date_to_datetime(activity.date)
                if activity_date.month == datetime.now().month:
                    monthly_activities.append(activity)

        result = self.__compute_top_3(monthly_activities)

        return {
            "count": self.__compute_activities_str(result["activities"]),
            "time": self.__compute_time_str(result["time"]),
            "distance": self.__compute_distance_str(result["distance"]),
        }

    def compute_yearly_stats(self) -> dict:
        yearly_activities: List[Activity] = []
        for activity in self.activity_repo.fetch_all():
            if activity.date is not None:
                activity_date = self.__convert_str_date_to_datetime(activity.date)
                if activity_date.year == datetime.now().year:
                    yearly_activities.append(activity)

        result = self.__compute_top_3(yearly_activities)

        return {
            "count": self.__compute_activities_str(result["activities"]),
            "time": self.__compute_time_str(result["time"]),
            "distance": self.__compute_distance_str(result["distance"]),
        }

    def sync_stats(self) -> List[Activity]:
        activities_added: List[Activity] = []
        if self.strava_access.expires_at < int(time.time()):
            self.refresh_access_token()

        for activity in self.club_activities:
            athlete = self.athlete_repo.get_by_name(activity.athlete.firstname, activity.athlete.lastname)
            if athlete is None:
                tomi_logger.error(f"Activity {activity.name} ({activity.athlete.firstname} "
                                  f"{activity.athlete.lastname}) will be skipped")
                continue

            distance_in_km = float("{:.1f}".format(activity.distance.num / 1000))
            time_in_seconds = int(activity.moving_time.total_seconds())
            speed_in_kmh = distance_in_km / (time_in_seconds / 3600)
            formatted_speed = float("{:.1f}".format(speed_in_kmh))
            new_activity = Activity(
                athlete_id=athlete.internal_id,
                date=None,
                distance=distance_in_km,
                internal_id=str(uuid.uuid4()),
                name=activity.name,
                time=time_in_seconds,
                error=None,
                speed=formatted_speed,
                type=str(activity.type),
            )
            existing_activity = self.activity_repo.get_by_time_and_distance(new_activity.time, new_activity.distance)
            if speed_in_kmh > 90:
                tomi_logger.error(f"Activity {activity.name} ({activity.athlete.firstname} "
                                  f"{activity.athlete.lastname}) will be skipped due to speed of {formatted_speed}")
                new_activity.error = f"Speed of {formatted_speed} km/h"
                activities_added.append(new_activity)

            if (existing_activity is None
                    and (new_activity.distance > 0.00 or new_activity.time > 0)
                    and new_activity.error is None):
                new_activity.date = datetime.now().strftime("%Y-%m-%d %H:%M")
                self.activity_repo.add(new_activity)
                activities_added.append(new_activity)

        return activities_added
