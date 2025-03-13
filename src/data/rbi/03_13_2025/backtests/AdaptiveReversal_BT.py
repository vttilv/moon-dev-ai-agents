import pandas as pd
import numpy as np
from talib import abstract as ta
from backtrader import Strategy, BTParameters, notifyStrategy, get_data_api
from backtrader.data import Data feed
from moon.dev.backtest import BaseStrategy

# Strategy class inheriting from BaseStrategy
class AdaptiveReversal(Strategy, BaseStrategy):
    # Define the parameters our strategy requires
    params = (
        ('period', BTParameters(period=20)),
        ('volatility_period', BTParameters(volatility_period=14)),
        ('risk_parameter', 1),
    )

    def __init__(self):
        # Initialize the indicators and position sizing logic
        self.volatility_indicator = self.I(ta.BBANDS, self.data.close, timeperiod=self.params.period.value)[2]
        self.position_size = self.size * (self.volatility_indicator[0] / 100)
        self.position_size = int(round(self.position_size))

    def next(self):
        # Override the default next() to implement our strategy logic
        try:
            if not hasattr(self, 'spread'):
                return

            if not hasattr(self, 'current_position'):
                return
            
            if not hasattr(self, 'position_size'):
                return
            
            if self.position_size > 0 and self.spread <= 2:
                self.position_size = int(round(self.size * (self.volatility_indicator[0] / 100)))
                
                # Close any existing position before opening a new one
                if self.current_position > 0:
                    self.position_size = -int(abs(self.current_position))
                
                self.current_position = self.position_size
                
                if abs(self.position_size) > 0:
                    self.buy(size=self.position_size)
            
            elif self.spread >= 2 and self.current_position < 0:
                if self.position_size != int(round(self.size * (self.volatility_indicator[0] / 100))):
                    self.position_size = -int(round(self.size * (self.volatility_indicator[0] / 100)))
                    
                    # Close any existing position before opening a new one
                    if self.current_position > 0:
                        self.position_size = -int(abs(self.current_position))
                    
                    self.current_position = self.position_size
                    
                    if abs(self.position_size) > 0:
                        self.sell(size=self.position_size)
            
            elif self.spread >= 2 and self.current_position == 0:
                pass
            
            else:  # Spread is within the threshold
                if self.position_size != int(round(self.size * (self.volatility_indicator[0] / 100))):
                    self.position_size = int(round(self.size * (self.volatility_indicator[0] / 100)))
                    
                    # Close any existing position before opening a new one
                    if self.current_position > 0:
                        self.position_size = -int(abs(self.current_position))
                    
                    self.current_position = self.position_size
                    
                    if abs(self.position_size) > 0:
                        self.sell(size=self.position_size)
        except Exception as e:
            notifyStrategy(f"Error in AdaptiveReversal strategy: {str(e)}")

    def get_data_api(self, feed):
        try:
            return super().get_data_api(feed)
        except Exception as e:
            notifyStrategy(f"Error in getting data API: {str(e)}")

    def init(self):
        # Process the initial data
        self.data = self feeds[0]

        # Rename columns to match Backtrader's expectations
        df = self.data._get_data()
        if 'datetime' in df.columns:
            df.rename(columns={'datetime': 'date'}, inplace=True)
        
        cols = ['open', 'high', 'low', 'close', 'volume']
        if all(col in df.columns for col in cols):
            df.dropna(subset=cols, axis=0, inplace=True)
            
        self.data = Datafeed feed(self.data._get_data,
                                 fromdate=self.data[0].datetime,
                                 todate=self.data[-1].datetime,
                                 reverse=False)

    def get_bars(self, count=250):
        return super().get_bars(count=count)

# Set up the backtester class
backtester = Backtester(
    startdate="2013-01-01",
    enddate="2024-12-31",
    strategy_class=AdaptiveReversal,
    data feeds=[btFEEDStrategy],
    cash=100000,
    commission=COMMISSION_FEE
)

# Run the backtest and print results
backtester.run()
backtester.print()