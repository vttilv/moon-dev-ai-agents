Below is the complete Python script for your TimeframeTrendAnalyzer strategy. This implementation:

• Imports all required modules (including os, pandas, numpy, talib, and backtesting.py)  
• Loads and cleans the data (stripping spaces, dropping any “unnamed” columns, converting the datetime column, and renaming columns to “Open”, “High”, “Low”, “Close”, “Volume”)  
• Computes multi‐timeframe “candles” (1‑hour, 4‑hour, daily, weekly) in the strategy’s init() method  
• Defines entry rules based on whether all higher timeframes agree and the 15‑minute close breaks the last complete 1‑hour high (long) or low (short)  
• Calculates the stop loss and take profit based on the given risk–reward ratio and then sizes the order based on a fixed risk percentage of equity (using int(round(...)) so only whole numbers are used)  
• Prints plenty of Moon Dev debug messages with emojis  
• Runs an initial backtest (cash=1,000,000) before executing a parameter optimization (optimizing “risk_reward”)  
• Saves both charts (initial and optimized) to the charts directory

Just copy and run the script. Have fun backtesting and good luck – Moon Dev style! 🚀🌙✨

------------------------------------------------------------
#!/usr/bin/env python3
import os
import pandas as pd
import numpy as np
import talib
from backtesting import Backtest, Strategy

# Define the TimeframeTrendAnalyzer strategy
class TimeframeTrendAnalyzer(Strategy):
    # ----- Optimization parameters -----
    risk_reward = 2.0       # target risk-reward ratio (can be optimized over a range, e.g. 2,3,4)
    risk_pct    = 0.01      # risk percentage per trade

    def init(self):
        # • Compute multi-timeframe aggregated candles from the 15-min data.
        #   (Our data index is the datetime so we can use resample.)
        self.mtf_1h = self.data.resample('1H').agg({
            'Open':  'first',
            'High':  'max',
            'Low':   'min',
            'Close': 'last',
            'Volume':'sum'
        }).dropna()

        self.mtf_4h = self.data.resample('4H').agg({
            'Open':  'first',
            'High':  'max',
            'Low':   'min',
            'Close': 'last',
            'Volume':'sum'
        }).dropna()

        self.mtf_daily = self.data.resample('D').agg({
            'Open':  'first',
            'High':  'max',
            'Low':   'min',
            'Close': 'last',
            'Volume':'sum'
        }).dropna()

        self.mtf_weekly = self.data.resample('W').agg({
            'Open':  'first',
            'High':  'max',
            'Low':   'min',
            'Close': 'last',
            'Volume':'sum'
        }).dropna()

        print("🌙✨ [Init] Multi-timeframe (1H, 4H, Daily, Weekly) data computed. Ready to scour the trends! 🚀")
        self.breakeven_adjusted = False  # flag for break-even adjustment
        self.entry_sl = None            # store the stop loss level at entry

    def next(self):
        # Get the current bar’s timestamp and price
        current_time = self.data.index[-1]
        current_price = self.data.Close[-1]

        # -------------------------------
        # Retrieve the most recent completed candle for each timeframe
        # -------------------------------
        mtf_1h_all = self.mtf_1h[self.mtf_1h.index <= current_time]
        if len(mtf_1h_all) == 0:
            return
        last_1h = mtf_1h_all.iloc[-1]

        mtf_4h_all = self.mtf_4h[self.mtf_4h.index <= current_time]
        if len(mtf_4h_all) == 0:
            return
        last_4h = mtf_4h_all.iloc[-1]

        mtf_daily_all = self.mtf_daily[self.mtf_daily.index <= current_time]
        if len(mtf_daily_all) == 0:
            return
        last_daily = mtf_daily_all.iloc[-1]

        mtf_weekly_all = self.mtf_weekly[self.mtf_weekly.index <= current_time]
        if len(mtf_weekly_all) == 0:
            return
        last_weekly = mtf_weekly_all.iloc[-1]

        # -------------------------------
        # Determine trends (using the simple idea: candle bullish if Close > Open)
        # -------------------------------
        trend_1h    = 'up' if last_1h.Close > last_1h.Open else 'down'
        trend_4h    = 'up' if last_4h.Close > last_4h.Open else 'down'
        trend_daily = 'up' if last_daily.Close > last_daily.Open else 'down'
        trend_weekly= 'up' if last_weekly.Close > last_weekly.Open else 'down'
        print(f"🌙✨ [Debug] Time: {current_time}, 1H: {trend_1h}, 4H: {trend_4h}, Daily: {trend_daily}, Weekly: {trend_weekly}. 🚀")

        # Only trade if the higher timeframes agree.
        if (trend_daily == trend_4h == trend_weekly):
            overall_trend = trend_daily
            print(f"🌙✨ [Signal] Overall trend is {overall_trend.upper()} based on Daily/4H/Weekly. Let’s ride the wave!")
        else:
            print("🌙✨ [Signal] Conflicting higher timeframe trends… No trade this round!")
            return  # Exit if higher timeframe trends are not in agreement

        # -------------------------------
        # ----- Entry Logic -----
        # If no open position, we look for a trade signal based on the 1H structure:
        #   > For LONG: if overall trend is UP and current price > last 1H High.
        #   > For SHORT: if overall trend is DOWN and current price < last 1H Low.
        # -------------------------------
        if not self.position:
            # LONG ENTRY
            if overall_trend == 'up' and current_price > last_1h.High:
                sl = last_1h.Low  # Stop loss just below the last 1H low
                risk = current_price - sl
                if risk <= 0:
                    print("🌙✨ [Warning] Computed risk for LONG is <= 0. Skipping trade. 🚀")
                    return
                tp = current_price + self.risk_reward * risk  # take profit set for at least 1:2 risk-reward
                risk_amount = self.equity * self.risk_pct    # amount of cash risked this trade
                position_size = risk_amount / risk           # number of units to risk
                position_size = int(round(position_size))     # ensure integer units!
                print(f"🌙✨ [Entry LONG] Price: {current_price:.2f}, SL: {sl:.2f}, TP: {tp:.2f}, Risk: {risk:.2f}, Units: {position_size}. 🚀")
                self.buy(size=position_size, sl=sl, tp=tp)
                self.entry_sl = sl
                self.breakeven_adjusted = False

            # SHORT ENTRY
            elif overall_trend == 'down' and current_price < last_1h.Low:
                sl = last_1h.High  # Stop loss just above the last 1H high
                risk = sl - current_price
                if risk <= 0:
                    print("🌙✨ [Warning] Computed risk for SHORT is <= 0. Skipping trade. 🚀")
                    return
                tp = current_price - self.risk_reward * risk
                risk_amount = self.equity * self.risk_pct
                position_size = risk_amount / risk
                position_size = int(round(position_size))
                print(f"🌙✨ [Entry SHORT] Price: {current_price:.2f}, SL: {sl:.2f}, TP: {tp:.2f}, Risk: {risk:.2f}, Units: {position_size}. 🚀")
                self.sell(size=position_size, sl=sl, tp=tp)
                self.entry_sl = sl
                self.breakeven_adjusted = False
        else:
            # -------------------------------
            # ----- Position Management -----
            # We consider a break-even adjustment once the position is in profit.
            # (Note: Backtesting.py does not directly support dynamic stop updates so we only print a debug message.)
            # -------------------------------
            if self.position.is_long:
                if (current_price - self.position.entry_price) >= (self.position.entry_price - self.entry_sl) and not self.breakeven_adjusted:
                    print(f"🌙✨ [Adjust] LONG BE triggered! Price is in profit. Consider moving SL to {self.position.entry_price:.2f} (break-even). 🚀")
                    self.breakeven_adjusted = True
            elif self.position.is_short:
                if (self.entry_sl - self.position.entry_price) <= (self.position.entry_price - current_price) and not self.breakeven_adjusted:
                    print(f"🌙✨ [Adjust] SHORT BE triggered! Price is in profit. Consider moving SL to {self.position.entry_price:.2f} (break-even). 🚀")
                    self.breakeven_adjusted = True

