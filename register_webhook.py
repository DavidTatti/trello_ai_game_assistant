#!/usr/bin/env python3
"""
Script to register a Trello webhook for the In Progress list
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

TRELLO_KEY = os.getenv("TRELLO_KEY")
TRELLO_TOKEN = os.getenv("TRELLO_TOKEN")
TRELLO_BOARD_ID = os.getenv("TRELLO_BOARD_ID")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # Your server's webhook URL

def get_board_lists():
    """Get all lists in the board to find the In Progress list"""
    url = f"https://api.trello.com/1/boards/{TRELLO_BOARD_ID}/lists"
    params = {
        "key": TRELLO_KEY,
        "token": TRELLO_TOKEN
    }
    
    response = requests.get(url, params=params)
    response.raise_for_status()
    
    lists = response.json()
    print("📋 Available lists:")
    for lst in lists:
        print(f"  - {lst['name']} (ID: {lst['id']})")
    
    return lists

def find_in_progress_list(lists):
    """Find the In Progress list by name"""
    in_progress_names = ["In Progress", "In-Progress", "InProgress", "Doing", "Active"]
    
    for lst in lists:
        if lst['name'] in in_progress_names:
            return lst
    
    return None

def register_webhook(list_id, webhook_url):
    """Register a webhook for the specified list"""
    url = "https://api.trello.com/1/webhooks/"
    
    data = {
        "key": TRELLO_KEY,
        "callbackURL": webhook_url,
        "idModel": list_id,
        "description": "Webhook for In Progress list changes"
    }
    
    response = requests.post(url, data=data)
    
    if response.status_code == 200:
        webhook_data = response.json()
        print(f"✅ Webhook registered successfully!")
        print(f"   Webhook ID: {webhook_data['id']}")
        print(f"   List ID: {webhook_data['idModel']}")
        print(f"   Callback URL: {webhook_data['callbackURL']}")
        return webhook_data
    else:
        print(f"❌ Failed to register webhook: {response.status_code}")
        print(f"   Response: {response.text}")
        return None

def list_existing_webhooks():
    """List all existing webhooks for the board"""
    url = f"https://api.trello.com/1/tokens/{TRELLO_TOKEN}/webhooks"
    params = {
        "key": TRELLO_KEY
    }
    
    response = requests.get(url, params=params)
    response.raise_for_status()
    
    webhooks = response.json()
    if webhooks:
        print("🔗 Existing webhooks:")
        for webhook in webhooks:
            print(f"  - ID: {webhook['id']}")
            print(f"    Description: {webhook.get('description', 'N/A')}")
            print(f"    URL: {webhook['callbackURL']}")
            print(f"    Model: {webhook['idModel']}")
            print()
    else:
        print("📭 No existing webhooks found")
    
    return webhooks

def delete_webhook(webhook_id):
    """Delete a webhook by ID"""
    url = f"https://api.trello.com/1/webhooks/{webhook_id}"
    params = {
        "key": TRELLO_KEY,
        "token": TRELLO_TOKEN
    }
    
    response = requests.delete(url, params=params)
    
    if response.status_code == 200:
        print(f"✅ Webhook {webhook_id} deleted successfully")
        return True
    else:
        print(f"❌ Failed to delete webhook: {response.status_code}")
        return False

def main():
    print("🔧 Trello Webhook Registration Tool")
    print("=" * 50)
    
    # Check required environment variables
    if not all([TRELLO_KEY, TRELLO_TOKEN, TRELLO_BOARD_ID]):
        print("❌ Missing required environment variables:")
        print("   - TRELLO_KEY")
        print("   - TRELLO_TOKEN") 
        print("   - TRELLO_BOARD_ID")
        return
    
    if not WEBHOOK_URL:
        print("❌ Missing WEBHOOK_URL environment variable")
        print("   Set this to your server's webhook endpoint (e.g., https://your-domain.com/webhook)")
        return
    
    print(f"🎯 Target webhook URL: {WEBHOOK_URL}")
    print()
    
    # List existing webhooks
    print("📋 Checking existing webhooks...")
    existing_webhooks = list_existing_webhooks()
    print()
    
    # Get board lists
    print("📋 Getting board lists...")
    lists = get_board_lists()
    print()
    
    # Find In Progress list
    in_progress_list = find_in_progress_list(lists)
    
    if not in_progress_list:
        print("❌ Could not find 'In Progress' list")
        print("   Available list names: " + ", ".join([lst['name'] for lst in lists]))
        print("   Supported names: In Progress, In-Progress, InProgress, Doing, Active")
        return
    
    print(f"✅ Found In Progress list: {in_progress_list['name']} (ID: {in_progress_list['id']})")
    print()
    
    # Check if webhook already exists for this list
    existing_webhook = None
    for webhook in existing_webhooks:
        if webhook['idModel'] == in_progress_list['id']:
            existing_webhook = webhook
            break
    
    if existing_webhook:
        print(f"⚠️  Webhook already exists for this list:")
        print(f"   ID: {existing_webhook['id']}")
        print(f"   URL: {existing_webhook['callbackURL']}")
        
        choice = input("   Do you want to delete the existing webhook and create a new one? (y/N): ")
        if choice.lower() == 'y':
            if delete_webhook(existing_webhook['id']):
                print("   Proceeding with new webhook registration...")
            else:
                print("   Failed to delete existing webhook. Aborting.")
                return
        else:
            print("   Keeping existing webhook. No changes made.")
            return
    
    # Register new webhook
    print("🔗 Registering new webhook...")
    webhook_data = register_webhook(in_progress_list['id'], WEBHOOK_URL)
    
    if webhook_data:
        print()
        print("🎉 Webhook registration complete!")
        print("   Your server will now receive webhooks for any changes to cards in the In Progress list.")
        print()
        print("📝 Next steps:")
        print("   1. Make sure your server is running and accessible at the webhook URL")
        print("   2. Test by moving a card to the In Progress list")
        print("   3. Check your server logs for incoming webhook requests")

if __name__ == "__main__":
    main() 