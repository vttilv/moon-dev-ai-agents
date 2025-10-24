# Moon Dev AI Agents - Architecture Diagrams

## 1. System Architecture Overview

```
┌────────────────────────────────────────────────────────────────────────────┐
│                     MAIN ORCHESTRATOR (main.py)                             │
│                    15-minute execution loop control                          │
└────────────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    │               │               │
                    ▼               ▼               ▼
        ┌─────────────────┐ ┌──────────────┐ ┌─────────────────┐
        │  RISK AGENT     │ │TRADING AGENT │ │ STRATEGY AGENT  │
        │ (First Priority)│ │ (Dual-Mode)  │ │ (Custom Logic)  │
        │                 │ │              │ │                 │
        │ • Balance check │ │Single: ~10s  │ │ • User-defined  │
        │ • Loss/gain     │ │Swarm: ~45-60s│ │ • Buy/Sell      │
        │   limits        │ │              │ │   signals       │
        │ • AI override   │ │Calls swarm   │ │                 │
        │                 │ │agent if      │ │ Returns:        │
        │ Config:         │ │enabled       │ │ - Signal        │
        │ MAX_LOSS_USD    │ │              │ │ - Confidence    │
        │ MAX_GAIN_USD    │ │Executes      │ │ - Reasoning     │
        │ MIN_BALANCE_USD │ │trades        │ │                 │
        └─────────────────┘ └──────────────┘ └─────────────────┘
           │                       │                    │
           └───────────┬───────────┴────────────────────┘
                       │
        ┌──────────────────────────────────────────────┐
        │    MARKET DATA COLLECTION LAYER              │
        ├──────────────────────────────────────────────┤
        │ • Fetch OHLCV (3 days @ 1H = 72 bars)       │
        │ • Get token overview (BirdEye)               │
        │ • Calculate indicators (pandas_ta):          │
        │   - MA20, MA40, RSI, Bollinger Bands         │
        │ • Validate trading activity                  │
        │ • Store in temp_data/                        │
        └──────────────────────────────────────────────┘
                       │
        ┌──────────────────────────────────────────────┐
        │   UNIFIED LLM ABSTRACTION LAYER              │
        │        (ModelFactory Pattern)                │
        ├──────────────────────────────────────────────┤
        │ Factory creates model instances:             │
        │                                              │
        │ model = ModelFactory.create_model('type')    │
        │                                              │
        │ Type options:                                │
        │ • 'claude'    → Anthropic                    │
        │ • 'openai'    → OpenAI GPT                   │
        │ • 'gemini'    → Google Gemini                │
        │ • 'deepseek'  → DeepSeek API                 │
        │ • 'groq'      → Groq Cloud                   │
        │ • 'xai'       → xAI Grok                     │
        │ • 'ollama'    → Local models                 │
        │                                              │
        │ All use same interface:                      │
        │ model.generate_response(...)                 │
        └──────────────────────────────────────────────┘
           │        │         │         │        │        │
           ▼        ▼         ▼         ▼        ▼        ▼
    ┌─────────┐ ┌──────┐ ┌───────┐ ┌─────────┐ ┌────┐ ┌───────┐
    │ Claude  │ │ GPT  │ │Gemini │ │DeepSeek │ │Groq│ │ Grok  │
    │         │ │      │ │       │ │         │ │    │ │       │
    │ Latest  │ │GPT-  │ │Gemini │ │deepseek-│ │Mix-│ │grok-4-│
    │ version │ │4o    │ │2.5    │ │reasoner │ │tral│ │fast   │
    └─────────┘ └──────┘ └───────┘ └─────────┘ └────┘ └───────┘
            │                                               │
            └───────────────────┬───────────────────────────┘
                                │
                        ┌───────────────┐
                        │ Environment   │
                        │ Variables     │
                        │               │
                        │ .env file     │
                        │ Contains all  │
                        │ API keys      │
                        └───────────────┘
```

---

## 2. Dual-Mode Trading Decision Flow

