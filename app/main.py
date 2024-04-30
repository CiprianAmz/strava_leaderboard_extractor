from app.clients.tomita.tomita_pet import tomita
from app.config.config import config

DISCORD_TOKEN = config["discord_token"]


def main():
    tomita.run(DISCORD_TOKEN)


if __name__ == '__main__':
    main()
