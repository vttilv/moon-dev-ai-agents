Here is the fixed code without any usage of backtesting.lib:

```python
#!/usr/bin/env python3
import os
import pandas as pd
import talib
import numpy as np

# ─── DATA HANDLING ───────────────────────────────────────────────
# Load CSV data and massage it into the proper format
data_path = "/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv"
print("🌙 Loading data from:", data_path)
data = pd.read_csv(data_path, parse_dates=["datetime"])

# Clean column names: remove spaces, lowercase, drop unnamed
data.columns = data.columns.str.strip().str.lower()
data = data.drop(columns=[col for col in data.columns if 'unnamed' in col.lower()])

# Rename required columns to match backtesting requirements: Open, High, Low, Close, Volume
rename_map = {"open": "Open", "high": "High", "low": "Low", "close": "Close", "volume": "Volume"}
data = data.rename(columns=rename_map)

# (Optional) Set the datetime column as index if needed by backtesting.py
if 'datetime' in data.columns:
    data.index = data["datetime"]

print("🌙 Data columns after cleaning and renaming:", list(data.columns))


# ─── STRATEGY IMPLEMENTATION ──────────────────────────────────────
class AccumulationManipulation(Strategy):
    # PARAMETERS (these can be optimized later)
    # risk_reward: multiplier for how many times the risk we want to reward (TP calculation)
    risk_reward = 2.0  
    # accumulation_factor: how many times larger the manipulation candle must be vs. recent accumulation range 
    accumulation_factor = 1.5  
    # risk percentage of current equity to risk per trade
    risk_percentage = 0.01

    def init(self):
        # Calculate a "daily bias" indicator using the 1H timeframe.
        # Since our data is 15m candles, a 1H SMA = SMA(4) of Close.
        self.daily_bias = talib.SMA(self.data.Close.values, timeperiod=4)
        print("🌙 [INIT] Daily bias (1H SMA) indicator set using TA‑Lib!")

    def next(self):
        # Current candle index is the last one available.
        i = len(self.data) - 1

        # Skip if not enough data candles (need 3 previous candles for accumulation window)
        if i < 3:
            return

        # ─── TIME WINDOW CHECK ─────────────────────────────────
        # Only take trades between 10:00 and 11:30 Eastern Standard Time.
        # (Assuming the CSV datetime is in Eastern Time – adjust if needed.)
        current_time = self.data.index[-1].time()
        if not (current_time >= time(10, 0) and current_time <= time(11, 30)):
            # Print Moon Dev debug message 🚀
            # (We will ignore candles outside the allowed trading window.)
            print(f"🌙 [TimeGate] Skipping candle at {current_time} (outside 10:00-11:30 EST)")
            return

        # ─── IDENTIFY ACCUMULATION ─────────────────────────────
        # Use the previous three candles to define an accumulation range.
        accumulation_high = np.max(self.data.High[-3:])
        accumulation_low = np.min(self.data.Low[-3:])
        accumulation_range = accumulation_high - accumulation_low
        print(f"🌙 [Accumulation] High: {acc