```
TRADING AGENT DECISION PROCESS

Input: Market Data + Token Info
         │
         ▼
    ┌─────────────────────────────┐
    │ Check USE_SWARM_MODE flag   │
    └─────────────────────────────┘
         │              │
         │ False        │ True
         ▼              ▼
    ┌──────────────┐  ┌─────────────────────────────────┐
    │ SINGLE MODEL │  │ SWARM CONSENSUS VOTING          │
    │ MODE         │  │                                 │
    │              │  │ Query 6 models in PARALLEL:     │
    │ • Query 1    │  │                                 │
    │   AI model   │  │ 1. Claude 4.5                   │
    │              │  │    ├─ Vote: Buy/Sell/Do-Nothing│
    │ • Return:    │  │    └─ Confidence: 100%          │
    │   Buy/       │  │                                 │
    │   Sell/      │  │ 2. GPT-5                        │
    │   Do Nothing │  │    ├─ Vote: Buy/Sell/Do-Nothing│
    │              │  │    └─ Confidence: 100%          │
    │ • Confidence:│  │                                 │
    │   Scalar 0-1 │  │ 3. Gemini 2.5                   │
    │              │  │    ├─ Vote: Buy/Sell/Do-Nothing│
    │ • Time: ~10s │  │    └─ Confidence: 100%          │
    │              │  │                                 │
    │ AI Model     │  │ 4. Grok-4                       │
    │ Type:        │  │    ├─ Vote: Buy/Sell/Do-Nothing│
    │ xai/openai/  │  │    └─ Confidence: 100%          │
    │ claude/groq/ │  │                                 │
    │ deepseek/    │  │ 5. DeepSeek-Chat                │
    │ gemini       │  │    ├─ Vote: Buy/Sell/Do-Nothing│
    │              │  │    └─ Confidence: 100%          │
    │              │  │                                 │
    │              │  │ 6. DeepSeek-R1 (Ollama)         │
    │              │  │    ├─ Vote: Buy/Sell/Do-Nothing│
    │              │  │    └─ Confidence: 100%          │
    │              │  │                                 │
    │              │  │ VOTE COUNTING:                  │
    │              │  │ • Buy votes: 4                  │
    │              │  │ • Sell votes: 1                 │
    │              │  │ • Do-Nothing: 1                 │
    │              │  │                                 │
    │              │  │ MAJORITY: Buy (4/6 = 67%)       │
    │              │  │                                 │
    │              │  │ SYNTHESIS:                      │
    │              │  │ Claude 4.5 summarizes all       │
    │              │  │ responses into 3-sentence max   │
    │              │  │                                 │
    │              │  │ • Time: ~45-60s total           │
    │              │  │ • Individual responses saved    │
    │              │  │ • Consensus summary returned    │
    │              │  │ • Model mapping logged          │
    └──────────────┘  └─────────────────────────────────┘
         │                              │
         └──────────────┬───────────────┘
                        │
                        ▼
                ┌──────────────────────┐
                │ POSITION MANAGEMENT  │
                │                      │
                │ If "BUY":            │
                │ • Check position     │
                │ • Calculate target   │
                │ • Break into chunks  │
                │ • Execute orders     │
                │                      │
                │ If "SELL":           │
                │ • Close position     │
                │ • Exit to cash       │
                │                      │
                │ If "DO NOTHING":     │
                │ • Hold current       │
                │ • No action          │
                └──────────────────────┘
                        │
                        ▼
                ┌──────────────────────┐
                │ RECORD & PERSIST     │
                │                      │
                │ • Save trade to CSV  │
                │ • Log execution      │
                │ • Update portfolio   │
                │ • Cleanup temp data  │
                └──────────────────────┘
```

---

## 3. RBI Agent (Research-Backtest-Implement) Workflow

