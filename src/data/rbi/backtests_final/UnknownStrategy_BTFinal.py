Here's the debugged version of the code:

```python
import os
import pandas as pd
import talib
import numpy as np

class StochasticReversalOscillator:
    def __init__(self, data):
        self.data = data

        self.short_term_stoch_k = 14
        self.short_term_stoch_d = 3
        self.medium_term_stoch_k = 14
        self.medium_term_stoch_d = 3
        self.long_term_stoch_k = 14
        self.long_term_stoch_d = 3
        self.risk_reward_ratio = 2

    def init(self):
        self.stoch_rsi_short = talib.STOCHRSI(self.data.Close, fastk_period=self.short_term_stoch_k, fastd_period=self.short_term_stoch_d)
        self.stoch_rsi_medium = talib.STOCHRSI(self.data.Close, fastk_period=self.medium_term_stoch_k, fastd_period=self.medium_term_stoch_d)
        self.stoch_rsi_long = talib.STOCHRSI(self.data.Close, fastk_period=self.long_term_stoch_k, fastd_period=self.long_term_stoch_d)

    def next(self):
        size = 1_000_000 / self.data.Close[-1]

        # Short-term (hourly) entry/exit
        if self.stoch_rsi_short[-2] < 20 and self.stoch_rsi_short[-1] > 20 and not self.position:
            self.position = 'Long'
            print(f"🌙 Short-term buy signal: Stochastic RSI {self.stoch_rsi_short[-1]:.2f} crossed above 20% 🚀")
        elif self.stoch_rsi_short[-2] > 80 and self.stoch_rsi_short[-1] < 80 and self.position == 'Long':
            self.position = 'Cash'
            print(f"✨ Short-term sell signal: Stochastic RSI {self.stoch_rsi_short[-1]:.2f} crossed below 80% 🌟")

        # Medium-term (4-hour) entry/exit
        if self.stoch_rsi_medium[-2] < 20 and self.stoch_rsi_medium[-1] > 20 and not self.position:
            self.position = 'Long'
            print(f"🌙 Medium-term buy signal: Stochastic RSI {self.stoch_rsi_medium[-1]:.2f} crossed above 20% 🚀")
        elif self.stoch_rsi_medium[-2] > 80 and self.stoch_rsi_medium[-1] < 80 and self.position == 'Long':
            self.position = 'Cash'
            print(f"✨ Medium-term sell signal: Stochastic RSI {self.stoch_rsi_medium[-1]:.2f} crossed below 80% 🌟")

        # Long-term (daily/weekly) entry/exit
        if self.stoch_rsi_long[-2] < 15 and self.stoch_rsi_long[-1] > 15 and not self.position:
            self.position = 'Long'
            print(f"🌙 Long-term buy signal: Stochastic RSI {self.stoch_rsi_long[-1]:.2f} crossed above 15% 🚀")
        elif self.stoch_rsi_long[-2] > 80 and self.stoch_rsi_long[-1] < 80 and self.position == 'Long':
            self.position = 'Cash'
            print(f"✨ Long-term sell signal: Stochastic RSI {self.stoch_rsi_long[-1]:.2f} crossed below 80%