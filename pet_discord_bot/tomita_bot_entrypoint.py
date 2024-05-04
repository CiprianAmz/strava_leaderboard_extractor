import os

# Needed for the bash script to work on Raspberry Pi
# import sys
# sys.path.insert(0, '/Users/mihaimatraguna/Projects/Clients/strava_leaderboard_extractor')

from tomita.tomita_pet import tomita
from utils.bot_config import load_bot_config_from_json


def main():
    tomita.run(
        load_bot_config_from_json(
            os.path.join(os.path.dirname(__file__), '../configs/discord_bot_config.json')
        ).access_token
    )


if __name__ == "__main__":
    main()
