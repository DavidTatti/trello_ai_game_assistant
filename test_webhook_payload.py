import requests
import json

# Update if your local server is running on a different port
WEBHOOK_URL = "http://localhost:5000/webhook"

def test_comment_card():
    payload = {
        "action": {
            "type": "commentCard",
            "data": {
                "card": {
                    "id": "abc123",
                    "name": "Implement Boss Loot Chest Logic"
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
                    "name": "Formation Hold Position Fix"
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
                    "name": "Settlement Trade Interface – Quantity Adjuster"
                },
                "text": "Also disable 'Confirm' if quantity exceeds caravan weight."
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
