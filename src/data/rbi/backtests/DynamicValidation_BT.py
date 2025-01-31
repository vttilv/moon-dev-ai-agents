#!/usr/bin/env python3
"""
Moon Dev's Backtest AI 🌙 – DynamicValidation Strategy Backtest Implementation

This strategy – DynamicValidation – focuses on market structure,
supply & demand zones and strict risk-reward management. It uses TA‐Lib
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

    Parameters for optimization are defined as class attributes:
      • risk_reward_min : Minimum acceptable risk/reward ratio (default 2.5)
      • zone_buffer_bp  : Stop-loss offset (in basis points, where 1 bp = 0.001) (default 2 → 0.002)
      • zone_tolerance_bp : Tolerance for re-entry into the zone (default 2 bp)
      • risk_percent    : Risk percentage per trade (as an integer percentage; default 1 → 1%)
      • ma_period       : Moving Average period for trend determination (default 50)
      • pivot_period    : Period to compute recent swing highs/lows (default 20)
    """
    risk_reward_min = 2.5       # Must be >=2.5 (non-negotiable risk/reward threshold)
    zone_buffer_bp = 2          # Basis points for stop-loss buffer (e.g., 2 => 0.002)
    zone_tolerance_bp = 2       # Basis points for acceptable zone re-entry (e.g., 2 => 0.002)
    risk_percent = 1            # Risk 1% of equity per trade (as a whole percent)
    ma_period = 50              # Period for trend indicator (SMA)
    pivot_period = 20           # Lookback period to compute swing highs/lows as zones

    def init(self):
        # Indicators: Use self.I() wrapper with talib functions!
        self.sma = self.I(talib.SMA, self.data.Close, timeperiod=self.ma_period)
        self.pivot_high = self.I(talib.MAX, self.data.High, timeperiod=self.pivot_period)
        self.pivot_low = self.I(talib.MIN, self.data.Low, timeperiod=self.pivot_period)

        print("🌙✨ [INIT] DynamicValidation initialized with parameters:")
        print(f"    MA Period: {self.ma_period}, Pivot Period: {self.pivot_period}")
        print(f"    Risk Reward Min: {self.risk_reward_min}")
        print(f"    Zone Buffer (bp): {self.zone_buffer_bp}, Zone Tolerance (bp): {self.zone_tolerance_bp}")
        print(f"    Risk Percent per trade: {self.risk_percent}% 🚀")

    def next(self):
        # Convert basis point parameters to floats
        zone_buffer = self.zone_buffer_bp / 1000.0      # E.g., 2 bp -> 0.002
        zone_tolerance = self.zone_tolerance_bp / 1000.0  # E.g., 2 bp -> 0.002
        risk_pct = self.risk_percent / 100.0              # E.g., 1% -> 0.01

        current_close = self.data.Close[-1]
        current_sma = self.sma[-1]
        # Determine trend: uptrend if close > SMA, else downtrend
        uptrend = current_close > current_sma

        if uptrend:
            print("🌙💫 [TREND] Uptrend confirmed!")
            # In an uptrend, demand zone = recent swing low
            demand_zone = self.pivot_low[-1]
            # Debug print the zone levels
            print(f"🌙 [ZONE] Demand Zone (Pivot Low): {demand_zone:.2f}")
            # Entry condition: price re-enters (i.e. is near) the demand zone
            if current_close <= demand_zone * (1 + zone_tolerance):
                entry_price = current_close
                stop_loss = demand_zone * (1 - zone_buffer)  # Stop loss just below the demand zone
                take_profit = self.pivot_high[-1]             # Take profit at the recent swing high
                risk = entry_price - stop_loss
                reward = take_profit - entry_price

                if risk <= 0:
                    print("🌙⚠️ [SKIP] Long trade skipped: NON-POSITIVE risk calculation!")
                else:
                    rr = reward / risk
                    print(f"🌙🔍 [SETUP] Long Trade Setup: Entry={entry_price:.2f}, SL={stop_loss:.2f}, TP={take_profit:.2f}")
                    print(f"         Risk = {risk:.2f}, Reward = {reward:.2f}, RR = {rr:.2f}")
                    if rr >= self.risk_reward_min:
                        # Calculate position size based on risk amount (risk_pct of current equity)
                        risk_amount = risk_pct * self.equity
                        qty = risk_amount / risk
                        print(f"🚀🌙 [ORDER] MOON LAUNCH LONG: Entry: {entry_price:.2f}, SL: {stop_loss:.2f}, TP: {take_profit:.2f}, Qty: {qty:.4f}")
                        self.buy(size=qty, sl=stop_loss, tp=take_profit)
                    else:
                        print(f"🌙⚠️ [SKIP] Long trade rejected: Insufficient RR ({rr:.2f} < {self.risk_reward_min})")
        else:
            print("🌙💫 [TREND] Downtrend confirmed!")
            # In a downtrend, supply zone = recent swing high
            supply_zone = self.pivot_high[-1]
            print(f"🌙 [ZONE] Supply Zone (Pivot High): {supply_zone:.2f}")
            # Entry condition: price re-enters the supply zone
            if current_close >= supply_zone * (1 - zone_tolerance):
                entry_price = current_close
                stop_loss = supply_zone * (1 + zone_buffer)  # Stop loss just above the supply zone
                take_profit = self.pivot_low[-1]              # Take profit at the recent swing low
                risk = stop_loss - entry_price
                reward = entry_price - take_profit

                if risk <= 0:
                    print("🌙⚠️ [SKIP] Short trade skipped: NON-POSITIVE risk calculation!")
                else:
                    rr = reward / risk
                    print(f"🌙🔍 [SETUP] Short Trade Setup: Entry={entry_price:.2f}, SL={stop_loss:.2f}, TP={take_profit:.2f}")
                    print(f"         Risk = {risk:.2f}, Reward = {reward:.2f}, RR = {rr:.2f}")
                    if rr >= self.risk_reward_min:
                        risk_amount = risk_pct * self.equity
                        qty = risk_amount / risk
                        print(f"🚀🌙 [ORDER] MOON LAUNCH SHORT: Entry: {entry_price:.2f}, SL: {stop_loss:.2f}, TP: {take_profit:.2f}, Qty: {qty:.4f}")
                        self.sell(size=qty, sl=stop_loss, tp=take_profit)
                    else:
                        print(f"🌙⚠️ [SKIP] Short trade rejected: Insufficient RR ({rr:.2f} < {self.risk_reward_min})")

