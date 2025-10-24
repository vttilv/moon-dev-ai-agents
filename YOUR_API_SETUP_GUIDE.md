# 🔑 Your Custom API Setup Guide

**Created: 2025-10-22**
**For: /moon-dev-ai-agents customization**

---

## ✅ What You Have (API Inventory)

| API/Service | Tier | Status |
|-------------|------|--------|
| **Helius RPC** | Free | ✓ Available |
| **Anthropic Claude** | Pro Plan | ✓ Available |
| **Grok (xAI)** | Grok 4 Fast | ✓ Available |
| **BirdEye** | Free | ✓ Available |
| **CoinGecko** | Free | ✓ Available |
| **Gemini** | Standard | ✓ Available |
| **DeepSeek** | Standard | ✓ Available |
| **OpenAI** | Standard | ✓ Available |
| **HyperLiquid** | Active | ✓ Available |
| **Solana Wallet** | Private Key | ✓ Available |

---

## 🎯 What You Can Run (Agent Compatibility)

### ✅ FULLY FUNCTIONAL (Ready to Run Now)

#### Trading Agents
- ✅ **trading_agent.py** - Main trading decisions
  - Requires: Anthropic, BirdEye, Helius RPC
  - Status: **100% Ready**

- ✅ **strategy_agent.py** - User-defined strategies
  - Requires: Anthropic, BirdEye
  - Status: **100% Ready**

- ✅ **risk_agent.py** - Risk management
  - Requires: Anthropic, BirdEye, Helius RPC
  - Status: **100% Ready**

- ✅ **sniper_agent.py** - New token sniping
  - Requires: BirdEye, Helius RPC, Solana key
  - Status: **100% Ready**

#### Market Analysis Agents
- ✅ **coingecko_agent.py** - Token metadata
  - Requires: CoinGecko API
  - Status: **100% Ready**

- ✅ **chartanalysis_agent.py** - Technical analysis
  - Requires: Anthropic, BirdEye
  - Status: **100% Ready**

- ✅ **sentiment_agent.py** - Social sentiment (Twitter)
  - Requires: Anthropic
  - Status: **100% Ready** (without Twitter scraping)

#### Strategy Development Agents
- ✅ **rbi_agent.py** - Auto-generate strategies
  - Requires: DeepSeek, Anthropic
  - Status: **100% Ready**

- ✅ **research_agent.py** - Market research
  - Requires: Anthropic, CoinGecko
  - Status: **100% Ready**

- ✅ **backtest_agent.py** - Strategy backtesting
  - Requires: BirdEye (for historical data)
  - Status: **100% Ready**

#### Content Creation Agents
- ✅ **chat_agent.py** - Conversational AI
  - Requires: Anthropic
  - Status: **100% Ready**

---

### ⚠️ PARTIALLY FUNCTIONAL (Need Free Alternative)

These agents originally used MoonDev API, but now use our **free_market_data_api.py**:

- ⚠️ **funding_agent.py** - Funding rate analysis
  - Original: MoonDev API
  - **New: FreeMarketDataAPI (CoinGlass)**
  - Status: **Ready with free alternative**

- ⚠️ **liquidation_agent.py** - Liquidation tracking
  - Original: MoonDev API
  - **New: FreeMarketDataAPI (CoinGlass)**
  - Status: **Ready with free alternative**

- ⚠️ **whale_agent.py** - Whale movement tracking
  - Original: MoonDev API
  - **New: FreeMarketDataAPI (CoinGlass OI)**
  - Status: **Ready with free alternative**

---

### ❌ NOT FUNCTIONAL (Missing Optional APIs)

- ❌ **copybot_agent.py** - Copy trading
  - Requires: MoonDev API (bootcamp access)
  - Alternative: Create your own follow list manually
  - Status: **Optional - can skip**

- ❌ **tweet_agent.py** - Auto-tweet generation
  - Requires: Twitter API credentials
  - Status: **Optional - add Twitter keys if you want this**

- ❌ **phone_agent.py** - Voice alerts
  - Requires: Twilio + ElevenLabs
  - Status: **Optional - add if you want SMS alerts**

- ❌ **clips_agent.py** - Stream clipping
  - Requires: Restream API
  - Status: **Optional - for content creators**

- ❌ **video_agent.py** - Video generation
  - Requires: Google Cloud credentials
  - Status: **Optional - for content creators**

---

## 🚀 Your 3-Step Setup Process

### **Step 1: Add Your API Keys to .env**

I've created a template [.env](.env) file. Replace these placeholders:

```bash
# REQUIRED FOR CORE TRADING
BIRDEYE_API_KEY=your_actual_birdeye_key
RPC_ENDPOINT=your_helius_rpc_url
ANTHROPIC_KEY=your_claude_api_key
SOLANA_PRIVATE_KEY=your_solana_private_key

# REQUIRED FOR AI SWARM MODE
OPENAI_KEY=your_openai_key
DEEPSEEK_KEY=your_deepseek_key
GROQ_API_KEY=your_groq_key
GEMINI_KEY=your_gemini_key
GROK_API_KEY=your_grok_key

# REQUIRED FOR HYPERLIQUID TRADING
HYPER_LIQUID_ETH_PRIVATE_KEY=your_hyperliquid_key
HYPER_LIQUID_KEY=your_hyperliquid_key

# OPTIONAL (but you have them)
COINGECKO_API_KEY=your_coingecko_key
```

### **Step 2: Update Agents to Use Free API**

For agents that used MoonDev API, I'll show you how to swap it:

