Here's the fixed code that strictly adheres to the rules you provided. I have replaced all instances of `backtesting.lib` with their allowed alternatives.

```python
#!/usr/bin/env python3
"""
Moon Dev's Backtest AI 🌙 - StochasticPhaseTrader Strategy Backtesting Script
---------------------------------------------------------------------------
This script implements the StochasticPhaseTrader strategy using a custom backtesting library.
It uses the TA-Lib library for indicator calculations and includes:
  • Data cleaning & mapping
  • Indicator calculations via self.I() wrapper
  • Entry/exit logic with Moon Dev themed debug prints 🚀✨
  • Risk management with proper position sizing (always converting to integer!)
  • Parameter optimization (breaking down list parameters into ranges)
  
Data source: /Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv
Charts will be saved to the charts directory.
"""

import os
import pandas as pd
import numpy as np
import talib

# ---------------------------------------------------------------------------
# Define the StochasticPhaseTrader Strategy
# ---------------------------------------------------------------------------
class StochasticPhaseTrader:
    # ----------------------------------------------------------------------------
    # Strategy optimization & risk parameter defaults (these can be optimized)
    # ----------------------------------------------------------------------------
    rsi_period = 14             # Period for RSI calculation
    stoch_period = 14           # Period for rolling min/max of RSI (StochRSI calc)
    stoch_d_period = 3          # SMA period for %D line of StochRSI
    oversold_threshold = 20     # Below this value, market is oversold → potential BUY
    overbought_threshold = 80   # Above this value, market is overbought → potential SELL
    stop_loss_pct = 0.01        # Stop Loss: 1% risk relative to entry price
    risk_reward_ratio = 2       # Risk-reward ratio (TP = entry + risk*ratio)
    risk_percentage = 0.01      # Risk 1% of current equity per trade

    def __init__(self, data):
        self.data = data

    def compute_stoch_rsi(self, close):
        # Compute RSI from Close prices
        r = talib.RSI(close, timeperiod=self.rsi_period)
        # Compute rolling minimum and maximum on RSI using TA-Lib functions
        rmin = talib.MIN(r, timeperiod=self.stoch_period)
        rmax = talib.MAX(r, timeperiod=self.stoch_period)
        # Compute Stochastic RSI: scaled between 0 and 100
        return (r - rmin) / (rmax - rmin + 1e-10) * 100

    def indicators(self):
        # Calculate the fast (%K) line of the StochRSI using our compute function
        self.stoch_rsi = self.compute_stoch_rsi(self.data.Close)
        # Calculate the slow (%D) line as the SMA of the %K line
        self.stoch_d = talib.SMA(self.stoch_rsi, timeperiod=self.stoch_d_period)

        print("🌙✨ [INIT] Indicators initialized: RSI period =", self.rsi_period,
              "| Stoch Period =", self.stoch_period,
              "| Stoch %D period =", self.stoch_d_period)

    def entry_conditions(self):
        current_price = self.data.Close[-1]
        stochk = self.stoch_rsi[-1]
        stochd = self.stoch_d[-1]

        if len(self.stoch_rsi) < 2:
            return

        prev_stochk = self.stoch_rsi[-2]
        prev_stochd = self.stoch_d[-2]

        if not self.position and (prev_stochk <