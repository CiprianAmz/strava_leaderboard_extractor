from humanfriendly import format_timespan
from stravalib import Client

from app.config.config import config
from app.config.constants import strava_activity_to_emoji


class TomitaStrava:
    def __init__(self):
        self.strava_client = Client(access_token=config["strava_access_token"])
        self.club_activities = self.strava_client.get_club_activities(
            club_id=config["strava_club_id"],
            limit=config.get("activities_limit", None)
        )

    def print_stats(self):
        activity_type_dict = {}
        activity_type_time_dict = {}
        activity_type_distance_dict = {}

        for activity in self.club_activities:
            if activity.type not in activity_type_dict:
                activity_type_dict.update({activity.type: 0})

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
            result_time += f"{activity_emoji} {key}: {format_timespan(val)} seconds\n"

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
