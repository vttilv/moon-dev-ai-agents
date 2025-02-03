#!/usr/bin/env python3
"""
Moon Dev Debug AI 🌙 - Debugged Backtest Code
Fixes:
 • Imported missing modules (e.g. datetime.time)
 • Added a dummy Strategy base class to simulate the backtesting engine.
 • Ensured position sizing is by fraction (0 < size < 1) per CRITICAL BACKTESTING REQUIREMENTS.
 • Used price levels (not distances) for stop loss and take profit.
 • Corrected syntax issues and debug print formatting.
Note: The strategy logic is kept intact.
"""

import os
import pandas as pd
import talib
import numpy as np
from datetime import time
# math not used, but available if needed

print("🌙 Moon Dev Debug AI 🌙 - Starting backtest script debugging!")

# ─── DATA HANDLING ───────────────────────────────────────────────
data_path = "/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv"
print("🌙 Loading data from:", data_path)
data = pd.read_csv(data_path, parse_dates=["datetime"])

# Clean column names: remove spaces, lowercase, drop unnamed columns
data.columns = data.columns.str.strip().str.lower()
data = data.drop(columns=[col for col in data.columns if 'unnamed' in col.lower()])

# Rename required columns: Open, High, Low, Close, Volume
rename_map = {"open": "Open", "high": "High", "low": "Low", "close": "Close", "volume": "Volume"}
data = data.rename(columns=rename_map)

# Optionally set the datetime column as the index
if 'datetime' in data.columns:
    data.index = data["datetime"]

print("🌙 Data columns after cleaning and renaming:", list(data.columns))

# ─── Dummy Backtesting Engine (Base Strategy) ─────────────────────
class Strategy:
    def __init__(self, data):
        self.data = data
        self.position = None
        self.initial_equity = 10000
        self.equity = self.initial_equity
        self.trades = []
        self.max_equity = self.initial_equity
        self.min_equity = self.initial_equity
        self.init()

    def init(self):
        pass

    def next(self):
        pass

    def update_equity_stats(self):
        self.max_equity = max(self.max_equity, self.equity)
        self.min_equity = min(self.min_equity, self.equity)

