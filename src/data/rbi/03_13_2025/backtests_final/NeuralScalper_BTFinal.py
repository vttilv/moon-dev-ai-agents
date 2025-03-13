from pandas import Series
import pandas_ta as ta  # Ensure pandas_ta is imported

class PatrickStrategy:
    def __init__(self, data, window):
        self.data = data
        self.window = window
        
    def buy(self, price):
        print(f"DEBUG: Potential BUY signal detected at price {price}")
        pass
    
    def sell(self, price):
        print(f"DEBUG: Potential SELL signal detected at price {price}")
        pass
    
    def monthly(self):
        print("DEBUG: Monthly evaluation trigger")
        pass
    
    def yearly(self):
        print("DEBUG: Yearly evaluation trigger")
        pass
    
    def quarterly(self):
        print("DEBUG: Quarterly evaluation trigger")
        pass

    def calculateRSI(self, close: Series) -> Series:
        """Calculates Relative Strength Index using pandas_talib"""
        print(f"DEBUG: Calculating RSI for {len(close)} periods")
        delta = close.diff()
        up = delta.where(delta > 0, 0).mean(14)
        down = -delta.where(delta < 0, 0).mean(14)
        rs = up / down
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def calculateVWAP(self, high: Series, low: Series, volume: Series) -> Series:
        """Calculates Volume-Weighted Average Price using pandas_ta"""
        print(f"DEBUG: Calculating VWAP for {len(high)} periods")
        vwma = ta.trendline_volume_weighted(high, low, volume)
        return vwma

    def _rsi(self, close: Series) -> Series:
        """Calculates Relative Strength Index using pandas_talib"""
        print(f"DEBUG: Calculating intermediate RSI values")
        delta = close.diff()
        up = delta.where(delta > 0, 0).mean(14)
        down = -delta.where(delta < 0, 0).mean(14)
        rs = up / down
        rsi = 100 - (100 / (1 + rs))
        return pd.Series(rsi)

    def _vwap(self, high: Series, low: Series, volume: Series) -> Series:
        """Calculates Volume-Weighted Average Price using pandas_ta"""
        print(f"DEBUG: Calculating VWAP intermediate values")
        vwma = ta.trendline_volume_weighted(high, low, volume)
        return pd.Series(vwma)

    def _vwap(self, high: Series, low: Series, volume: Series) -> Series:
        """Calculates Volume-Weighted Average Price using pandas_ta"""
        print(f"DEBUG: Final VWAP calculation")
        vwma = ta.trendline_volume_weighted(high, low, volume)
        return pd.Series(vwma)