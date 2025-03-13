import pandas as pd
import numpy as np
from talib import abstract, SMA, MAX, MIN, VWAP
from pandas import DataFrame, Series

# Backtest class
class PatrickStrategy(bt.Strategy):
    # List of indicators and parameters to be initialized
    _indicators = [SMA, MAX, MIN, VWAP]
    
    def __init__(self):
        """Initialize strategy"""
        self.position = None
        
        # Calculate indicators using the data series from self.data
        self.rsi = self.I(talib.RSI, self.data.close, timeperiod=14)
        
        # Calculate pivot point and VWAP
        high = self.data.high
        low = self.data.low
        close = self.data.close
        volume = self.data.volume
        
        # Calculate pivot point for current candle
        self.current_pivot_point = (high.iloc[-1] + low.iloc[-1] + close.iloc[-1]) / 3
        
        # Calculate VWAP up to the last candle
        self.vwap = self.I(VWAP, high, low, volume, timeperiod=20)
        
    def next(self):
        """Next bar is processed"""
        if not hasattr(self, 'current_pivot_point') or not hasattr(self, 'vwap'):
            return
            
        # Check for trend reversal conditions
        if self.position and (self.rsi[-1] < 30 and self.rsi[-2] > 30):
            # Close position with take-profit
            self.position.close()
            
        elif not self.position:
            if self.rsi[-1] > 50 and (high.iloc[-1] > high.iloc[:-1].max() or low.iloc[-1] < low.iloc[:-1].min()):
                # Calculate price reversal signal
                self.position = self.buy()
                
    def stop(self):
        """Stop method is called when backtest ends"""
        pass

# Backtesting setup
def run_backtest():
    """Run backtest and return results"""
    data = pd.read_csv('/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv',
                       index_col=0, parse_dates=True)
    
    # Clean column names by stripping whitespace
    data.columns = [col.strip() for col in data.columns]
    
    if 'datetime' not in data.columns:
        return
        
    close_prices = data['close']
    volume_series = data['volume']
    
    strategy = PatrickStrategy()
    # Backtest from the start of data to end
    bt_result = bt.run(strategy, data, cash=100000)
    
    if not bt_result:
        print("No positions found")
        return
        
    else:
        stats = bt_result.stats
    
    # Print strategy statistics
    print("\nStrategy Statistics\n", stats)
    
    return stats

if __name__ == '__main__':
    run_backtest()