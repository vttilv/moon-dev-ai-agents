#!/usr/bin/env python3
"""
Moon Dev's ATR MeanReversion Strategy Backtest
This strategy uses Kelter Channels (20‐period SMA ± multiplier*STDDEV) and ATR for risk management.
It looks for when price pokes outside a Kelter Channel, then checks for a reversal candlestick pattern
(bullish engulfing for long – when price has slipped below the lower channel – or bearish engulfing for short –
when price has poked above the upper channel). A stop order is then simulated, with risk managed by ATR.
------------------------------------------------------------
"""

import os
import pandas as pd
import talib
import numpy as np

# ////////////////////////////////////////////////////////////////////////
# Data Handling Function
# ////////////////////////////////////////////////////////////////////////
def load_and_clean_data(filepath):
    print("🌙✨ Moon Dev is loading and cleaning the data... 🚀")
    data = pd.read_csv(filepath, parse_dates=['datetime'])
    # Clean column names: remove spaces and change to lower
    data.columns = data.columns.str.strip().str.lower()
    # Drop any unnamed columns
    data = data.drop(columns=[col for col in data.columns if 'unnamed' in col.lower()], errors='ignore')
    # Ensure proper column mapping (capital first letter required)
    rename_mapping = {'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close', 'volume': 'Volume', 'datetime': 'Date'}
    data = data.rename(columns=rename_mapping)
    # Set Date as the index
    data.index = pd.to_datetime(data['Date'])
    print("🌙✨ Moon Dev has finished loading the data. Number of records: {} 🚀".format(len(data)))
    return data

