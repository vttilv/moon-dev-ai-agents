import backtrader as bt
from backtrader.feeds import get_dataloop


class Moonshot(bt.Strategy):
    params = (
        ('period', 252),
        ('rsi_period', 14),
        ('ama_period', 20)
    )

    def __init__(self):
        """Initializes the strategy and sets up data feeding."""
        self.data = self._get_data()
        self.rsi = None
        self.ama = None

    def _get_data(self):
        """Fetches and processes market data."""
        data = get_dataloop()  # Fixed import and removed extra spaces
        data['RSI'] = bt.ind.rsi(data.close, period=self.params.rsi_period)
        data['AMA'] = bt.ind.ama(data.close, period=self.params.ama_period)
        data['EMA'] = bt.ind.ema(data.close, period=20)

        return data

    def next(self):
        """Handles each trading bar."""
        # Removed reference to last_* variables as they are not defined
        # Key logic remains: check for trend reversals based on indicators
        
        if self.data['RSI'] < 30 and self.data['EMA'] < self.data['RSI']:
            print(f"Strong bullish signal - RSI {self.data.RSI:.2f} EMA {self.data.EMA:.2f}")
        
        if self.data['RSI'] > 70 and self.data['EMA'] > self.data['RSI']:
            print(f"Strong bearish signal - RSI {self.data.RSI:.2f} EMA {self.data.EMA:.2f}")

        # Similar logic can be added for other indicators like AMA and EMA
        if self.data['AMA'] < 0.5:
            print(f"AMA divergence warning: {self.data.AMA:.2f}")
            
        if self.data['AMA'] > 1.5:
            print(f"AMA divergence warning: {self.data.AMA:.2f}")

    def stop(self):
        """Cancels the strategy when close() is called."""
        pass


# Create and run the strategy
strategy = bt.run(Moonshot, symbol='BTCUSDT', period=252)