```
USER INPUT (one of these):
├─ YouTube URL
├─ PDF file
└─ Text description

         │
         ▼
┌──────────────────────────────────────┐
│ STEP 1: RESEARCH PHASE               │
├──────────────────────────────────────┤
│ DeepSeek / GPT-5 / Claude            │
│                                      │
│ • Extract strategy logic             │
│ • Identify entry/exit rules          │
│ • Analyze technical patterns         │
│ • Extract parameters                 │
│                                      │
│ Output: research/ folder             │
│ - Strategy summary                   │
│ - Key findings                       │
│ - Extracted parameters               │
└──────────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────┐
│ STEP 2: CODE GENERATION              │
├──────────────────────────────────────┤
│ DeepSeek / GPT-5 / Claude            │
│                                      │
│ • Generate backtesting.py code       │
│ • Implement entry logic              │
│ • Implement exit logic               │
│ • Add indicators                     │
│                                      │
│ Output: backtests/ folder            │
│ - Initial Python code                │
│ - Commented strategy                 │
│ - Ready to execute                   │
└──────────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────┐
│ STEP 3: BACKTEST EXECUTION           │
├──────────────────────────────────────┤
│ backtesting.py library               │
│                                      │
│ • Load historical OHLCV data         │
│ • Run strategy simulation            │
│ • Calculate performance metrics:     │
│   - Total return %                   │
│   - Sharpe ratio                     │
│   - Max drawdown                     │
│   - Win rate                         │
│   - Number of trades                 │
│                                      │
│ Output: Performance report           │
│ - Charts with results                │
│ - Equity curve                       │
│ - Monthly returns                    │
└──────────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────┐
│ STEP 4: DEBUGGING (if errors)        │
├──────────────────────────────────────┤
│ DeepSeek / GPT-5 / Claude            │
│                                      │
│ • Analyze error messages             │
│ • Fix syntax errors                  │
│ • Fix logic errors                   │
│ • Optimize performance               │
│                                      │
│ Output: backtests_package/ folder    │
│ - Fixed Python code                  │
│ - Optimized version                  │
│ - Ready for production                │
└──────────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────┐
│ STEP 5: FINALIZATION                 │
├──────────────────────────────────────┤
│                                      │
│ Output: backtests_final/ folder      │
│ ├─ Final executable code             │
│ ├─ Full documentation                │
│ ├─ Parameter guide                   │
│ ├─ charts/ subfolder                 │
│ │  ├─ Equity curve                   │
│ │  ├─ Drawdown chart                 │
│ │  └─ Monthly returns heatmap        │
│ └─ Performance summary               │
│                                      │
│ COST: ~$0.027 per backtest           │
│ TIME: ~6 minutes execution           │
└──────────────────────────────────────┘
         │
         ▼
   READY TO TRADE!
   (Or iterate with improvements)
```

---

## 4. Agent Category Breakdown

```
MOON DEV'S 34+ AGENTS
│
├─ TRADING AGENTS (5)
│  ├─ Trading Agent (Dual-mode)
│  ├─ Risk Agent (First priority)
│  ├─ Strategy Agent (Custom logic)
│  ├─ Copy Bot Agent
│  └─ Swarm Agent (Consensus voting)
│
├─ MARKET ANALYSIS (8)
│  ├─ Sentiment Agent (Twitter sentiment)
│  ├─ Whale Agent (Large transactions)
│  ├─ Funding Agent (Funding rates)
│  ├─ Liquidation Agent (Liquidation spikes)
│  ├─ Chart Analysis Agent
│  ├─ Funding Arbitrage Agent
│  ├─ New/Top Tokens Agent
│  └─ CoinGecko Agent
│
├─ STRATEGY DEVELOPMENT (5)
│  ├─ RBI Agent v1/v2/v3
│  ├─ RBI Batch Backtester
│  └─ Research Agent (Auto-fills ideas.txt)
│
├─ CONTENT CREATION (6)
│  ├─ Chat Agent (YouTube live chat)
│  ├─ Clips Agent (Video clipping)
│  ├─ Real-Time Clips Agent (OBS streaming)
│  ├─ Tweet Agent (Tweet generation)
│  ├─ Video Agent (Text → video)
│  └─ Phone Agent (AI phone calls)
│
└─ SPECIALIZED (10+)
   ├─ Sniper Agent (Token launches)
   ├─ Transaction Agent
   ├─ Solana Agent (Cross-agent)
   ├─ Million Agent (Gemini 1M context)
   ├─ TikTok Agent (Social arbitrage)
   ├─ Compliance Agent (FB compliance)
   ├─ HouseCoin Agent (DCA with AI)
   ├─ Listing Arbitrage Agent
   ├─ Focus Agent (Productivity)
   └─ Code Runner Agent (Dynamic execution)
```

