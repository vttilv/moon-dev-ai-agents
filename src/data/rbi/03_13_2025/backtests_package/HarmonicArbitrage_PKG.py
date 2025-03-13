import pandas as pd
from backtrader import Cerebro, Strategy
from backtrader.data import DataProvider
from pandas_ta import fibonacci

class DynamicBreakoutWithinFib(Strategy):
    params = (
        ('risk_percentage', 2),
        ('position_size', 'all'),
        ('stop_loss_distance', 10),
    )

    def __init__(self):
        self.position_size = self.params.position_size
        self.risk_percentage = self.params.risk_percentage
        self.stop_loss_distance = self.params.stop_loss_distance

        # Initialize indicators using pandas_ta
        self.macd, self.signal_line, self Histograms = self._calculate_talib_indicators()
        self.fib_levels = self.calculate_fib_levels()

    def _calculate_talib_indicators(self):
        close = pd.Series(self.data.close)
        macd, signal, hist = ta.MACD(close, fastperiod=12, slowperiod=26, signalperiod=9)
        return (macd, signal, hist)

    def calculate_fib_levels(self):
        close = pd.Series(self.data.close)
        max_close = close.max()
        min_close = close.min()
        
        total_range = max_close - min_close
        fib_23 = max_close - total_range * 0.236
        fib_38 = max_close - total_range * 0.382
        fib_50 = max_close - total_range * 0.5
        fib_61 = max_close - total_range * 0.618
        
        return [fib_23, fib_38, fib_50, fib_61]

    def next(self):
        if self.position:
            current_price = self.data.close[0]
            stop_loss = abs(current_price - self.position.close)
            
            risk = (self.risk_percentage / 100) * stop_loss
            lot_size = round(risk * 100 / (current_price - self.position.close), 2)
            
            if lot_size > 0:
                self.position.close()
                self.position.size = int(lot_size)
                self.position.open()

    def populate_risk_management(self):
        pass

def backtest():
    cerebro = Cerebro()
    cerebro.addstrategy(DynamicBreakoutWithinFib)
    
    # Add your data provider here
    cerebro.load_data(symbols='^DJI', from_date='2023-01-01', to_date='2023-12-31')
    
    cerebro.run()
    cerebro.plot()

if __name__ == '__main__':
    backtest()