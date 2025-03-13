import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import backtrader as bt
import talib as ta
import random

class Backtester:
    """Backtester class with data handling and indicators"""
    
    def __init__(self, data_path):
        self.data = pd.read_csv(data_path)
        self.data.columns = self.data.columns.str.strip().str.lower()
        self.data = self.data.drop(columns=[col for col in self.data.columns if 'unnamed' in col.lower()])
        
        # Ensure proper column mapping
        required_columns = ['open', 'high', 'low', 'close', 'volume']
        self.data = self.data[required_columns]
        
    def getindicators(self):
        """Calculate indicators"""
        close = self.data['close'].values
        volume = self.data['volume'].values
        
        # MACD Oscillator (Adaptive)
        macd, macdsignal, macdhist = ta.MACD(close, fastperiod=20, slowperiod=30, signalperiod=10)
        
        # Machine Learning Model predictions
        n = len(self.data)
        mlm_predictions = np.random.uniform(-1, 1, size=n)  # Random dummy data
        
        return macd, macdsignal, macdhist, mlm_predictions

class AdaptiveDivergence(bt.Strategy):
    """Adaptive Divergence trading strategy"""
    
    params = (
        ('macd_length', 20),
        ('mlm_threshold', 0.5),
        ('risk_threshold', 10),
        ('stop_loss_units', 5)
    )
    
    def __init__(self):
        self macd_length = self.params['macd_length']
        self.mlm_threshold = self.params['mlm_threshold']
        self.risk_threshold = self.params['risk_threshold']
        self.stop_loss_units = self.params['stop_loss_units']
        
        # Initialize indicators
        self.macd, self.macdsignal, self.macdhist = self.getindicators()
        
    def getmacd(self):
        """Get MACD values"""
        return self(macd=self.macd, macdsignal=self.macdsignal)
    
    def getmlm(self):
        """Get Machine Learning Model predictions"""
        return np.random.uniform(-1, 1, size=len(self.data))
    
    def __enter__(self):
        """Initialize strategy variables"""
        self.position = None
        self Entered = False
        
        # Initialize indicators reference
        self.macd_ref = None
        self.macdsignal_ref = None
        self.macdhist_ref = None
        
        return self
    
    def next(self):
        """Next iteration logic"""
        if not selfpositioned() or position().size != 1:
            return
            
        # Calculate divergence percentage
        close_diff = (self.data['close'][-1] - self.data['close'][-2]) / self.data['close'][-2]
        macd_diff = (self.macd[-1] - self.macd[-2]) / self.macd[-2]
        
        divergence_percent = abs(close_diff - macd_diff) * 100
        
        # Get ML predictions for current period
        mlm_pred = self.mlmpreds[-1 if len(self.mlmpreds) > 0 else 0]
        
        if divergence_percent > self.mlm_threshold and (mlm_pred > 0 or self.macdsignal[-2] < self.macdhist[-2]):
            if not self positioned() or self.position.size != 1:
                return
            
            # Calculate stop loss
            stop_loss = self.data['close'][-1] * (1 - (self.risk_threshold / 100))
            
            # Place stop loss order
            self.position.close()
            
        elif divergence_percent < -self.mlm_threshold and (mlm_pred < 0 or self.macdsignal[-2] > self.macdhist[-2]):
            if not self.positioned() or self.position.size != 1:
                return
            
            # Calculate stop loss
            stop_loss = self.data['close'][-1] * (1 + (self.risk_threshold / 100))
            
            # Place stop loss order
            self.position.close()
    
    def run(self):
        """Run the backtester"""
        print("\nStarting backtesting...")
        start = datetime.now() - timedelta(days=365)
        
        # Initialize backtester
        bt = Backtester(self.data_path)
        test cerebro = bt.Cerebro()
        test cerebro.loadstrats(AdaptiveDivergence)
        test cerebro.addind(bt.macd)
        test cerebro.addind(bt.macdsignal)
        test cerebro.addind(bt.macdhist)
        test cerebro.addind(bt.mlmpreds)
        
        # Run backtester
        stats = test cerebro.run(
            start=start,
            end=datetime.now(),
            cerebro=True,
            loglevel=bt.LOGLEVEL Lowest,
            plot=1,
            plot_mode='ilogy',
            stdout=False
        )
        
        print("\nBacktesting complete. Printing results...")
        bt.printstats(stats)
        print("\nStrategy closed.")

if __name__ == '__main__':
    AdaptiveDivergence().run()