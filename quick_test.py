#!/usr/bin/env python3
"""Quick test of critical components"""

import os
from dotenv import load_dotenv

load_dotenv()

print("🔍 Quick Component Test\n")

# Test 1: Environment loading
print("1. Environment Variables:")
anthropic_key = os.getenv("ANTHROPIC_KEY")
if anthropic_key and anthropic_key.startswith("sk-ant-"):
    print(f"  ✓ ANTHROPIC_KEY loaded: {anthropic_key[:15]}...{anthropic_key[-10:]}")
else:
    print(f"  ✗ ANTHROPIC_KEY not properly loaded")

birdeye_key = os.getenv("BIRDEYE_API_KEY")
if birdeye_key and len(birdeye_key) > 10:
    print(f"  ✓ BIRDEYE_API_KEY loaded: {birdeye_key[:10]}...")
else:
    print(f"  ✗ BIRDEYE_API_KEY: {birdeye_key}")

# Test 2: Core imports
print("\n2. Core Dependencies:")
try:
    import anthropic
    print("  ✓ anthropic")
except:
    print("  ✗ anthropic")

try:
    import openai
    print("  ✓ openai")
except:
    print("  ✗ openai")

try:
    import pandas
    print("  ✓ pandas")
except:
    print("  ✗ pandas")

try:
    import solana
    print("  ✓ solana")
except:
    print("  ✗ solana")

# Test 3: Anthropic API test
print("\n3. Anthropic API Test:")
try:
    if anthropic_key and anthropic_key.startswith("sk-ant-"):
        client = anthropic.Anthropic(api_key=anthropic_key)
        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=50,
            messages=[{"role": "user", "content": "Say 'API works!' in 2 words"}]
        )
        print(f"  ✓ API Response: {message.content[0].text}")
    else:
        print("  ⚠ Skipping (no valid key)")
except Exception as e:
    print(f"  ✗ Error: {str(e)[:60]}...")

print("\n✅ Quick test complete!")
