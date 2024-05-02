from discord_config import load_discord_config_from_json
from vendors.discord import tomita


def main():
    tomita.run(
        load_discord_config_from_json("configs/discord_bot_config.json").access_token
    )


if __name__ == "__main__":
    main()
