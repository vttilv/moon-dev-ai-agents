Here's the fixed code with no usage of backtesting.lib:

```python
#!/usr/bin/env python3
"""
Moon Dev's Backtest AI 🌙 🚀

Backtesting implementation for the GapAdvantage strategy.
This strategy focuses on capturing a sliver of a large move after a gap/breakout.
Please ensure you have installed the required packages:
    pip install pandas numpy TA-Lib pandas_ta
"""

import os
import numpy as np
import pandas as pd
import talib
import pandas_ta as pta  # may be used in helper functions if needed

# ─── UTILITY FUNCTIONS FOR INDICATORS ────────────────────────────────────────────────────
def VWAP(high, low, close, volume):
    """
    Calculate the Volume Weighted Average Price (VWAP).

    VWAP = cumulative((typical price × volume))/cumulative(volume)
    Typical Price = (High + Low + Close)/3
    """
    typical = (high + low + close) / 3.0
    cum_vol = np.cumsum(volume)
    # Avoid division by zero
    cum_vol[cum_vol == 0] = 1e-10
    vwap = np.cumsum(typical * volume) / cum_vol
    return vwap

# ─── STRATEGY CLASS DEFINITION ─────────────────────────────────────────────────────
class GapAdvantage:
    # Optimization parameters
    fast_ma_period = 9          # Moving average period for entry signal (default 9)
    slow_ma_period = 20         # Moving average period for trend (default 20)
    risk_reward_ratio = 1       # risk-reward ratio; must be at least 1 (default 1)
    
    # Fixed risk percentage per trade (percentage of equity to risk)
    risk_pct = 0.01             # 1% risk per trade

    def __init__(self, data):
        self.data = data
        self.fast_ma = None
        self.slow_ma = None
        self.vwap = None
        self.recent_high = None
        self.entry_price = None
        self.current_stop = None
        self.trailing_stop = None

        self.calculate_indicators()

    def calculate_indicators(self):
        # Debug print: initialize indicators 🌙✨
        print("🌙 [MoonDev Debug] Initializing GapAdvantage Strategy indicators...")

        # Calculate the fast and slow moving averages using TA-Lib's SMA.
        self.fast_ma = talib.SMA(self.data.Close.values, timeperiod=self.fast_ma_period)
        self.slow_ma = talib.SMA(self.data.Close.values, timeperiod=self.slow_ma_period)
        
        # Calculate VWAP indicator using our custom function.
        self.vwap = VWAP(self.data.High.values, self.data.Low.values, self.data.Close.values, self.data.Volume.values)
        
        # For a recent swing high used for entry check, we use a 5-period highest high.
        self.recent_high = talib.MAX(self.data.High.values, timeperiod=5)

        print("🚀 [MoonDev Debug] Indicators loaded: fast MA (period={}), slow MA (period={}), VWAP.".format(
            self.fast_ma_period, self.slow_ma_period))

    def should_enter_position(self):
        # Get current price information
        price = self.data.Close[-1]
        high = self.data.High[-1]
        
        # Moon Dev themed debug prints
        print("🌙 [MoonDev] New candle: Price = {:.2f}, High = {:.2f}, Low = {:.2f}