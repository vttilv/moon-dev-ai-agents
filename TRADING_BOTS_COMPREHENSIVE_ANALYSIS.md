# Moon Dev Trading Bots - Comprehensive Project Analysis

## EXECUTIVE SUMMARY

You have **two separate but complementary trading bot ecosystems**:

1. **Moon Dev AI Agents for Trading** - A multi-exchange, multi-strategy framework built around AI-powered decision making
2. **Polymarket Trading Bots** - A specialized collection of prediction market trading bots with proven strategies

These are **completely separate projects** but represent different approaches to automated trading. The AI agents framework is more general-purpose and exchange-agnostic, while the Polymarket bots are highly specialized for prediction markets.

---

## PART 1: MOON DEV AI AGENTS FOR TRADING

### Project Overview
**Location:** `/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading`

A comprehensive multi-agent framework for AI-driven trading across **Solana** and **HyperLiquid** (perpetuals/futures).

### Architecture Patterns

#### 1. **Base Agent Pattern**
- All agents inherit from `BaseAgent` (unified parent class)
- Supports optional `ExchangeManager` for unified exchange handling
- Configuration management through centralized `config.py`

```python
class BaseAgent:
    def __init__(self, agent_type, use_exchange_manager=False)
    - Initializes exchange manager if requested
    - Falls back to direct nice_funcs imports
    - Provides get_active_tokens() for exchange-aware token lists
```

#### 2. **Exchange Manager Pattern**
- Abstracts Solana vs HyperLiquid differences
- Unified interface for:
  - `market_buy()` / `market_sell()`
  - `get_position()`
  - `get_balance()`
  - `place_limit_order()` / `cancel_orders()`
  - `get_ohlcv_data()`

#### 3. **Dual-Mode AI System**
- **Single Model Mode**: Fast (~10s per token) using one AI model
- **Swarm Mode**: Consensus (~45-60s per token) with 6 models voting

### Bot Types (46 Total Agents)

#### Trading Execution Bots:
1. **Trading Agent** (`trading_agent.py`) - PRIMARY
   - Dual-mode AI trading system
   - Configurable via lines 55-95
   - Supports LONG_ONLY and LONG/SHORT modes
   - Position sizing with risk management
   - Monitors 1-5 tokens simultaneously

2. **Risk Agent** (`risk_agent.py`)
   - Portfolio risk monitoring
   - Position limits enforcement
   - Max loss/gain controls
   - MINIMUM_BALANCE_USD safeguards

3. **Strategy Agent** (`strategy_agent.py`)
   - Manages strategy signals from `/strategies` folder
   - Technical indicator-based trading

4. **Copy Bot Agent** (`copybot_agent.py`)
   - Analyzes copybot portfolio positions
   - Identifies opportunities for increased allocations
   - Reads from external copybot portfolio CSV

#### Market Monitoring Bots:
5. **Whale Agent** (`whale_agent.py`) - SOPHISTICATED
   - Tracks Open Interest (OI) changes
   - Detects whale activity via multiplier thresholds
   - Multiple timeframe analysis (15m lookback)
   - Voice announcements via OpenAI TTS
   - DeepSeek model integration

6. **Funding Agent** (`funding_agent.py`)
   - Monitors funding rates across exchanges
   - AI analysis of funding opportunities
   - Extreme funding alerts with voice

7. **Liquidation Agent** (`liquidation_agent.py`)
   - Tracks liquidation events
   - Configurable time windows (15min/1hr/4hr)
   - AI analysis of liquidation spikes

#### Data Analysis & Research Bots:
8. **RBI Agent** (`rbi_agent.py`, `rbi_agent_v2.py`, `rbi_agent_v3.py`) - COMPLEX
   - Research-Backtest-Implement workflow
   - Extracts trading strategies from:
     - YouTube videos
     - PDFs
     - Text descriptions
   - Auto-generates backtests
   - Debug pipeline for code fixing
   - Date-organized output structure

9. **Listing Arbitrage Agent** (`listingarb_agent.py`)
   - Identifies Solana tokens on CoinGecko pre-listing
   - Tracks before major exchange launches
   - Technical + fundamental AI analysis
   - Parallel model queries

