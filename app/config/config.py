import json


def load_config():
    with open("../config.json") as f:
        return dict(json.load(f))


config = load_config()
