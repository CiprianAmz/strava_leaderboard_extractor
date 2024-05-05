import threading
import schedule

from pet_discord_bot.tomita.tomita_pet import TomitaBiciclistul


class TomitaScheduler:
    def __init__(self, tomita_pet: TomitaBiciclistul):
        self.tomita_pet = tomita_pet

    def __start_scheduler(self):
        schedule.every(30).minutes.do(self.tomita_pet.fetch_new_activities)
        while True:
            schedule.run_pending()

    def run(self):
        print("Starting scheduler")
        thread = threading.Thread(target=self.__start_scheduler, daemon=True)
        thread.start()

