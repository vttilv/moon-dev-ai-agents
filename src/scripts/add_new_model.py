#!/usr/bin/env python3
"""
🌙 Moon Dev's Model Updater
Quick script to add new models to the registry
Built with love by Moon Dev 🚀

Usage:
python add_new_model.py openai gpt-6 "Next generation GPT-6 model"
python add_new_model.py claude claude-opus-5 "Claude Opus 5 with enhanced reasoning"
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from termcolor import cprint
import json

def add_model(provider, model_name, description):
    """Add a new model to the registry"""

    # Map providers to file paths
    file_mapping = {
        "openai": "src/models/openai_model.py",
        "claude": "src/models/claude_model.py",
        "xai": "src/models/xai_model.py",
        "groq": "src/models/groq_model.py",
        "deepseek": "src/models/deepseek_model.py",
        "ollama": "src/models/ollama_model.py"
    }

    if provider not in file_mapping:
        cprint(f"❌ Unknown provider: {provider}", "red")
        cprint(f"Available providers: {', '.join(file_mapping.keys())}", "yellow")
        return False

    cprint(f"\n📝 Adding {model_name} to {provider}...", "cyan")
    cprint(f"   Description: {description}", "white")

    # Instructions for manual update (safer than auto-editing)
    cprint("\n" + "="*60, "green")
    cprint("✅ TO ADD THIS MODEL:", "green", attrs=['bold'])
    cprint("="*60, "green")
    cprint(f"\n1. Open: {file_mapping[provider]}", "yellow")
    cprint("\n2. Find AVAILABLE_MODELS dictionary", "yellow")

    if provider == "openai":
        cprint("\n3. Add this entry:", "yellow")
        cprint(f'''
        "{model_name}": {{
            "description": "{description}",
            "input_price": "TBD",
            "output_price": "TBD",
            "supports_reasoning_effort": False
        }},''', "white")

    elif provider == "claude":
        cprint("\n3. Add this entry:", "yellow")
        cprint(f'''        "{model_name}": "{description}",''', "white")

    else:
        cprint("\n3. Add model to the appropriate list/dict", "yellow")

    cprint("\n4. Save the file", "yellow")
    cprint("\n5. Test with:", "yellow")
    cprint(f"   python src/scripts/test_all_models.py", "cyan")
    cprint("="*60 + "\n", "green")

    # Also create a JSON record for tracking
    models_file = "src/scripts/tracked_models.json"

    try:
        if os.path.exists(models_file):
            with open(models_file, 'r') as f:
                tracked = json.load(f)
        else:
            tracked = {}

        if provider not in tracked:
            tracked[provider] = []

        # Add if not already tracked
        if not any(m['name'] == model_name for m in tracked[provider]):
            tracked[provider].append({
                "name": model_name,
                "description": description,
                "added": "pending"
            })

            with open(models_file, 'w') as f:
                json.dump(tracked, f, indent=2)

            cprint(f"📊 Model tracked in {models_file}", "green")
    except Exception as e:
        cprint(f"⚠️  Could not update tracking file: {e}", "yellow")

    return True

def check_pending_models():
    """Check for models that need to be added"""
    models_file = "src/scripts/tracked_models.json"

    if not os.path.exists(models_file):
        return

    with open(models_file, 'r') as f:
        tracked = json.load(f)

    pending = []
    for provider, models in tracked.items():
        for model in models:
            if model.get('added') == 'pending':
                pending.append(f"{provider}/{model['name']}")

    if pending:
        cprint("\n⏳ PENDING MODELS TO ADD:", "yellow", attrs=['bold'])
        for model in pending:
            cprint(f"   • {model}", "yellow")

def main():
    """Main entry point"""

    if len(sys.argv) == 1:
        # No args - show instructions and check pending
        cprint("\n🌙 MOON DEV'S MODEL UPDATER", "cyan", attrs=['bold'])
        cprint("="*60, "cyan")

        cprint("\nUsage:", "white")
        cprint("  python add_new_model.py [provider] [model_name] [description]", "yellow")

        cprint("\nExamples:", "white")
        cprint('  python add_new_model.py openai gpt-6 "GPT-6 with enhanced capabilities"', "green")
        cprint('  python add_new_model.py claude claude-5 "Claude 5 next generation"', "green")
        cprint('  python add_new_model.py xai grok-5 "Grok 5 with advanced reasoning"', "green")

        cprint("\nProviders:", "white")
        cprint("  • openai  - OpenAI GPT models", "cyan")
        cprint("  • claude  - Anthropic Claude models", "cyan")
        cprint("  • xai     - xAI Grok models", "cyan")
        cprint("  • groq    - Groq fast inference", "cyan")
        cprint("  • deepseek - DeepSeek reasoning models", "cyan")
        cprint("  • ollama  - Local Ollama models", "cyan")

        check_pending_models()
        cprint("="*60 + "\n", "cyan")

    elif len(sys.argv) == 4:
        provider = sys.argv[1].lower()
        model_name = sys.argv[2]
        description = sys.argv[3]

        add_model(provider, model_name, description)
        check_pending_models()

    else:
        cprint("❌ Invalid arguments", "red")
        cprint("Usage: python add_new_model.py [provider] [model_name] [description]", "yellow")
        sys.exit(1)

if __name__ == "__main__":
    main()