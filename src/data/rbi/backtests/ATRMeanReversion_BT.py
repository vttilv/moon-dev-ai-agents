Below is an example implementation of backtesting.py for the ATR MeanReversion strategy. (Remember: this strategy uses TA‑Lib for indicators – no backtesting.py built–ins!) Enjoy the Moon Dev debug prints! 🌙✨🚀

------------------------------------------------------------
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
from backtesting import Backtest, Strategy

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
    # Set Date as the index (if desired by backtesting.py)
    data.index = pd.to_datetime(data['Date'])
    return data

# ////////////////////////////////////////////////////////////////////////
# Strategy Implementation – ATR MeanReversion
# ////////////////////////////////////////////////////////////////////////
class ATRMeanReversion(Strategy):
    # Strategy parameters (will be optimized later)
    kelter_period = 20
    # Use an integer factor (divided by 10) for the Kelter multiplier to allow optimization as an int.
    kelter_multiplier_factor = 25  # This equals 2.5 when divided by 10.
    atr_period = 14
    # Use an integer factor (divided by 10) for risk reward ratio.
    risk_reward_factor = 20  # This equals 2.0 when divided by 10.
    risk_per_trade = 0.01  # 1% of equity risk per trade

    def init(self):
        # Calculate Kelter Channels using TA-lib functions via self.I() wrapper
        # Middle = Simple Moving Average (SMA)
        self.sma = self.I(talib.SMA, self.data.Close, timeperiod=self.kelter_period)
        # Standard Deviation of Close prices over kelter_period
        self.std = self.I(talib.STDDEV, self.data.Close, timeperiod=self.kelter_period, nbdev=1)
        # Calculate multiplier from factor
        self.multiplier = self.kelter_multiplier_factor / 10.0
        # Upper and Lower Kelter Channels
        self.kelter_upper = self.sma + self.multiplier * self.std
        self.kelter_lower = self.sma - self.multiplier * self.std

        # ATR for risk management (the ATR period is a tunable parameter)
        self.atr = self.I(talib.ATR, self.data.High, self.data.Low, self.data.Close, timeperiod=self.atr_period)

        # To store reversal candle values for exit rules
        self.reversal_high = None
        self.reversal_low = None

        print("🌙✨ [INIT] Strategy initialized with kelter_period =", self.kelter_period,
              ", kelter_multiplier =", self.multiplier,
              ", atr_period =", self.atr_period,
              ", risk_reward_ratio =", self.risk_reward_factor / 10.0)

    def next(self):
        # Ensure we have at least two candles to check for engulfing pattern
        if len(self.data.Close) < 2:
            return

        # Get previous and current candles from data (using -2 and -1 indexes)
        prev_open = self.data.Open[-2]
        prev_close = self.data.Close[-2]
        curr_open = self.data.Open[-1]
        curr_close = self.data.Close[-1]
        curr_high = self.data.High[-1]
        curr_low = self.data.Low[-1]

        # Debug print current bar info
        print(f"🌙✨ [BAR] Current Candle >> Open: {curr_open:.2f}, High: {curr_high:.2f}, Low: {curr_low:.2f}, Close: {curr_close:.2f}")

        # Check for bullish and bearish engulfing patterns
        bullish_engulf = (prev_close < prev_open) and (curr_close > curr_open) and (curr_open < prev_close) and (curr_close > prev_open)
        bearish_engulf = (prev_close > prev_open) and (curr_close < curr_open) and (curr_open > prev_close) and (curr_close < prev_open)

        # Get current Kelter channel boundaries
        upper = self.kelter_upper[-1]
        lower = self.kelter_lower[-1]
        # Get current ATR value (used in risk calculation if needed)
        atr_val = self.atr[-1]
        # Calculate risk reward ratio (float, e.g. 2.0)
        rr_ratio = self.risk_reward_factor / 10.0

        # If no open position, check for entry condition
        if not self.position:
            # LONG Setup: Price pokes below lower channel and bullish engulfing occurs.
            if (curr_close < lower) and bullish_engulf:
                entry_price = curr_high  # Simulate buy stop order above the reversal candle high
                stop_loss = curr_low    # Protective stop loss below the reversal candle low
                risk = entry_price - stop_loss
                if risk <= 0:
                    print("🌙❗ [LONG] Invalid risk measure calculated. Skipping trade.")
                    return
                # Calculate position sizing based on risk_per_trade from equity and half normal size!
                risk_amount = self.equity * self.risk_per_trade
                raw_size = risk_amount / risk
                position_size = int(round(raw_size / 2))  # Use half of the normal sizing (integer units)
                # Calculate take profit target using risk-reward ratio
                take_profit = entry_price + rr_ratio * risk

                print(f"🌙🚀 [LONG ENTRY SIGNAL] Bullish Engulfing detected! Entry pending (buy stop above reversal candle).")
                print(f"   ➡ reversal candle high: {curr_high:.2f}, low: {curr_low:.2f}")
                print(f"   ➡ Kelter lower channel: {lower:.2f}, Equity: {self.equity:,.2f}")
                print(f"   ➡ Calculated risk: {risk:.2f}, Risk Amount: {risk_amount:.2f}")
                print(f"   ➡ Position Size (using half normal risk): {position_size} units")
                # Store reversal candle boundaries for exit logic
                self.reversal_high = curr_high
                self.reversal_low = curr_low
                # Enter long with protective stop loss and take profit
                self.buy(size=position_size, sl=stop_loss, tp=take_profit)
                print("🌙✨ [ORDER] Long order executed! 🚀")

            # SHORT Setup: Price pokes above upper channel and bearish engulfing occurs.
            elif (curr_close > upper) and bearish_engulf:
                entry_price = curr_low  # Simulate sell stop order below the reversal candle low
                stop_loss = curr_high   # Protective stop loss above the reversal candle high
                risk = stop_loss - entry_price
                if risk <= 0:
                    print("🌙❗ [SHORT] Invalid risk measure calculated. Skipping trade.")
                    return
                risk_amount = self.equity * self.risk_per_trade
                raw_size = risk_amount / risk
                position_size = int(round(raw_size / 2))  # Use half normal risk - integer units
                take_profit = entry_price - rr_ratio * risk

                print(f"🌙🚀 [SHORT ENTRY SIGNAL] Bearish Engulfing detected! Entry pending (sell stop below reversal candle).")
                print(f"   ➡ reversal candle high: {curr_high:.2f}, low: {curr_low:.2f}")
                print(f"   ➡ Kelter upper channel: {upper:.2f}, Equity: {self.equity:,.2f}")
                print(f"   ➡ Calculated risk: {risk:.2f}, Risk Amount: {risk_amount:.2f}")
                print(f"   ➡ Position Size (using half normal risk): {position_size} units")
                self.reversal_high = curr_high
                self.reversal_low = curr_low
                self.sell(size=position_size, sl=stop_loss, tp=take_profit)
                print("🌙✨ [ORDER] Short order executed! 🚀")

        # Exit Rules: If already in a trade, look for exit signal
        else:
            # LONG EXIT: When in a long position AND price breaks above the reversal candle high
            if self.position.is_long and (curr_close > (self.reversal_high if self.reversal_high is not None else curr_high)):
                print("🌙💫 [EXIT] Long position exit signal: price broke above the reversal candle high!")
                self.position.close()
                # Reset reversal candle values
                self.reversal_high = None
                self.reversal_low = None

            # SHORT EXIT: When in a short position AND price breaks below the reversal candle low
            elif self.position.is_short and (curr_close < (self.reversal_low if self.reversal_low is not None else curr_low)):
                print("🌙💫 [EXIT] Short position exit signal: price broke below the reversal candle low!")
                self.position.close()
                self.reversal_high = None
                self.reversal_low = None

