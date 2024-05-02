from strava_config import load_strava_config_from_json
from leaderboard_extractor import extract_leaderboard


def main():
    extract_leaderboard(
        load_strava_config_from_json("configs/strava_config.json")
    )


if __name__ == "__main__":
    main()