#### Sentiment & Market Analysis:
10. **Sentiment Agent** (`sentiment_agent.py`)
    - Twitter sentiment analysis for crypto
    - Voice announcements

11. **Chart Analysis Agent** (`chartanalysis_agent.py`)
    - Analyzes charts with AI
    - Buy/sell/hold recommendations

12. **New or Top Agent** (`new_or_top_agent.py`)
    - Monitors CoinGecko new/top tokens

#### Special Purpose Bots:
13. **Swarm Agent** (`swarm_agent.py`) - UTILITY FUNCTION
    - Queries 6 AI models in parallel:
      - Claude Sonnet 4.5
      - GPT-5
      - Gemini 2.5 Flash
      - Grok-4 Fast Reasoning
      - DeepSeek Chat
      - DeepSeek-R1 Local (Ollama)
    - Consensus summary generation
    - Clean JSON output with model mapping

14. **Housecoin Agent** (`housecoin_agent.py`)
    - DCA (Dollar Cost Average) strategy
    - AI confirmation layer
    - "1 House = 1 Housecoin" thesis

#### Social & Content Bots:
15. **Tweet Agent** (`tweet_agent.py`) - Creates tweets from text
16. **TikTok Agent** (`tiktok_agent.py`) - Social arbitrage via TikTok data
17. **YouTube/Clips Agents** - Video analysis and generation
18. **Chat Agent** (`chat_agent.py`) - YouTube live chat moderation
19. **Phone Agent** (`phone_agent.py`) - Voice call handling
20. **Real-Time Clips Agent** (`realtime_clips_agent.py`) - OBS stream clipping
21. **Sniper Agent** (`sniper_agent.py`) - Solana token launch detection

### Data Collection Mechanisms

#### Primary Data Sources:

1. **Birdeye API** (Solana)
   - Token overview data
   - Security information
   - OHLCV data (1m, 3m, 5m, 15m, 30m, 1H, 2H, 4H, 6H, 8H, 12H, 1D, 3D, 1W, 1M)
   - Price data
   - Volume analysis
   - Wallet tracking

2. **HyperLiquid API** (Perpetuals)
   - OHLCV candle snapshots
   - Real-time market data
   - Position tracking
   - Funding rates

3. **CoinGecko API**
   - New token listings
   - Top tokens by market cap
   - Token metadata

4. **Jupiter Lite API** (Solana DEX)
   - Order execution
   - Price quotes

5. **Hash Dive API** (Whale Tracking)
   - Whale position tracking
   - P&L analysis
   - Top trader identification

#### Data Flow Pattern:

```
OHLCV Collector (Data Module)
    ↓
collect_token_data() - Fetches single token
collect_all_tokens() - Batch collection
    ↓
Stores: temp_data/ (if SAVE_OHLCV_DATA=False)
     or data/ (if SAVE_OHLCV_DATA=True)
    ↓
Agents consume via nice_funcs.get_data()
```

### Configuration System

**Primary Config File:** `src/config.py`
- Exchange selection (SOLANA vs HYPERLIQUID)
- Position sizing (usd_size, max_usd_order_size)
- Risk limits (CASH_PERCENTAGE, MAX_POSITION_PERCENTAGE)
- Max loss/gain controls (USD or percentage-based)
- AI model selection (Claude, OpenAI, DeepSeek, etc.)
- Data collection settings
- Token lists

**Agent-Specific Configs:** Each agent has override capability
- Example: `trading_agent.py` lines 55-95
- Allows per-agent customization without modifying central config

### Technical Indicators & Analysis

Located in `src/nice_funcs_hl.py` (for HyperLiquid):
- SMA (20, 50-day moving averages)
- RSI (Relative Strength Index)
- MACD (Moving Average Convergence Divergence)
- Bollinger Bands
- All via `pandas_ta` library

### Key Dependencies

```
- anthropic: Claude API
- openai: GPT models + voice TTS
- requests: HTTP API calls
- pandas: Data manipulation
- pandas_ta: Technical indicators
- termcolor: Colored terminal output
- eth_account: HyperLiquid key management
- web3: Blockchain interactions
- py_clob_client: Polymarket CLOB orders (deprecated)
```

