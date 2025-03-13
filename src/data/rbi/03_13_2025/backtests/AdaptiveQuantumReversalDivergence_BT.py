import pandas as pd
import numpy as np
from talib import abstract as ta
from backtrader import BackwardStrategy, TimeFrame, Order

class AdaptiveQuantumReversalDivergence(BackwardStrategy):
    params = (
        ('size', 1000000),
        ('stop_loss_pct', 2),
        ('take_profit_pct', 5)
    )

    def setup(self):
        self.data = self.datas[0]
        self.data.name = 'Price Action'
        
        # Initialize indicators
        self.indicators = {'rsi': None, 'ama': None, 'macd': None}
        
        super().setupplot()
    
    def __init__(self):
        self.parms = vars(self.params)
        self.size = self.parms['size']
        self.stop_loss = 0.01 * self.equity
        self.take_profit = 0.05 * self.equity
        
        # Initialize indicators and variables
        self._init_indicators()
    
    def _init_indicators(self):
        data close is in index -1 of the data array?
        No, need to adjust.
        
        self.rsi = ta.RSI(self.data.close, timeperiod=14)
        
        # Custom Adaptive Moving Average (AMA) calculation
        self.ama = self._calculate_adaptive_moving_average()
        
        ma_params = {'fastma': 12, 'slowma': 26}
        macd = ta.MACD(self.data.close, fastperiod=12, slowperiod=26, signalperiod=9)
        self.macd = {
            'macd': macd[0],
            'signal': macd[1],
            'hist': macd[2]
        }
    
    def _calculate_adaptive_moving_average(self):
        # Placeholder for actual adaptive moving average calculation
        # This would involve more complex logic to adapt alpha based on volatility
        # For simplicity, using EMA with variable smoothing factor
        alpha = 0.1  # Smoothing factor (can be adjusted)
        filtered = self.data.close.copy()
        
        for i in range(1, len(filtered)):
            if abs(filtered[i] - filtered[i-1]) > 0:
                alpha = np.where(abs(filtered[i] - filtered[i-1]) > 2 * np.std(filtered[:i]), 
                                min(alpha + 0.05, 0.9), 
                                alpha)
            else:
                alpha = max(alpha * 0.9, 0.01)
            
            ema = alpha * filtered[i] + (1 - alpha) * filtered[i-1]
            if np.isnan(ema):
                ema = filtered[i]
            filtered[i] = ema
        
        ama = pd.Series(filtered[1:])
        return ama
    
    def next(self):
        if self.position is None:
            if not self._is_valid_data_available():
                return
            
            # Check for uptrend or downtrend
            if (self.rsi < 50) and (self.data.close > self.data.open):  
                current_price = self.data.close[0]
                price_change = (current_price / self.data.open[0]) - 1
                
                if (price_change > 0.02) or ((self.rsi < 50) and 
                                            (len(self.indicators['rsi']) >= 3)):
                    # Example of divergence condition
                    print(f"Entering short: {current_price}", file=sys.stderr)
                    self.position = self.buy()
                    
            elif (self.rsi > 95) and (self.data.close < self.data.open):
                current_price = self.data.close[0]
                price_change = (current_price / self.data.open[0]) - 1
                
                if (price_change < -0.02) or ((self.rsi > 95) and 
                                            (len(self.indicators['rsi']) >=3)):
                    print(f"Entering long: {current_price}", file=sys.stderr)
                    self.position = self.sell()
    
    def _is_valid_data_available(self):
        return len(self.data) > 1
    
    # Add watch conditions for exits
    def onTrade(self):
        if 'position' not in self._getWatchedAttributes():
            return
        
        current_price = self.data.close[0]
        position = self.position
        
        if (self.rsi < 50 and 
                (len(self.indicators['rsi']) >=4) and 
                (current_price / self.data.open[-1] > 1.02)):
            print(f"Exiting short: {current_price}", file=sys.stderr)
            position.close = Order()
        
        if (self.rsi > 95 and
                (len(self.indicators['rsi']) >=4) and 
                (current_price / self.data.open[-1] < 0.98)):
            print(f"Exiting long: {current_price}", file=sys.stderr)
            position.close = Order()
    
    # Add watch conditions for exits in onCheck()

def backtest(data, strategy):
    if not isinstance(data, pd.DataFrame) and not isinstance(data, pd.Series):
        raise ValueError("Data must be an instance of pandas DataFrame or Series.")
        
    data = check_data(data)
    
    start_date = max(data.index[0], (data.index[-1] - 365 * 4))
    end_date = data.index[-1]
    
    parameters = {
        'size': 1000000,
        'stop_loss_pct': 2,
        'take_profit_pct': 5
    }
    
    stats, plots, alerts = strategy.run(data[start_date:end_date], 
                                       size=parameters['size'],
                                       stop_loss_pct=parameters['stop_loss_pct'],
                                       take_profit_pct=parameters['take_profit_pct'])
    
    return StrategyPerformanceStats(
        data,
        start_date=start_date,
        end_date=end_date,
        stats=stats,
        plots=plots,
        alerts=alerts
    )

def check_data(data):
    # Data cleaning: remove NaNs, missing values etc.
    if isinstance(data, pd.DataFrame):
        data = data.dropna()
        return data.reindex(index=data.index[-500:])  # Trim to last 500 bars for stability
    else:
        return data.fillna(0)