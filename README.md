### Strava Leaderboard Extractor (Tomâțul Biciclistu)

#### What is this?

This is a simple leaderboard extractor for Strava clubs using stravalib. You can also hook it to a Discord bot to send
updates to your server - or respond to different commands. (like `!leaderboard` `!stats` etc.)

#### How to use?

1. Complete `config.json` with your configuration. Access https://www.strava.com/settings/api to retrieve your API_KEY
2. Run: `./run.sh`

#### How to get the Firebase .json credentials?

To generate a json file with the credentials for Firebase, follow these steps:

- In the Firebase console, open Settings > [Service Accounts](https://console.firebase.google.com/project/_/settings/serviceaccounts/adminsdk?authuser=0).

- Click Generate New Private Key, then confirm by clicking Generate Key.

- Securely store the JSON file containing the key.