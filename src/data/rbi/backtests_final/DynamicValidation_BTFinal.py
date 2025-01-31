#!/usr/bin/env python3
"""
Moon Dev's Backtest AI 🌙 – DynamicValidation Strategy Backtest Implementation

This strategy – DynamicValidation – focuses on market structure,
supply & demand zones and strict risk–reward management. It uses TA‐Lib
calculations (wrapped in self.I()) for indicators like SMA and swing highs/lows.
It enters long trades in an uptrend when price re‐enters a demand zone
(with stop loss right below the zone and take profit at a recent high),
and enters short trades in a downtrend when price re‐enters a supply zone
(with stop loss just above the zone and take profit at a recent low).
Trades are executed only if the risk:reward is above the defined minimum.

Plenty of Moon Dev themed debug prints included for easier troubleshooting! 🌙✨🚀
"""

# ─── ALL NECESSARY IMPORTS ─────────────────────────────────────────────
import os
import pandas as pd
import numpy as np
import talib
from backtesting import Backtest, Strategy

# ─── STRATEGY CLASS DEFINITION WITH INDICATORS, ENTRY/EXIT LOGIC & RISK MANAGEMENT ─────────────────────────
class DynamicValidation(Strategy):
    """
    DynamicValidation Strategy

    Class Attributes for optimization:
      • risk_reward_min : Minimum acceptable risk/reward ratio (default 2.5)
      • zone_buffer_bp  : Stop-loss offset in basis points (default 2 bp → 0.002)
      • zone_tolerance_bp : Tolerance for re-entry into the zone in basis points (default 2 bp)
      • risk_percent    : Risk percentage per trade (as an integer percentage; default 1%)
      • ma_period       : Moving Average period for trend determination (default 50)
      • pivot_period    : Lookback period to compute swing highs/lows as zones (default 20)
    """
    risk_reward_min = 2.5       # Must be >=2.5 (non-negotiable risk/reward threshold)
    zone_buffer_bp = 2          # Basis points for stop-loss buffer (e.g., 2 bp -> 0.002)
    zone_tolerance_bp = 2       # Basis points for acceptable zone re-entry (e.g., 2 bp)
    risk_percent = 1            # Risk 1% of equity per trade (as a whole percent)
    ma_period = 50              # Period for trend indicator (SMA)
    pivot_period = 20           # Lookback period for computing swing highs/lows as zones

    def init(self):
        # Indicators: Use self.I() wrapper with TA-Lib functions!
        self.sma = self.I(talib.SMA, self.data.Close, timeperiod=self.ma_period)
        self.pivot_high = self.I(talib.MAX, self.data.High, timeperiod=self.pivot_period)
        self.pivot_low = self.I(talib.MIN, self.data.Low, timeperiod=self.pivot_period)

        print("🌙✨ [INIT] DynamicValidation initialized with parameters:")
        print(f"    MA Period: {self.ma_period}, Pivot Period: {self.pivot_period}")
        print(f"    Risk Reward Min: {self.risk_reward_min}")
        print(f"    Zone Buffer (bp): {self.zone_buffer_bp}, Zone Tolerance (bp): {self.zone_tolerance_bp}")
        print(f"    Risk Percent per trade: {self.risk_percent}% 🚀")

    def next(self):
        # Convert basis point parameters to float values
        zone_buffer = self.zone_buffer_bp / 1000.0
        zone_tolerance = self.zone_tolerance_bp / 1000.0

        price = self.data.Close[-1]
        sma_value = self.sma[-1]

        # Determine market trend based on SMA
        if price > sma_value:
            trend = 'up'
        elif price < sma_value:
            trend = 'down'
        else:
            trend = 'neutral'

        print(f"🌙✨ [NEXT] Price: {price:.4f}, SMA: {sma_value:.4f}, Trend: {trend}")

        # Do not open new trades if already in a position
        if self.position:
            print("🌙 No new trade: Position already open.")
            return

        # For an uptrend, look for a long entry when price re-enters the demand zone
        if trend == 'up':
            demand_zone = self.pivot_low[-1]
            print(f"🌙 Demand Zone (Pivot Low): {demand_zone:.4f}")
            # Check if price is within the acceptable tolerance of the demand zone
            if abs(price - demand_zone) <= zone_tolerance:
                # Set stop loss just below the demand zone and take profit at recent high
                stop_loss = demand_zone - zone_buffer
                take_profit = self.pivot_high[-1]
                risk = price - stop_loss
                reward = take_profit - price
                print(f"🌙 Long Trade Check: SL={stop_loss:.4f}, TP={take_profit:.4f}, Risk={risk:.4f}, Reward={reward:.4f}")
                if risk > 0 and (reward / risk) >= self.risk_reward_min:
                    print("🌙 Trade Signal: BUY")
                    self.buy(sl=stop_loss, tp=take_profit)
                    return
                else:
                    print("🌙 Long trade risk/reward ratio insufficient.")

        # For a downtrend, look for a short entry when price re-enters the supply zone
        if trend == 'down':
            supply_zone = self.pivot_high[-1]
            print(f"🌙 Supply Zone (Pivot High): {supply_zone:.4f}")
            if abs(price - supply_zone) <= zone_tolerance:
                # Set stop loss just above the supply zone and take profit at recent low
                stop_loss = supply_zone + zone_buffer
                take_profit = self.pivot_low[-1]
                risk = stop_loss - price
                reward = price - take_profit
                print(f"🌙 Short Trade Check: SL={stop_loss:.4f}, TP={take_profit:.4f}, Risk={risk:.4f}, Reward={reward:.4f}")
                if risk > 0 and (reward / risk) >= self.risk_reward_min:
                    print("🌙 Trade Signal: SELL")
                    self.sell(sl=stop_loss, tp=take_profit)
                    return
                else:
                    print("🌙 Short trade risk/reward ratio insufficient.")

        print("🌙✨ [NEXT] No trade triggered this period.")


# ─── BACKTEST EXECUTION ─────────────────────────────────────────────
if __name__ == "__main__":
    # For demonstration purposes, we create a sample dataset.
    # In a real scenario, load your historical data file (e.g., CSV) with OHLC data.
    rng = pd.date_range(start="2021-01-01", periods=100, freq="D")
    np.random.seed(42)
    data = pd.DataFrame(index=rng)
    
    # Create a random walk for the Close prices
    data["Close"] = 100 + np.random.randn(100).cumsum()
    # Generate High and Low prices around the Close
    data["High"] = data["Close"] + np.random.rand(100) * 2
    data["Low"] = data["Close"] - np.random.rand(100) * 2
    data["Open"] = data["Close"]  # For simplicity, set Open equal to Close

    # Initialize and run the backtest
    bt = Backtest(data, DynamicValidation, cash=10000, commission=0.002)
    stats = bt.run()
    print("\nBacktest Results:")
    print(stats)
    bt.plot()