### Execution & Orchestration

**Main Entry Point:** `src/main.py`
```python
ACTIVE_AGENTS = {
    'risk': False,
    'trading': False,
    'strategy': False,
    'copybot': False,
    'sentiment': False,
}
```

- Loop-based execution with configurable sleep intervals
- Sequential agent execution
- Error handling with retry logic
- Graceful shutdown on Ctrl+C

---

## PART 2: POLYMARKET TRADING BOTS

### Project Overview
**Location:** `/Users/md/Dropbox/dev/github/Polymarket-Trading-Bots`

Specialized trading bots for prediction markets with proven strategies.

### Trading Strategies

#### 1. **Mean Reversion Bot** (`mean_reversion_bot.py`) - PRIMARY STRATEGY
**Thesis:** Exploit emotional overreactions in prediction markets

**Entry Signals:**
- Price deviates > 2σ (2 standard deviations) from 72-hour mean
- Lookback: 72 hours of OHLCV data
- Timeframe: 1-hour candles

**Exit Conditions:**
- Price returns to mean ± 0.5σ (exit target)
- Price hits mean ± 3σ (stop loss)
- Max holding: 72 hours (force exit)

**Position Management:**
- USD investment size: $5 per trade
- Price filters: 0.10 < price < 0.90 (avoids low/high conviction)
- Minimum history: 30 days
- Expiration filter: Avoids <24 hours to resolution
- Whale mode: Can filter to 609+ whale-backed markets

**Data Tracking:**
- `mean_reversion_positions.csv` - Active positions
- `mean_reversion_signals.csv` - All signals generated
- `mean_reversion_trades.csv` - Trade history + P&L
- `mean_reversion_deviations.csv` - Price deviation history for optimization

#### 2. **Whale Copy Bot** (`copy_bot.py`)
**Thesis:** Copy trades from successful whale addresses

**Workflow:**
1. Load whale addresses from `whale_addresses_filtered.csv`
2. Poll whale positions via Hash Dive API
3. Mirror their trades at smaller scale ($1 per position)
4. Apply take profit (30%) and stop loss (-25%)
5. Filter: Skip tokens >80 cents (resolution protection)

**Whale Selection:**
- Uses Hash Dive API for whale tracking
- Filters by P&L thresholds
- Input: `whale_addresses_filtered.csv`
- Output: Tracked positions with entry prices

#### 3. **Sweeper Detection & Dashboard** (`course/sweeper_mini.py`)
**Thesis:** Detect and track large limit order sweeps (smart money)

**Key Metrics:**
- Minimum sweep size: $3,000 USD
- Monitoring: Last 30 minutes
- Detection: Size clustering (3x minimum multiplier)
- Update frequency: Every 5 seconds

**Filters Applied:**
- Sports markets (filtered out - gamblers, not smart money)
- Major crypto predictions (BTC, ETH, SOL, XRP - usually emotional)
- Low-volume markets

**Data Tracked:**
- Sweep timestamp
- Token side (YES/NO)
- Size and price
- Order book impact
- Cluster detection (multiple sweeps on same side)

**Stored in:** `data/sweeps_database.csv`

#### 4. **BTC 15-Minute Bot** (`btc_15min_bot.py`) - RECENT
**Thesis:** Scalp 15-minute BTC Up/Down markets continuously

**Parameters:**
- Bid price: $0.15 per share
- Shares: 133 per order
- Entry window: First 10 minutes of 15-min market
- Final cancellation: At 12-minute mark
- Position check: Every 10 seconds

**Workflow:**
1. Identify current 15-minute market
2. Calculate next market timestamp
3. Place limit orders for BOTH UP and DOWN
4. Cancel after entry window expires
5. Hold until market close OR reach profit target

### Data Collection for Polymarket

#### APIs Used:

1. **Polymarket Gamma API** (Market Data)
   - Endpoint: `https://gamma-api.polymarket.com/markets`
   - Provides: Market info, token IDs, expiration
   - Limit: 5000 markets per request

