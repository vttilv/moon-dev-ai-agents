Below is an example implementation. Copy the code into your backtesting.py file. (Remember to install the required libraries, for example “pip install Backtesting TA‑Lib pandas”.) Enjoy the Moon Dev debugging magic! 🌙🚀✨

------------------------------------------------------------
#!/usr/bin/env python3
import os
import pandas as pd
import talib
from backtesting import Backtest, Strategy
from backtesting.lib import resample_apply
from datetime import time

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
        self.daily_bias = self.I(talib.SMA, self.data.Close, timeperiod=4)
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
        if not (time(10, 0) <= current_time <= time(11, 30)):
            # Print Moon Dev debug message 🚀
            # (We will ignore candles outside the allowed trading window.)
            print(f"🌙 [TimeGate] Skipping candle at {current_time} (outside 10:00-11:30 EST)")
            return

        # ─── IDENTIFY ACCUMULATION ─────────────────────────────
        # Use the previous three candles to define an accumulation range.
        accumulation_high = max(self.data.High[-3:])
        accumulation_low = min(self.data.Low[-3:])
        accumulation_range = accumulation_high - accumulation_low
        print(f"🌙 [Accumulation] High: {accumulation_high:.2f}, Low: {accumulation_low:.2f}, Range: {accumulation_range:.2f}")

        # ─── CHECK FOR MANIPULATION SIGNAL ─────────────────────
        # Current candle (candidate for manipulation move)
        manipulation_high = self.data.High[-1]
        manipulation_low = self.data.Low[-1]
        manipulation_range = manipulation_high - manipulation_low
        print(f"🌙 [Manipulation] Current candle range: {manipulation_range:.2f}")

        # Only consider if manipulation candle is significantly larger than accumulation range
        if manipulation_range < self.accumulation_factor * accumulation_range:
            print("🌙 [Signal] No significant manipulation detected – candle range is too small.")
            return

        # ─── DETERMINE DAILY BIAS ───────────────────────────────
        # If the current close is above daily bias then bullish bias, else bearish bias.
        current_close = self.data.Close[-1]
        current_bias = "up" if current_close > self.daily_bias[-1] else "down"
        print(f"🌙 [Bias] Current Close: {current_close:.2f}, Daily Bias: {self.daily_bias[-1]:.2f} => Bias {current_bias.upper()}")

        # ─── IDENTIFY FAIR VALUE GAP & SIGNAL ENTRY ────────────
        # For simplicity, we assume:
        #   • Long signal if bullish bias and current candle closes above the accumulation-high (fair value gap high)
        #   • Short signal if bearish bias and current candle closes below the accumulation-low (fair value gap low)
        longSignal = current_bias == "up" and current_close > accumulation_high
        shortSignal = current_bias == "down" and current_close < accumulation_low

        if not (longSignal or shortSignal):
            print("🌙 [Signal] No valid entry signal found this candle.")
            return

        # ─── ENTRY, STOP LOSS, TAKE PROFIT, AND POSITION SIZING ──
        entry_price = current_close
        if longSignal:
            # For longs, stop loss is set at the low of the manipulation candle
            stop_loss = manipulation_low
            # And take profit is set using the risk_reward ratio.
            take_profit = entry_price + (entry_price - stop_loss) * self.risk_reward
            signal_type = "LONG"
        else:
            # For shorts, stop loss is set at the high of the manipulation candle
            stop_loss = manipulation_high
            # And take profit is set using the risk_reward ratio.
            take_profit = entry_price - (stop_loss - entry_price) * self.risk_reward
            signal_type = "SHORT"

        # Calculate risk per trade and determine position size.
        risk_amount = self.equity * self.risk_percentage
        # Avoid division by zero
        risk = abs(entry_price - stop_loss) if abs(entry_price - stop_loss) != 0 else 0.0001  
        position_size = int(round(risk_amount / risk))
        print(f"🌙 [RiskMgmt] {signal_type} Entry: {entry_price:.2f}, Stop Loss: {stop_loss:.2f}, Take Profit: {take_profit:.2f}")
        print(f"🌙 [RiskMgmt] Risk Amount: {risk_amount:.2f}, Risk per unit: {risk:.4f} => Position Size: {position_size}")

        # ─── SEND ENTRY ORDERS ──────────────────────────────────
        if longSignal and not self.position:
            print("🚀🌙 [ENTRY] Moon Dev says: Let's go LONG! 💫")
            self.buy(size=position_size, sl=stop_loss, tp=take_profit)
        elif shortSignal and not self.position:
            print("🚀🌙 [ENTRY] Moon Dev says: Let's go SHORT! 💫")
            self.sell(size=position_size, sl=stop_loss, tp=take_profit)
        # Else: If already in position, let backtesting.py handle TP/SL exits.
        

# ─── RUN INITIAL BACKTEST ──────────────────────────────────────────
print("🌙🚀 Starting initial backtest for AccumulationManipulation strategy!")
bt = Backtest(data,
              AccumulationManipulation,
              cash=1000000,
              commission=0.0,
              exclusive_orders=True)

stats = bt.run()
print("\n🌙🚀 Moon Dev Initial Backtest Stats:")
print(stats)
print("\n🌙🚀 Strategy Parameters:")
print(stats._strategy)

# Save initial performance chart to charts directory
strategy_name = "AccumulationManipulation"
chart_dir = "/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/charts"
os.makedirs(chart_dir, exist_ok=True)
chart_file = os.path.join(chart_dir, f"{strategy_name}_chart.html")
bt.plot(filename=chart_file, open_browser=False)
print(f"🌙🚀 Initial performance chart saved to: {chart_file}")

# ─── OPTIMIZATION ──────────────────────────────────────────────────
print("\n🌙🚀 Starting parameter optimization for Moon Dev strategy!")
optimized_stats, optimized_params = bt.optimize(
    risk_reward= [1.5, 2.0, 2.5],           # TP risk reward multiplier options
    accumulation_factor= [1.0, 1.5, 2.0],     # Manipulation candle factor options
    risk_percentage= [0.005, 0.01, 0.015],      # Risk per trade as fraction of equity
    maximize="Equity Final [$]"
)

print("\n🌙🚀 Optimized Stats:")
print(optimized_stats)
print("\n🌙🚀 Optimized Strategy Parameters:")
print(optimized_params)

# Save optimized performance chart to charts directory
opt_chart_file = os.path.join(chart_dir, f"{strategy_name}_optimized_chart.html")
bt.plot(filename=opt_chart_file, open_browser=False)
print(f"🌙🚀 Optimized performance chart saved to: {opt_chart_file}")

------------------------------------------------------------

Notes:
• We use the self.I() wrapper for TA‑Lib SMA indicator on the Close price.
• Data cleaning steps ensure the CSV columns match Backtesting requirements.
• The entry/exit logic checks that the current candle falls within the allowed EST time window (10:00–11:30) and uses the previous three candles to define an accumulation zone.
• The “manipulation” is assumed when the current candle’s range exceeds a set multiple (accumulation_factor) of the accumulation range.
• Position sizing is computed by dividing the risk amount (a fraction of current equity) by the per‑unit risk. The result is rounded to an integer.
• Optimization parameters have been provided as lists (which Backtesting.optimize will iterate over) so we never optimize lists directly.
• Plenty of Moon Dev debug prints with emojis have been added! 🌙🚀✨

Happy backtesting and may your trades shoot for the moon!