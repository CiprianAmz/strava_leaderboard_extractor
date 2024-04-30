from src.utils.config import config
from src.vendors.discords import tomita

DISCORD_TOKEN = config["discord_token"]


def main():
    tomita.run(DISCORD_TOKEN)


if __name__ == '__main__':
    main()
