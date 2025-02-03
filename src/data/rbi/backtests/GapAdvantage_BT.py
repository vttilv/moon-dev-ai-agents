#!/usr/bin/env python3
"""
Moon Dev's Backtest AI 🌙 🚀

Backtesting implementation for the GapAdvantage strategy.
This strategy focuses on capturing a sliver of a large move after a gap/breakout.
Please ensure you have installed the required packages:
    pip install backtesting pandas numpy TA-Lib pandas_ta
"""

import os
import numpy as np
import pandas as pd
import talib
import pandas_ta as pta  # may be used in helper functions if needed
from backtesting import Backtest, Strategy

# ─── UTILITY FUNCTIONS FOR INDICATORS ────────────────────────────────────────────
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
class GapAdvantage(Strategy):
    # Optimization parameters
    fast_ma_period = 9          # Moving average period for entry signal (default 9)
    slow_ma_period = 20         # Moving average period for trend (default 20)
    risk_reward_ratio = 1       # risk-reward ratio; must be at least 1 (default 1)
    
    # Fixed risk percentage per trade (percentage of equity to risk)
    risk_pct = 0.01             # 1% risk per trade

    def init(self):
        # Debug print: initialize indicators 🌙✨
        print("🌙 [MoonDev Debug] Initializing GapAdvantage Strategy indicators...")

        # Calculate the fast and slow moving averages using TA-Lib's SMA.
        self.fast_ma = self.I(talib.SMA, self.data.Close, timeperiod=self.fast_ma_period)
        self.slow_ma = self.I(talib.SMA, self.data.Close, timeperiod=self.slow_ma_period)
        
        # Calculate VWAP indicator using our custom function.
        self.vwap = self.I(VWAP, self.data.High, self.data.Low, self.data.Close, self.data.Volume)
        
        # For a recent swing high used for entry check, we use a 5-period highest high.
        self.recent_high = self.I(talib.MAX, self.data.High, timeperiod=5)
        
        # Store entry order details for risk management.
        self.entry_price = None
        self.current_stop = None
        self.trailing_stop = None

        print("🚀 [MoonDev Debug] Indicators loaded: fast MA (period={}), slow MA (period={}), VWAP.".format(
            self.fast_ma_period, self.slow_ma_period))

    def next(self):
        # Get current price information
        price = self.data.Close[-1]
        high = self.data.High[-1]
        low = self.data.Low[-1]
        
        # Moon Dev themed debug prints
        print("🌙 [MoonDev] New candle: Price = {:.2f}, High = {:.2f}, Low = {:.2f}".format(price, high, low))
        
        # Check if we are not in the market and look for an entry signal.
        if not self.position:
            # Entry Condition: Price must be above fast MA and VWAP.
            # Also, check that current high exceeds the previous swing high turning point.
            if price > self.fast_ma[-1] and price > self.vwap[-1]:
                # Use the recent high indicator: if today's high is a new high compared to 1 period ago.
                if high >= self.recent_high[-2]:
                    # Debug print
                    print("🚀 [MoonDev ENTRY] Conditions met! Price {:.2f} > fast MA {:.2f} and VWAP {:.2f}.".format(
                        price, self.fast_ma[-1], self.vwap[-1]))
                    
                    # Calculate stop loss based on a fixed risk% of the entry price.
                    risk_dollar = price * self.risk_pct
                    stop_loss = price - risk_dollar
                    # Calculate position size safely: position_size = risk_amount / risk per share.
                    # Since risk per share = price - stop_loss = price * risk_pct.
                    position_size = int(round(self.equity * self.risk_pct / (price - stop_loss)))
                    
                    if position_size <= 0:
                        print("🌙 [MoonDev ERROR] Position size calculated as 0. Skipping trade.")
                    else:
                        print("🌙 [MoonDev ENTRY] Buying {} units at {:.2f} with stop loss {:.2f} (Risk: ${:.2f}).".format(
                            position_size, price, stop_loss, risk_dollar))
                        self.entry_price = price
                        self.current_stop = stop_loss
                        # Set trailing stop initially equal to stop loss.
                        self.trailing_stop = stop_loss
                        self.buy(size=position_size)
        else:
            # We are in a trade. Update trailing stop if price is moving in our favor.
            # For simplicity, our new trailing stop will be a fraction (risk_dollar) below the highest price reached.
            highest_price = max(self.data.Close[-len(self.data.Close):])
            new_trailing_stop = highest_price - (self.entry_price * self.risk_pct)
            # Only update if it moves upward.
            if new_trailing_stop > self.trailing_stop:
                self.trailing_stop = new_trailing_stop
                print("✨ [MoonDev] Trailing stop updated to {:.2f}".format(self.trailing_stop))
            
            # Check exit conditions:
            # 1. Price goes above profit target: target = entry + risk_reward_ratio * (entry * risk_pct)
            profit_target = self.entry_price + self.risk_reward_ratio * (self.entry_price * self.risk_pct)
            if high >= profit_target:
                print("🚀 [MoonDev EXIT] Profit target hit! Price reached {:.2f} (target: {:.2f}). Exiting trade.".format(
                    high, profit_target))
                self.position.close()
                self.entry_price = None
                self.current_stop = None
                self.trailing_stop = None
            # 2. Price falls below trailing stop or the initial stop loss.
            elif low <= self.trailing_stop or low <= self.current_stop:
                print("🌙 [MoonDev EXIT] Stop loss triggered! Price dropped to {:.2f} (stop: {:.2f}). Exiting trade.".format(
                    low, self.trailing_stop if low <= self.trailing_stop else self.current_stop))
                self.position.close()
                self.entry_price = None
                self.current_stop = None
                self.trailing_stop = None

