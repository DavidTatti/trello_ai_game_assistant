import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv

load_dotenv()

SLACK_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_CHANNEL = os.getenv("SLACK_CHANNEL")
SLACK_LOG_CHANNEL = os.getenv("SLACK_LOG_CHANNEL")

client = WebClient(token=SLACK_TOKEN)

def post_to_main(message: str):
    """
    Send a message to the main Slack channel (e.g., for daily summaries).
    """
    try:
        client.chat_postMessage(channel=SLACK_CHANNEL, text=message)
    except SlackApiError as e:
        print(f"[Slack ERROR] Failed to post to main channel: {e.response['error']}")

def log_to_slack(message: str):
    """
    Send a log or debug message to the Slack log channel.
    """
    try:
        client.chat_postMessage(channel=SLACK_LOG_CHANNEL, text=f"[LOG] {message}")
    except SlackApiError as e:
        print(message)
        # print(f"[Slack ERROR] Failed to log to Slack: {e.response['error']}")