---

## 5. Data Flow: From Market to Trade

```
EXTERNAL APIs              DATA COLLECTION           PROCESSING            STORAGE
                                                                            
┌───────────────┐          ┌──────────────────┐    ┌──────────────┐    ┌─────────┐
│  BirdEye API  │────────▶│ Fetch OHLCV data │   │  Calculate   │   │ temp_   │
│               │         │ for token        │   │  technical   │   │ data/   │
│ • Price       │         │                  │   │  indicators  │   │         │
│ • Volume      │         │ Status:          │   │              │   │ or CSV  │
│ • Liquidity   │         │ 3 days @ 1H      │   │  - MA20/40   │   │ storage │
└───────────────┘         │ = 72 bars        │   │  - RSI       │   └─────────┘
                          └──────────────────┘   │  - BBands    │        │
┌───────────────┐                                 │  - Volume    │        │
│ CoinGecko API │────────────────────────────┐   │  - Momentum  │        │
│               │                            │   │              │        ▼
│ • Market cap  │                            │   └──────────────┘   ┌──────────┐
│ • Sentiment   │                            │                      │   USED   │
│ • Metadata    │                            │                      │    BY    │
└───────────────┘                            │                      │ TRADING  │
                                             │                      │  AGENTS  │
┌───────────────┐          ┌──────────────────┐                      │          │
│Moon Dev API   │────────▶│ Fetch:           │                      │  • AI    │
│               │         │ • Liquidations   │                      │    Models│
│ • Custom      │         │ • Funding rates  │                      │  • Risk  │
│   signals     │         │ • New tokens     │                      │    Agent │
│ • Copy list   │         │ • OI data        │                      │  • Other │
└───────────────┘         └──────────────────┘                      │    agents│
                                                                     └──────────┘
┌───────────────┐          ┌──────────────────┐
│Twitter API    │────────▶│ Collect tweets   │
│               │         │ on tracked tokens│
│ • Sentiment   │         │                  │
│ • Mentions    │         │ Analyze with:    │
│ • Trends      │         │ • HuggingFace    │
└───────────────┘         │ • Transformers   │
                          └──────────────────┘

                                │
                                ▼
                    ┌────────────────────┐
                    │  FINAL TRADE DATA  │
                    ├────────────────────┤
                    │ • Token address    │
                    │ • Action: B/S/Hold │
                    │ • Confidence       │
                    │ • Price/amount     │
                    │ • Timestamp        │
                    └────────────────────┘
                                │
                    ┌───────────┴────────────┐
                    │                        │
                    ▼                        ▼
            ┌──────────────┐        ┌──────────────┐
            │  Execution   │        │   Record &   │
            │              │        │   Persist    │
            │ • Solana     │        │              │
            │   exchange   │        │ • CSV files  │
            │ • HyperLiquid│        │ • Portfolios │
            │   exchange   │        │ • Audit log  │
            └──────────────┘        └──────────────┘
```

---

## 6. Risk Management Priority Chain

```
MAIN ORCHESTRATOR STARTS

    │
    ▼
    ┌────────────────────────────────────────────┐
    │ 1. RISK AGENT RUNS FIRST (ALWAYS)          │
    │                                            │
    │ Check:                                     │
    │ • Account balance                          │
    │ • Realized P&L                             │
    │ • Max loss limit (MAX_LOSS_USD)            │
    │ • Max gain limit (MAX_GAIN_USD)            │
    │ • Min balance threshold                    │
    │                                            │
    │ Decision Tree:                             │
    │ IF breach detected:                        │
    │   IF USE_AI_CONFIRMATION:                  │
    │     Consult AI with market context         │
    │     AI recommends: Override or Respect     │
    │   ELSE:                                    │
    │     Close positions immediately            │
    │ ELSE:                                      │
    │   Continue to trading agents               │
    └────────────────────────────────────────────┘
             │
             ├─── VIOLATION → HALT ──────┐
             │                           │
             └─ SAFE TO CONTINUE ──┐     │
                                   │     │
                                   ▼     ▼
                        ┌────────────────────────┐
                        │ 2. TRADING AGENT       │
                        │    (if enabled)        │
                        │                        │
                        │ Proceeds with:         │
                        │ • Market data fetch    │
                        │ • AI decision          │
                        │ • Trade execution      │
                        └────────────────────────┘
                                   │
                                   ▼
                        ┌────────────────────────┐
                        │ 3. STRATEGY AGENT      │
                        │    (if enabled)        │
                        │                        │
                        │ Analyzes strategies    │
                        │ Provides signals       │
                        └────────────────────────┘
                                   │
                                   ▼
                        ┌────────────────────────┐
                        │ 4. COPY BOT AGENT      │
                        │ 5. SENTIMENT AGENT     │
                        │ 6. OTHER AGENTS        │
                        │    (as configured)     │
                        └────────────────────────┘
                                   │
                                   ▼
                        ┌────────────────────────┐
                        │ SLEEP                  │
                        │ SLEEP_BETWEEN_RUNS     │
                        │ (default: 15 minutes)  │
                        └────────────────────────┘
                                   │
                                   └─── Loop Back ───→
```

