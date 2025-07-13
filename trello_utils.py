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
    "ghi789": "mock_card_trade_ui.json",
    "foo123": "mock_card_character_rotation.json"
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
    
    # Check message length - if it's very large, split into multiple comments
    if len(message) > 8000:  # Trello has limits around 10k characters
        split_comments = split_large_message(message)
        for i, comment_part in enumerate(split_comments, 1):
            comment_text = f"[Part {i}/{len(split_comments)}]\n{comment_part}"
            _post_single_comment(url, comment_text)
    else:
        _post_single_comment(url, message)

def _post_single_comment(url, message):
    """Helper function to post a single comment"""
    # Check message length - if it's large, use request body instead of query params
    if len(message) > 1000:  # Threshold for switching to body
        params = {
            "key": TRELLO_KEY,
            "token": TRELLO_TOKEN
        }
        data = {
            "text": message
        }
        response = requests.post(url, params=params, data=data)
    else:
        # For smaller messages, use query params (more efficient)
        params = {
            "key": TRELLO_KEY,
            "token": TRELLO_TOKEN,
            "text": message
        }
        response = requests.post(url, params=params)
    
    response.raise_for_status()

def split_large_message(message, max_length=7000):
    """Split a large message into smaller chunks"""
    if len(message) <= max_length:
        return [message]
    
    # Try to split on paragraph breaks first
    paragraphs = message.split('\n\n')
    chunks = []
    current_chunk = ""
    
    for paragraph in paragraphs:
        if len(current_chunk) + len(paragraph) + 2 <= max_length:
            current_chunk += (paragraph + '\n\n')
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = paragraph + '\n\n'
    
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    # If still too large, split on sentences
    if any(len(chunk) > max_length for chunk in chunks):
        new_chunks = []
        for chunk in chunks:
            if len(chunk) <= max_length:
                new_chunks.append(chunk)
            else:
                sentences = chunk.split('. ')
                current_sentence_chunk = ""
                for sentence in sentences:
                    if len(current_sentence_chunk) + len(sentence) + 2 <= max_length:
                        current_sentence_chunk += sentence + '. '
                    else:
                        if current_sentence_chunk:
                            new_chunks.append(current_sentence_chunk.strip())
                        current_sentence_chunk = sentence + '. '
                if current_sentence_chunk:
                    new_chunks.append(current_sentence_chunk.strip())
        chunks = new_chunks
    
    return chunks

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