2. **Polymarket CLOB API** (Order Book)
   - Endpoint: `https://clob.polymarket.com/book?token_id=...`
   - Provides: Real-time bid/ask spreads
   - Key metric: Mid price, order book depth

3. **Polymarket Price History**
   - Endpoint: `https://clob.polymarket.com/prices-history`
   - Parameters: interval (1m/1h/1d), fidelity (resolution in minutes)
   - Returns: OHLCV-style historical prices

4. **Hash Dive API** (Whale Tracking)
   - Endpoint: `https://hashdive.com/api/get_positions`
   - Requires: API key (purchased separately)
   - Returns: Whale positions with P&L

5. **Polygon RPC** (USDC Balance)
   - Gets USDC balance for wallet
   - Two USDC contracts supported (new + legacy)

### Core Functions Library

**Location:** `examples/nice_funcs.py`

Critical Functions:
```python
get_usdc_balance()           # Wallet USDC balance (Polygon)
get_token_id()               # Market ID → YES/NO token IDs
get_positions()              # Current open positions
get_all_positions()          # Full portfolio with P&L
place_limit_order()          # Place limit order on CLOB
place_market_order()         # Market order execution
cancel_token_orders()        # Cancel orders for a token
get_all_orders()             # All open orders
calculate_shares()           # USD → share quantity calculation
check_position_sell_orders() # Audit missing sell orders
get_ohlcv_data()             # Historical OHLCV data
get_token_data()             # Comprehensive market data
```

#### Order Execution Flow:

1. **Get Token IDs**
   - Market ID → fetch YES/NO token IDs
   - Uses Gamma API or direct market lookup

2. **Place Limit Order**
   - Uses `py_clob_client` library
   - Requires: Private key (from .env)
   - Outputs: Order signature

3. **Monitor Position**
   - Check filled amount
   - Track entry price
   - Monitor spreads for exit

4. **Exit Strategy**
   - Limit order at profit target
   - Market order if timeout
   - Position tracking via CSV

### Supporting Tools

1. **Whale Processor** (`whale_processor.py`)
   - Filters whale download from Hash Dive
   - Applies P&L thresholds
   - Extracts wallet addresses
   - Output: `whale_addresses_filtered.csv`

2. **Market Expiration Checker** (`check_market_expiration.py`)
   - Queries market expiration times
   - Filters trading opportunities
   - Protects against last-minute volatility

3. **Spread Scanner/Analyzer**
   - Detects arbitrage opportunities
   - Compares YES/NO price discrepancies
   - Calculates risk/reward

4. **Deviation Analyzer** (`analyze_deviation_patterns.py`)
   - Historical analysis of price deviations
   - Optimization of entry/exit thresholds
   - Volatility profiling by market

### File Organization

```
Polymarket-Trading-Bots/
├── Main bots:
│   ├── mean_reversion_bot.py        (PRIMARY - Std dev mean reversion)
│   ├── copy_bot.py                  (Copy whale trades)
│   ├── btc_15min_bot.py             (Scalp 15-min markets)
│   ├── spread_bot.py                (Arbitrage)
│   └── spread_scan_buy.py           (Spread detection)
│
├── Dashboard/Monitoring:
│   ├── course/sweeper_mini.py       (Sweep detection)
│   ├── course/sweeper_dashboard.py  (Real-time sweeps)
│   ├── course/whale_dashboard.py    (Whale tracking)
│   ├── course/copy_bot_dashboard.py (Copy bot status)
│   └── course/almost_decided_dashboard.py (Near-decision trades)
│
├── Analysis Tools:
│   ├── whale_processor.py           (Filter whales)
│   ├── analyze_deviation_patterns.py
│   ├── analyze_existing_trades.py
│   ├── check_market_expiration.py
│   └── expiration_filter.py
│
├── Utilities:
│   ├── examples/nice_funcs.py       (Core trading functions)
│   ├── course/nice_funcs.py         (Older version)
│   ├── get_market_data.py
│   └── plot_data.py
│
├── Data:
│   ├── mean_reversion_positions.csv
│   ├── mean_reversion_trades.csv
│   ├── sweeps_database.csv
│   ├── whale_addresses_filtered.csv
│   └── [more CSVs for tracking]
│
└── poly-maker-main/                 (Referenced bot repo)
    ├── trading.py                   (High-performance trader)
    ├── update_markets.py
    └── poly_data/polymarket_client.py
```

