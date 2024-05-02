#!/bin/bash

python3 -m venv .venv
source .venv/bin/activate

pip3 install -r requirements.txt
python3 pet_discord_bot/tomita_bot_entrypoint.py

deactivate
