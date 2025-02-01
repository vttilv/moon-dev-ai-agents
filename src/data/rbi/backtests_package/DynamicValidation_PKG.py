Here's the fixed code with proper Moon Dev themed debug prints and no usage of backtesting.lib:

```python
#!/usr/bin/env python3
import os
import pandas as pd
import numpy as np
import talib

# ─── DYNAMIC VALIDATION STRATEGY ──────────────────────────────
class DynamicValidation:
    # Strategy parameters (these will be optimized later)
    lookback = 20                # Lookback period for swing detection
    risk_reward_ratio = 2.5      # Minimum risk-reward ratio required (e.g. 2.5:1)
    zone_buffer = 10             # Price offset buffer (in dollars) for validating zones
    risk_pct = 0.01              # Risk 1% of equity per trade

    def init(self):
        # Calculate swing levels using TA‐Lib functions wrapped by self.I() 
        # (DON’T use backtesting.py’s built‐in indicators!)
        self.demand = self.I(talib.MIN, self.data.Low, timeperiod=self.lookback)   # Swing low = Demand Zone in uptrends
        self.supply = self.I(talib.MAX, self.data.High, timeperiod=self.lookback)  # Swing high = Supply Zone in downtrends
        print("🌙 [DynamicValidation] Indicators INIT – Swing Low (Demand) & Swing High (Supply) set with lookback =", self.lookback, "🚀")

    def next(self):
        # Get the current bar price and time (for debug prints)
        current_price = self.data.Close[-1]
        bar_time = self.data.index[-1]
        print(f"✨ [DynamicValidation] New bar @ {bar_time}: Price = {current_price:.2f}")

        # Ensure we have at least 'lookback' bars for trend validation
        if len(self.data.Close) < self.lookback:
            return

        # Simple trend determination: compare current close with the close from 'lookback' bars ago
        previous_price = self.data.Close[-self.lookback]
        trend = "uptrend" if current_price > previous_price else "downtrend" if current_price < previous_price else "sideways"
        print(f"🚀 [Moon Dev] Market trend determined as: {trend.upper()}")

        # Get the most-recent swing levels from our TA indicators
        current_demand = self.demand[-1]
        current_supply = self.supply[-1]
        print(f"🌙 [Moon Dev] Current Demand Zone (Swing LOW): {current_demand:.2f}")
        print(f"🌙 [Moon Dev] Current Supply Zone (Swing HIGH): {current_supply:.2f}")

        # If already in a trade, maintain the position.
        if self.position:
            print("✨ [Moon Dev] Already in a position – holding... 🚀")
            return

        # ─── LONG ENTRY (Uptrend: Price reenters a DEMAND zone) ───────────────
        if trend == "uptrend" and current_price <= (current_demand + self.zone_buffer):
            entry = current_price
            stop_loss = current_demand - self.zone_buffer  # Place SL just below demand zone
            take_profit = current_supply                    # TP at recent high (supply zone)
            risk = entry - stop_loss
            reward = take_profit - entry

            print(f"🚀 [Moon Dev] Evaluating LONG trade – Entry: {entry:.2f}, SL: {stop_loss:.2f}, TP: {take_profit:.2f}")
            print(f"🌙 [Moon Dev] Calculated Risk: {risk:.2f} | Reward: {reward:.2f}")

            if risk <= 0:
                print("🌙 [Moon Dev] Invalid (non-positive)