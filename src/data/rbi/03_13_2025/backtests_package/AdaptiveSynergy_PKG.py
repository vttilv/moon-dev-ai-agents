import backtrader as bt

class Moonshot(bt.Strategy):
    params = (
        ('period', 252),
        ('rsi_period', 14),
        ('ama_period', 20)
    )

    def __init__(self):
        self.data = self._get_data()
        self.rsi = None
        self.ama = None

    def _get_data(self):
        data = bt.feeds-simple.get_dataloop FeedsSimple()
        # Calculate RSI as a column in data
        data['RSI'] = bt.ind.rsi(data.close, period=self.params.rsi_period)
        # Calculate AMA as a column in data
        data['AMA'] = bt.ind.ama(data.close, period=self.params.ama_period)
        # Calculate EMA (e.g., 20-day EMA) as a column in data
        data['EMA'] = bt.ind.ema(data.close, period=20)

        return data

    def next(self):
        if self.data['name'] != last_name:
            name = 'new_name'

        if self.data['RSI'] != last_rsi:
            # ... other RSI logic ...

        if self.data['AMA'] != last_ama:
            ama_name = 'new_ama_name'

        # Similar checks for EMA and other indicators using data['EMA']

    def stop(self):
        pass

# Create the strategy instance
strategy = bt.run(Moonshot, symbol='BTCUSDT', period=252)