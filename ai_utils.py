import os
import re
import requests
from dotenv import load_dotenv
from trello_utils import comment_on_card, update_card_description, set_card_labels
from slack_utils import log_to_slack

load_dotenv()

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")

PROJECT_CONTEXT = """
You are assisting with a game development project built in Unreal Engine.

🎮 Game Overview:
- A medieval sandbox game with open-world mechanics, modular systems, and third-person combat.
- Two primary modes:

1. World Map Mode:
   - Strategic layer where players travel, trade, build, and enter POIs or Dungeons.
   - Can build Houses, Crop Fields, Watch Towers, etc.

2. Settlement Mode (Combat Mode):
   - Real-time combat: Battles, Sieges, Skirmishes, and Dungeons.
   - Player commands an army, rides horses, and loots dungeons.
   - Combat systems include Followers, Formations, and Boss fights.

Assume Trello tasks may relate to AI, UI, animation, loot, multiplayer, or level design within this framework.
"""

def ask_ollama(prompt):
    try:
        response = requests.post("http://localhost:11434/api/generate", json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False
        })
        return response.json().get("response", "").strip()
    except Exception as e:
        return f"[ERROR from Ollama: {e}]"

def extract_context_from_description(desc):
    match = re.search(r'\[Context\](.*?)(\n\n|\Z)', desc, re.DOTALL)
    if match:
        context_block = match.group(1).strip()
        cleaned = desc.replace(match.group(0), '').strip()
    else:
        context_block = None
        cleaned = desc
    return context_block, cleaned

def extract_tags_from_context(context_block):
    lines = context_block.splitlines()
    tags = []
    for line in lines:
        if ":" in line:
            label = line.split(":", 1)[1].strip()
            if label.lower() != "none":
                tags.extend(label.split("/"))
    return [tag.strip() for tag in tags]

def generate_card_metadata(card_name, desc, comment=None):
    prompt = f"""{PROJECT_CONTEXT}

You're reviewing a Trello card without metadata.

Infer the following:
- GameSystem (World Map, Settlement Mode, Dungeon)
- Mode (Battle, Siege, Skirmish, Dungeon)
- Subsystem (Combat AI, UI, Animation, Loot, etc.)

Format like:
[Context]
GameSystem: ...
Mode: ...
Subsystem: ...

Card Title: {card_name}
Description: {desc}
{f"Comment: {comment}" if comment else ""}
"""
    return ask_ollama(prompt)

def process_card_update(card, action):
    card_id = card["id"]
    name = card["name"]
    desc = card["desc"]
    comment = action.get("data", {}).get("text", "")

    meta, desc_clean = extract_context_from_description(desc)
    if not meta:
        inferred_context = generate_card_metadata(name, desc_clean, comment)
        updated_desc = f"[Context]\n{inferred_context}\n\n{desc_clean}"
        update_card_description(card_id, updated_desc)
        log_to_slack(f"🧠 Added metadata to '{name}'")
        meta = inferred_context

        tags = extract_tags_from_context(inferred_context)
        set_card_labels(card_id, tags)
        log_to_slack(f"🏷️ Labels added to '{name}': {tags}")
        
    log_to_slack(f"✅ Processing Trello card: {name} - {desc_clean}")

    prompt = f"""{PROJECT_CONTEXT}

🧩 Metadata:
{meta}

📌 Task: {name}
📝 Description: {desc_clean}
💬 Comment: {comment}

Explain what the developer should do next in the context of Unreal Engine development. Keep it helpful, technical, and relevant.
"""
    reply = ask_ollama(prompt)
    signed_reply = f"[🤖 AI Reply]\n{reply}"
    log_to_slack(f"🤖 AI Reply: {reply}")
    comment_on_card(card_id, signed_reply)