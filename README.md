# 🧠 Trello AI Assistant for Unreal Engine Game Development

This bot integrates with **Trello**, **Slack**, and **AI models** to automate intelligent task assistance for your **medieval sandbox game built in Unreal Engine**.

---

## 🚀 What It Does

✅ Responds to Trello card comments and updates  
✅ Infers and inserts `[Context]` metadata if missing  
✅ Tags cards with labels like `Dungeon`, `Combat AI`, `UI`, etc.  
✅ Posts AI-generated help as Trello comments  
✅ Sends a daily summary of active tasks to Slack at 9:30 AM  
✅ Supports both local AI (Ollama) and cloud AI (ChatGPT API)  
✅ Queues webhook requests to prevent AI API overload  
✅ Runs offline using test cards and mock Trello data

---

## ⚙️ Setup Guide

### 🔧 Step 1: Install

```
pip install -r requirements.txt
```

### 🤖 Step 2: Configure AI Provider

Choose between local AI (Ollama) or cloud AI (ChatGPT API):

**Option A: Local AI (Ollama) - Recommended for privacy**
```
set OLLAMA_HOST=0.0.0.0
ollama serve
```

**Option B: Cloud AI (ChatGPT API) - Better responses**
Get your API key from https://platform.openai.com/api-keys

See [AI_CONFIGURATION.md](AI_CONFIGURATION.md) for detailed setup instructions.

### Step 3: Register Trello Webhook

Register a webhook for your "In Progress" list to automatically trigger the AI assistant:

```bash
python register_webhook.py
```

This script will:
- Find your "In Progress" list (supports various naming conventions)
- Register a webhook that triggers on card changes and comments
- Send webhooks to your server's `/webhook` endpoint

**Required environment variables:**
- `TRELLO_KEY` - Your Trello API key
- `TRELLO_TOKEN` - Your Trello API token  
- `TRELLO_BOARD_ID` - Your board ID
- `WEBHOOK_URL` - Your server's webhook URL (e.g., `https://your-domain.com/webhook`)

### Step 4: Start the Webhook Server

Start the server to receive webhook notifications:
```bash
python app.py
```

For local development with a tunnel:
```bash
npx localtunnel --port 5000
```
#### Enable Daily Summary at 9:30 AM:
```bash
crontab -e
# Insert this line:
30 9 * * * /usr/bin/python3 /path/to/daily_summary.py >> /tmp/trello_summary.log 2>&1
```

### Step 5 (Optional): Run tests

Test with Mock Webhooks locally:
```
python test_webhook_payload.py
```
To use offline card data instead of live API:
.env file
```
MOCK_TRELLO=true
```
### Step 6 (Optional): Compare different LLM outputs with Ollama

Compare LLM Responses Across Models
make compare         # macOS/Linux
compare.bat          # Windows

Output is saved to:
model_logs/model_comparison_YYYY-MM-DD_HH-MM.md
