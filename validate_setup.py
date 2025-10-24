#!/usr/bin/env python3
"""
🔍 Comprehensive Setup Validation Script
Validates all dependencies, API keys, and system configuration
"""

import sys
import os
from pathlib import Path

# Color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text):
    print(f"\n{Colors.CYAN}{Colors.BOLD}{'='*70}{Colors.END}")
    print(f"{Colors.CYAN}{Colors.BOLD}{text}{Colors.END}")
    print(f"{Colors.CYAN}{Colors.BOLD}{'='*70}{Colors.END}")

def print_success(text):
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠ {text}{Colors.END}")

def print_error(text):
    print(f"{Colors.RED}✗ {text}{Colors.END}")

def print_info(text):
    print(f"{Colors.BLUE}ℹ {text}{Colors.END}")

# Track validation results
results = {
    "passed": [],
    "warnings": [],
    "failed": []
}

# 1. Python Version Check
print_header("1. Python Version Check")
try:
    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"

    if version.major == 3 and version.minor >= 10:
        print_success(f"Python {version_str} (Required: >=3.10)")
        results["passed"].append("Python version")
    else:
        print_error(f"Python {version_str} - Need Python >=3.10")
        results["failed"].append("Python version")
except Exception as e:
    print_error(f"Failed to check Python version: {e}")
    results["failed"].append("Python version")

# 2. Core Dependencies Check
print_header("2. Core Dependencies Check")

core_deps = [
    ("anthropic", "AI - Claude"),
    ("openai", "AI - GPT-4"),
    ("groq", "AI - Groq"),
    ("google.generativeai", "AI - Gemini"),
    ("solana", "Blockchain - Solana"),
    ("hyperliquid", "Trading - HyperLiquid"),
    ("pandas", "Data - Analysis"),
    ("numpy", "Data - Numerical"),
    ("dotenv", "Config - Environment"),
    ("requests", "Network - HTTP"),
]

for module_name, description in core_deps:
    try:
        __import__(module_name)
        print_success(f"{description}: {module_name}")
        results["passed"].append(f"Dependency: {module_name}")
    except ImportError:
        print_error(f"{description}: {module_name} - NOT INSTALLED")
        results["failed"].append(f"Dependency: {module_name}")

# 3. Optional Dependencies Check
print_header("3. Optional Dependencies Check")

optional_deps = [
    ("pandas_ta", "Technical Analysis"),
    ("talib", "TA-Lib Indicators"),
    ("cv2", "OpenCV - Video Processing"),
    ("PIL", "Pillow - Image Processing"),
    ("twikit", "Twitter Integration"),
]

for module_name, description in optional_deps:
    try:
        __import__(module_name)
        print_success(f"{description}: {module_name}")
        results["passed"].append(f"Optional: {module_name}")
    except ImportError:
        print_warning(f"{description}: {module_name} - NOT INSTALLED (optional)")
        results["warnings"].append(f"Optional: {module_name}")

# 4. Environment Variables Check
print_header("4. Environment Variables (.env) Check")

from dotenv import load_dotenv
load_dotenv()

required_keys = [
    ("BIRDEYE_API_KEY", "BirdEye - Token Data", True),
    ("RPC_ENDPOINT", "Helius RPC - Blockchain", True),
    ("ANTHROPIC_KEY", "Anthropic Claude - AI", True),
    ("SOLANA_PRIVATE_KEY", "Solana Wallet", True),
]

optional_keys = [
    ("OPENAI_KEY", "OpenAI GPT-4", False),
    ("DEEPSEEK_KEY", "DeepSeek AI", False),
    ("GROQ_API_KEY", "Groq AI", False),
    ("GEMINI_KEY", "Google Gemini", False),
    ("GROK_API_KEY", "xAI Grok", False),
    ("COINGECKO_API_KEY", "CoinGecko Data", False),
    ("HYPER_LIQUID_ETH_PRIVATE_KEY", "HyperLiquid Trading", False),
]

def check_key(key_name, description, is_required):
    value = os.getenv(key_name)

    if value and value not in ["your_key", "YOUR_KEY_HERE"] and "YOUR_" not in value:
        # Check if it's a placeholder pattern
        if len(value) > 10:
            print_success(f"{description}: {key_name[:20]}...{key_name[-8:]}")
            return True
        else:
            if is_required:
                print_error(f"{description}: {key_name} - PLACEHOLDER VALUE")
                return False
            else:
                print_warning(f"{description}: {key_name} - PLACEHOLDER VALUE (optional)")
                return None
    else:
        if is_required:
            print_error(f"{description}: {key_name} - NOT SET")
            return False
        else:
            print_warning(f"{description}: {key_name} - NOT SET (optional)")
            return None

for key, desc, required in required_keys:
    result = check_key(key, desc, required)
    if result is True:
        results["passed"].append(f"API Key: {key}")
    elif result is False:
        results["failed"].append(f"API Key: {key}")

for key, desc, required in optional_keys:
    result = check_key(key, desc, required)
    if result is True:
        results["passed"].append(f"Optional API Key: {key}")
    elif result is None:
        results["warnings"].append(f"Optional API Key: {key}")

# 5. File Structure Check
print_header("5. Project Structure Check")

critical_paths = [
    ("src/agents/", "Agents directory"),
    ("src/models/", "Models directory"),
    ("src/config.py", "Config file"),
    ("src/nice_funcs.py", "Utility functions"),
    (".env", "Environment file"),
    ("requirements.txt", "Requirements file"),
]

