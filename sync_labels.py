import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

TRELLO_KEY = os.getenv("TRELLO_KEY")
TRELLO_TOKEN = os.getenv("TRELLO_TOKEN")
TRELLO_BOARD_ID = os.getenv("TRELLO_BOARD_ID")
OUTPUT_FILE = "label_map.json"

def sync_labels():
    url = f"https://api.trello.com/1/boards/{TRELLO_BOARD_ID}/labels"
    params = {
        "key": TRELLO_KEY,
        "token": TRELLO_TOKEN,
        "limit": 1000  # Fetch up to 1000 labels
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        labels = response.json()

        label_map = {label["name"]: label["id"] for label in labels if label["name"]}

        with open(OUTPUT_FILE, "w") as f:
            json.dump(label_map, f, indent=2)

        print(f"✅ Synced {len(label_map)} labels to {OUTPUT_FILE}")

    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to sync labels: {e}")

if __name__ == "__main__":
    sync_labels()
