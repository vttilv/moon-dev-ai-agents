#!/usr/bin/env python3
"""
🔍 API Compatibility Checker
Verifies which agents can run with your current API setup
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from termcolor import colored

# Load environment variables
load_dotenv()

def check_api_key(key_name, display_name, required_for):
    """Check if an API key is configured"""
    value = os.getenv(key_name)

    if value and value != f"YOUR_{key_name}_HERE" and "your_" not in value.lower():
        print(colored(f"  ✓ {display_name}", "green"))
        return True
    else:
        print(colored(f"  ✗ {display_name}", "red") + colored(f" (needed for: {required_for})", "yellow"))
        return False

def main():
    print(colored("\n🔍 Moon Dev AI Agents - API Compatibility Check", "cyan", attrs=["bold"]))
    print("=" * 70)

    results = {}

    # Core Trading APIs
    print(colored("\n📊 CORE TRADING APIs", "cyan", attrs=["bold"]))
    print("-" * 70)
    results['birdeye'] = check_api_key("BIRDEYE_API_KEY", "BirdEye API", "token prices, OHLCV data")
    results['helius'] = check_api_key("RPC_ENDPOINT", "Helius RPC", "Solana blockchain access")
    results['solana_key'] = check_api_key("SOLANA_PRIVATE_KEY", "Solana Private Key", "trade execution")

    # AI Provider APIs
    print(colored("\n🤖 AI PROVIDER APIs", "cyan", attrs=["bold"]))
    print("-" * 70)
    results['anthropic'] = check_api_key("ANTHROPIC_KEY", "Anthropic Claude", "primary AI decisions")
    results['openai'] = check_api_key("OPENAI_KEY", "OpenAI GPT", "swarm mode, multi-AI voting")
    results['deepseek'] = check_api_key("DEEPSEEK_KEY", "DeepSeek", "reasoning tasks, RBI agent")
    results['groq'] = check_api_key("GROQ_API_KEY", "Groq", "fast inference, swarm mode")
    results['gemini'] = check_api_key("GEMINI_KEY", "Google Gemini", "multi-modal AI, swarm mode")
    results['grok'] = check_api_key("GROK_API_KEY", "Grok (xAI)", "swarm mode voting")

    # Market Data APIs
    print(colored("\n📈 MARKET DATA APIs", "cyan", attrs=["bold"]))
    print("-" * 70)
    results['coingecko'] = check_api_key("COINGECKO_API_KEY", "CoinGecko", "token metadata")
    results['moondev'] = check_api_key("MOONDEV_API_KEY", "MoonDev API", "liquidations, funding (OPTIONAL)")

    # Exchange APIs
    print(colored("\n💱 EXCHANGE APIs", "cyan", attrs=["bold"]))
    print("-" * 70)
    results['hyperliquid'] = check_api_key("HYPER_LIQUID_ETH_PRIVATE_KEY", "HyperLiquid", "HyperLiquid trading")

    # Optional APIs
    print(colored("\n🎨 OPTIONAL APIs (for content/social features)", "cyan", attrs=["bold"]))
    print("-" * 70)
    results['twitter'] = check_api_key("TWITTER_USERNAME", "Twitter", "tweet_agent")
    results['youtube'] = check_api_key("YOUTUBE_API_KEY", "YouTube", "video analysis in RBI")
    results['elevenlabs'] = check_api_key("ELEVENLABS_API_KEY", "ElevenLabs", "voice synthesis")
    results['twilio'] = check_api_key("TWILIO_ACCOUNT_SID", "Twilio", "SMS/phone alerts")

    # Summary
    print("\n" + "=" * 70)
    print(colored("\n📋 AGENT COMPATIBILITY SUMMARY", "cyan", attrs=["bold"]))
    print("=" * 70)

    # Trading Agents
    print(colored("\n✅ TRADING AGENTS", "green", attrs=["bold"]))
    if results.get('anthropic') and results.get('birdeye') and results.get('helius'):
        print(colored("  ✓ trading_agent.py", "green") + " - Main trading decisions")
        print(colored("  ✓ strategy_agent.py", "green") + " - User strategies")
        print(colored("  ✓ risk_agent.py", "green") + " - Risk management")
    else:
        print(colored("  ✗ Trading agents", "red") + " - Need: Anthropic, BirdEye, Helius")

    if results.get('birdeye') and results.get('helius') and results.get('solana_key'):
        print(colored("  ✓ sniper_agent.py", "green") + " - New token sniping")
    else:
        print(colored("  ✗ sniper_agent.py", "red") + " - Need: BirdEye, Helius, Solana key")

    # Market Analysis Agents
    print(colored("\n📊 MARKET ANALYSIS AGENTS", "green", attrs=["bold"]))
    if results.get('coingecko'):
        print(colored("  ✓ coingecko_agent.py", "green") + " - Token metadata")
    else:
        print(colored("  ✗ coingecko_agent.py", "red") + " - Need: CoinGecko API")

    if results.get('anthropic') and results.get('birdeye'):
        print(colored("  ✓ chartanalysis_agent.py", "green") + " - Technical analysis")
        print(colored("  ✓ sentiment_agent.py", "green") + " - Social sentiment")
    else:
        print(colored("  ✗ Analysis agents", "red") + " - Need: Anthropic, BirdEye")

    # Check for free alternative availability
    print(colored("\n  ⚠️  funding_agent.py", "yellow") + " - Uses FREE CoinGlass API (no MoonDev needed)")
    print(colored("  ⚠️  liquidation_agent.py", "yellow") + " - Uses FREE CoinGlass API (no MoonDev needed)")
    print(colored("  ⚠️  whale_agent.py", "yellow") + " - Uses FREE CoinGlass API (no MoonDev needed)")

    # Strategy Development Agents
    print(colored("\n🔬 STRATEGY DEVELOPMENT AGENTS", "green", attrs=["bold"]))
    if results.get('deepseek') and results.get('anthropic'):
        print(colored("  ✓ rbi_agent.py", "green") + " - Auto-generate strategies")
    else:
        print(colored("  ✗ rbi_agent.py", "red") + " - Need: DeepSeek, Anthropic")

    if results.get('anthropic'):
        print(colored("  ✓ research_agent.py", "green") + " - Market research")
        print(colored("  ✓ backtest_agent.py", "green") + " - Backtesting")
    else:
        print(colored("  ✗ Research/Backtest agents", "red") + " - Need: Anthropic")

    # Content Creation Agents
    print(colored("\n🎨 CONTENT CREATION AGENTS", "green", attrs=["bold"]))
    if results.get('anthropic'):
        print(colored("  ✓ chat_agent.py", "green") + " - Conversational AI")
    else:
        print(colored("  ✗ chat_agent.py", "red") + " - Need: Anthropic")

    if results.get('twitter'):
        print(colored("  ✓ tweet_agent.py", "green") + " - Auto-tweet")
    else:
        print(colored("  ✗ tweet_agent.py", "yellow") + " - Need: Twitter API (optional)")

    if results.get('twilio') and results.get('elevenlabs'):
        print(colored("  ✓ phone_agent.py", "green") + " - Voice alerts")
    else:
        print(colored("  ✗ phone_agent.py", "yellow") + " - Need: Twilio, ElevenLabs (optional)")

    # Swarm Mode Check
    print(colored("\n🐝 SWARM MODE (Multi-AI Voting)", "cyan", attrs=["bold"]))
    swarm_count = sum([
        results.get('anthropic', False),
        results.get('openai', False),
        results.get('deepseek', False),
        results.get('groq', False),
        results.get('gemini', False),
        results.get('grok', False)
    ])

    if swarm_count >= 3:
        print(colored(f"  ✓ Swarm Mode Available", "green") + f" ({swarm_count}/6 AI providers configured)")
        print(colored("    You can enable multi-AI consensus voting!", "green"))
    else:
        print(colored(f"  ⚠️  Limited Swarm Mode", "yellow") + f" ({swarm_count}/6 AI providers)")
        print(colored("    Add more AI providers for full swarm functionality", "yellow"))

    # Overall Status
    print("\n" + "=" * 70)
    core_ready = (results.get('anthropic') and results.get('birdeye') and
                  results.get('helius') and results.get('solana_key'))

    if core_ready:
        print(colored("\n🎉 CORE TRADING SYSTEM: READY TO RUN!", "green", attrs=["bold"]))
        print(colored("   You have all required APIs for trading operations", "green"))
    else:
        print(colored("\n⚠️  CORE TRADING SYSTEM: INCOMPLETE", "yellow", attrs=["bold"]))
        print(colored("   Add missing APIs to enable full trading functionality", "yellow"))

    # Recommendations
    print(colored("\n💡 RECOMMENDATIONS", "cyan", attrs=["bold"]))
    print("-" * 70)

    if not results.get('anthropic'):
        print(colored("  ⚠️  CRITICAL: Add ANTHROPIC_KEY for AI decision making", "red"))

    if not results.get('birdeye'):
        print(colored("  ⚠️  CRITICAL: Add BIRDEYE_API_KEY for token data", "red"))

    if not results.get('helius'):
        print(colored("  ⚠️  CRITICAL: Add RPC_ENDPOINT for blockchain access", "red"))

    if not results.get('moondev'):
        print(colored("  ✓ MoonDev API not needed - using FREE CoinGlass alternative", "green"))

    if swarm_count < 6:
        print(colored(f"  💡 Optional: Add {6-swarm_count} more AI providers for full swarm mode", "yellow"))

    # Next Steps
    print(colored("\n🚀 NEXT STEPS", "cyan", attrs=["bold"]))
    print("-" * 70)
    print("1. Add missing API keys to your .env file")
    print("2. Run: python src/agents/free_market_data_api.py (test free data)")
    print("3. Run: python src/agents/coingecko_agent.py (test agent)")
    print("4. Configure strategies in src/config.py")
    print("5. Start trading with: python src/main.py")

    print("\n" + "=" * 70)
    print(colored("✨ Check complete! See YOUR_API_SETUP_GUIDE.md for details\n", "cyan"))

if __name__ == "__main__":
    main()
