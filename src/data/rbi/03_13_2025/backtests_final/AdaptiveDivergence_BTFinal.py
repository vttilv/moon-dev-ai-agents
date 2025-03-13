# -*- coding: utf-8 -*-
import backtrader as bt
from . import AdaptiveDivergenceStrategy

class AdaptiveDivergence(bt.Strategy, AdaptiveDivergenceStrategy):
    params = dict(
        period=250,
        volatility_threshold=1.645,  # One standard deviation
        min_divergence=30,
    )

    def load_data(self):
        return super().load_data()

    def _load_indicators(self):
        bars = self.data.load()
        close = [bar.close for bar in bars]
        
        macd = []
        macdsignal = []
        macdhist = []
        prev_macd = 0
        
        for bar in bars:
            ema_short = bt.ind.EMA(bar.close, period=26)
            ema_long = bt.ind.EMA(ema_short, period=9)
            
            macd_val = ema_long - ema_short
            macdsignal_val = bt.ind.EMA(macd_val, 26 / (1 + 4))
            hist = macd_val - macdsignal_val
            
            macd.append(macd_val)
            macdsignal.append(macdsignal_val)
            macdhist.append(hist)
            
        self._close = close
        self._macd = macd
        self._macdsignal = macdsignal
        self._macdhist = macdhist

    def getmacd(self):
        return (
            self._close,
            self._macd,
            self._macdsignal,
            self._macdhist,
        )

    def next(self):
        super().next()
        
        if not self._close:
            return
            
        self.load_data()
        close = self._close
        macd, macdsignal, macdhist = self.getmacd()

        divergence = (macd[-1] > 0 and 
                     (macdsignal[-2] - macdsignal[-1]) < 0) or \
                    (macd[-1] < 0 and 
                     (macdsignal[-2] - macdsignal[-1]) > 0)

        if divergence:
            self._calculate_position_size()
            
    def _calculate_position_size(self, current_equity):
        position_size = 0.01  # Default to 1% of equity
        volatility = bt.ind.Bollinger Bands(current_equity, period=20)[1]
        
        if volatility > 1:
            position_size = min(0.5, position_size / (volatility ** 2))
        elif volatility < 1:
            position_size = max(0.5, position_size * (volatility ** 2))

        size = int(current_equity * position_size) if self.params.position_type == 'integer' else current_equity * position_size
        if size > 0:
            self._execute_stop_loss(size)

    def _execute_stop_loss(self, size):
        stop_price = self.data.close
        self.buy(limit_price=stop_price - 1, exectype='market', size=size)
        self.sell(limit_price=stop_price + 1, exectype='market', size=size)

# Example usage:
if __name__ == '__main__':
    cerebro = bt.Cerebro()
    cerebro.addstrategy(AdaptiveDivergence)
    cerebro.broker.setcash(100000)
    
    # Add data
    data =bt.data.YahooData(
        dataloader='quandl',
        name='MSFT',
        from_='2000-01-01',
        to_='2023-12-31',
        reverse=True,
        adjust=True
    )
    cerebro.load(data)
    
    cerebro.run()
    print('Final Equity:', cerebro.broker.getequity())

# Add logging and debug statements with the moon theme 🌙
if __name__ == '__main__':
    log = []
    def append_log(msg):
        log.append(f"✨ {msg} ✨")
        
    # Add more logging utility here...
    print = lambda *args, **kwargs: None  # Disable normal printing for a cleaner output