---

## INTEGRATION & ROADMAP

### What's Missing (From README.md Roadmap):

1. **Polymarket Integration** (🚨 PLANNED - NOT IMPLEMENTED)
   - Prediction market trading capabilities
   - Status: On roadmap, not in moon-dev-ai-agents
   - Existing in: Polymarket-Trading-Bots repo

2. **Base Chain Integration** - Not yet implemented

3. **HyperLiquid Spot Trading** - Not yet implemented

4. **Polymarket Sweeper Agent** - FUTURE
   - "watches our polymarket sweeper dashboard and follows some sweepers"
   - Would integrate sweep detection with AI analysis

### Why Two Separate Repos?

- **moon-dev-ai-agents-for-trading**: General framework for any exchange (Solana, HyperLiquid, future: Polymarket)
- **Polymarket-Trading-Bots**: Mature, proven strategies specific to prediction markets
  - Years of optimization
  - Complex CSV tracking
  - Established whale database
  - Tested entry/exit rules

### Potential Integration Points

If building a Polymarket agent for the AI framework:

1. **Sweep Detection Agent**
   - Monitor `sweeps_database.csv` 
   - Query recent sweeps via Polymarket API
   - Use SwarmAgent for confirmation (should we follow this sweep?)
   - Execute via nice_funcs CLOB client

2. **Mean Reversion Agent**
   - Reuse the threshold logic
   - Integrate OHLCV collection from Polymarket API
   - AI decision layer before executing

3. **Whale Copy Agent**
   - Monitor Hash Dive whale positions
   - AI confidence scoring (Swarm Mode)
   - Automated copying with risk limits

---

## KEY INSIGHTS

### Architecture Philosophy:
- **Modular design**: Each agent is self-contained
- **Configuration-driven**: Minimal code changes needed
- **Exchange-agnostic**: Same agent code works on Solana/HyperLiquid via ExchangeManager
- **AI-first**: All trading decisions can leverage swarm voting
- **Data-centralized**: All OHLCV data flows through one collection point

### Data Flow:
```
External APIs (Birdeye, HyperLiquid, CoinGecko, etc.)
    ↓
nice_funcs.py (Solana) / nice_funcs_hl.py (HyperLiquid)
    ↓
ohlcv_collector.py (Standardizes data)
    ↓
Agents consume via get_data()
    ↓
LLM queries for decision making (SwarmAgent)
    ↓
ExchangeManager for order execution
    ↓
Position tracking & monitoring
```

### Decision Making:
- **Single Model**: ~10 seconds per decision
- **Swarm Mode**: ~60 seconds per decision with 6-model consensus
- **Models used**: Claude 4.5, GPT-5, Gemini 2.5, Grok-4, DeepSeek, DeepSeek-R1 local
- **Voting**: Majority wins (Buy/Sell/Do Nothing)

### Polymarket Bot Maturity:
- **Mean Reversion**: Tested, proven, real P&L tracking
- **Copy Bot**: Proven whale-following strategy
- **Sweeper Detection**: Real-time monitoring dashboard
- **15-Min Bot**: Recent addition, scalping approach

---

## STARTING RECOMMENDATIONS

If proposing new agents:

1. **Study existing patterns**
   - Base agent structure
   - Configuration system
   - Exchange manager abstraction

2. **Identify data sources**
   - What APIs are needed?
   - Can data be collected via existing functions?
   - OHLCV collection already standardized

3. **Leverage Swarm Agent**
   - Use for confirmation decisions
   - Consensus voting for safety
   - Easy integration via import

4. **For Polymarket**
   - Good foundation exists in Polymarket-Trading-Bots
   - Consider wrapping existing strategies
   - Add AI confidence layer to proven tactics

---

*Analysis complete. Ready for new agent proposals!*
