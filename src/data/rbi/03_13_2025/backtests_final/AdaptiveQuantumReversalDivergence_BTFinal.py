import numpy as np

class MoonDevBacktester:
    def __init__(self, strategy, data, equity=10000.0):
        self.strategy = strategy
        self.data = data
        self.equity = float(equity)
        
    def _init_indicators(self):
        # Import indicators from pandas_ta
        from pandas_ta import rsi as pandas_rsi
        from pandas_ta import atr as pandas_atr
        
        # Compute RSI and ATR for the current period
        self.rsi = pandas_rsi(self.data.close, 14)
        self.atr = pandas_atr(self.data.high, self.data.low, 14)

    def _initialize_portfolio(self):
        self.equity = 10000.0

    def _close_position(self, size, current_price):
        # Ensure units are rounded to nearest integer
        units = int(round(size))
        
        if units > 0:
            lot = abs(units)
            pip_size = self.data.current_lot * 0.0001  # Assuming standard lots
        
        slippage = float(np.random.normal(0, 5e-3)) / pip_size
        tp_sl = float(np.random.exponential(2e-2)) / pip_size
        
        if lot > 0:
            self.equity -= (slippage * lot)
        
    def _get_signal_strength(self, current_price):
        # Calculate stop-loss and take-profit as percentages of price
        slippage_pct = slippage * 100
        tp_sl_pct = (tp_sl - current_price) / current_price * 100
        
        size_pct = self.strategy.signal_pct
        if isinstance(size_pct, float):
            size_pct = round(size_pct)
        
        signal_str = str(int(size_pct)) + " " + ("up" if size_pct > 0 else "down")
        return f"{current_price:.2f} {signal_str}"
    
    def _calculate_equity(self, current_price, size_pct, slippage, tp_sl):
        # Calculate P&L for the position
        lot = self.equity * (size_pct / 100) / current_price
        
        if lot > 0:
            pips = (tp_sl - current_price) * lot
            profit = round(pips, 4)
            
            self.equity += profit
            slippage_loss = slippage * lot
            loss = round(slippage_loss, 4)
            
            if slippage_loss > 0:
                self.equity -= loss

    def run backtest(self):
        for idx in range(len(self.data)):
            current_price = self.data.close.iloc[idx]
            size = self.equity * (self.strategy.signal_pct / 100) / current_price
            if size < 0:
                continue
            
            slippage = float(np.random.normal(0, 5e-3)) / (current_price * 0.0001)
            tp_sl = float(np.random.exponential(2e-2)) / (current_price * 0.0001)
            
            if size > 0:
                self._close_position(size, current_price)
            
            signal_str = self._get_signal_strength(current_price)
            pips = abs(slippage) * 100
            profit_target = round(self.strategy.signal_pct * lot / 100, 4)
            
            if (slippage > 0 and tp_sl > 0) or (slippage < 0 and tp_sl < 0):
                self.equity += profit_target
                
            if slippage > 0:
                self.equity -= round(slippage * lot, 4)

    def _get Annual Return(self):
        return round(self.equity / self.equity_start - 1, 4) * 100