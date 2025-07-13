import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

TRELLO_KEY = os.getenv("TRELLO_KEY")
TRELLO_TOKEN = os.getenv("TRELLO_TOKEN")
TRELLO_BOARD_ID = os.getenv("TRELLO_BOARD_ID")
MOCK_TRELLO = os.getenv("MOCK_TRELLO", "false").lower() == "true"

LABEL_MAP_FILE = "label_map.json"
MOCK_CARDS = {
    "abc123": "mock_card_dungeon.json",
    "def456": "mock_card_battle.json",
    "ghi789": "mock_card_trade_ui.json"
}

# Load label map if available
LABELS_BY_NAME = {}
try:
    with open(LABEL_MAP_FILE, "r") as f:
        LABELS_BY_NAME = json.load(f)
except FileNotFoundError:
    print("⚠️ Warning: label_map.json not found. Run sync_labels.py first.")

def fetch_card_data(card_id):
    if MOCK_TRELLO:
        file = MOCK_CARDS.get(card_id)
        if not file:
            raise ValueError(f"No mock file defined for card ID: {card_id}")
        with open(f"mock_data/{file}", "r") as f:
            return json.load(f)

    url = f"https://api.trello.com/1/cards/{card_id}"
    params = {
        "key": TRELLO_KEY,
        "token": TRELLO_TOKEN,
        "fields": "name,desc,url,idList"
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

def fetch_cards_from_list(list_id):
    if MOCK_TRELLO:
        with open("mock_data/mock_list_cards.json", "r") as f:
            return json.load(f)

    url = f"https://api.trello.com/1/lists/{list_id}/cards"
    params = {
        "key": TRELLO_KEY,
        "token": TRELLO_TOKEN
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

def comment_on_card(card_id, message):
    url = f"https://api.trello.com/1/cards/{card_id}/actions/comments"
    params = {
        "key": TRELLO_KEY,
        "token": TRELLO_TOKEN,
        "text": message
    }
    response = requests.post(url, params=params)
    response.raise_for_status()

def update_card_description(card_id, new_desc):
    url = f"https://api.trello.com/1/cards/{card_id}"
    params = {
        "key": TRELLO_KEY,
        "token": TRELLO_TOKEN
    }
    data = {
        "desc": new_desc
    }
    response = requests.put(url, params=params, data=data)
    response.raise_for_status()

def set_card_labels(card_id, labels_to_add):
    url = f"https://api.trello.com/1/cards/{card_id}/idLabels"
    for label_name in labels_to_add:
        label_id = LABELS_BY_NAME.get(label_name)
        if label_id:
            response = requests.post(url, params={
                "key": TRELLO_KEY,
                "token": TRELLO_TOKEN,
                "value": label_id
            })
            if response.status_code != 200:
                print(f"⚠️ Failed to apply label: {label_name}")
