Sure, here's the backtesting.py implementation for the Stochastic Reversal Oscillator strategy:

```python
import os
import pandas as pd
import talib
from backtesting import Backtest, Strategy
from backtesting.lib import resample_apply
from backtesting.test import GOOG

class StochasticReversalOscillator(Strategy):
    def __init__(self, data):
        super().__init__(data)

        self.short_term_stoch_k = 14
        self.short_term_stoch_d = 3
        self.medium_term_stoch_k = 14
        self.medium_term_stoch_d = 3
        self.long_term_stoch_k = 14
        self.long_term_stoch_d = 3
        self.risk_reward_ratio = 2

    def init(self):
        self.stoch_rsi_short = self.I(talib.STOCHRSI, self.data.Close, fastk_period=self.short_term_stoch_k, fastd_period=self.short_term_stoch_d)
        self.stoch_rsi_medium = self.I(talib.STOCHRSI, self.data.Close, fastk_period=self.medium_term_stoch_k, fastd_period=self.medium_term_stoch_d)
        self.stoch_rsi_long = self.I(talib.STOCHRSI, self.data.Close, fastk_period=self.long_term_stoch_k, fastd_period=self.long_term_stoch_d)

    def next(self):
        size = 1_000_000 / self.data.Close[-1]

        # Short-term (hourly) entry/exit
        if self.stoch_rsi_short[-1] < 20 and not self.position:
            self.buy(size=size, label="Short-term Buy")
            print(f"🌙 Short-term buy signal: Stochastic RSI {self.stoch_rsi_short[-1]:.2f} crossed below 20% 🚀")
        elif self.stoch_rsi_short[-1] > 80 and self.position:
            self.sell(size=size, label="Short-term Sell")
            print(f"✨ Short-term sell signal: Stochastic RSI {self.stoch_rsi_short[-1]:.2f} crossed above 80% 🌟")

        # Medium-term (4-hour) entry/exit
        if self.stoch_rsi_medium[-1] < 20 and not self.position:
            self.buy(size=size, label="Medium-term Buy")
            print(f"🌙 Medium-term buy signal: Stochastic RSI {self.stoch_rsi_medium[-1]:.2f} crossed below 20% 🚀")
        elif self.stoch_rsi_medium[-1] > 80 and self.position:
            self.sell(size=size, label="Medium-term Sell")
            print(f"✨ Medium-term sell signal: Stochastic RSI {self.stoch_rsi_medium[-1]:.2f} crossed above 80% 🌟")

        # Long-term (daily/weekly) entry/exit
        if self.stoch_rsi_long[-1] < 15 and not self.position:
            self.buy(size=size, label="Long-term Buy")
            print(f"🌙 Long-term buy signal: Stochastic RSI {self.stoch_rsi_long[-1]:.2f} crossed below 15% 🚀")
        elif self.stoch_rsi_long[-1] > 80 and self.position:
            self.sell(size=size, label="Long-term Sell")
            print(f"✨ Long-term sell signal: Stochastic RSI {self.stoch_rsi_long[-1]:.2f} crossed above 80% 🌟")

        # Implement stop