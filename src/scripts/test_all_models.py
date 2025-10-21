#!/usr/bin/env python3
"""
🌙 Moon Dev's Model Tester
Tests all available AI models with a simple prompt
Built with love by Moon Dev 🚀
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from termcolor import cprint
from models.model_factory import ModelFactory
from models.openai_model import OpenAIModel
from models.claude_model import ClaudeModel
from models.xai_model import XAIModel
from models.groq_model import GroqModel
from models.deepseek_model import DeepSeekModel
from models.ollama_model import OllamaModel
import time
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Test prompt
TEST_PROMPT = "Give me a fun 2-line poem about algorithmic trading"

# Models to test
MODELS_TO_TEST = {
    "OpenAI": {
        "provider": "openai",
        "models": [
            "gpt-5",
            "gpt-5-mini",
            "gpt-5-nano",
            "gpt-4o",
            "gpt-4o-mini",
            "o1-mini"
        ]
    },
    "Claude": {
        "provider": "claude",
        "models": [
            "claude-opus-4-1",
            "claude-sonnet-4-5",
            "claude-haiku-4-5",
            "claude-3-5-sonnet-latest",
            "claude-3-5-haiku-latest"
        ]
    },
    "xAI Grok": {
        "provider": "xai",
        "models": [
            "grok-4-fast-reasoning",
            "grok-4-0709",
            "grok-3"
        ]
    },
    "Groq": {
        "provider": "groq",
        "models": [
            "mixtral-8x7b-32768",
            "llama-3.2-90b-text-preview"
        ]
    },
    "DeepSeek": {
        "provider": "deepseek",
        "models": [
            "deepseek-reasoner",
            "deepseek-chat"
        ]
    },
    "Ollama (Local)": {
        "provider": "ollama",
        "models": [
            "llama3.2",
            "mistral"
        ]
    }
}

def test_model(provider, model_name):
    """Test a single model"""
    try:
        cprint(f"\n📝 Testing {model_name}...", "cyan")
        start_time = time.time()

        # Create model instance
        model = ModelFactory.create_model(provider, model_name)

        # Generate response
        response = model.generate_response(
            system_prompt="You are a helpful AI assistant who creates fun poems.",
            user_content=TEST_PROMPT,
            max_tokens=100,
            temperature=0.7
        )

        elapsed = time.time() - start_time

        # Print result
        cprint(f"✅ {model_name} SUCCESS ({elapsed:.2f}s):", "green")
        cprint(f"   {response.content[:150]}...", "white")

        return True, elapsed

    except Exception as e:
        error_msg = str(e)

        # Check for common errors
        if "not found" in error_msg.lower() or "does not exist" in error_msg.lower():
            cprint(f"⏳ {model_name}: Model not yet available", "yellow")
        elif "api" in error_msg.lower() and "key" in error_msg.lower():
            cprint(f"🔑 {model_name}: API key issue", "yellow")
        elif "connection" in error_msg.lower() or "network" in error_msg.lower():
            cprint(f"🌐 {model_name}: Connection error", "yellow")
        else:
            cprint(f"❌ {model_name}: {error_msg[:100]}", "red")

        return False, 0

def main():
    """Run all model tests"""
    cprint("\n" + "="*60, "cyan")
    cprint("🚀 MOON DEV'S AI MODEL TESTER", "cyan", attrs=['bold'])
    cprint("="*60, "cyan")
    cprint("\nTesting all models with prompt:", "white")
    cprint(f'"{TEST_PROMPT}"', "yellow")
    cprint("="*60, "cyan")

    # Track results
    results = {
        "working": [],
        "not_available": [],
        "errors": []
    }

    # Test each provider's models
    for provider_name, config in MODELS_TO_TEST.items():
        cprint(f"\n\n{'='*40}", "blue")
        cprint(f"🏢 Testing {provider_name} Models", "blue", attrs=['bold'])
        cprint(f"{'='*40}", "blue")

        provider = config["provider"]

        # Check if provider has API key
        key_mapping = {
            "openai": "OPENAI_KEY",
            "claude": "ANTHROPIC_KEY",
            "xai": "GROK_API_KEY",
            "groq": "GROQ_API_KEY",
            "deepseek": "DEEPSEEK_KEY",
            "ollama": None  # No API key needed
        }

        api_key = key_mapping.get(provider)
        if api_key and not os.getenv(api_key):
            cprint(f"⚠️  Skipping {provider_name}: No {api_key} found in .env", "yellow")
            continue

        # Test each model
        for model_name in config["models"]:
            success, elapsed = test_model(provider, model_name)

            if success:
                results["working"].append(f"{provider_name}/{model_name} ({elapsed:.2f}s)")
            else:
                if elapsed == 0:
                    results["not_available"].append(f"{provider_name}/{model_name}")
                else:
                    results["errors"].append(f"{provider_name}/{model_name}")

            # Small delay between tests
            time.sleep(0.5)

    # Print summary
    cprint("\n\n" + "="*60, "cyan")
    cprint("📊 TEST SUMMARY", "cyan", attrs=['bold'])
    cprint("="*60, "cyan")

    cprint(f"\n✅ WORKING MODELS ({len(results['working'])}):", "green", attrs=['bold'])
    for model in results["working"]:
        cprint(f"   • {model}", "green")

    if results["not_available"]:
        cprint(f"\n⏳ NOT YET AVAILABLE ({len(results['not_available'])}):", "yellow", attrs=['bold'])
        for model in results["not_available"]:
            cprint(f"   • {model}", "yellow")

    if results["errors"]:
        cprint(f"\n❌ ERRORS ({len(results['errors'])}):", "red", attrs=['bold'])
        for model in results["errors"]:
            cprint(f"   • {model}", "red")

    cprint("\n" + "="*60, "cyan")
    cprint("💡 TIP: To add new models, update AVAILABLE_MODELS in each model file", "cyan")
    cprint("📝 Models marked 'NOT YET AVAILABLE' will work once APIs are updated", "cyan")
    cprint("="*60 + "\n", "cyan")

if __name__ == "__main__":
    main()