# ─── MAIN BACKTEST EXECUTION ─────────────────────────────────────────
if __name__ == '__main__':
    # Data Handling and Cleaning (Moon Dev style! 🌙🚀)
    data_path = "/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv"
    print("🌙🚀 [DATA] Loading data from:", data_path)
    data = pd.read_csv(data_path)
    # Clean column names: remove extra spaces & lower-case
    data.columns = data.columns.str.strip().str.lower()
    # Drop any unnamed columns
    data = data.drop(columns=[col for col in data.columns if 'unnamed' in col.lower()])
    # Map columns to backtesting requirements with proper case
    data.rename(columns={'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close', 'volume': 'Volume'}, inplace=True)
    # Convert datetime if available & set as index
    if "datetime" in data.columns:
        data["datetime"] = pd.to_datetime(data["datetime"])
        data.set_index("datetime", inplace=True)
    print("🌙✨ [DATA] Data cleansing complete! Ready for liftoff! 🚀")

    # Run initial backtest with default parameters and starting cash of 1,000,000
    bt = Backtest(data, DynamicValidation, cash=1000000, commission=0.0)
    print("🚀🌕 [BACKTEST] Running initial backtest with default parameters!")
    stats = bt.run()
    print("🌙✨ [STATS] Initial Backtest Results:")
    print(stats)
    print("🌙✨ [STRATEGY PARAMS] " + str(stats._strategy))
    # Save initial performance chart to charts directory
    chart_file_initial = os.path.join("/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/charts", "DynamicValidation_initial_chart.html")
    bt.plot(filename=chart_file_initial, open_browser=False)
    print("🌙🚀 [CHART] Initial chart saved to:")
    print(chart_file_initial)

    # ─── PARAMETER OPTIMIZATION ─────────────────────────────
    print("🚀🌕 [OPTIMIZE] Running optimization – Moon Dev is polishing your parameters! 🌙✨")
    optimized_stats = bt.optimize(
        risk_reward_min=range(3, 6, 1),      # Try risk_reward_min values: 3, 4, 5
        zone_buffer_bp=range(1, 4, 1),         # Try 1, 2, 3 bp → (0.001, 0.002, 0.003)
        pivot_period=range(15, 31, 5),          # Try pivot periods: 15, 20, 25, 30
        ma_period=range(40, 61, 10)             # Try MA periods: 40, 50, 60
    )
    print("🌙✨ [OPTIMIZED STATS] Optimized Backtest Results:")
    print(optimized_stats)
    best_params = optimized_stats._strategy
    print("🌙🚀 [BEST PARAMS] Best strategy parameters found:")
    print(best_params)

    # Re-run backtest using the optimized parameters for the final performance plot
    bt_opt = Backtest(data, DynamicValidation, cash=1000000, commission=0.0)
    # Depending on the Backtesting version, best_params might be a namedtuple.
    # Use its dictionary representation.
    try:
        params_dict = best_params._asdict()
    except AttributeError:
        params_dict = vars(best_params)
    stats_opt = bt_opt.run(**params_dict)
    chart_file_optimized = os.path.join("/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/charts", "DynamicValidation_optimized_chart.html")
    bt_opt.plot(filename=chart_file_optimized, open_browser=False)
    print("🌙🚀 [CHART] Optimized chart saved to:")
    print(chart_file_optimized)
    print("🌙🚀 [DONE] Optimization & backtesting complete! Enjoy your Moon Dev charts! ✨")
    
# END OF FILE