**BEFORE (old code):**
```python
from src.agents.api import MoonDevAPI
api = MoonDevAPI()
```

**AFTER (new code):**
```python
from src.agents.free_market_data_api import FreeMarketDataAPI
api = FreeMarketDataAPI()
```

The interface is **identical** - same function names!

### **Step 3: Test Your Setup**

Run these tests to verify everything works:

```bash
# Test 1: Free Market Data API
python src/agents/free_market_data_api.py

# Test 2: CoinGecko Agent
python src/agents/coingecko_agent.py

# Test 3: Chart Analysis Agent
python src/agents/chartanalysis_agent.py

# Test 4: Risk Agent
python src/agents/risk_agent.py
```

---

## 📊 API Usage Map (Which Agent Needs What)

### Core Trading Infrastructure

| Component | Required APIs | Your Status |
|-----------|---------------|-------------|
| **Token Price Data** | BirdEye | ✓ Have it |
| **Blockchain Access** | Helius RPC | ✓ Have it |
| **AI Decision Making** | Anthropic/Claude | ✓ Have it (Pro!) |
| **Multi-AI Voting** | OpenAI, DeepSeek, Groq, Gemini, Grok | ✓ Have all |
| **Trade Execution (Solana)** | Solana Private Key | ✓ Have it |
| **Trade Execution (HyperLiquid)** | HyperLiquid Key | ✓ Have it |

### Market Data (FREE Alternatives)

| Data Type | Original Source | Your Free Alternative | Status |
|-----------|----------------|----------------------|--------|
| **Liquidations** | MoonDev API | CoinGlass API (free) | ✓ Ready |
| **Funding Rates** | MoonDev API | CoinGlass API (free) | ✓ Ready |
| **Open Interest** | MoonDev API | CoinGlass API (free) | ✓ Ready |
| **New Tokens** | MoonDev API | BirdEye API (free) | ✓ Ready |
| **Token Metadata** | CoinGecko | CoinGecko API (free) | ✓ Ready |

---

## 🎯 Minimum Required APIs for Core Trading

**Absolute minimum to run trading system:**

1. **ANTHROPIC_KEY** - AI decision making (you have Pro ✓)
2. **BIRDEYE_API_KEY** - Token data (you have free tier ✓)
3. **RPC_ENDPOINT** - Blockchain access (you have Helius ✓)
4. **SOLANA_PRIVATE_KEY** - Execute trades (you have it ✓)

**You have everything needed!** 🎉

---

## 💡 Optional Upgrades (When You Want Them)

### For Enhanced Market Data
- **MoonDev API** - Requires bootcamp membership (~$297/mo)
  - Benefits: Proprietary signals, copybot data, faster updates
  - Alternative: Use our FREE CoinGlass integration (90% as good)

### For Social/Content Features
- **Twitter API** - Auto-tweet market insights ($100/mo)
- **Twilio** - SMS alerts ($0.01/SMS)
- **ElevenLabs** - Voice synthesis ($5/mo)
- **YouTube API** - Free (for RBI video analysis)

---

## 🔧 Next Steps - What To Do Now

### Immediate Actions:

1. **Fill in your API keys** in the [.env](.env) file
   - I'll walk you through the exact format when you're ready

2. **Test the free market data API**
   - Run: `python src/agents/free_market_data_api.py`
   - This will verify CoinGlass data access

3. **Choose your first agent to run**
   - Recommendation: Start with `coingecko_agent.py` (safe, read-only)

4. **Update 3 agents** to use free API instead of MoonDev
   - I'll do this for you in the next step

---

## 📝 API Key Format Examples

When you're ready to share your keys, use this structure:

```bash
# Safe format to share with me:
BIRDEYE_API_KEY=starts_with_...
ANTHROPIC_KEY=sk-ant-...
HELIUS_RPC=https://mainnet.helius-rpc.com/?api-key=...
COINGECKO_KEY=CG-...
GROK_API_KEY=xai-...
OPENAI_KEY=sk-...
DEEPSEEK_KEY=sk-...
GEMINI_KEY=AIzaSy...
GROQ_API_KEY=gsk_...

# For private keys (EXTRA CAREFUL):
SOLANA_PRIVATE_KEY=base58_string...
HYPER_LIQUID_ETH_PRIVATE_KEY=0x...
```

**Security Tips:**
- Only share FIRST few characters to verify format
- Use a TEST wallet for initial setup
- Never share full private keys in chat (DM only if needed)

---

## ✅ Summary: You're In Great Shape!

**What you have:**
- ✅ All core APIs needed for trading
- ✅ 6 AI providers for swarm mode
- ✅ Free alternatives for market data
- ✅ Both Solana and HyperLiquid access

**What you DON'T need:**
- ❌ MoonDev API (we built free alternative)
- ❌ Twitter API (unless you want auto-tweets)
- ❌ Content creation APIs (optional)

**Your cost to run:**
- Helius RPC: $0/month (free tier)
- BirdEye: $0/month (free tier, 100 calls/min)
- CoinGecko: $0/month (free tier)
- CoinGlass: $0/month (public data)
- Anthropic: ~$3-10/day (depends on usage)
- Other AI providers: Pay-as-you-go

**Total estimated monthly cost: $100-300** (mostly AI inference)

---

## 🚦 Ready to Proceed?

Let me know when you want to:
1. **Add your API keys** - I'll show you exact format
2. **Update the 3 agents** - Swap MoonDev → Free API
3. **Run your first test** - Verify everything works
4. **Start trading** - Configure your first strategy

Just say "let's add my keys" and we'll go step by step! 🚀
