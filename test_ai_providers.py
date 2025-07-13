#!/usr/bin/env python3
"""
Test script to verify AI provider configurations
"""

import os
from dotenv import load_dotenv
from ai_utils import ask_ai, AI_PROVIDER, OLLAMA_MODEL, OPENAI_MODEL

load_dotenv()

def test_ai_provider():
    """Test the configured AI provider with a simple prompt"""
    
    print(f"🤖 Testing AI Provider: {AI_PROVIDER.upper()}")
    print(f"📋 Model: {OLLAMA_MODEL if AI_PROVIDER == 'ollama' else OPENAI_MODEL}")
    print("-" * 50)
    
    test_prompt = "Hello! Please respond with a brief greeting and confirm you're working."
    
    try:
        response = ask_ai(test_prompt)
        print(f"✅ Response received:")
        print(response)
        print("-" * 50)
        print("🎉 AI provider is working correctly!")
        return True
    except Exception as e:
        print(f"❌ Error testing AI provider: {e}")
        return False

def test_both_providers():
    """Test both providers if credentials are available"""
    
    print("🧪 Testing Both AI Providers")
    print("=" * 60)
    
    # Test Ollama
    print("\n1️⃣ Testing Ollama...")
    original_provider = os.getenv("AI_PROVIDER", "ollama")
    os.environ["AI_PROVIDER"] = "ollama"
    
    if test_ai_provider():
        print("✅ Ollama is working")
    else:
        print("❌ Ollama failed - make sure it's running: ollama serve")
    
    # Test OpenAI
    print("\n2️⃣ Testing OpenAI...")
    if os.getenv("OPENAI_API_KEY"):
        os.environ["AI_PROVIDER"] = "openai"
        if test_ai_provider():
            print("✅ OpenAI is working")
        else:
            print("❌ OpenAI failed - check your API key")
    else:
        print("⚠️  OpenAI API key not found - skipping test")
    
    # Restore original provider
    os.environ["AI_PROVIDER"] = original_provider

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "both":
        test_both_providers()
    else:
        test_ai_provider() 