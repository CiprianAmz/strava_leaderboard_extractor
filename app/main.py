import threading

from app.clients.tomita.tomita_pet import tomita
from app.config.config import config
from app.repository.leaderboard import RepositoryLeaderboard

DISCORD_TOKEN = config["discord_token"]


def main():
    leaderboard = RepositoryLeaderboard()
    scheduler_thread = threading.Thread(target=leaderboard.start_scheduler)
    scheduler_thread.start()

    tomita.run(DISCORD_TOKEN)


if __name__ == '__main__':
    main()