---

## 7. Data Storage Organization

```
src/data/
│
├── Trading Results
│   ├── ai_analysis_buys.csv          [AI trading decisions]
│   ├── portfolio_balance.csv         [Account value history]
│   ├── current_allocation.csv        [Current position allocation]
│   └── execution_results/            [Trade execution details]
│
├── Analysis Data
│   ├── sentiment_history.csv         [Twitter sentiment scores]
│   ├── funding_history.csv           [Funding rate data]
│   ├── liquidation_history.csv       [Liquidation events]
│   ├── oi_history.csv                [Open interest]
│   ├── sniper_analysis.csv           [Token launch analysis]
│   └── transactions_analysis.csv     [Copy list transactions]
│
├── Market Data
│   ├── ohlcv/                        [Price data]
│   │   ├── token_address_1H.csv
│   │   ├── token_address_15m.csv
│   │   └── [more timeframes]
│   └── charts/                       [Chart images & analysis]
│
├── Strategy Data
│   ├── rbi/                          [RBI outputs (original)]
│   │   ├── ideas.txt                 [Input: trading ideas]
│   │   ├── 10_22_2024/               [Date-based organization]
│   │   │   ├── research/             [Strategy analysis]
│   │   │   ├── backtests/            [Initial code]
│   │   │   ├── backtests_package/    [Optimized code]
│   │   │   ├── backtests_final/      [Production code]
│   │   │   └── charts/               [Performance charts]
│   │   └── [more date folders]
│   ├── rbi_v2/                       [RBI v2 outputs]
│   └── rbi_v3/                       [RBI v3 outputs]
│
├── Content Data
│   ├── tweets/                       [Generated tweets]
│   ├── videos/                       [Generated videos]
│   ├── realtime_clips/               [Stream clips]
│   └── stream_thumbnails/            [Analysis images]
│
├── Agent-Specific
│   ├── housecoin_agent/              [HouseCoin DCA data]
│   ├── coingecko_results/            [Token discovery results]
│   └── code_runner/                  [Dynamic code execution logs]
│
└── Temporary (Auto-cleaned)
    └── temp_data/                    [Deleted after each run]
```

---

## 8. LLM Provider Model Hierarchy

