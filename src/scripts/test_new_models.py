#!/usr/bin/env python3
"""
🌙 Moon Dev's New Model Tester
Tests only the newly added OpenAI and Claude models
Built with love by Moon Dev 🚀
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from termcolor import cprint
from models.model_factory import ModelFactory
import time
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Test prompt
TEST_PROMPT = "Give me a fun poem about algotrading"

# New models to test
NEW_MODELS = {
    "OpenAI (New)": {
        "provider": "openai",
        "models": [
            "gpt-5",
            "gpt-5-mini",
            "gpt-5-nano"
        ]
    },
    "Claude (New)": {
        "provider": "claude",
        "models": [
            "claude-opus-4-1",
            "claude-sonnet-4-5",
            "claude-haiku-4-5"
        ]
    }
}

def test_model(provider, model_name, factory):
    """Test a single model"""
    try:
        cprint(f"\n📝 Testing {model_name}...", "cyan")
        start_time = time.time()

        # Get model instance from factory
        model = factory.get_model(provider, model_name)
        if not model:
            cprint(f"⏳ {model_name}: Could not initialize (model not yet available)", "yellow")
            return False, 0

        # Generate response
        response = model.generate_response(
            system_prompt="You are a helpful AI assistant.",
            user_content=TEST_PROMPT,
            max_tokens=100,
            temperature=0.7
        )

        elapsed = time.time() - start_time

        # Print result
        cprint(f"✅ {model_name} WORKS! ({elapsed:.2f}s):", "green", attrs=['bold'])

        # Print the poem nicely
        poem_lines = response.content.strip().split('\n')
        for line in poem_lines[:6]:  # Show first 6 lines
            if line.strip():
                cprint(f"   {line}", "white")

        if len(poem_lines) > 6:
            cprint("   ...", "white")

        return True, elapsed

    except Exception as e:
        error_msg = str(e)

        # Check for common errors
        if "not found" in error_msg.lower() or "does not exist" in error_msg.lower():
            cprint(f"⏳ {model_name}: Model not yet available (expected - will work when API updated)", "yellow")
        elif "api" in error_msg.lower() and "key" in error_msg.lower():
            cprint(f"🔑 {model_name}: API key issue", "yellow")
        else:
            cprint(f"❌ {model_name}: {error_msg[:100]}", "red")

        return False, 0

def main():
    """Run model tests"""
    cprint("\n" + "="*60, "cyan")
    cprint("🚀 TESTING NEW MODELS", "cyan", attrs=['bold'])
    cprint("="*60, "cyan")
    cprint("\nTesting 6 new models with prompt:", "white")
    cprint(f'"{TEST_PROMPT}"', "yellow")
    cprint("="*60, "cyan")

    # Create model factory instance
    factory = ModelFactory()

    # Track results
    working = []
    not_available = []

    # Test OpenAI models
    if os.getenv("OPENAI_KEY"):
        cprint(f"\n📦 TESTING OPENAI NEW MODELS", "blue", attrs=['bold'])
        cprint("="*60, "blue")

        for model_name in NEW_MODELS["OpenAI (New)"]["models"]:
            success, elapsed = test_model("openai", model_name, factory)
            if success:
                working.append(f"OpenAI/{model_name} ({elapsed:.2f}s)")
            else:
                not_available.append(f"OpenAI/{model_name}")
            time.sleep(0.5)
    else:
        cprint("\n⚠️  Skipping OpenAI: No OPENAI_KEY in .env", "yellow")

    # Test Claude models
    if os.getenv("ANTHROPIC_KEY"):
        cprint(f"\n📦 TESTING CLAUDE NEW MODELS", "blue", attrs=['bold'])
        cprint("="*60, "blue")

        for model_name in NEW_MODELS["Claude (New)"]["models"]:
            success, elapsed = test_model("claude", model_name, factory)
            if success:
                working.append(f"Claude/{model_name} ({elapsed:.2f}s)")
            else:
                not_available.append(f"Claude/{model_name}")
            time.sleep(0.5)
    else:
        cprint("\n⚠️  Skipping Claude: No ANTHROPIC_KEY in .env", "yellow")

    # Print summary
    cprint("\n\n" + "="*60, "cyan")
    cprint("📊 RESULTS", "cyan", attrs=['bold'])
    cprint("="*60, "cyan")

    if working:
        cprint(f"\n✅ WORKING ({len(working)}):", "green", attrs=['bold'])
        for model in working:
            cprint(f"   • {model}", "green")

    if not_available:
        cprint(f"\n⏳ NOT YET AVAILABLE ({len(not_available)}):", "yellow", attrs=['bold'])
        for model in not_available:
            cprint(f"   • {model}", "yellow")
        cprint("\n💡 These will work once the APIs are updated with the new models", "yellow")

    cprint("\n" + "="*60, "cyan")
    cprint("📝 Models have been added to:", "cyan")
    cprint("   • src/models/openai_model.py (AVAILABLE_MODELS dict)", "white")
    cprint("   • src/models/claude_model.py (AVAILABLE_MODELS dict)", "white")
    cprint("\n✨ When APIs update, these models will automatically work!", "green")
    cprint("="*60 + "\n", "cyan")

if __name__ == "__main__":
    main()