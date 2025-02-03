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
    risk_reward_ratio = 1       # Risk-reward ratio; must be at least 1 (default 1)
    
    # Fixed risk percentage per trade (percentage of equity to risk)
    risk_pct = 0.01             # 1% risk per trade

    def __init__(self, data):
        self.data = data.copy().reset_index(drop=True)
        self.trades = []  # Add this line to store trades
        self.equity = 10000  # Add this line to track equity
        self.fast_ma = None
        self.slow_ma = None
        self.vwap = None
        self.recent_high = None
        self.entry_price = None
        self.current_stop = None
        self.take_profit = None

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

    def should_enter_position(self, idx):
        """
        Determine if a new position should be entered based on the current candle.

        The logic (unmodified) checks if the current close is a new high relative to the past few periods.
        """
        if idx < 5:
            return False  # Not enough data
        
        price = self.data.Close.iloc[idx]
        high = self.data.High.iloc[idx]
        low = self.data.Low.iloc[idx]
        # Moon Dev themed debug print for the new candle
        print("🌙 [MoonDev] New candle: Price = {:.2f}, High = {:.2f}, Low = {:.2f}".format(
            price, high, low))

        # Entry signal: if the current price makes a new high versus the previous 5 candles.
        recent_period_high = self.data.High.iloc[idx-5:idx].max()
        if price > recent_period_high:
            return True
        return False

    def backtest(self, initial_equity=10000):
        """
        A simple backtesting loop that iterates over the provided data.
        It enters a trade when the current candle's close is higher than the maximum high of the previous 5 candles.
        The stop loss is set at the lowest low of the previous 5 candles.
        The take profit is derived from the risk-reward ratio.
        Position sizing is calculated based on a fixed risk percentage of equity (risk_pct)
        and rounded to an integer number of units.
        """
        self.equity = initial_equity
        trade_open = False
        position_units = 0
        entry_price = None
        trade_entry_idx = None

        print("🌙 [MoonDev Debug] Starting backtest with initial equity: {:.2f}".format(self.equity))
        # Loop through each candle, starting from index 5 to ensure indicator availability.
        for i in range(5, len(self.data)):
            if not trade_open:
                if self.should_enter_position(i):
                    # Entry conditions met
                    entry_price = self.data.Close.iloc[i]
                    trade_entry_idx = i
                    self.entry_price = entry_price
                    # Define stop loss as the lowest low in the previous 5 periods.
                    current_stop = self.data.Low.iloc[i-5:i].min()
                    self.current_stop = current_stop
                    # Define take profit as entry_price plus risk_reward_ratio*(entry_price - current_stop).
                    take_profit = entry_price + self.risk_reward_ratio * (entry_price - current_stop)
                    self.take_profit = take_profit
                    # Calculate risk amount and position size in units (rounded to a whole number).
                    risk_amount = self.equity * self.risk_pct
                    unit_risk = entry_price - current_stop
                    if unit_risk <= 0:
                        unit_risk = 0.01  # safeguard against nonsensical values
                    # Ensure unit-based sizing is an integer
                    position_units = int(round(risk_amount / unit_risk, 0))
                    if position_units < 1:
                        position_units = 1

                    print("🌙 [MoonDev Debug] Entering trade at price {:.2f} | Stop Loss: {:.2f} | Take Profit: {:.2f} | Units: {}".format(
                        entry_price, current_stop, take_profit, position_units))
                    trade_open = True
            else:
                # Trade is active. Check for exit conditions.
                current_low = self.data.Low.iloc[i]
                current_high = self.data.High.iloc[i]

                # Stop Loss Exit: if current low is less than or equal to stop loss level.
                if current_low <= self.current_stop:
                    print("🌙 [MoonDev Debug] Stop loss triggered at {:.2f} on candle index {}.".format(
                        self.current_stop, i))
                    # Loss = (Entry Price - Stop Loss) * units
                    loss = (entry_price - self.current_stop) * position_units
                    self.equity -= loss
                    print("🌙 [MoonDev Debug] Trade result: LOSS of {:.2f}. Updated equity: {:.2f}".format(loss, self.equity))
                    trade_open = False
                    self.entry_price = None
                    
                    # When a trade is closed, store it in self.trades
                    trade = {
                        'entry_price': entry_price,
                        'exit_price': self.current_stop,
                        'profit': -loss,
                        'type': 'long' if position_units > 0 else 'short'
                    }
                    self.trades.append(trade)
                # Take Profit Exit: if current high is greater than or equal to take profit level.
                elif current_high >= self.take_profit:
                    print("🌙 [MoonDev Debug] Take profit triggered at {:.2f} on candle index {}.".format(
                        self.take_profit, i))
                    profit = (self.take_profit - entry_price) * position_units
                    self.equity += profit
                    print("🌙 [MoonDev Debug] Trade result: PROFIT of {:.2f}. Updated equity: {:.2f}".format(profit, self.equity))
                    trade_open = False
                    self.entry_price = None
                    
                    # When a trade is closed, store it in self.trades
                    trade = {
                        'entry_price': entry_price,
                        'exit_price': self.take_profit,
                        'profit': profit,
                        'type': 'long' if position_units > 0 else 'short'
                    }
                    self.trades.append(trade)

        # At the end, call run_backtest() to show statistics
        self.run_backtest()

    def run_backtest(self):
        # Calculate final statistics
        initial_equity = 10000.0  # Starting equity
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
        
        print("\n🌙✨ === Moon Dev's Gap Advantage Results === 🚀")
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

# ─── MAIN EXECUTION ─────────────────────────────────────────────────────────────
if __name__ == '__main__':
    # For demonstration, attempt to load 'data.csv' from the working directory.
    # If not found, generate a sample DataFrame with synthetic data.
    data_file = 'data.csv'
    if os.path.exists(data_file):
        print("🌙 [MoonDev Debug] Loading data from '{}'...".format(data_file))
        data = pd.read_csv(data_file)
    else:
        print("🌙 [MoonDev Debug] Data file not found. Generating synthetic data...")
        # Generate synthetic OHLCV data
        np.random.seed(42)
        dates = pd.date_range(start="2023-01-01", periods=200, freq="D")
        price = np.cumsum(np.random.randn(len(dates))) + 100
        high = price + np.random.rand(len(dates)) * 2
        low = price - np.random.rand(len(dates)) * 2
        open_price = price + np.random.randn(len(dates)) * 0.5
        volume = np.random.randint(1000, 5000, size=len(dates))
        data = pd.DataFrame({
            'Date': dates,
            'Open': open_price,
            'High': high,
            'Low': low,
            'Close': price,
            'Volume': volume
        })
    
    # Ensure the DataFrame has the required columns
    required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
    for col in required_cols:
        if col not in data.columns:
            raise ValueError("Data is missing required column: {}".format(col))
    
    # Create an instance of the GapAdvantage strategy.
    strategy = GapAdvantage(data)
    
    # Execute the backtest.
    strategy.backtest(initial_equity=10000)
    
    print("🌙 [MoonDev Debug] Backtest simulation complete. Keep reaching for the moon! ✨")
    
# End of file