```
UNIFIED INTERFACE
        │
        │  ModelFactory.create_model(provider_type)
        │
        ├─────────────────────────────────────────────────┐
        │                                                 │
        ▼                                                 ▼
    ┌─────────────┐                           ┌──────────────────┐
    │ Claude      │                           │ Local Option     │
    │             │                           │                  │
    │ Latest:     │                           │ Ollama Server    │
    │ 3.5-haiku   │                           │ (requires local) │
    │ 3.5-sonnet  │                           │                  │
    │ 4.0         │                           │ Model options:   │
    │ 4.5-sonnet  │                           │ • llama3.2       │
    │             │                           │ • mistral        │
    │ Use for:    │                           │ • deepseek-r1    │
    │ • Reasoning │                           │ • neural-chat    │
    │ • Synthesis │                           │ • zephyr         │
    │ • Consensus │                           │                  │
    │ • Analysis  │                           │ Use for:         │
    └─────────────┘                           │ • Privacy (local)│
                                              │ • No API key     │
    ┌─────────────┐                           │ • Fast inference │
    │ OpenAI GPT  │                           │ • Testing        │
    │             │                           └──────────────────┘
    │ Latest:     │
    │ gpt-4o      │
    │ gpt-4o-mini │
    │ gpt-4-      │
    │  turbo      │
    │             │
    │ Use for:    │
    │ • Speed     │
    │ • Vision    │
    │ • Multimodal│
    │ • General   │
    └─────────────┘

    ┌─────────────┐
    │ Google      │
    │ Gemini      │
    │             │
    │ Latest:     │
    │ 2.5-flash   │
    │ 1.5-pro     │
    │ 1M context  │
    │             │
    │ Use for:    │
    │ • Speed     │
    │ • Context   │
    │ • Images    │
    │ • Cost      │
    └─────────────┘

    ┌──────────────┐
    │ DeepSeek     │
    │              │
    │ Latest:      │
    │ deepseek-    │
    │  reasoner    │
    │ deepseek-    │
    │  chat        │
    │              │
    │ Use for:     │
    │ • Reasoning  │
    │ • Logic      │
    │ • Complex    │
    │ • Analysis   │
    └──────────────┘

    ┌──────────────┐
    │ Groq         │
    │              │
    │ Latest:      │
    │ mixtral-     │
    │  8x7b        │
    │              │
    │ Use for:     │
    │ • Speed      │
    │ • Inference  │
    │ • Low cost   │
    │ • Real-time  │
    └──────────────┘

    ┌──────────────┐
    │ xAI Grok     │
    │              │
    │ Latest:      │
    │ grok-4-fast- │
    │  reasoning   │
    │ 2M context   │
    │              │
    │ Use for:     │
    │ • Context    │
    │ • Reasoning  │
    │ • Cost ratio │
    │ • Speed      │
    └──────────────┘
```

---

## 9. Configuration Decision Tree

```
                START - CHOOSE EXCHANGE
                       │
                       ▼
            ┌─────────────────────┐
            │ EXCHANGE = 'solana' │ or 'hyperliquid'
            └─────────────────────┘
                       │
         ┌─────────────┴──────────────┐
         │                            │
         ▼                            ▼
    SOLANA (SPOT)              HYPERLIQUID (PERP)
    │                          │
    │ LONG_ONLY = True         │ LONG_ONLY = False
    │                          │
    │ • Spot trading           │ • Perpetual futures
    │ • Token pairs            │ • Leverage trading
    │ • No shorting            │ • Long & short
    │                          │ • Funding rates
    │                          │
    └─────────────────────────┘
             │
             ▼
    CHOOSE TRADING MODE
             │
    ┌────────┴────────┐
    │                 │
    ▼                 ▼
SINGLE MODEL    SWARM CONSENSUS
│               │
│ USE_SWARM_    │ • 6 models query
│ MODE = False  │ • Majority voting
│               │ • Higher confidence
│ • AI_MODEL_   │ • Takes ~45-60s
│   TYPE        │ • Better for long
│ • Fast ~10s   │   timeframes
│ • For quick   │
│   decisions   │
│               │
└───────────────┘
        │
        ▼
CONFIGURE POSITION SIZING
│
├─ usd_size: $25 (target)
├─ max_usd_order_size: $3 (chunks)
├─ MAX_POSITION_PERCENTAGE: 30%
└─ CASH_PERCENTAGE: 20%

        │
        ▼
CONFIGURE RISK MANAGEMENT
│
├─ MAX_LOSS_USD: $25
├─ MAX_GAIN_USD: $25
├─ MINIMUM_BALANCE_USD: $50
└─ USE_AI_CONFIRMATION: True

        │
        ▼
SELECT TOKENS
│
├─ MONITORED_TOKENS = [...]
└─ Min 1, recommended 1-5

        │
        ▼
SET API KEYS (.env)
│
├─ BIRDEYE_API_KEY
├─ ANTHROPIC_KEY (or others)
├─ SOLANA_PRIVATE_KEY (if Solana)
└─ HYPER_LIQUID_ETH_PRIVATE_KEY (if HL)

        │
        ▼
    READY TO TRADE!
```

