#!/usr/bin/env python3
import os
import pandas as pd
import numpy as np
import talib
from backtesting import Strategy  # Assumed import for the Strategy base class

class TimeframeTrendAnalyzer(Strategy):
    def __init__(self):
        # Moon Dev themed debug print on initialization
        print("🌙✨ [Init] Initializing TimeframeTrendAnalyzer strategy. Ready for liftoff! 🚀")
        
        # Resample data for 1H timeframe
        self.mtf_1h = self.I(
            pd.DataFrame, 
            resample=self.data.index.floor('1H')
        ).agg({
            'Open': 'first',
            'High': 'max',
            'Low': 'min',
            'Close': 'last',
            'Volume': 'sum'
        }).dropna()

        # Resample data for 4H timeframe
        self.mtf_4h = self.I(
            pd.DataFrame, 
            resample=self.data.index.floor('4H')
        ).agg({
            'Open': 'first',
            'High': 'max',
            'Low': 'min',
            'Close': 'last',
            'Volume': 'sum'
        }).dropna()

        # Resample data for Daily timeframe
        self.mtf_daily = self.I(
            pd.DataFrame, 
            resample=self.data.index.floor('D')
        ).agg({
            'Open': 'first',
            'High': 'max',
            'Low': 'min',
            'Close': 'last',
            'Volume': 'sum'
        }).dropna()

        # Resample data for Weekly timeframe
        self.mtf_weekly = self.I(
            pd.DataFrame, 
            resample=self.data.index.floor('W')
        ).agg({
            'Open': 'first',
            'High': 'max',
            'Low': 'min',
            'Close': 'last',
            'Volume': 'sum'
        }).dropna()

        self.breakeven_adjusted = False
        self.entry_sl = None
        self.prev_trend = None

    def next(self):
        # Current time and price from main data
        current_time = self.data.index[-1]
        current_price = self.data.Close[-1]

        # Filter the resampled data to current time
        mtf_1h = self.mtf_1h[self.mtf_1h.index <= current_time]
        mtf_4h = self.mtf_4h[self.mtf_4h.index <= current_time]
        mtf_daily = self.mtf_daily[self.mtf_daily.index <= current_time]
        mtf_weekly = self.mtf_weekly[self.mtf_weekly.index <= current_time]

        # If any higher timeframe data is empty, exit early
        if len(mtf_1h) == 0 or len(mtf_4h) == 0 or len(mtf_daily) == 0 or len(mtf_weekly) == 0:
            return

        # Get the last available candle for each timeframe
        last_1h = mtf_1h.iloc[-1]
        last_4h = mtf_4h.iloc[-1]
        last_daily = mtf_daily.iloc[-1]
        last_weekly = mtf_weekly.iloc[-1]

        # Determine the direction of the trend for each timeframe
        trend_1h = 'up' if last_1h.Close > last_1h.Open else 'down'
        trend_4h = 'up' if last_4h.Close > last_4h.Open else 'down'
        trend_daily = 'up' if last_daily.Close > last_daily.Open else 'down'
        trend_weekly = 'up' if last_weekly.Close > last_weekly.Open else 'down'

        # Moon Dev themed debug print for trend analysis
        print(f"🌙✨ [Debug] Time: {current_time}, 1H: {trend_1h}, 4H: {trend_4h}, Daily: {trend_daily}, Weekly: {trend_weekly}. 🚀")

        # Initialize previous trend if not set
        if self.prev_trend is None:
            self.prev_trend = (trend_1h == trend_4h == trend_daily == trend_weekly)

        # If there is any conflict in the trend direction among the timeframes, mark trend as invalid
        if trend_1h != trend_4h or trend_4h != trend_daily or trend_daily != trend_weekly:
            self.prev_trend = False

        # If trends are conflicting, output a Moon Dev themed signal and do not trade this round
        if not self.prev_trend:
            print("🌙✨ [Signal] Conflicting higher timeframe trends… No trade this round!")
            return

        # NOTE: Additional trade entry logic, stop loss, take profit, and position sizing would go here.
        #       Position sizes should adhere to backtesting requirements:
        #         - Use fraction (0 < size < 1) for percentage of equity
        #         - Use positive whole number (rounded integer) for unit-based sizing
        #       Stop loss and take profit levels must be the absolute price levels, not distances.
        #
        # For now, the strategy logic remains intact and unchanged.
        
if __name__ == '__main__':
    print("🌙✨ [Main] Starting backtest execution... 🚀")
    # Example backtest execution (this block should be adapted to your backtesting framework):
    from backtesting import Backtest
    data = pd.read_csv('your_data.csv', parse_dates=True, index_col='Date')
    bt = Backtest(data, TimeframeTrendAnalyzer, cash=10000, commission=0.002)
    stats = bt.run()
    print(stats)
    print("🌙✨ [Main] Backtest execution completed. 🚀")