# ////////////////////////////////////////////////////////////////////////
# Strategy Implementation – ATR MeanReversion
# ////////////////////////////////////////////////////////////////////////
class ATRMeanReversion:
    # Strategy parameters (will be optimized later)
    kelter_period = 20
    kelter_multiplier_factor = 25  # Equals 2.5 when divided by 10.
    atr_period = 14
    risk_reward_factor = 20  # Equals 2.0 when divided by 10.
    risk_per_trade = 0.01  # 1% of equity risk per trade

    def __init__(self, data):
        self.data = data.reset_index(drop=True)  # work with integer index
        self.sma = None
        self.std = None
        self.multiplier = None
        self.kelter_upper = None
        self.kelter_lower = None
        self.atr = None
        # Trading state
        self.equity = 100000.0  # starting equity
        self.position = None   # will hold dictionary with trade details if in a trade
        self.trades = []       # record of completed trades
        self.init()

    def init(self):
        # Calculate Kelter Channels using TA-lib functions
        self.sma = talib.SMA(self.data.Close.values, timeperiod=self.kelter_period)
        self.std = talib.STDDEV(self.data.Close.values, timeperiod=self.kelter_period, nbdev=1)
        self.multiplier = self.kelter_multiplier_factor / 10.0
        self.kelter_upper = self.sma + self.multiplier * self.std
        self.kelter_lower = self.sma - self.multiplier * self.std
        self.atr = talib.ATR(self.data.High.values, self.data.Low.values, self.data.Close.values, timeperiod=self.atr_period)

        print("🌙✨ [INIT] Strategy initialized with kelter_period =", self.kelter_period,
              ", kelter_multiplier =", self.multiplier,
              ", atr_period =", self.atr_period,
              ", risk_reward_ratio =", self.risk_reward_factor / 10.0)

    def is_bullish_engulfing(self, prev, curr):
        # Bullish engulfing: previous candle is bearish, current is bullish and engulfs previous body.
        return (prev.Close < prev.Open) and \
               (curr.Close > curr.Open) and \
               (curr.Open < prev.Close) and \
               (curr.Close > prev.Open)

    def is_bearish_engulfing(self, prev, curr):
        # Bearish engulfing: previous candle is bullish, current is bearish and engulfs previous body.
        return (prev.Close > prev.Open) and \
               (curr.Close < curr.Open) and \
               (curr.Open > prev.Close) and \
               (curr.Close < prev.Open)

    def next(self, i):
        # Ensure we have at least two periods for pattern recognition
        if i < 1:
            return

        # Avoid processing if data is insufficient for indicators
        if np.isnan(self.kelter_lower[i]) or np.isnan(self.kelter_upper[i]) or np.isnan(self.atr[i]):
            return

        current = self.data.iloc[i]
        prev = self.data.iloc[i - 1]

        # If already in a position, check for exit conditions
        if self.position is not None:
            pos = self.position
            # For exit check, use the high and low of current candle
            if pos['direction'] == 'long':
                # Stop loss: if current low breaches or equals stop loss -> exit at stop loss level
                if current.Low <= pos['stop_loss']:
                    exit_price = pos['stop_loss']
                    profit = pos['units'] * (exit_price - pos['entry_price'])
                    self.equity += profit
                    pos['exit_index'] = i
                    pos['exit_price'] = exit_price
                    pos['profit'] = profit
                    self.trades.append(pos)
                    print("🌙✨ [EXIT- LONG STOP] Exited long trade at index {} with exit price {:.2f}, profit: {:.2f}".format(i, exit_price, profit))
                    self.position = None
                    return
                # Take profit: if current high goes above or equals take profit -> exit at take profit level
                elif current.High >= pos['take_profit']:
                    exit_price = pos['take_profit']
                    profit = pos['units'] * (exit_price - pos['entry_price'])
                    self.equity += profit
                    pos['exit_index'] = i
                    pos['exit_price'] = exit_price
                    pos['profit'] = profit
                    self.trades.append(pos)
                    print("🌙✨ [EXIT- LONG TP] Exited long trade at index {} with exit price {:.2f}, profit: {:.2f}".format(i, exit_price, profit))
                    self.position = None
                    return
            elif pos['direction'] == 'short':
                # For a short position, stop loss if current high breaches stop loss.
                if current.High >= pos['stop_loss']:
                    exit_price = pos['stop_loss']
                    profit = pos['units'] * (pos['entry_price'] - exit_price)
                    self.equity += profit
                    pos['exit_index'] = i
                    pos['exit_price'] = exit_price
                    pos['profit'] = profit
                    self.trades.append(pos)
                    print("🌙✨ [EXIT- SHORT STOP] Exited short trade at index {} with exit price {:.2f}, profit: {:.2f}".format(i, exit_price, profit))
                    self.position = None
                    return
                # Take profit: if current low goes below take profit -> exit at take profit level.
                elif current.Low <= pos['take_profit']:
                    exit_price = pos['take_profit']
                    profit = pos['units'] * (pos['entry_price'] - exit_price)
                    self.equity += profit
                    pos['exit_index'] = i
                    pos['exit_price'] = exit_price
                    pos['profit'] = profit
                    self.trades.append(pos)
                    print("🌙✨ [EXIT- SHORT TP] Exited short trade at index {} with exit price {:.2f}, profit: {:.2f}".format(i, exit_price, profit))
                    self.position = None
                    return
            # If still in position, do nothing further this candle.
            return

        # If not in a position, check for entry signals
        # LONG signal: price poked below lower channel and bullish engulfing pattern
        if (current.Low < self.kelter_lower[i]) and self.is_bullish_engulfing(prev, current):
            # Entry conditions met for long trade.
            entry_price = current.Close  # using current close as entry
            # Stop loss at the reversal candle's low (current candle low)
            stop_loss = current.Low
            risk_per_unit = entry_price - stop_loss
            if risk_per_unit <= 0:
                # Avoid division by zero or negative risk
                return
            # Calculate position size (use half of normal position size)
            # Using unit-based sizing: integer number of units; ensure rounding to whole number.
            raw_units = (self.equity * self.risk_per_trade / risk_per_unit) * 0.5
            units = int(max(1, round(raw_units)))
            # Take profit: risk_reward_factor/10 times the risk
            take_profit = entry_price + (risk_per_unit * (self.risk_reward_factor / 10.0))
            # Initiate long position
            self.position = {
                'direction': 'long',
                'entry_index': i,
                'entry_price': entry_price,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'units': units
            }
            print("🌙✨ [ENTRY- LONG] At index {} - entry price: {:.2f}, stop_loss: {:.2f}, take_profit: {:.2f}, units: {}".format(
                i, entry_price, stop_loss, take_profit, units))
            return

        # SHORT signal: price poked above upper channel and bearish engulfing pattern
        if (current.High > self.kelter_upper[i]) and self.is_bearish_engulfing(prev, current):
            entry_price = current.Close  # using current close as entry
            # Stop loss at the reversal candle's high (current candle high)
            stop_loss = current.High
            risk_per_unit = stop_loss - entry_price
            if risk_per_unit <= 0:
                return
            raw_units = (self.equity * self.risk_per_trade / risk_per_unit) * 0.5
            units = int(max(1, round(raw_units)))
            take_profit = entry_price - (risk_per_unit * (self.risk_reward_factor / 10.0))
            self.position = {
                'direction': 'short',
                'entry_index': i,
                'entry_price': entry_price,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'units': units
            }
            print("🌙✨ [ENTRY- SHORT] At index {} - entry price: {:.2f}, stop_loss: {:.2f}, take_profit: {:.2f}, units: {}".format(
                i, entry_price, stop_loss, take_profit, units))
            return

    def run_backtest(self):
        print("🌙✨ Moon Dev is starting the backtest... 🚀")
        n = len(self.data)
        i = 0
        while i < n:
            self.next(i)
            i += 1
        
        # Calculate additional statistics
        initial_equity = 100000.0
        final_equity = self.equity
        total_return = ((final_equity - initial_equity) / initial_equity) * 100
        
        # Calculate max drawdown
        peak = initial_equity
        max_drawdown = 0
        running_equity = initial_equity
        
        for trade in self.trades:
            running_equity += trade['profit']
            if running_equity > peak:
                peak = running_equity
            drawdown = (peak - running_equity) / peak * 100
            if drawdown > max_drawdown:
                max_drawdown = drawdown
        
        # Calculate win rate and profit metrics
        wins = [t for t in self.trades if t['profit'] > 0]
        losses = [t for t in self.trades if t['profit'] <= 0]
        win_rate = len(wins) / len(self.trades) * 100 if self.trades else 0
        
        avg_win = sum(t['profit'] for t in wins) / len(wins) if wins else 0
        avg_loss = sum(t['profit'] for t in losses) / len(losses) if losses else 0
        profit_factor = abs(sum(t['profit'] for t in wins) / sum(t['profit'] for t in losses)) if losses else float('inf')
        
        print("\n🌙✨ === Moon Dev's Backtest Results === 🚀")
        print(f"🌙✨ Initial Equity: ${initial_equity:,.2f}")
        print(f"🌙✨ Final Equity: ${final_equity:,.2f}")
        print(f"🌙✨ Total Return: {total_return:.2f}%")
        print(f"🌙✨ Maximum Drawdown: {max_drawdown:.2f}%")
        print(f"🌙✨ Total Trades: {len(self.trades)}")
        print(f"🌙✨ Win Rate: {win_rate:.2f}%")
        print(f"🌙✨ Average Win: ${avg_win:.2f}")
        print(f"🌙✨ Average Loss: ${avg_loss:.2f}")
        print(f"🌙✨ Profit Factor: {profit_factor:.2f}")
        print(f"🌙✨ Winning Trades: {len(wins)}")
        print(f"🌙✨ Losing Trades: {len(losses)}")
        print("🌙✨ === End of Backtest Results === 🚀")

# ////////////////////////////////////////////////////////////////////////
# Main Execution
# ////////////////////////////////////////////////////////////////////////
if __name__ == "__main__":
    # Replace 'your_data.csv' with the path to your CSV file containing OHLCV data.
    data_filepath = "/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv"
    if not os.path.exists(data_filepath):
        print("🌙✨ [ERROR] Data file '{}' does not exist. Exiting.".format(data_filepath))
        exit(1)
    data = load_and_clean_data(data_filepath)
    strategy = ATRMeanReversion(data)
    strategy.run_backtest()
    print("🌙✨ Moon Dev has finished execution. Happy Trading! 🚀")
    
# End of backtest code.