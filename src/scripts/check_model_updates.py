#!/usr/bin/env python3
"""
🌙 Moon Dev's Model Update Checker
Checks for new model releases from AI providers
Built with love by Moon Dev 🚀
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from termcolor import cprint
from datetime import datetime
import json

# Known model release patterns to watch for
MODEL_RELEASE_PATTERNS = {
    "OpenAI": {
        "current": ["gpt-5", "gpt-5-mini", "gpt-5-nano", "gpt-4o", "o1", "o3"],
        "expected_patterns": ["gpt-", "o", "-mini", "-nano"],
        "release_cycle": "3-6 months"
    },
    "Claude": {
        "current": ["claude-opus-4-1", "claude-sonnet-4-5", "claude-haiku-4-5"],
        "expected_patterns": ["claude-", "-opus", "-sonnet", "-haiku"],
        "release_cycle": "2-4 months"
    },
    "xAI": {
        "current": ["grok-4-fast-reasoning", "grok-4-0709", "grok-3"],
        "expected_patterns": ["grok-"],
        "release_cycle": "2-3 months"
    }
}

def check_model_config():
    """Check current model configuration"""
    cprint("\n🔍 CHECKING CURRENT MODEL CONFIGURATION", "cyan", attrs=['bold'])
    cprint("="*60, "cyan")

    # Check each provider's model file
    providers = {
        "OpenAI": "src/models/openai_model.py",
        "Claude": "src/models/claude_model.py",
        "xAI": "src/models/xai_model.py"
    }

    model_counts = {}

    for provider, filepath in providers.items():
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                content = f.read()
                # Count models in AVAILABLE_MODELS
                model_count = content.count('": "') + content.count('": {')
                model_counts[provider] = model_count
                cprint(f"✅ {provider}: {model_count} models configured", "green")
        else:
            cprint(f"❌ {provider}: File not found", "red")

    return model_counts

def suggest_updates():
    """Suggest potential new models to watch for"""
    cprint("\n🔮 POTENTIAL UPCOMING MODELS TO WATCH", "yellow", attrs=['bold'])
    cprint("="*60, "yellow")

    suggestions = {
        "OpenAI": [
            "gpt-6 (likely Q2 2025)",
            "gpt-5-ultra (premium tier)",
            "o4 series (reasoning models)",
            "gpt-5.5 (mid-cycle update)"
        ],
        "Claude": [
            "claude-5 series (next major version)",
            "claude-opus-4-2 (incremental update)",
            "claude-ultra (new tier)",
            "claude-haiku-5 (next gen fast model)"
        ],
        "xAI": [
            "grok-5 (next major version)",
            "grok-4-ultra (premium model)",
            "grok-mini (efficient tier)",
            "grok-5-reasoning (specialized)"
        ]
    }

    for provider, models in suggestions.items():
        cprint(f"\n{provider}:", "white", attrs=['bold'])
        for model in models:
            cprint(f"  • {model}", "cyan")

def create_update_log():
    """Create or update the model update log"""
    log_file = "src/scripts/model_updates.log"

    entry = {
        "timestamp": datetime.now().isoformat(),
        "checked": True
    }

    cprint(f"\n📝 Logged check to {log_file}", "green")

    # Append to log
    with open(log_file, 'a') as f:
        f.write(json.dumps(entry) + "\n")

def show_update_strategy():
    """Show strategy for staying updated"""
    cprint("\n📚 STRATEGY TO STAY UPDATED", "cyan", attrs=['bold'])
    cprint("="*60, "cyan")

    strategy = """
1. WEEKLY CHECKS
   • Run `python src/scripts/check_model_updates.py` weekly
   • Check provider blogs/announcements

2. QUICK ADDITION PROCESS
   • Use `python src/scripts/add_new_model.py [provider] [model] [desc]`
   • Update AVAILABLE_MODELS dict in model files
   • Test with `python src/scripts/test_all_models.py`

3. MONITORING SOURCES
   • OpenAI: https://platform.openai.com/docs/models
   • Anthropic: https://docs.anthropic.com/claude/docs/models
   • xAI: https://docs.x.ai/

4. TESTING NEW MODELS
   • Add to AVAILABLE_MODELS first
   • Run test script to verify
   • Update DEFAULT_MODELS if better

5. BACKWARDS COMPATIBILITY
   • Keep old models in AVAILABLE_MODELS
   • Mark deprecated with "(deprecated)" in description
   • Never remove working models
"""

    cprint(strategy, "white")

def main():
    """Main entry point"""
    cprint("\n" + "="*60, "cyan")
    cprint("🚀 MOON DEV'S MODEL UPDATE CHECKER", "cyan", attrs=['bold'])
    cprint("="*60, "cyan")

    # Check current configuration
    model_counts = check_model_config()

    # Show release cycles
    cprint("\n⏰ TYPICAL RELEASE CYCLES", "blue", attrs=['bold'])
    cprint("="*60, "blue")
    for provider, info in MODEL_RELEASE_PATTERNS.items():
        cprint(f"{provider}: New models every {info['release_cycle']}", "white")

    # Suggest upcoming models
    suggest_updates()

    # Show update strategy
    show_update_strategy()

    # Create log entry
    create_update_log()

    cprint("\n✨ QUICK COMMANDS", "green", attrs=['bold'])
    cprint("="*60, "green")
    cprint("Test all models:     python src/scripts/test_all_models.py", "yellow")
    cprint("Add new model:       python src/scripts/add_new_model.py", "yellow")
    cprint("Check for updates:   python src/scripts/check_model_updates.py", "yellow")
    cprint("="*60 + "\n", "green")

if __name__ == "__main__":
    main()