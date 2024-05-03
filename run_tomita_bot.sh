#!/bin/bash

python3 -m venv .venv
source .venv/bin/activate

pip3 install -r requirements.txt

chmod +x pet_discord_bot/tomita_bot_entrypoint.py
#python3 pet_discord_bot/tomita_bot_entrypoint.py
nohup python3 pet_discord_bot/tomita_bot_entrypoint.py &

deactivate
