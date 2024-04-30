import random

from discord import Intents, Client

from src.utils.logs import tomi_logger

owner_id = 279996271388000256 # Maurice

class TomitaBiciclistul(Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bobite_replies = self.get_replies('bobite.txt')

    def get_replies(self, file_name):
        with open('replies/' + file_name, 'r') as file:
            replies = file.read().splitlines()
        return replies

    async def on_ready(self):
        tomi_logger.info("Tomâțul is running (around the house)!")
        tomi_logger.info(f'Logged in as {self.user} (ID: {self.user.id})')
        tomi_logger.info('------')

    async def on_message(self, message):
        # We do not want the bot to reply to itself
        if message.author.id == self.user.id:
            return

        if message.content.startswith('!bobite'):
            random_reply = random.choice(self.bobite_replies)
            await message.reply(random_reply, mention_author=True)

        if message.content.startswith('!ping'):
            await message.reply('Pong!', mention_author=True)

        if message.content.startswith('!treats'):
            await message.reply('Primesc doar un treat? Am fost baiat cuminte!!!', mention_author=True)

        if message.content.startswith('!pupic'):
            if message.author.id == owner_id:
                await message.reply('Frr, frr _sunete de tors_', mention_author=True)
            else:
                await message.reply('Nu pot să te pup, nu te cunosc!', mention_author=True)

intents = Intents.default()
intents.message_content = True
tomita = TomitaBiciclistul(intents=intents)