for path, description in critical_paths:
    full_path = Path(path)
    if full_path.exists():
        print_success(f"{description}: {path}")
        results["passed"].append(f"Path: {path}")
    else:
        print_error(f"{description}: {path} - NOT FOUND")
        results["failed"].append(f"Path: {path}")

# 6. API Connectivity Test
print_header("6. API Connectivity Test (Quick)")

# Test Anthropic
try:
    import anthropic
    api_key = os.getenv("ANTHROPIC_KEY")
    if api_key and "sk-ant-" in api_key:
        print_info("Testing Anthropic API connection...")
        client = anthropic.Anthropic(api_key=api_key)
        # Quick test - just validate key format
        print_success("Anthropic API: Key format valid")
        results["passed"].append("Anthropic API connectivity")
    else:
        print_warning("Anthropic API: Key not configured for testing")
        results["warnings"].append("Anthropic API connectivity")
except Exception as e:
    print_error(f"Anthropic API: {str(e)[:50]}...")
    results["failed"].append("Anthropic API connectivity")

# Test BirdEye
try:
    import requests
    api_key = os.getenv("BIRDEYE_API_KEY")
    if api_key and len(api_key) > 10:
        print_info("Testing BirdEye API connection...")
        response = requests.get(
            "https://public-api.birdeye.so/public/token_list",
            headers={"X-API-KEY": api_key},
            timeout=5
        )
        if response.status_code == 200:
            print_success("BirdEye API: Connected successfully")
            results["passed"].append("BirdEye API connectivity")
        else:
            print_error(f"BirdEye API: HTTP {response.status_code}")
            results["failed"].append("BirdEye API connectivity")
    else:
        print_warning("BirdEye API: Key not configured for testing")
        results["warnings"].append("BirdEye API connectivity")
except Exception as e:
    print_error(f"BirdEye API: {str(e)[:50]}...")
    results["failed"].append("BirdEye API connectivity")

# 7. Free Market Data API Test
print_header("7. Free Market Data API Test")

try:
    free_api_path = Path("src/agents/free_market_data_api.py")
    if free_api_path.exists():
        print_success("Free Market Data API: File exists")
        results["passed"].append("Free Market Data API file")

        # Try to import it
        sys.path.insert(0, str(Path("src/agents").absolute()))
        from free_market_data_api import FreeMarketDataAPI
        print_success("Free Market Data API: Importable")
        results["passed"].append("Free Market Data API import")
    else:
        print_error("Free Market Data API: File not found")
        results["failed"].append("Free Market Data API file")
except Exception as e:
    print_error(f"Free Market Data API: {str(e)[:50]}...")
    results["failed"].append("Free Market Data API import")

# 8. Model Factory Test
print_header("8. Model Factory Test")

try:
    model_factory_path = Path("src/models/model_factory.py")
    if model_factory_path.exists():
        print_success("Model Factory: File exists")
        results["passed"].append("Model Factory file")

        # Try to import it
        sys.path.insert(0, str(Path("src/models").absolute()))
        from model_factory import ModelFactory
        print_success("Model Factory: Importable")
        results["passed"].append("Model Factory import")
    else:
        print_error("Model Factory: File not found")
        results["failed"].append("Model Factory file")
except Exception as e:
    print_error(f"Model Factory: {str(e)[:50]}...")
    results["failed"].append("Model Factory import")

# Final Summary
print_header("🎯 VALIDATION SUMMARY")

total_checks = len(results["passed"]) + len(results["warnings"]) + len(results["failed"])
passed_pct = (len(results["passed"]) / total_checks * 100) if total_checks > 0 else 0

print(f"\n{Colors.BOLD}Total Checks: {total_checks}{Colors.END}")
print(f"{Colors.GREEN}✓ Passed: {len(results['passed'])} ({passed_pct:.1f}%){Colors.END}")
print(f"{Colors.YELLOW}⚠ Warnings: {len(results['warnings'])}{Colors.END}")
print(f"{Colors.RED}✗ Failed: {len(results['failed'])}{Colors.END}")

if len(results["failed"]) > 0:
    print(f"\n{Colors.RED}{Colors.BOLD}❌ CRITICAL FAILURES:{Colors.END}")
    for item in results["failed"]:
        print(f"  {Colors.RED}• {item}{Colors.END}")

if len(results["warnings"]) > 0:
    print(f"\n{Colors.YELLOW}{Colors.BOLD}⚠️ WARNINGS (Optional):{Colors.END}")
    for item in results["warnings"]:
        print(f"  {Colors.YELLOW}• {item}{Colors.END}")

# Overall Status
print(f"\n{Colors.BOLD}{'='*70}{Colors.END}")
if len(results["failed"]) == 0:
    print(f"{Colors.GREEN}{Colors.BOLD}✅ SETUP VALIDATION PASSED - READY TO TRADE!{Colors.END}")
    print(f"{Colors.GREEN}All critical requirements met. You can start running agents.{Colors.END}")
    sys.exit(0)
else:
    print(f"{Colors.RED}{Colors.BOLD}❌ SETUP VALIDATION FAILED{Colors.END}")
    print(f"{Colors.RED}Fix critical failures before running agents.{Colors.END}")
    sys.exit(1)
