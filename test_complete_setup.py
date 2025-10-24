#!/usr/bin/env python3
"""
✅ Complete Setup Test - Tests all critical components
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment with override
load_dotenv('.env', override=True)

print("=" * 70)
print("🔍 MOON DEV AI AGENTS - COMPLETE SETUP TEST")
print("=" * 70)

# Test results tracker
tests_passed = 0
tests_failed = 0

def test(name, passed, details=""):
    global tests_passed, tests_failed
    if passed:
        print(f"✓ {name}")
        if details:
            print(f"  → {details}")
        tests_passed += 1
    else:
        print(f"✗ {name}")
        if details:
            print(f"  → {details}")
        tests_failed += 1

# 1. Python Version
print("\n📍 1. Python Environment")
version = sys.version_info
test("Python 3.10+", version.major == 3 and version.minor >= 10,
     f"Python {version.major}.{version.minor}.{version.micro}")

# 2. Core AI Dependencies
print("\n📍 2. Core AI Dependencies")
try:
    import anthropic
    test("Anthropic SDK", True, f"Version: {anthropic.__version__}")
except ImportError as e:
    test("Anthropic SDK", False, str(e))

try:
    import openai
    test("OpenAI SDK", True, f"Version: {openai.__version__}")
except ImportError as e:
    test("OpenAI SDK", False, str(e))

try:
    import groq
    test("Groq SDK", True)
except ImportError as e:
    test("Groq SDK", False, str(e))

try:
    import google.generativeai
    test("Google Gemini SDK", True)
except ImportError as e:
    test("Google Gemini SDK", False, str(e))

# 3. Data & Analysis
print("\n📍 3. Data & Analysis Libraries")
try:
    import pandas
    test("Pandas", True, f"Version: {pandas.__version__}")
except ImportError as e:
    test("Pandas", False, str(e))

try:
    import numpy
    test("NumPy", True, f"Version: {numpy.__version__}")
except ImportError as e:
    test("NumPy", False, str(e))

# 4. Blockchain Dependencies
print("\n📍 4. Blockchain Dependencies")
try:
    import solana
    test("Solana SDK", True)
except ImportError as e:
    test("Solana SDK", False, str(e))

try:
    import hyperliquid
    test("HyperLiquid SDK", True)
except ImportError as e:
    test("HyperLiquid SDK", False, str(e))

try:
    import eth_account
    test("Eth Account", True)
except ImportError as e:
    test("Eth Account", False, str(e))

# 5. Environment Variables
print("\n📍 5. Environment Variables (API Keys)")
anthropic_key = os.getenv("ANTHROPIC_KEY")
test("ANTHROPIC_KEY",
     anthropic_key and anthropic_key.startswith("sk-ant-"),
     f"{anthropic_key[:20]}...{anthropic_key[-10:]}" if anthropic_key and len(anthropic_key) > 30 else "Not set properly")

birdeye_key = os.getenv("BIRDEYE_API_KEY")
test("BIRDEYE_API_KEY",
     birdeye_key and len(birdeye_key) > 10 and "YOUR_" not in birdeye_key,
     f"{birdeye_key[:15]}..." if birdeye_key and len(birdeye_key) > 15 else "Not set properly")

rpc_endpoint = os.getenv("RPC_ENDPOINT")
test("RPC_ENDPOINT (Helius)",
     rpc_endpoint and "helius" in rpc_endpoint.lower(),
     f"{rpc_endpoint[:40]}..." if rpc_endpoint and len(rpc_endpoint) > 40 else "Not set properly")

coingecko_key = os.getenv("COINGECKO_API_KEY")
test("COINGECKO_API_KEY",
     coingecko_key and coingecko_key.startswith("CG-"),
     f"{coingecko_key[:15]}..." if coingecko_key and len(coingecko_key) > 15 else "Not set properly")

# 6. Project Structure
print("\n📍 6. Project Structure")
test("src/agents/", Path("src/agents").is_dir())
test("src/models/", Path("src/models").is_dir())
test("src/config.py", Path("src/config.py").is_file())
test("src/nice_funcs.py", Path("src/nice_funcs.py").is_file())
test(".env file", Path(".env").is_file())
test("pyproject.toml", Path("pyproject.toml").is_file())

# 7. Custom APIs
print("\n📍 7. Custom Free Market Data API")
test("free_market_data_api.py",
     Path("src/agents/free_market_data_api.py").is_file())

# 8. Live API Test (Anthropic)
print("\n📍 8. Live API Test (Anthropic Claude)")
if anthropic_key and anthropic_key.startswith("sk-ant-"):
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=anthropic_key)
        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=20,
            messages=[{"role": "user", "content": "Reply with exactly: 'API works!'"}]
        )
        response = message.content[0].text
        test("Anthropic API Live Call",
             "API" in response or "works" in response,
             f"Response: {response[:50]}")
    except Exception as e:
        test("Anthropic API Live Call", False, f"Error: {str(e)[:60]}...")
else:
    test("Anthropic API Live Call", False, "No valid API key to test")

# 9. Model Factory
print("\n📍 9. Model Factory Integration")
try:
    sys.path.insert(0, str(Path("src").absolute()))
    from models.model_factory import ModelFactory
    test("ModelFactory Import", True)

    # Try to create a model instance
    model = ModelFactory.create_model('anthropic')
    test("ModelFactory.create_model()", True, "Anthropic model created")
except Exception as e:
    test("ModelFactory", False, f"Error: {str(e)[:60]}...")

# Final Summary
print("\n" + "=" * 70)
print("📊 TEST SUMMARY")
print("=" * 70)
total_tests = tests_passed + tests_failed
pass_rate = (tests_passed / total_tests * 100) if total_tests > 0 else 0

print(f"\nTotal Tests: {total_tests}")
print(f"✓ Passed: {tests_passed} ({pass_rate:.1f}%)")
print(f"✗ Failed: {tests_failed}")

if tests_failed == 0:
    print("\n🎉 ALL TESTS PASSED!")
    print("✅ Your setup is ready for trading!")
    print("\nNext steps:")
    print("  1. Review src/config.py for trading parameters")
    print("  2. Test an agent: python src/agents/coingecko_agent.py")
    print("  3. Test free API: python src/agents/free_market_data_api.py")
    print("  4. Start trading: python src/main.py")
    sys.exit(0)
else:
    print(f"\n⚠️  {tests_failed} TEST(S) FAILED")
    print("Please fix the failures before running the trading system.")
    sys.exit(1)