# -------------------------------
# Main backtesting execution
# -------------------------------
def main():
    # Load data from CSV and clean up
    data_path = "/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv"
    data = pd.read_csv(data_path)
    # Clean column names (remove spaces, to lower case)
    data.columns = data.columns.str.strip().str.lower()
    # Drop any unnamed columns
    data = data.drop(columns=[col for col in data.columns if 'unnamed' in col.lower()])
    # Map the required columns to proper case names
    data.rename(columns={'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close', 'volume': 'Volume'}, inplace=True)
    # Convert datetime column to datetime type and set as index (if exists)
    if 'datetime' in data.columns:
        data['Datetime'] = pd.to_datetime(data['datetime'])
        data.set_index('Datetime', inplace=True)

    print("🌙✨ [Data] Data loaded and cleaned. Here’s a peek:")
    print(data.head())

    # Initialize Backtest with 1,000,000 cash – our “moon mission” capital!
    bt = Backtest(data, TimeframeTrendAnalyzer, cash=1000000, commission=0.0, trade_on_close=True)
    print("🌙✨ [Backtest] Running initial backtest with default parameters. 🚀")
    stats = bt.run()
    print("🌙✨ [Stats] Full statistics:")
    print(stats)
    print("🌙✨ [Strategy] Strategy details:")
    print(stats._strategy)

    # Save the initial performance plot to the charts directory
    strategy_name = "TimeframeTrendAnalyzer"
    chart_file = os.path.join("/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/charts",
                              f"{strategy_name}_chart.html")
    print(f"🌙✨ [Plot] Saving initial performance chart to {chart_file}")
    bt.plot(filename=chart_file, open_browser=False)

    # -------------------------------
    # Parameter Optimization (for example, risk_reward from 2 to 4)
    # -------------------------------
    print("🌙✨ [Optimize] Starting optimization of risk_reward... 🚀")
    optimized_stats = bt.optimize(risk_reward=range(2, 5), risk_pct=[0.01],
                                  maximize='Equity Final [$]', constraint=lambda param: True)
    print("🌙✨ [Optimized Stats] Optimization complete. Best parameters:")
    print(optimized_stats)

    # Save the optimized performance plot
    optimized_chart_file = os.path.join("/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/charts",
                              f"{strategy_name}_optimized_chart.html")
    print(f"🌙✨ [Plot] Saving optimized performance chart to {optimized_chart_file}")
    bt.plot(filename=optimized_chart_file, open_browser=False)

if __name__ == '__main__':
    main()

------------------------------------------------------------

Remember:
• All indicator‐like calculations (if needed) are to be wrapped in self.I(). In this strategy we rely on multi‐timeframe aggregation and simple candle comparisons (no built-in TA signals).
• Position size is calculated as an integer (using int(round(...))) so you won’t face floating‑point errors.
• Debug prints are sprinkled generously with 🌙 ✨ 🚀 – just like a true Moon Dev backtest!

Happy backtesting and may your trades shoot for the moon!