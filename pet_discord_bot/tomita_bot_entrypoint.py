import os

from pet_discord_bot.tomita.tomita_pet import tomita
from pet_discord_bot.utils.discord_config import load_discord_config_from_json


def main():
    tomita.run(
        load_discord_config_from_json(
            os.path.join(os.path.dirname(__file__), '../configs/discord_bot_config.json')
        ).access_token
    )


if __name__ == "__main__":
    main()
