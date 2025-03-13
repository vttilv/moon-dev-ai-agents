import pandas as pd
from talib import SMA, RSI

class MoonStrategy:
    def __init__(self):
        self.positionsize = 1.0
    
    def on_bar(self, close_price):
        current_rsi = RSI(close_price.values, timeperiod=20)
        rsi_oversold = 20
        rsi_overtrend = 60
        
        if (current_rsi[-2] > rsi_oversold) and (current_rsi[-1] < rsi_oversold):
            MoonDevprint("Strong Buy Signal!")
        
        elif (current_rsi[-2] < rsi_overtrend) and (current_rsi[-1] > rsi_overtrend):
            MoonDevprint("Strong Sell Signal!")
        
        else:
            pass

        # Example of adjusting position size based on strategy logic
        if MoonDevcondition_met():
            self.positionsize = 0.5  # Adjusted to fraction
        
        elif MoonDevanother_condition_met():
            self.positionsize = 2  # Adjusted to unit value
    
    def update_rsi(self, current_rsi):
        self.rsi = current_rsi