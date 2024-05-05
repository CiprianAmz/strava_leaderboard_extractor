import os

# Needed for the bash script to work on Raspberry Pi
# import sys
# sys.path.insert(0, '/home/mihai/strava_extractor')

from discord import Intents
from pet_discord_bot.tomita.tomita_pet import TomitaBiciclistul
from pet_discord_bot.tomita.tomita_scheduler import TomitaScheduler
from utils.bot_config import load_bot_config_from_json


def main():
    intents = Intents.default()
    intents.message_content = True
    tomita = TomitaBiciclistul(intents=intents)

    scheduler = TomitaScheduler(tomita)
    scheduler.run()

    tomita.run(
        load_bot_config_from_json(
            os.path.join(os.path.dirname(__file__), '../configs/discord_bot_config.json')
        ).access_token
    )


if __name__ == "__main__":
    main()
