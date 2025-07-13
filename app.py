from flask import Flask, request
from dotenv import load_dotenv
import os
import threading
import queue
import time
from datetime import datetime

from trello_utils import fetch_card_data
from ai_utils import process_card_update
from slack_utils import log_to_slack

load_dotenv()

app = Flask(__name__)

# Request queue for processing webhooks sequentially
webhook_queue = queue.Queue()
processing_thread = None
queue_running = True

def webhook_processor():
    """Background thread to process webhook requests sequentially"""
    global queue_running
    
    while queue_running:
        try:
            # Get next webhook request from queue (blocking with timeout)
            webhook_data = webhook_queue.get(timeout=1)
            
            if webhook_data is None:  # Shutdown signal
                break
                
            payload, action, action_type = webhook_data
            
            try:
                card_id = action['data']['card']['id']
                card_name = action.get('data', {}).get('card', {}).get('name', 'Unknown')
                card_desc = action.get('data', {}).get('card', {}).get('desc', '')
                
                log_to_slack(f"🔄 Processing queued webhook: {action_type} for card '{card_name}' (ID: {card_id})")
                
                # Fetch card data
                card = fetch_card_data(card_id)
                
                # Enhance card data with webhook description if available
                if card_desc and not card.get('desc'):
                    card['desc'] = card_desc
                    log_to_slack(f"📝 Enhanced card with webhook description for '{card_name}'")
                
                # Process the card update
                process_card_update(card, action)
                
                log_to_slack(f"✅ Completed queued webhook: {action_type} for card '{card['name']}'")
                
            except Exception as e:
                log_to_slack(f"❌ Queued webhook error: {str(e)}")
            finally:
                # Mark task as done
                webhook_queue.task_done()
                
                # Check if this was the last item in queue
                if webhook_queue.empty():
                    log_to_slack("📭 Queue is now empty - all webhook requests processed")
                
        except queue.Empty:
            # No webhook requests in queue, continue waiting
            # Note: This runs every second when queue is empty, so we don't log here to avoid spam
            continue
        except Exception as e:
            log_to_slack(f"❌ Webhook processor error: {str(e)}")
            time.sleep(1)  # Brief pause on error

def start_webhook_processor():
    """Start the background webhook processing thread"""
    global processing_thread
    processing_thread = threading.Thread(target=webhook_processor, daemon=True)
    processing_thread.start()
    log_to_slack("🚀 Webhook queue processor started")

def stop_webhook_processor():
    """Stop the background webhook processing thread"""
    global queue_running, processing_thread
    queue_running = False
    webhook_queue.put(None)  # Send shutdown signal
    if processing_thread:
        processing_thread.join(timeout=5)
    log_to_slack("🛑 Webhook queue processor stopped")

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

    # Add webhook request to queue for sequential processing
    try:
        webhook_queue.put((payload, action, action_type))
        queue_size = webhook_queue.qsize()
        
        card_name = action.get('data', {}).get('card', {}).get('name', 'Unknown')
        if queue_size > 1:
            log_to_slack(f"📋 Webhook queued (position: {queue_size}) - {action_type} for card '{card_name}'")
        else:
            log_to_slack(f"📋 Webhook queued for immediate processing - {action_type} for card '{card_name}'")
            
    except Exception as e:
        log_to_slack(f"❌ Failed to queue webhook: {str(e)}")
        return '', 500

    return '', 200

@app.route('/queue/status', methods=['GET'])
def queue_status():
    """Endpoint to check queue status"""
    return {
        'queue_size': webhook_queue.qsize(),
        'processor_running': queue_running,
        'timestamp': datetime.now().isoformat()
    }

if __name__ == '__main__':
    port = int(os.getenv("PORT", 5000))
    
    # Start the webhook processor thread
    start_webhook_processor()
    
    try:
        app.run(host="0.0.0.0", port=port)
    finally:
        # Ensure processor is stopped on shutdown
        stop_webhook_processor()
