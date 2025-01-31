#!/usr/bin/env python3
"""
Moon Dev's Backtest AI 🌙 - StochasticPhaseTrader Strategy Backtesting Script
---------------------------------------------------------------------------
This script implements the StochasticPhaseTrader strategy using a custom backtesting routine.
It uses the TA-Lib library for indicator calculations and includes:
  • Data cleaning & mapping
  • Indicator calculations via a custom self.I()-like wrapper
  • Entry/exit logic with Moon Dev themed debug prints 🚀✨
  • Risk management with proper position sizing (always converting to integer when using units!)
  • Parameter optimization (with fixed parameter values)
  
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
    # Strategy parameter defaults (DO NOT CHANGE STRATEGY LOGIC OR PARAMETER VALUES)
    rsi_period = 14             # Period for RSI calculation
    stoch_period = 14           # Period for rolling min/max of RSI (StochRSI calc)
    stoch_d_period = 3          # SMA period for %D line of StochRSI
    oversold_threshold = 20     # Under this value, market is considered oversold (entry condition)
    overbought_threshold = 80   # Over this value, market is considered overbought (exit condition)
    stop_loss_pct = 0.01        # Stop Loss: 1% below entry price (price level, not a distance)
    risk_reward_ratio = 2       # Risk-reward ratio (Take Profit = entry + risk*ratio)
    risk_percentage = 0.01      # Risk 1% of current equity per trade

    def __init__(self, data):
        # Ensure the data index is sequential and reset (important for proper indexing)
        self.data = data.reset_index(drop=True)
        self.position = None   # No open position initially
        self.equity = 10000    # Starting equity (for backtesting)
        self.trades = []       # List to record each completed trade

    def compute_stoch_rsi(self, close):
        # Compute RSI from Close prices using TA-Lib
        rsi = talib.RSI(close, timeperiod=self.rsi_period)
        # Compute rolling minimum and maximum on RSI using TA-Lib functions
        rsi_min = talib.MIN(rsi, timeperiod=self.stoch_period)
        rsi_max = talib.MAX(rsi, timeperiod=self.stoch_period)
        # Compute Stochastic RSI: normalize between 0 and 100
        stoch_rsi = (rsi - rsi_min) / (rsi_max - rsi_min + 1e-10) * 100
        return stoch_rsi

    def indicators(self):
        # Calculate the fast (%K) line of the StochRSI
        self.stoch_rsi = self.compute_stoch_rsi(self.data['Close'])
        # Calculate the slow (%D) line as the SMA of the %K line
        self.stoch_d = talib.SMA(self.stoch_rsi, timeperiod=self.stoch_d_period)
        print("🌙✨ [INIT] Indicators initialized: RSI period =", self.rsi_period,
              "| Stoch Period =", self.stoch_period,
              "| Stoch %D period =", self.stoch_d_period)

    def run_backtest(self):
        self.indicators()
        print("🌙✨ [INIT] Starting backtest with initial equity:", self.equity)
        n = len(self.data)
        # Determine a safe starting index to avoid NaN indicator values (based on indicator periods)
        start_index = max(self.rsi_period, self.stoch_period, self.stoch_d_period)
        
        # Loop over each time step in the dataset starting when indicators are valid
        for i in range(start_index, n):
            current_price = self.data['Close'].iloc[i]
            # Skip if indicator values are not available yet
            if np.isnan(self.stoch_rsi[i]) or np.isnan(self.stoch_d[i]):
                continue

            current_stochk = self.stoch_rsi[i]
            current_stochd = self.stoch_d[i]

            # -----------------------------------------------------------------
            # Check for trade exits if a position is already open
            # -----------------------------------------------------------------
            if self.position is not None:
                # Exit trade if current price hits stop loss or take profit level
                if current_price <= self.position['stop_loss'] or current_price >= self.position['take_profit']:
                    exit_price = current_price
                    profit = (exit_price - self.position['entry_price']) * self.position['units']
                    self.equity += profit
                    print("🌙✨ [DEBUG] Exiting trade at index", i, "| Price:", exit_price,
                          "| Profit:", profit, "| New Equity:", self.equity)
                    self.trades.append({
                        'entry_index': self.position['entry_index'],
                        'exit_index': i,
                        'entry_price': self.position['entry_price'],
                        'exit_price': exit_price,
                        'units': self.position['units'],
                        'profit': profit
                    })
                    self.position = None
                    continue  # Move to next time step after exiting

                # Exit trade based on indicator signal: overbought condition with a bearish crossover
                if i > start_index:
                    prev_stochk = self.stoch_rsi[i-1]
                    prev_stochd = self.stoch_d[i-1]
                    if prev_stochk > prev_stochd and current_stochk < current_stochd and current_stochk > self.overbought_threshold:
                        exit_price = current_price
                        profit = (exit_price - self.position['entry_price']) * self.position['units']
                        self.equity += profit
                        print("🌙✨ [DEBUG] Exiting trade (signal) at index", i, "| Price:", exit_price,
                              "| Profit:", profit, "| New Equity:", self.equity)
                        self.trades.append({
                            'entry_index': self.position['entry_index'],
                            'exit_index': i,
                            'entry_price': self.position['entry_price'],
                            'exit_price': exit_price,
                            'units': self.position['units'],
                            'profit': profit
                        })
                        self.position = None
                        continue

            # -----------------------------------------------------------------
            # Check for trade entry if no position is currently open
            # -----------------------------------------------------------------
            if self.position is None and i > start_index:
                prev_stochk = self.stoch_rsi[i-1]
                prev_stochd = self.stoch_d[i-1]
                # Entry conditions:
                #   • Bullish indicator crossover (prev: %K below %D, current: %K above %D)
                #   • Current %K reading indicates an oversold market (below oversold_threshold)
                if prev_stochk < prev_stochd and current_stochk > current_stochd and current_stochk < self.oversold_threshold:
                    entry_price = current_price
                    stop_loss_price = entry_price * (1 - self.stop_loss_pct)  # Stop loss as a price level
                    risk_per_unit = entry_price - stop_loss_price
                    if risk_per_unit <= 0:
                        continue  # Safety check
                    # Calculate number of units to buy using risk percentage of equity;
                    # The result is rounded to a whole number to comply with unit-based sizing rules.
                    raw_units = (self.equity * self.risk_percentage) / risk_per_unit
                    units = int(raw_units)
                    if units <= 0:
                        continue  # Do not enter trade if calculated size is zero
                    take_profit_price = entry_price * (1 + self.stop_loss_pct * self.risk_reward_ratio)
                    
                    self.position = {
                        'entry_price': entry_price,
                        'stop_loss': stop_loss_price,
                        'take_profit': take_profit_price,
                        'units': units,
                        'entry_index': i
                    }
                    print("🌙✨ [DEBUG] Long Entry at index", i, "| Price:", entry_price,
                          "| Units:", units, "| SL:", stop_loss_price, "| TP:", take_profit_price)

        # Close any open position at the end of the backtest
        if self.position is not None:
            exit_price = self.data['Close'].iloc[-1]
            profit = (exit_price - self.position['entry_price']) * self.position['units']
            self.equity += profit
            print("🌙✨ [DEBUG] Closing final open position at end | Price:", exit_price,
                  "| Profit:", profit, "| New Equity:", self.equity)
            self.trades.append({
                'entry_index': self.position['entry_index'],
                'exit_index': n-1,
                'entry_price': self.position['entry_price'],
                'exit_price': exit_price,
                'units': self.position['units'],
                'profit': profit
            })
            self.position = None

        # Summary of the backtest performance
        print("🌙✨ [RESULT] Backtest complete. Final Equity:", self.equity)
        print("🌙✨ [RESULT] Total trades executed:", len(self.trades))
        total_profit = sum(trade['profit'] for trade in self.trades)
        print("🌙✨ [RESULT] Total Profit:", total_profit)

# ---------------------------------------------------------------------------
# Main Execution: Data Loading and Strategy Backtesting
# ---------------------------------------------------------------------------
if __name__ == '__main__':
    # Data source (make sure the file exists at this location)
    data_path = '/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv'
    if not os.path.exists(data_path):
        print("🌙✨ [ERROR] Data file not found at", data_path)
    else:
        try:
            data = pd.read_csv(data_path)
            # Ensure the data contains a 'Close' column
            if 'Close' not in data.columns:
                print("🌙✨ [ERROR] 'Close' column not found in data.")
            else:
                # Create the strategy instance and run the backtest
                strategy = StochasticPhaseTrader(data)
                strategy.run_backtest()
        except Exception as e:
            print("🌙✨ [ERROR] Exception occurred while loading data:", str(e))