# ─── STRATEGY IMPLEMENTATION ──────────────────────────────────────
class AccumulationManipulation(Strategy):
    # PARAMETERS (unchanged)
    risk_reward = 2.0  
    accumulation_factor = 1.5  
    risk_percentage = 0.01  # Using fraction of current equity to risk per trade (0 < size < 1)

    def init(self):
        # Calculate the "daily bias" using 1H SMA (4 x 15m candles)
        self.daily_bias = talib.SMA(self.data.Close.values, timeperiod=4)
        print("🌙 [INIT] Daily bias (1H SMA) indicator set using TA‑Lib!")
    
    def next(self):
        i = len(self.data) - 1  # Current candle index

        # Need at least 4 candles (for accumulation window and bias comparison)
        if i < 3:
            return

        # ─── TIME WINDOW CHECK ─────────────────────────────
        # Only trade between 10:00 and 11:30 Eastern Standard Time.
        current_time = self.data.index[-1].time()
        if not (current_time >= time(10, 0) and current_time <= time(11, 30)):
            print(f"🌙 [TimeGate] Skipping candle at {current_time} (outside 10:00-11:30 EST)")
            return

        # ─── IDENTIFY ACCUMULATION ─────────────────────────
        # Define the accumulation range using the last three candles.
        accumulation_high = np.max(self.data.High[-3:])
        accumulation_low = np.min(self.data.Low[-3:])
        accumulation_range = accumulation_high - accumulation_low
        print(f"🌙 [Accumulation] High: {accumulation_high}, Low: {accumulation_low}, Range: {accumulation_range}")

        # ─── ENTRY CONDITIONS ─────────────────────────────
        # Check if there is already an open position
        if self.position is None:
            current_close = self.data.Close[-1]
            # LONG CONDITION:
            # If price closes above the accumulation range and the daily bias is up (or steady)
            if current_close > accumulation_high and self.daily_bias[i] >= self.daily_bias[i-1]:
                entry_price = current_close
                stop_loss = accumulation_low  # Stop loss at low of accumulation
                risk = entry_price - stop_loss
                take_profit = entry_price + risk * self.risk_reward
                # Use risk_percentage as fraction-based sizing.
                size = self.risk_percentage
                self.position = {
                    'type': 'long',
                    'entry': entry_price,
                    'stop': stop_loss,
                    'tp': take_profit,
                    'size': size
                }
                print(f"🌙 [ENTRY] LONG at {entry_price} | SL: {stop_loss} | TP: {take_profit} | Size: {size}")
            # SHORT CONDITION:
            # If price closes below the accumulation range and the daily bias is down (or steady)
            elif current_close < accumulation_low and self.daily_bias[i] <= self.daily_bias[i-1]:
                entry_price = current_close
                stop_loss = accumulation_high  # Stop loss at high of accumulation
                risk = stop_loss - entry_price
                take_profit = entry_price - risk * self.risk_reward
                size = self.risk_percentage
                self.position = {
                    'type': 'short',
                    'entry': entry_price,
                    'stop': stop_loss,
                    'tp': take_profit,
                    'size': size
                }
                print(f"🌙 [ENTRY] SHORT at {entry_price} | SL: {stop_loss} | TP: {take_profit} | Size: {size}")
            else:
                print("🌙 [Signal] No breakout signal detected.")
        else:
            # ─── POSITION MANAGEMENT ─────────────────────────
            # If a position is open, check for exit conditions based on stop loss or take profit
            current_price = self.data.Close[-1]
            pos = self.position
            if pos['type'] == 'long':
                if current_price <= pos['stop']:
                    print(f"🌙 [EXIT] LONG stop loss triggered at {current_price} (SL: {pos['stop']})")
                    self.close_position(current_price)
                elif current_price >= pos['tp']:
                    print(f"🌙 [EXIT] LONG take profit reached at {current_price} (TP: {pos['tp']})")
                    self.close_position(current_price)
            elif pos['type'] == 'short':
                if current_price >= pos['stop']:
                    print(f"🌙 [EXIT] SHORT stop loss triggered at {current_price} (SL: {pos['stop']})")
                    self.close_position(current_price)
                elif current_price <= pos['tp']:
                    print(f"🌙 [EXIT] SHORT take profit reached at {current_price} (TP: {pos['tp']})")
                    self.close_position(current_price)
    
    def close_position(self, exit_price):
        pos = self.position
        trade_details = {
            'type': pos['type'],
            'entry': pos['entry'],
            'exit': exit_price,
            'size': pos['size']
        }
        self.trades.append(trade_details)
        
        if pos['type'] == 'long':
            profit = (exit_price - pos['entry']) * pos['size'] * self.equity
        else:
            profit = (pos['entry'] - exit_price) * pos['size'] * self.equity
            
        self.equity += profit
        self.update_equity_stats()
        print(f"🌙 [CLOSE] {pos['type'].upper()} closed at {exit_price} with profit: {profit:.2f} | New equity: {self.equity:.2f}")
        self.position = None

# ─── BACKTEST SIMULATION ─────────────────────────────────────────
print("🌙 Starting backtest simulation...")

# Instantiate the strategy with the full dataset.
strategy = AccumulationManipulation(data)

# Simulate the backtest, iterating over each candle (starting after enough data is available)
for idx in range(4, len(data)):
    # Update the strategy data slice to simulate live updating candles
    strategy.data = data.iloc[:idx+1]
    strategy.next()

print("🌙 Backtest simulation completed!")
print("🌙 Trades executed:")
for trade in strategy.trades:
    print("🌙", trade)
print("🌙 Final Equity:", strategy.equity)

def main():
    # Initialize statistics
    stats = {
        'total_trades': 0,
        'winning_trades': 0,
        'initial_equity': 10000,
        'final_equity': 10000,
        'max_equity': 10000,
        'min_equity': 10000,
        'returns': [],
    }
    
    # ... your existing code ...
    
    # At the end of your backtest:
    print("\n🌙 ===== Moon Dev's Backtest Results =====")
    print(f"�� Total Trades: {len(strategy.trades)}")
    winning_trades = sum(1 for t in strategy.trades if 
        (t['type'] == 'long' and t['exit'] > t['entry']) or 
        (t['type'] == 'short' and t['exit'] < t['entry']))
    print(f"💫 Win Rate: {(winning_trades/len(strategy.trades)*100 if strategy.trades else 0):.2f}%")
    print(f"💰 Return: {((strategy.equity/strategy.initial_equity-1)*100):.2f}%")
    print(f"📉 Max Drawdown: {((1 - strategy.min_equity/strategy.max_equity)*100):.2f}%")
    print(f"�� Initial Equity: ${strategy.initial_equity}")
    print(f"🌟 Final Equity: ${strategy.equity:.2f}")
    print("🌙 ================================")
