import json


def main():
    json_file = open("strava-leaderboard-9d85f-default-rtdb-export.json", "r")
    json_content = json_file.read()

    json_dict = json.loads(json_content)

    for activity in list(json_dict["activities"]):
        # Remove activities with date "2024-05-05 19:38"
        if json_dict["activities"][activity]["date"] == "2024-05-05 19:38":
            json_dict["activities"].pop(activity)
            print("Removed activity with date 2024-05-05 19:38")
        else:
            old_distance = json_dict["activities"][activity]["distance"]
            json_dict["activities"][activity]["distance"] = round(old_distance, 1)

    print(len(json_dict["activities"]))
    json.dump(json_dict, open("strava-2.json", "w"))

if __name__ == "__main__":
    main()
