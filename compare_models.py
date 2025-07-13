import requests
import datetime
import os

# ✅ List of models to test
MODELS = ["llama3", "mistral", "codellama", "phi3"]

# ✅ Default Trello-style prompt
DEFAULT_PROMPT = """
[Context]
GameSystem: Settlement Mode
Mode: Dungeon
Subsystem: Loot

Task:
When the boss dies in a Dungeon, a locked chest should spawn nearby with randomized loot based on dungeon tier. The player must open it manually.

What should be implemented next?
"""

def ask_model(model, prompt):
    try:
        response = requests.post("http://localhost:11434/api/generate", json={
            "model": model,
            "prompt": prompt,
            "stream": False
        })
        result = response.json().get("response", "").strip()
        return result
    except Exception as e:
        return f"[ERROR: {e}]"

def save_to_markdown(prompt, responses):
    now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
    filename = f"model_comparison_{now}.md"
    os.makedirs("model_logs", exist_ok=True)
    path = os.path.join("model_logs", filename)

    with open(path, "w") as f:
        f.write(f"# 🤖 Model Comparison – {now}\n\n")
        f.write("### 📥 Prompt\n")
        f.write(f"```\n{prompt.strip()}\n```\n\n")

        for model, reply in responses.items():
            f.write(f"---\n### 🤖 Model: `{model}`\n")
            f.write("```\n")
            f.write(reply)
            f.write("\n```\n\n")

    print(f"\n📄 Markdown saved to: `{path}`")

def main():
    print("🧪 Comparing Ollama model responses...\n")
    prompt = input("Enter prompt (or press Enter to use default):\n").strip()
    if not prompt:
        prompt = DEFAULT_PROMPT

    responses = {}

    for model in MODELS:
        print(f"\n--- 🤖 Model: {model} ---")
        output = ask_model(model, prompt)
        print(output)
        print("-" * 50)
        responses[model] = output

    save_to_markdown(prompt, responses)

if __name__ == "__main__":
    main()
