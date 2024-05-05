import threading
import schedule

from pet_discord_bot.tomita.tomita_pet import TomitaBiciclistul
from pet_discord_bot.utils.logs import tomi_logger


class TomitaScheduler:
    def __init__(self, tomita_pet: TomitaBiciclistul):
        self.tomita_pet = tomita_pet

    def __start_scheduler(self):
        schedule.every(5).minutes.do(self.tomita_pet.fetch_new_activities)
        while True:
            schedule.run_pending()

    def run(self):
        tomi_logger.info("Starting Tomita scheduler")
        thread = threading.Thread(target=self.__start_scheduler, daemon=True)
        thread.start()

