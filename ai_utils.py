import os
import re
import time
import requests
from dotenv import load_dotenv
from trello_utils import comment_on_card, update_card_description, set_card_labels
from slack_utils import log_to_slack

load_dotenv()

# AI Configuration
AI_PROVIDER = os.getenv("AI_PROVIDER", "ollama")  # "ollama" or "openai"
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "deepseek-r1")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

# Ollama-specific optimizations
OLLAMA_TEMPERATURE = float(os.getenv("OLLAMA_TEMPERATURE", "0.3"))
OLLAMA_TOP_P = float(os.getenv("OLLAMA_TOP_P", "0.9"))
OLLAMA_TOP_K = int(os.getenv("OLLAMA_TOP_K", "40"))
OLLAMA_REPEAT_PENALTY = float(os.getenv("OLLAMA_REPEAT_PENALTY", "1.1"))
OLLAMA_MAX_TOKENS = int(os.getenv("OLLAMA_MAX_TOKENS", "2048"))

PROJECT_CONTEXT = """
You are assisting with a game development project built in Unreal Engine.
Provide concise, technical, and actionable advice. Focus on practical implementation steps.

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
    """
    Optimized Ollama function with deepseek-r1 specific parameters
    """
    start_time = time.time()
    
    try:
        # Model-specific optimizations for deepseek-r1
        payload = {
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": OLLAMA_TEMPERATURE,
                "top_p": OLLAMA_TOP_P,
                "top_k": OLLAMA_TOP_K,
                "repeat_penalty": OLLAMA_REPEAT_PENALTY,
                "num_predict": OLLAMA_MAX_TOKENS,
                # deepseek-r1 specific optimizations
                "num_ctx": 8192,  # Context window size
                "num_gpu": 1,     # Use GPU if available
                "num_thread": 8,  # Optimize threading
                "rope_freq_base": 10000,  # Better for coding tasks
                "rope_freq_scale": 0.5,
            }
        }
        
        # Add system prompt for better context
        payload["system"] = PROJECT_CONTEXT
        
        response = requests.post(
            "http://localhost:11434/api/generate", 
            json=payload,
            timeout=60  # Increased timeout for complex responses
        )
        
        if response.status_code == 200:
            result = response.json()
            response_text = result.get("response", "").strip()
            
            # Remove thinking tags from response
            response_text = re.sub(r'<think>.*?</think>', '', response_text, flags=re.DOTALL).strip()
            
            # Log performance metrics
            elapsed_time = time.time() - start_time
            if elapsed_time > 5:  # Log slow responses
                log_to_slack(f"⏱️ Slow Ollama response ({elapsed_time:.1f}s) for model {OLLAMA_MODEL}")
            
            return response_text
        else:
            return f"[ERROR from Ollama API: {response.status_code} - {response.text}]"
            
    except requests.exceptions.Timeout:
        return "[ERROR: Ollama request timed out - model may be processing a complex request]"
    except requests.exceptions.ConnectionError:
        return "[ERROR: Cannot connect to Ollama - make sure it's running with 'ollama serve']"
    except Exception as e:
        return f"[ERROR from Ollama: {e}]"

def ask_openai(prompt):
    try:
        if not OPENAI_API_KEY:
            return "[ERROR: OpenAI API key not configured]"
        
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": OPENAI_MODEL,
                "messages": [
                    {"role": "system", "content": "You are a helpful AI assistant for game development."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 1000,
                "temperature": 0.7
            }
        )
        
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"].strip()
        else:
            return f"[ERROR from OpenAI API: {response.status_code} - {response.text}]"
            
    except Exception as e:
        return f"[ERROR from OpenAI: {e}]"

def ask_ai(prompt):
    """Unified function to ask either Ollama or OpenAI based on configuration"""
    if AI_PROVIDER.lower() == "openai":
        return ask_openai(prompt)
    else:
        return ask_ollama(prompt)

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
    prompt = f"""You're reviewing a Trello card without metadata.

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
    return ask_ai(prompt)

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

    prompt = f"""🧩 Metadata:
{meta}

📌 Task: {name}
📝 Description: {desc_clean}
💬 Comment: {comment}

Explain what the developer should do next in the context of Unreal Engine development. Keep it helpful, technical, and relevant.
"""
    reply = ask_ai(prompt)
    signed_reply = f"[🤖 AI Reply]\n{reply}"
    log_to_slack(f"🤖 AI Reply: {reply}")
    comment_on_card(card_id, signed_reply)