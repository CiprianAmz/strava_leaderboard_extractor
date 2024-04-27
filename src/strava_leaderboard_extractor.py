from stravalib.client import Client
import datetime
import json

def load_config():
    with open("strava_extractor_config.json") as f:
        return dict(json.load(f))

def print_sorted_leaderboard(dict_leaderboard, print_func=lambda key, val: print(f"{key}: {val}")):
    for key, val in dict(sorted(dict_leaderboard.items(), key=lambda item: item[1], reverse=True)).items():
        print_func(key, val)

def main():
    config = load_config()

    client = Client(access_token=config["strava_access_token"])
    club_activities = client.get_club_activities(
        club_id=config["strava_club_id"],
        limit=config.get("activities_limit", None)
    )

    ranking_moving_time_dict = {}
    ranking_activities_count_dict = {}
    ranking_distance_dict = {}

    for activity in club_activities:
        athlete_name = f"{activity.athlete.firstname} {activity.athlete.lastname}"

        if athlete_name not in ranking_moving_time_dict:
            ranking_moving_time_dict.update({athlete_name : datetime.timedelta()})

        ranking_moving_time_dict[athlete_name] += activity.moving_time

        if athlete_name not in ranking_activities_count_dict:
            ranking_activities_count_dict.update({athlete_name : 0})

        ranking_activities_count_dict[athlete_name] += 1

        if athlete_name not in ranking_distance_dict:
            ranking_distance_dict.update({athlete_name : 0})

        ranking_distance_dict[athlete_name] += activity.distance

    print("\n Moving Time leaderboard:")
    print_sorted_leaderboard(ranking_moving_time_dict)

    print("\n Activities count leaderboard:")
    print_sorted_leaderboard(ranking_activities_count_dict)

    print("\n Distance leaderboard:")
    print_sorted_leaderboard(ranking_distance_dict)

if __name__ == "__main__":
    main()
