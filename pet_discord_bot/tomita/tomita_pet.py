import os
import random

from discord import Intents, Client as DiscordClient, Embed

from tomita_discord_bot.tomita.tomita_strava import TomitaStrava
from configs.constants import discord_channel_name_to_id
from app.utils.logs import tomi_logger
from tomita_discord_bot.athlete_pet import AthletePet


def get_replies(file_name):
    with open(os.path.join(os.path.dirname(__file__), 'replies', file_name), 'r') as file:
        replies = file.read().splitlines()
    return replies


class TomitaBiciclistul(AthletePet, DiscordClient):
    async def __playful_commands(self, message):
        if message.content.startswith('!bobite'):
            random_reply = random.choice(self.bobite_replies)
            await message.reply(random_reply, mention_author=True)

        if message.content.startswith('!cacacios'):
            random_reply = random.choice(self.caca_replies)
            await message.reply(random_reply, mention_author=True)

        if message.content.startswith('!sudo_pupic'):
            await message.reply('Frr, frr _sunete de tors_', mention_author=True)

        if message.content.startswith('!pupic'):
            if message.author.id == self.owner_id:
                await message.reply('Frr, frr _sunete de tors_', mention_author=True)
            else:
                await message.reply('Nu pot să te pup, nu te cunosc!', mention_author=True)

    async def __strava_commands(self, message):
        channel = message.channel
        await channel.send('Lăbuțele mele au calculat...')
        strava_stats = self.strava.print_stats()
        embedded_message = Embed(title="General Stats", description="Statisticile sportivilor", color=0x00ff00)
        embedded_message.add_field(name="Tipuri de activități", value=strava_stats["count"], inline=False)
        embedded_message.add_field(name="Timp total", value=strava_stats["time"], inline=False)
        embedded_message.add_field(name="Distanță totală", value=strava_stats["distance"], inline=False)
        await channel.send(embed=embedded_message)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bobite_replies = get_replies('bobite.txt')
        self.caca_replies = get_replies('cacacios.txt')
        self.owner_id = 279996271388000256  # Maurice
        self.commands_playful = ['!bobite', '!cacacios', '!pupic', '!sudo_pupic']
        self.commands_strava = [
            '!strava_stats',
            '!strava_weekly',
            '!strava_monthly',
            '!strava_yearly'
        ]
        self.strava = TomitaStrava()

    async def on_ready(self):
        tomi_logger.info("Your pet is running (around the house)!")
        tomi_logger.info(f'Logged in as {self.user} (ID: {self.user.id})')
        tomi_logger.info('------')

    async def on_message(self, message):
        # We do not want the bot to reply to itself
        if message.author.id == self.user.id:
            return

        if message.content.startswith('!ping'):
            await message.reply('Pong!', mention_author=True)

        # Add logs to playful and strava commands
        if message.content.startswith(tuple(self.commands_playful +
                                            self.commands_strava)):
            tomi_logger.info(f"Received command: {message.content} from {message.author} "
                             f"(id: {message.author.id}) on channel {message.channel} "
                             f"(id: {message.channel.id})")

        if message.content.startswith(tuple(self.commands_playful)):
            await self.__playful_commands(message)

        if message.content.startswith(tuple(self.commands_strava)):
            if message.channel.id != discord_channel_name_to_id['sportivii']:
                await message.reply('Comanda este disponibilă doar pe canalul #🚴🏽-sportivii', mention_author=True)
                return
            await self.__strava_commands(message)


intents = Intents.default()
intents.message_content = True
tomita = TomitaBiciclistul(intents=intents)
