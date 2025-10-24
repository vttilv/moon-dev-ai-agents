# Moon Dev AI Agents for Trading - Executive Summary

## Quick Overview

**Moon Dev's AI Agents for Trading** is an experimental, open-source framework that orchestrates 34+ specialized AI agents to analyze cryptocurrency markets, execute trading strategies, and manage risk autonomously. It's designed as both a practical trading tool AND an educational platform for understanding modern AI agent architecture.

### Key Statistics
- **34+ Specialized Agents** covering trading, analysis, strategy generation, and content creation
- **24,401 Lines of Code** across agent ecosystem
- **7 LLM Providers** supported (Claude, OpenAI, Gemini, DeepSeek, Groq, xAI, Ollama)
- **Multi-Exchange**: Solana spot trading + HyperLiquid perpetuals
- **Dual-Mode Trading**: Fast single-model (~10s) or consensus swarm (~45-60s)

---

## System Architecture at a Glance

```
Main Orchestrator → Agent Layer → LLM Factory → APIs → Exchanges
                    (34+ agents)  (7 models)   (6+)   (2 exchanges)
```

**Layer Breakdown:**
1. **Main Orchestrator** (`main.py`): 15-minute execution cycles
2. **Agent Layer**: Trading, analysis, strategy, content, specialized
3. **LLM Abstraction** (`model_factory.py`): Unified interface to 7 AI providers
4. **Data Layer**: BirdEye, Moon Dev API, CoinGecko, HyperLiquid, Twitter
5. **Exchange Layer**: ExchangeManager routes to Solana or HyperLiquid

---

## Core Trading Flow

### 1. Risk Management (First Priority)
- Check account balance, PnL limits, circuit breakers
- AI confirmation layer for limit overrides
- Prevents catastrophic losses

### 2. Market Data Collection
- Fetch OHLCV data (3 days @ 1H = 72 bars)
- Calculate technical indicators (MA, RSI, Bollinger Bands)
- Validate trading activity (minimum trades per hour)

### 3. AI Decision Making
**Mode A - Single Model (Fast):**
- 1 AI model queries in ~10 seconds
- Returns: Buy/Sell/Do Nothing + confidence

**Mode B - Swarm Consensus (High Confidence):**
- 6 models query in parallel (~45-60 seconds total)
- Each votes: Buy/Sell/Do Nothing
- Majority wins, Claude synthesizes summary
- Models: Claude 4.5, GPT-5, Gemini 2.5, Grok-4, DeepSeek, DeepSeek-R1

### 4. Execution & Position Management
- Order chunking: Break $25 target into $3 chunks
- Risk controls: Max 30% per position, 20% cash minimum
- Slippage protection: 2% tolerance
- Records all trades to CSV

### 5. Portfolio Tracking
- Updates balance and position allocation
- Calculates unrealized P&L
- Logs to portfolio_balance.csv

---

## 34 Agents Organized by Function

### Trading Agents (5)
- **Trading Agent**: Dual-mode (single/swarm) with position management
- **Risk Agent**: First-priority risk management & circuit breakers
- **Strategy Agent**: Loads & executes user-defined strategies
- **Copy Bot Agent**: Mirrors Moon Dev's copy trading list
- **Swarm Agent**: 6-model consensus voting (reusable by any agent)

### Market Analysis (8)
- **Sentiment Agent**: Twitter sentiment analysis with voice alerts
- **Whale Agent**: Large transaction detection + voice announcements
- **Funding Agent**: Funding rate monitoring + alerts
- **Liquidation Agent**: Liquidation event tracking (15m/1h/4h windows)
- **Chart Analysis Agent**: Chart pattern recognition & buy/sell signals
- **Funding Arbitrage Agent**: HyperLiquid ↔ Solana rate differential
- **New/Top Tokens Agent**: Token discovery via CoinGecko
- **CoinGecko Agent**: Comprehensive token metadata

### Strategy Development (5)
- **RBI Agent v1/v2/v3**: Research-Backtest-Implement automation
  - Takes YouTube URL/PDF/text → generates backtest code → executes
  - Cost: ~$0.027 per backtest (~6 min execution)
  - Outputs: research, backtest code, performance charts
- **RBI Batch Backtester**: Parallel backtest execution
- **Research Agent**: Auto-fills ideas.txt for perpetual RBI execution

