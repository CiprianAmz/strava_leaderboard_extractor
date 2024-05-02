#!/bin/bash

python3 -m venv .venv
source .venv/bin/activate

pip3 install -r requirements.txt
python3 strava_leaderboard_extractor/leaderboard_extractor_entrypoint.py

deactivate
