import os
from dotenv import load_dotenv
from trello_utils import fetch_cards_from_list
from ai_utils import summarize_for_morning
from slack_utils import post_to_main, log_to_slack

load_dotenv()

IN_PROGRESS_LIST_ID = os.getenv("IN_PROGRESS_LIST_ID")
SLACK_CHANNEL = os.getenv("SLACK_CHANNEL")

def main():
    try:
        log_to_slack("🌅 Starting daily summary script")

        # Fetch all in-progress cards
        cards = fetch_cards_from_list(IN_PROGRESS_LIST_ID)
        if not cards:
            post_to_main("✅ No active cards in progress this morning.")
            log_to_slack("📭 No cards to summarize.")
            return

        for card in cards:
            summary = summarize_for_morning(card)
            msg = f"📌 *{card['name']}*\n{summary}\n{card['url']}"
            post_to_main(msg)

        log_to_slack(f"✅ Sent {len(cards)} card summaries to Slack")

    except Exception as e:
        log_to_slack(f"❌ Error in daily summary: {str(e)}")

if __name__ == "__main__":
    main()
