import os
import random
from collections import deque
from datetime import datetime
from typing import List

import psutil

from discord import Embed, Message, Intents, File
from discord.ext import tasks
from humanfriendly import format_timespan

from pet_discord_bot.types.activity import Activity
from pet_discord_bot.types.athlete import Athlete
from strava_leaderboard_extractor.strava_config import load_strava_config_from_json

from pet_discord_bot.config.constants import discord_channel_name_to_id, strava_activity_to_emoji
from pet_discord_bot.utils.bot_config import load_bot_config_from_json
from pet_discord_bot.vendors.firebase import FirebaseClient
from pet_discord_bot.repository.athlete import AthleteRepository
from pet_discord_bot.repository.activity import ActivityRepository
from pet_discord_bot.bot_client import BotClient
from pet_discord_bot.tomita.tomita_strava import TomitaStrava
from pet_discord_bot.utils.logs import tomi_logger


def get_replies(file_name):
    with open(os.path.join(os.path.dirname(__file__), '../../bot_replies', file_name), 'r') as file:
        replies = file.read().splitlines()
    return replies


class TomitaBiciclistul(BotClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.firebase_client = FirebaseClient(
            db_url=load_bot_config_from_json(
                os.path.join(os.path.dirname(__file__), '../../configs/discord_bot_config.json')
            ).firebase_url,
            credential_path=os.path.join(os.path.dirname(__file__), '../../configs/firebase_config.json')
        )
        self.athlete_repository = AthleteRepository(client=self.firebase_client)
        self.activity_repository = ActivityRepository(client=self.firebase_client)

        self.bobite_replies = get_replies('bobite.txt')
        self.caca_replies = get_replies('cacacios.txt')
        self.sticks_replies = get_replies('sticks.txt')
        self.owner_id = 279996271388000256  # Maurice
        self.commands_playful = ['!bobite', '!cacacios', '!pupic', '!sudo_pupic', '!sticks']
        self.commands_strava = [
            '!strava_athlete',
            '!strava_auth',
            '!strava_daily',
            '!strava_monthly',
            '!strava_stats',
            '!strava_sync',
            '!strava_weekly',
            '!strava_yearly',
        ]
        self.commands_health = ['!verifica_labutele', '!verifica_puful', '!verifica_logurile', '!descarca_blanosul']

        self.strava = TomitaStrava(
            config_json=load_strava_config_from_json(
                os.path.join(os.path.dirname(__file__), '../../configs/strava_config.json')),
            activity_repo=self.activity_repository,
            athlete_repo=self.athlete_repository
        )

    async def __playful_commands(self, message: Message) -> None:
        if message.content.startswith('!bobite'):
            random_reply = random.choice(self.bobite_replies)
            await message.reply(random_reply, mention_author=True)

        if message.content.startswith('!cacacios'):
            random_reply = random.choice(self.caca_replies)
            await message.reply(random_reply, mention_author=True)

        if message.content.startswith('!sticks'):
            random_reply = random.choice(self.sticks_replies)
            await message.reply(random_reply, mention_author=True)

        if message.content.startswith('!sudo_pupic'):
            await message.reply('Frr, frr _sunete de tors_', mention_author=True)

        if message.content.startswith('!pupic'):
            if message.author.id == self.owner_id:
                await message.reply('Frr, frr _sunete de tors_', mention_author=True)
            else:
                await message.reply('Nu pot să te pup, nu te cunosc!', mention_author=True)

    async def __strava_commands(self, message: Message) -> None:
        channel = message.channel
        await channel.send('🐾 Lăbuțele mele verifică Strava 🐾')
        if message.content.startswith('!strava_stats'):
            strava_stats = self.strava.compute_overall_stats()
            embedded_message = Embed(title="General Stats", description="Statisticile sportivilor", color=0x00ff00)
            embedded_message.add_field(name="Tipuri de activități", value=strava_stats["count"], inline=False)
            embedded_message.add_field(name="Timp total", value=strava_stats["time"], inline=False)
            embedded_message.add_field(name="Distanță totală", value=strava_stats["distance"], inline=False)
            await channel.send(embed=embedded_message)

        if message.content.startswith('!strava_sync'):
            added_activities = self.strava.sync_stats()
            if len(added_activities) == 0:
                await channel.send('🥺 Nu am adăugat nicio activitate nouă în baza de date!')
            else:
                await self.__send_new_activities(added_activities)
                await channel.send(f'✅ Am adăugat {len(added_activities)} activități noi în baza de date!')

        if message.content.startswith('!strava_auth'):
            self.strava.refresh_access_token()
            await channel.send('🔑 Lăbuțele mele sunt iar autorizate pe Strava!')

        if message.content.startswith('!strava_athlete'):
            firstname = message.content.split(' ')[1]
            lastname = message.content.split(' ')[2]
            strava_stats = self.strava.compute_athlete_stats(firstname, lastname)
            if strava_stats is None:
                await channel.send(f'❌ Nu am găsit sportivul cu numele {firstname} {lastname}!')
                return

            embedded_message = Embed(title=f"{firstname} Stats", description="Statisticile sportivului", color=0x00ff00)
            embedded_message.add_field(name="Activități totale", value=strava_stats["count"], inline=False)
            embedded_message.add_field(name="Timp total", value=strava_stats["time"], inline=False)
            embedded_message.add_field(name="Distanță totală", value=strava_stats["distance"], inline=False)
            await channel.send(embed=embedded_message)

        if message.content.startswith('!strava_daily'):
            daily_stats = self.strava.compute_daily_stats()
            embedded_message = Embed(title="Daily Stats", description="Statisticile zilnice", color=0x00ff00)
            embedded_message.add_field(name="Numar de activități", value=daily_stats["count"], inline=False)
            embedded_message.add_field(name="Timp total", value=daily_stats["time"], inline=False)
            embedded_message.add_field(name="Distanță totală", value=daily_stats["distance"], inline=False)
            await channel.send(embed=embedded_message)

        if message.content.startswith('!strava_weekly'):
            weekly_stats = self.strava.compute_weekly_stats()
            embedded_message = Embed(title="Weekly Stats", description="Statisticile săptămânale", color=0x00ff00)
            embedded_message.add_field(name="Numar de activități", value=weekly_stats["count"], inline=False)
            embedded_message.add_field(name="Timp total", value=weekly_stats["time"], inline=False)
            embedded_message.add_field(name="Distanță totală", value=weekly_stats["distance"], inline=False)
            await channel.send(embed=embedded_message)

        if message.content.startswith('!strava_monthly'):
            monthly_stats = self.strava.compute_monthly_stats()
            embedded_message = Embed(title="Monthly Stats", description="Statisticile lunare", color=0x00ff00)
            embedded_message.add_field(name="Numar de activități", value=monthly_stats["count"], inline=False)
            embedded_message.add_field(name="Timp total", value=monthly_stats["time"], inline=False)
            embedded_message.add_field(name="Distanță totală", value=monthly_stats["distance"], inline=False)
            await channel.send(embed=embedded_message)

        if message.content.startswith('!strava_yearly'):
            yearly_stats = self.strava.compute_yearly_stats()
            embedded_message = Embed(title="Yearly Stats", description="Statisticile anuale", color=0x00ff00)
            embedded_message.add_field(name="Numar de activități", value=yearly_stats["count"], inline=False)
            embedded_message.add_field(name="Timp total", value=yearly_stats["time"], inline=False)
            embedded_message.add_field(name="Distanță totală", value=yearly_stats["distance"], inline=False)
            await channel.send(embed=embedded_message)

    async def __health_commands(self, message: Message) -> None:
        if message.content.startswith('!verifica_labutele'):
            await message.reply('🏥 Doctorul verifică labuțele!', mention_author=True)
            cpu_usage = psutil.cpu_percent()
            ram_usage = psutil.virtual_memory().percent
            await message.channel.send(
                f'ℹ️ Hostname: {os.uname().nodename} | 🖥️ CPU: {cpu_usage}% | 🧠 RAM: {ram_usage}%')

        if message.content.startswith('!verifica_puful'):
            await message.reply('𐄹 Se canterește blănosul!', mention_author=True)
            hdd = psutil.disk_usage('/')
            hdd_total = hdd.total / (2 ** 30)
            hdd_used = hdd.used / (2 ** 30)
            hdd_free = hdd.free / (2 ** 30)
            await message.channel.send(f'💾: {hdd_used:.1f}GB / {hdd_total:.1f}GB | 🎉 Liber: {hdd_free:.1f}GB')

        if message.content.startswith('!verifica_logurile'):
            await message.reply('🔦 Se verifică logurile!', mention_author=True)
            file_name = os.path.join(os.path.dirname(__file__), '../../nohup.out')
            with open(file_name, 'r') as file:
                last_15_lines = deque(file, 15)
            discord_logs = ""
            for line in last_15_lines:
                discord_logs += line
            print(discord_logs)
            await message.channel.send(f'```\n{discord_logs}\n```')

        if message.content.startswith('!descarca_blanosul'):
            start_time = datetime.now()
            await message.reply('📥 Se descarcă blănosul!', mention_author=True)
            backup_name = datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + "_backup.json"
            backup_path = os.path.join(os.path.dirname(__file__), '../backups', backup_name)
            self.firebase_client.backup_to_json(backup_path)
            await message.channel.send(f'📦 Backup-ul a fost salvat cu numele: {backup_name}')
            await message.channel.send(f'🔢 Size: {os.path.getsize(backup_path) / (2 ** 20):.2f} MB')
            await message.channel.send(f'🕛 Durata: {format_timespan(datetime.now() - start_time)}')
            await message.channel.send(file=File(backup_path))


    async def __send_startup_message(self, t_activities: int, t_athletes: int) -> None:
        channel = self.get_channel(discord_channel_name_to_id['bot_home'])
        embedded_message = Embed(
            title="✅ Tomita started",
            description=f"🐈 Tomita is running (around the house)!\n\nℹ️ Hostname: {os.uname().nodename}",
            color=0xFFC0CB
        )
        embedded_message.add_field(name="Athletes", value=f"{t_athletes} athletes", inline=False)
        embedded_message.add_field(name="Activities", value=f"{t_activities} activities", inline=False)
        await channel.send(embed=embedded_message)

    async def __send_new_activities(self, activities: List[Activity]) -> None:
        channel = self.get_channel(discord_channel_name_to_id['sportivii'])
        for activity in activities:
            athlete: Athlete = self.athlete_repository.get(activity.athlete_id)
            await channel.send(
                f"<@{athlete.discord_id}> a adăugat o nouă activitate **{activity.name}** pe Strava!\n"
                f"| {strava_activity_to_emoji.get(activity.type, '❓')} **Tip:** {activity.type} "
                f"| 🕒 **Timp:** {self.strava.convert_seconds_to_human_readable(activity.time)} "
                f"| 🛣️ **Distanță:** {activity.distance} km")

    @tasks.loop(minutes=10)
    async def fetch_new_activities(self) -> None:
        tomi_logger.info("Fetching new activities from Strava...")
        new_activities = self.strava.sync_stats()
        await self.__send_new_activities(new_activities)
        tomi_logger.info(f"Sent {len(new_activities)} new activities to Discord")

    async def on_ready(self):
        athletes = self.athlete_repository.fetch_all()
        activities = self.activity_repository.fetch_all()
        tomi_logger.info(f'Loaded {len(athletes)} athletes from Firebase')
        tomi_logger.info(f'Loaded {len(activities)} activities from Firebase')

        tomi_logger.info("Tomita is running (around the house)!")
        tomi_logger.info(f'Logged in as {self.user} (ID: {self.user.id})')
        tomi_logger.info('------')

        await self.__send_startup_message(len(activities), len(athletes))
        self.fetch_new_activities.start()

    async def on_message(self, message):
        # We do not want the bot to reply to itself
        if message.author.id == self.user.id:
            return

        if message.content.startswith('!ping'):
            await message.reply('Pong!', mention_author=True)

        # Add logs to playful and strava commands
        if message.content.startswith(tuple(self.commands_playful +
                                            self.commands_strava +
                                            self.commands_health)):
            tomi_logger.info(f"Received command: {message.content} from {message.author} "
                             f"(id: {message.author.id}) on channel {message.channel} "
                             f"(id: {message.channel.id})")

        if message.content.startswith(tuple(self.commands_playful)):
            await self.__playful_commands(message)

        if message.content.startswith(tuple(self.commands_strava)):
            if (message.channel.id != discord_channel_name_to_id['sportivii'] and
                    message.channel.id != discord_channel_name_to_id['bot_home']):
                await message.reply('Comanda este disponibilă doar pe canalul #🚴🏽-sportivii', mention_author=True)
                return
            await self.__strava_commands(message)

        if message.content.startswith(tuple(self.commands_health)):
            if message.channel.id != discord_channel_name_to_id['bot_home']:
                await message.reply('Comanda este disponibilă doar pe canalul 🔧-bot-testing', mention_author=True)
                return

            await self.__health_commands(message)


intents = Intents.default()
intents.message_content = True
tomita = TomitaBiciclistul(intents=intents)