### Content Creation (6)
- **Chat Agent**: YouTube live chat monitoring & auto-response
- **Clips Agent**: Long video → short clips (YouTube Shorts/TikTok)
- **Real-Time Clips Agent**: OBS stream → auto-clipped highlights
- **Tweet Agent**: Text → AI-generated tweets
- **Video Agent**: Text → audio → video composition
- **Phone Agent**: AI phone call handling

### Specialized Agents (10+)
- **Sniper Agent**: New Solana token launch detection
- **Transaction Agent**: Transaction monitoring from copy list
- **Solana Agent**: Coordinates sniper + tx agents
- **Million Agent**: Gemini's 1M context integration
- **TikTok Agent**: TikTok trend analysis ("social arbitrage")
- **Compliance Agent**: TikTok ad Facebook compliance check
- **HouseCoin Agent**: DCA agent with AI confirmation
- **Listing Arbitrage Agent**: Pre-exchange listing detection
- **Focus Agent**: Productivity monitoring with voice alerts
- **Code Runner Agent**: Dynamic trading code execution

---

## Data Sources & APIs

| Source | Purpose | Authentication |
|--------|---------|-----------------|
| **BirdEye** | Solana token data (OHLCV, overview) | API Key |
| **Moon Dev API** | Proprietary signals (liquidations, funding) | API Key |
| **CoinGecko** | Token metadata (15,000+ tokens) | None (free) |
| **Helius RPC** | Solana blockchain interaction | RPC endpoint |
| **Twitter/X** | Sentiment data collection | OAuth cookies |
| **HyperLiquid** | Perpetuals data & execution | ETH private key |
| **OpenAI TTS/Whisper** | Voice synthesis & transcription | API Key |
| **ElevenLabs** | Premium voice synthesis | API Key |

---

## LLM Provider Integration (Model Factory)

**Unified Interface:**
```python
model = ModelFactory.create_model('anthropic')  # or 'openai', 'gemini', etc.
response = model.generate_response(system_prompt, user_content, temperature, max_tokens)
```

**Supported Providers:**
- Anthropic Claude (claude-3-5-haiku-latest default)
- OpenAI GPT (gpt-4o default)
- Google Gemini (gemini-2.5-flash default)
- DeepSeek (deepseek-reasoner default)
- Groq (mixtral-8x7b-32768 default)
- xAI Grok (grok-4-fast-reasoning default)
- Local Ollama (llama3.2 default, requires `ollama serve`)

**Features:**
- Automatic API key detection from environment
- Fallback handling for missing keys
- Dynamic model switching per agent
- Extensive debugging output
- Support for custom model names

---

## Key Features & Design Patterns

### 1. Dual-Mode Trading System
- **Single Model**: Fast execution (~10s) for frequent decisions
- **Swarm Mode**: Consensus voting (~45-60s) for high-confidence trades
- **Toggle**: Simple config flag (`USE_SWARM_MODE`)

### 2. Risk-First Architecture
- Risk agent runs FIRST every cycle before any trading
- Circuit breakers: MAX_LOSS_USD, MAX_GAIN_USD, MINIMUM_BALANCE_USD
- AI confirmation layer for limit overrides
- Philosophy: "Control risk, not profit"

### 3. Modular Agent Design
- Base class pattern (`BaseAgent`) for standardization
- <800 lines per agent (architectural constraint)
- Automatic data directory creation per agent
- Standalone execution (each agent can run independently)

### 4. Graceful Error Handling
- Errors don't kill the system
- Brief pause before retry (prevents API hammering)
- Keyboard interrupt for clean shutdown
- Visible error logging

### 5. Configuration Consolidation
- Trading Agent: All settings in lines 55-110 (one file)
- Risk Management: config.py for global settings
- Exchange-specific: ExchangeManager routes based on config
- Strategy paths: User strategies in src/strategies/custom/

### 6. Data Organization
- Temporary data auto-cleaned after run
- CSV storage for historical analysis
- Date-based folders for RBI outputs (MM_DD_YYYY)
- Audit trails for all trades/decisions

---

## Configuration Essentials

