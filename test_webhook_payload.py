import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

# Update if your local server is running on a different port
WEBHOOK_URL = os.getenv("WEBHOOK_URL") # "http://localhost:5000/webhook"

def test_comment_card():
    payload = {
        "action": {
            "type": "commentCard",
            "data": {
                "card": {
                    "id": "abc123",
                    "name": "Implement Boss Loot Chest Logic",
                    "desc": "Design and implement the loot system for boss chests including rarity tiers, follower-specific items, and dynamic loot tables based on boss difficulty."
                },
                "text": "Should the loot include special follower-only items?"
            }
        }
    }
    r = requests.post(WEBHOOK_URL, json=payload)
    print(f"[CommentCard] Status: {r.status_code}")

def test_update_card():
    payload = {
        "action": {
            "type": "updateCard",
            "data": {
                "card": {
                    "id": "def456",
                    "name": "Formation Hold Position Fix",
                    "desc": "Fix the issue where formations don't maintain their positions during combat. Implement proper position holding logic and visual indicators."
                }
            }
        }
    }
    r = requests.post(WEBHOOK_URL, json=payload)
    print(f"[UpdateCard] Status: {r.status_code}")

def test_trade_ui_card():
    payload = {
        "action": {
            "type": "commentCard",
            "data": {
                "card": {
                    "id": "ghi789",
                    "name": "Settlement Trade Interface – Quantity Adjuster",
                    "desc": "Create a user interface component for adjusting trade quantities in settlements. Include validation for caravan weight limits and inventory constraints."
                },
                "text": "Also disable 'Confirm' if quantity exceeds caravan weight."
            }
        }
    }
    r = requests.post(WEBHOOK_URL, json=payload)
    print(f"[Trade UI Comment] Status: {r.status_code}")

def test_character_rotation_card():
    payload = {
        "action": {
            "type": "commentCard",
            "data": {
                "card": {
                    "id": "foo123",
                    "name": "Character Rotation is not smooth on client in multiplayer with dedicated server.",
                    "desc": "Rotation should be smooth on Clients, all characters use the Character Movement component. Also in Battles and Sieges there are hundreds of characters fighting, so should work for that amount of characters."
                },
                "text": "AI characters use normal ai system and behaviour tree, so they should be able to rotate smoothly. But somehow they are not rotating smoothly."
            }
        }
    }
    r = requests.post(WEBHOOK_URL, json=payload)
    print(f"[Trade UI Comment] Status: {r.status_code}")

if __name__ == "__main__":
    print("🚀 Simulating Trello webhook events...\n")
    test_comment_card()
    test_update_card()
    test_trade_ui_card()
    test_character_rotation_card()
