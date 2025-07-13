from flask import Flask, request
from dotenv import load_dotenv
import os

from trello_utils import fetch_card_data
from ai_utils import process_card_update
from slack_utils import log_to_slack

load_dotenv()

app = Flask(__name__)

@app.route('/webhook', methods=['HEAD', 'POST'])
def handle_webhook():
    if request.method == 'HEAD':
        # Trello webhook validation ping
        return '', 200

    payload = request.json
    action = payload.get('action', {})
    action_type = action.get('type')

    if action_type not in ['commentCard', 'updateCard']:
        log_to_slack(f"❌ Webhook action_type not commentCard or updateCard")
        return '', 200  # Ignore other event types

    # Prevent responding to its own AI-generated comment
    if action_type == "commentCard":
        comment_text = action.get("data", {}).get("text", "")
        if "[🤖 AI Reply]" in comment_text:
            log_to_slack("🛑 Skipped AI-generated comment to avoid loop.")
            return '', 200

    try:
        card_id = action['data']['card']['id']
        log_to_slack(f"✅ Fetch Card Data: {card_id}")
        card = fetch_card_data(card_id)
        log_to_slack(f"✅ Start Process Card: {card_id}")
        process_card_update(card, action)
        log_to_slack(f"✅ Processed Trello action: {action_type} for card '{card['name']}'")
    except Exception as e:
        log_to_slack(f"❌ Webhook error: {str(e)}")

    return '', 200

if __name__ == '__main__':
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