### Main Settings (config.py)
```python
EXCHANGE = 'solana'                    # or 'hyperliquid'
MONITORED_TOKENS = [...]              # Tokens to analyze
usd_size = 25                          # Target position
max_usd_order_size = 3                 # Order chunk size
MAX_POSITION_PERCENTAGE = 30           # Position size limit
CASH_PERCENTAGE = 20                   # Min cash buffer
MAX_LOSS_USD = 25                      # Loss circuit breaker
MINIMUM_BALANCE_USD = 50               # Account minimum
SLEEP_BETWEEN_RUNS_MINUTES = 15        # Cycle interval
```

### Trading Agent Settings (trading_agent.py, lines 55-110)
```python
USE_SWARM_MODE = True                  # Single model vs swarm
LONG_ONLY = True                       # Solana vs HyperLiquid
AI_MODEL_TYPE = 'xai'                  # Default for single mode
DAYSBACK_4_DATA = 3                    # Historical days
DATA_TIMEFRAME = '1H'                  # Bar timeframe
```

### Environment Variables (.env)
```
# AI Services
ANTHROPIC_KEY=
OPENAI_KEY=
DEEPSEEK_KEY=
GROQ_API_KEY=
GEMINI_KEY=
GROK_API_KEY=

# Blockchain & Market Data
BIRDEYE_API_KEY=
MOONDEV_API_KEY=
SOLANA_PRIVATE_KEY=
HYPER_LIQUID_ETH_PRIVATE_KEY=
RPC_ENDPOINT=

# Optional
TWITTER_USERNAME=
TWITTER_PASSWORD=
ELEVENLABS_API_KEY=
```

---

## Unique & Innovative Aspects

1. **Multi-AI Consensus** - 6 models vote simultaneously for democratic AI decisions
2. **Automated Strategy Development** - RBI agent turns ideas into backtests automatically
3. **Risk-First Philosophy** - Risk agent runs first, every cycle
4. **Unified LLM Abstraction** - One interface for 7 different AI providers
5. **Social Arbitrage** - TikTok agent extracts consumer trends for trading signals
6. **Real-Time Stream Clipping** - Auto-clips streaming content during live broadcasts
7. **AI-Driven Risk Override** - Limits can be overridden based on market context
8. **Self-Sustaining Research** - Research agent auto-fills ideas for perpetual RBI execution
9. **Multi-Exchange Unity** - Same code works on Solana and HyperLiquid
10. **Open-Source Transparency** - 100% transparent, no token, community-driven

---

## Important Disclaimers

**This is an experimental project. Read carefully:**

1. **NOT financial advice** - educational & research project only
2. **No profitability guarantees** - substantial risk of loss
3. **No token** - project is free and open-source forever
4. **User responsibility** - requires personal strategy development
5. **DYOR** - Do Your Own Research before trading
6. Success depends entirely on YOUR:
   - Trading strategy design
   - Risk management discipline
   - Market research & validation
   - Testing and iteration
   - Overall trading approach

---

## Quick Start

1. **Clone & Setup**
   ```bash
   git clone <repo>
   cd moon-dev-ai-agents
   conda activate tflow
   pip install -r requirements.txt
   ```

2. **Configure**
   - Copy `.env_example` → `.env`
   - Add API keys (BirdEye, OpenAI, etc.)
   - Edit `config.py` for trading parameters

3. **Run**
   ```bash
   python src/main.py              # Main orchestrator
   python src/agents/trading_agent.py   # Individual agent
   ```

4. **Monitor**
   - Check `src/data/` for results
   - Watch console output for color-coded status
   - Review CSV files for audit trails

---

## Resources & Community

- **Full Documentation**: `PROJECT_ANALYSIS.md` (1,386 lines)
- **YouTube**: Weekly updates and tutorials
- **Discord**: `discord.gg/8UPuVZ53bh` - Community discussion
- **Website**: `moondev.com` - Free trading education
- **Bootcamp**: `algotradecamp.com` - Advanced training

---

## Project Philosophy

"Code is the great equalizer and we have never seen a regime shift like this so I need to get this code to the people." - Moon Dev

The project emphasizes:
- **Transparency** over mystery
- **Education** over profit promises
- **Community** over gatekeeping
- **Iteration** over perfection
- **Responsibility** over hype

This is not a "set and forget" trading bot. It's a framework for understanding AI agent orchestration, multi-model consensus, risk management, and autonomous decision-making—with cryptocurrency trading as the practical domain.

