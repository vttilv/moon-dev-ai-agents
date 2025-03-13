import pandas as pd
import numpy as np
from talib import abstract as ta
from datetime import datetime, timedelta

# Import data handling functions from backtesting.py
from backtesting import Backtest

# Add Moon Dev themed imports and logging
from moon.dev.Enums import Strategy, Trade
from moon.dev.Log import logger

class AdaptiveDivergence(Strategy):
    def __init__(self, rsi_period=14, ema_period=20, dea_period=9, macd_period=26, macdo_period=9):
        self.rsi_period = rsi_period
        self.ema_period = ema_period
        self.dea_period = dea_period
        self.macd_period = macd_period
        self.macdo_period = macdo_period

    def calculateIndicators(self, data):
        # RSI
        rsi = ta.RSI(data['close'], timeperiod=self.rsi_period)
        
        # EMA
        ema_short = self.I(ta.EMA, data['close'], timeperiod=self.ema_period)
        ema_long = self.I(ta.EMA, data['close'], timeperiod=self.ema_period*2)
        
        # DEA (Difference between 2 EMAs)
        dea = self.I(ta.EMA, ema_short, timeperiod=self.dea_period)
        
        macd, macdsignal, macdhist = self.I(ta.MACD, data['close'], 
                                             fastperiod=self.macd_period,
                                             slowperiod=self.macdo_period,
                                             signalperiod=9)
        
        # MACD Histogram (for divergence)
        macddiv = self.I(ta.DIF, macdhist, 1)

        return {
            'RSI': rsi,
            'EMA_Short': ema_short,
            'EMA(Long)': ema_long,
            'DEA': dea,
            'MACD': macd,
            'MACDSignal': macdsignal,
            'MACDHist': macdhist,
            'MACDDiff': macddiv
        }

    def populateIndicators(self, data):
        # Calculate indicators
        self.data = data.copy()
        indicator_data = self.calculateIndicators(data)
        
        # Store calculated values in the DataFrame
        for ind, value in indicator_data.items():
            setattr(self, ind, value)

    def setParameters(self, params):
        self.rsi_period = params.get('rsi_period', 14)
        self.ema_period = params.get('ema_period', 20)
        self.dea_period = params.get('dea_period', 9)
        self.macd_period = params.get('macd_period', 26)
        self.macdo_period = params.get('macdo_period', 9)

    def iseligible(self, data):
        # Only proceed if we have sufficient data
        return len(data) >= 30
    
    def goLong(self, size=1_000_000):
        # Calculate position size with safety
        entry_price = self.data.iloc[-1]['close']
        
        # Ensure size is an integer
        size = int(round(size))
        
        if size > 0:
            stop_loss = entry_price * (1 - 0.02)  # 2% stop loss
            take_profit = entry_price * 1.05       # 5% take profit
            
            logger.info(f"Going long with size: {size}, Entry Price: {entry_price}")
            
            return {
                'action': 'long',
                'size': size,
                'enter_at': entry_price,
                'exit_at': None,
                'stop_loss': stop_loss,
                'take_profit': take_profit
            }
    
    def goShort(self, size=1_000_000):
        entry_price = self.data.iloc[-1]['close']
        
        # Ensure size is an integer
        size = int(round(size))
        
        if size > 0:
            stop_loss = entry_price * (1 + 0.02)  # 2% stop loss
            take_profit = entry_price * 0.95       # 5% take profit
            
            logger.info(f"Going short with size: {size}, Entry Price: {entry_price}")
            
            return {
                'action': 'short',
                'size': size,
                'enter_at': entry_price,
                'exit_at': None,
                'stop_loss': stop_loss,
                'take_profit': take_profit
            }
    
    def next(self):
        # Check if we have enough bars to use indicators
        if len(self.data) < 30:
            return
        
        # Simplified logic - you can expand this based on your strategy rules
        current_price = self.data.iloc[-1]['close']
        
        # Example long entry condition (RSI divergence)
        rsi = self.RSI[-1]
        macddiv = self.MACDDiff[-1]  # Simplified MACD divergence logic
        
        if (rsi > 50 and rsi < self.rsi_period - rsi) and (macddiv > 0):
            # Potential long signal
            logger.info(f"Long potential: RSI {rsi}, MACD Diff {macddiv}")
            
            # Execute long trade with calculated size if eligible
            if self.iseligible(self.data):
                return self.goLong(size=1_000_000)
        
        # Example short entry condition (RSI divergence in the opposite direction)
        rsi = self.RSI[-1]
        macddiv = self.MACDDiff[-1]  # Simplified MACD divergence logic
        
        if (rsi < 50 and rsi > self.rsi_period - rsi) and (macddiv < 0):
            logger.info(f"Short potential: RSI {rsi}, MACD Diff {macddiv}")
            
            # Execute short trade with calculated size if eligible
            if self.iseligible(self.data):
                return self.goShort(size=1_000_000)
    
    def stop(self):
        pass

# Initialize backtester and run the strategy
backtest = Backtest(AdaptiveDivergence, 
                   AdaptiveDivergence.EMA(20),
                   population_size=30,
                   tournament_count=50,
                   num_generations=10)

result = backtest.run()

if result:
    print(f"\n\nFinal Result - {result}")