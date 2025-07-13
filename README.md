# 🧠 Trello AI Assistant for Unreal Engine Game Development

This bot integrates with **Trello**, **Slack**, and **Ollama (local LLM)** to automate intelligent task assistance for your **medieval sandbox game built in Unreal Engine**.

---

## 🚀 What It Does

✅ Responds to Trello card comments and updates  
✅ Infers and inserts `[Context]` metadata if missing  
✅ Tags cards with labels like `Dungeon`, `Combat AI`, `UI`, etc.  
✅ Posts AI-generated help as Trello comments  
✅ Sends a daily summary of active tasks to Slack at 9:30 AM  
✅ Runs offline using Ollama with test cards and mock Trello data

---

## ⚙️ Setup Guide

### 🔧 Step 1: Install

```
pip install -r requirements.txt
```
Make sure you have ollama pulled and started:
```
ollama run deepseek-r1
```
If needing to sync labels to Trello run:
```
python sync_labels.py
```
### Step 2: Start the Webhook Server listening to Trello changes:
```
python app.py
```
Or with a tunnel:
```
npx localtunnel --port 5000
```
#### Enable Daily Summary at 9:30 AM:
```
crontab -e
insert:
30 9 * * * /usr/bin/python3 /path/to/daily_summary.py >> /tmp/trello_summary.log 2>&1
```
### Step 3 (Optional): Run tests

Test with Mock Webhooks locally:
```
python test_webhook_payload.py
```
To use offline card data instead of live API:
.env file
```
MOCK_TRELLO=true
```
### Step 4 (Optional): Compare different LLM outputs with Ollama

Compare LLM Responses Across Models
make compare         # macOS/Linux
compare.bat          # Windows

Output is saved to:
model_logs/model_comparison_YYYY-MM-DD_HH-MM.md