# ─── DATA LOADING AND CLEANING ────────────────────────────────────────────────────
data_path = "/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv"
print("🌙 [MoonDev] Loading data from {} ...".format(data_path))
data = pd.read_csv(data_path)

# Clean column names: remove spaces and set proper case.
data.columns = data.columns.str.strip().str.lower()  # lower case for cleaning
data = data.drop(columns=[col for col in data.columns if 'unnamed' in col.lower()])

# Map cleaned columns to expected Backtesting column names with capitalized first letters.
column_mapping = {'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close', 'volume': 'Volume'}
data = data.rename(columns=column_mapping)

# If datetime is present, convert (if needed) and set as index.
if "datetime" in data.columns:
    data["Datetime"] = pd.to_datetime(data["datetime"])
    data = data.sort_values("Datetime")
    data.set_index("Datetime", inplace=True)

print("🚀 [MoonDev] Data loaded and cleaned. Columns: {}".format(list(data.columns)))

# ─── INITIAL BACKTEST EXECUTION ────────────────────────────────────────────────────
# Set initial cash to 1,000,000 as instructed.
initial_cash = 1000000

print("🌙 [MoonDev] Running initial backtest for GapAdvantage with default parameters...")

bt = Backtest(data, GapAdvantage, cash=initial_cash, commission=.000, exclusive_orders=True)
stats = bt.run()
print("🚀 [MoonDev] Initial Backtest Stats:")
print(stats)
print("🌙 [MoonDev] Strategy details:")
print(stats._strategy)

# Save initial performance chart to charts directory.
strategy_name = "GapAdvantage"
chart_dir = "/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/charts"
if not os.path.exists(chart_dir):
    os.makedirs(chart_dir)
chart_file = os.path.join(chart_dir, f"{strategy_name}_chart.html")
print("✨ [MoonDev] Saving initial performance chart to {}...".format(chart_file))
bt.plot(filename=chart_file, open_browser=False)

# ─── OPTIMIZATION ───────────────────────────────────────────────────────────────────
print("🌙 [MoonDev] Starting parameter optimization for GapAdvantage strategy...")

# Optimize parameters:
# fast_ma_period: range(7, 12, 1)
# slow_ma_period: range(18, 23, 1)
# risk_reward_ratio: using integer values [1, 2, 3]
optimized_stats = bt.optimize(
    fast_ma_period=range(7, 12, 1),
    slow_ma_period=range(18, 23, 1),
    risk_reward_ratio=[1, 2, 3],
    maximize='Equity Final [$]',
    constraint=lambda param: param.fast_ma_period < param.slow_ma_period  # fast MA must be below slow MA period
)

print("🚀 [MoonDev] Optimization complete!")
print("🌙 [MoonDev] Optimized Stats:")
print(optimized_stats)
print("✨ [MoonDev] Optimized Strategy Details:")
print(optimized_stats._strategy)

# Save optimized performance chart to charts directory.
chart_file_optimized = os.path.join(chart_dir, f"{strategy_name}_optimized_chart.html")
print("🌙 [MoonDev] Saving optimized performance chart to {} ...".format(chart_file_optimized))
bt.plot(filename=chart_file_optimized, open_browser=False)

print("🚀 [MoonDev] Backtest and optimization complete! Happy Trading! 🌙✨")
