#!/usr/bin/env python3
import os
import pandas as pd
import numpy as np
import talib

# ─── DYNAMIC VALIDATION STRATEGY ──────────────────────────────
class DynamicValidation:
    # Strategy parameters (will be optimized later)
    lookback = 20                # Lookback period for swing detection
    risk_reward_ratio = 2.5      # Minimum risk-reward ratio required (e.g. 2.5:1)
    zone_buffer = 10             # Price offset buffer (in dollars) for validating zones
    risk_pct = 0.01              # Risk 1% of equity per trade

    def __init__(self, data):
        self.data = data
        self.position = None       # No open position at the start
        self.equity = 10000        # Starting equity (for position sizing calculations)
        self.init()                # Initialize indicators

    def init(self):
        # Calculate swing levels using TA‐Lib functions wrapped by self.I()
        self.demand = self.I(talib.MIN, self.data['Low'], timeperiod=self.lookback)   # Swing low = Demand Zone in uptrends
        self.supply = self.I(talib.MAX, self.data['High'], timeperiod=self.lookback)  # Swing high = Supply Zone in downtrends
        self.latest_data_length = len(self.data)
        print("🌙 [DynamicValidation] Indicators INIT – Swing Low (Demand) & Swing High (Supply) set with lookback =", 
              self.lookback, "🚀")

    def update_indicators(self):
        # Recalculate indicators if new bars have arrived
        self.demand = self.I(talib.MIN, self.data['Low'], timeperiod=self.lookback)
        self.supply = self.I(talib.MAX, self.data['High'], timeperiod=self.lookback)
        self.latest_data_length = len(self.data)
        print("🌙 [DynamicValidation] Indicators UPDATED – Data length now:", self.latest_data_length, "🚀")

    def I(self, func, series, **kwargs):
        # Wraps a TA‐Lib function ensuring input conversion to numpy array
        return func(np.array(series), **kwargs)

    def buy(self, size, sl, tp):
        # Execute a simulated BUY (LONG) order
        print(f"🚀 [Moon Dev] BUY order placed: Size = {size}, Entry = {self.data['Close'].iloc[-1]:.2f}, SL = {sl:.2f}, TP = {tp:.2f}")
        self.position = "long"

    def sell(self, size, sl, tp):
        # Execute a simulated SELL (SHORT) order
        print(f"🚀 [Moon Dev] SELL order placed: Size = {size}, Entry = {self.data['Close'].iloc[-1]:.2f}, SL = {sl:.2f}, TP = {tp:.2f}")
        self.position = "short"

    def next(self):
        # If new data has been added, update our indicators.
        if len(self.data) != self.latest_data_length:
            self.update_indicators()

        # Get current bar price and time
        current_price = self.data['Close'].iloc[-1]
        bar_time = self.data.index[-1]
        print(f"✨ [DynamicValidation] New bar @ {bar_time}: Price = {current_price:.2f}")

        # Only proceed if we have enough data for trend validation
        if len(self.data) < self.lookback:
            print("🌙 [Moon Dev] Not enough data for trend validation.")
            return

        # Determine trend by comparing current price with price 'lookback' bars ago
        previous_price = self.data['Close'].iloc[-self.lookback]
        trend = "uptrend" if current_price > previous_price else "downtrend" if current_price < previous_price else "sideways"
        print(f"🚀 [Moon Dev] Market trend determined as: {trend.upper()}")

        # Get the most recent swing levels from our TA‐Lib indicators
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
            stop_loss = current_demand - self.zone_buffer  # Place SL just below the demand zone
            take_profit = current_supply                    # TP at recent high (supply zone)
            risk = entry - stop_loss
            reward = take_profit - entry

            print(f"🚀 [Moon Dev] Evaluating LONG trade – Entry: {entry:.2f}, SL: {stop_loss:.2f}, TP: {take_profit:.2f}")
            print(f"🌙 [Moon Dev] Calculated Risk: {risk:.2f} | Reward: {reward:.2f}")

            if risk <= 0:
                print("🌙 [Moon Dev] Invalid trade setup (non-positive risk).")
                return

            if reward / risk < self.risk_reward_ratio:
                print("🌙 [Moon Dev] Risk-reward ratio below threshold. Trade not taken.")
                return

            # Calculate position size in whole units: units = floor( (equity * risk_pct) / risk )
            units = int((self.equity * self.risk_pct) / risk)
            if units < 1:
                print("🌙 [Moon Dev] Calculated position size less than 1 unit. Trade not executed.")
                return
            print(f"🌙 [Moon Dev] LONG trade position sizing: {units} units based on equity {self.equity} and risk percentage {self.risk_pct}")
            self.buy(size=units, sl=stop_loss, tp=take_profit)
            print("🚀 [Moon Dev] LONG trade executed!")
            return

        # ─── SHORT ENTRY (Downtrend: Price reenters a SUPPLY zone) ───────────────
        if trend == "downtrend" and current_price >= (current_supply - self.zone_buffer):
            entry = current_price
            stop_loss = current_supply + self.zone_buffer  # Place SL just above the supply zone
            take_profit = current_demand                     # TP at recent low (demand zone)
            risk = stop_loss - entry
            reward = entry - take_profit

            print(f"🚀 [Moon Dev] Evaluating SHORT trade – Entry: {entry:.2f}, SL: {stop_loss:.2f}, TP: {take_profit:.2f}")
            print(f"🌙 [Moon Dev] Calculated Risk: {risk:.2f} | Reward: {reward:.2f}")

            if risk <= 0:
                print("🌙 [Moon Dev] Invalid trade setup (non-positive risk).")
                return

            if reward / risk < self.risk_reward_ratio:
                print("🌙 [Moon Dev] Risk-reward ratio below threshold. Trade not taken.")
                return

            units = int((self.equity * self.risk_pct) / risk)
            if units < 1:
                print("🌙 [Moon Dev] Calculated position size less than 1 unit. Trade not executed.")
                return
            print(f"🌙 [Moon Dev] SHORT trade position sizing: {units} units based on equity {self.equity} and risk percentage {self.risk_pct}")
            self.sell(size=units, sl=stop_loss, tp=take_profit)
            print("🚀 [Moon Dev] SHORT trade executed!")
            return

        print("🌙 [Moon Dev] No valid trade conditions met on this bar.")

# ─── MAIN BACKTEST SIMULATION ──────────────────────────────
if __name__ == '__main__':
    print("🌙 [Moon Dev] Starting backtest simulation...")
    # Create dummy historical price data
    dates = pd.date_range(start="2023-01-01", periods=50, freq="D")
    np.random.seed(42)
    prices = np.cumsum(np.random.randn(50)) + 100  # Random walk starting at 100
    high = prices + np.random.rand(50) * 2          # High = price + small random premium
    low = prices - np.random.rand(50) * 2           # Low = price - small random discount
    data = pd.DataFrame({'High': high, 'Low': low, 'Close': prices}, index=dates)

    # Ensure we start with enough data for the lookback period
    initial_data = data.iloc[:20].copy()  # Using first 20 bars as initial data
    strategy = DynamicValidation(initial_data)

    # Simulate incoming bars one by one
    for i in range(20, len(data)):
        # Update strategy data to include new bars
        strategy.data = data.iloc[:i+1].copy()
        strategy.next()

    print("🌙 [Moon Dev] Backtest simulation complete!")