from pandas import Series

class PatrickStrategy:
    def __init__(self, data, window):
        self.data = data
        self.window = window
        
    def buy(self, price):
        # Example logic for buying
        pass
    
    def sell(self, price):
        # Example logic for selling
        pass
    
    def monthly(self):
        pass

    def yearly(self):
        pass

    def quarterly(self):
        pass

    def calculateRSI(self, close: Series) -> Series:
        return self._rsi(close)

    def calculateVWAP(self, high: Series, low: Series, volume: Series) -> Series:
        return self._vwap(high, low, volume)

    def _rsi(self, close: Series) -> Series:
        """Calculates Relative Strength Index using pandas_talib"""
        delta = closediff(close)
        up = delta.where(delta > 0, 0).mean(14)
        down = -delta.where(delta < 0, 0).mean(14)
        rs = up / down
        rsi = 100 - (100 / (1 + rs))
        return pd.Series(rsi)

    def _vwap(self, high: Series, low: Series, volume: Series) -> Series:
        """Calculates Volume-Weighted Average Price using pandas_ta"""
        vwma = ta.trendline_volume_weighted moving average(high, low, volume)
        return vwma