# ////////////////////////////////////////////////////////////////////////
# Main Backtest and Optimization Execution
# ////////////////////////////////////////////////////////////////////////
if __name__ == "__main__":
    DATA_PATH = "/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv"
    data = load_and_clean_data(DATA_PATH)
    # Only keep the required columns if present:
    data = data[['Open', 'High', 'Low', 'Close', 'Volume']]

    # Set initial capital 1,000,000
    initial_capital = 1000000

    # Create the backtest object with our strategy
    print("🌙✨ [BACKTEST] Running initial backtest with default parameters... 🚀")
    bt = Backtest(data, ATRMeanReversion, cash=initial_capital, commission=.000)
    stats = bt.run()
    print("🌙✨ [STATS] Full Backtest Stats:")
    print(stats)
    print("🌙✨ [STRATEGY INFO] Strategy Parameters & Details:")
    print(stats._strategy)

    # Save initial performance chart
    strategy_name = "ATRMeanReversion"
    chart_dir = "/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/charts"
    if not os.path.exists(chart_dir):
        os.makedirs(chart_dir)
    chart_file = os.path.join(chart_dir, f"{strategy_name}_chart.html")
    bt.plot(filename=chart_file, open_browser=False)
    print(f"🌙✨ [PLOT] Initial performance chart saved to: {chart_file}")

    # ////////////////////////////////////////////////////////////////////////
    # Parameter Optimization
    # ////////////////////////////////////////////////////////////////////////
    print("🌙✨ [OPTIMIZATION] Starting parameter optimization... 🚀")
    # Optimize parameters:
    #  - attr_period: from 10 to 18 stepping by 2
    #  - kelter_multiplier_factor: from 20 to 30 stepping by 5 (i.e. 2.0, 2.5, 3.0)
    #  - risk_reward_factor: from 15 to 30 stepping by 5 (i.e. 1.5, 2.0, 2.5, 3.0)
    opt_results = bt.optimize(
        atr_period=range(10, 20, 2),
        kelter_multiplier_factor=range(20, 31, 5),
        risk_reward_factor=range(15, 31, 5),
        maximize='Equity Final [$]',
        return_stats=True
    )
    print("🌙✨ [OPTIMIZATION] Optimized Strategy Stats:")
    print(opt_results)
    # Re-run the backtest using the optimized parameters
    print("🌙✨ [FINAL BACKTEST] Running backtest using optimized parameters... 🚀")
    bt_opt = Backtest(data, ATRMeanReversion, cash=initial_capital, commission=.000)
    final_stats = bt_opt.run(**opt_results._strategy)
    print("🌙✨ [FINAL STATS] Optimized Backtest Stats:")
    print(final_stats)
    final_chart_file = os.path.join(chart_dir, f"{strategy_name}_optimized_chart.html")
    bt_opt.plot(filename=final_chart_file, open_browser=False)
    print(f"🌙✨ [PLOT] Optimized performance chart saved to: {final_chart_file}")

------------------------------------------------------------
End of file.

Notes:
• We use self.I() to wrap all TA‑Lib indicator calls.
• Data is cleaned: column names stripped and re–mapped to 'Open', 'High', 'Low', 'Close', and 'Volume'.
• Position sizes are calculated using risk amount/amount-risk and then halved; conversion to int avoids float issues.
• Plenty of Moon Dev debug prints with emojis have been added.
• Optimize parameters with ranges – lists are broken into individual parameters.
Happy backtesting! 🌙🚀✨
