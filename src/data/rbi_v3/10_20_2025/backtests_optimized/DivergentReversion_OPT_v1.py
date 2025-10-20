import pandas as pd
import talib
import numpy as np
from backtesting import Backtest, Strategy

# Load data
data_path = '/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv'
df = pd.read_csv(data_path)

# Clean column names
df.columns = df.columns.str.strip().str.lower()

# Drop any unnamed columns
df = df.drop(columns=[col for col in df.columns if 'unnamed' in col.lower()])

# Set datetime as index
df = df.set_index(pd.to_datetime(df['datetime']))

# Rename columns properly
df.rename(columns={'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close', 'volume': 'Volume'}, inplace=True)

# Sort index to ensure chronological order
df = df.sort_index()

# Ensure required columns
print("🌙 Moon Dev: Data loaded and cleaned. Shape:", df.shape)
print("Columns:", df.columns.tolist())

class DivergentReversion(Strategy):
    adx_threshold = 20  # Tightened from 25 to focus on stronger ranging markets for better reversion setups
    risk_per_trade = 0.02  # Increased from 1% to 2% to amplify returns while still managing risk
    atr_multiplier_sl = 2
    atr_multiplier_tp = 6  # Increased from 4 to 6 for 1:3 RR (tighter risk control with higher reward potential)

    def init(self):
        # RSI(20)
        self.rsi = self.I(talib.RSI, self.data.Close, timeperiod=20)
        self.rsi_sma = self.I(talib.SMA, self.rsi, timeperiod=20)
        
        # Stochastic %K(8)
        self.stoch_k, _ = self.I(talib.STOCH, self.data.High, self.data.Low, self.data.Close,
                                  fastk_period=8, slowk_period=1, slowd_period=1)
        self.stoch_sma = self.I(talib.SMA, self.stoch_k, timeperiod=20)
        
        # ATR(14) for dynamic stops
        self.atr = self.I(talib.ATR, self.data.High, self.data.Low, self.data.Close, timeperiod=14)
        
        # ADX(14) for trend filter
        self.adx = self.I(talib.ADX, self.data.High, self.data.Low, self.data.Close, timeperiod=14)
        
        # Volume SMA for entry filter (added to avoid low-volume false signals)
        self.volume_sma = self.I(talib.SMA, self.data.Volume, timeperiod=20)
        
        print("🌙 Moon Dev: Indicators initialized ✨")

    def next(self):
        # Check for exits first if in position
        if self.position.is_long:
            # Exit long on reversion signal (RSI becomes overbought or Stoch becomes oversold)
            if (self.rsi[-1] > self.rsi_sma[-1]) or (self.stoch_k[-1] < self.stoch_sma[-1]):
                self.position.close()
                print(f"🌙 Moon Dev: Long Exit on Reversion Signal at {self.data.Close[-1]:.2f} 🚀")
            return
        
        if self.position.is_short:
            # Exit short on reversion signal (RSI becomes oversold or Stoch becomes overbought)
            if (self.rsi[-1] < self.rsi_sma[-1]) or (self.stoch_k[-1] > self.stoch_sma[-1]):
                self.position.close()
                print(f"🌙 Moon Dev: Short Exit on Reversion Signal at {self.data.Close[-1]:.2f} 🚀")
            return
        
        # Entry conditions (only if no position and sufficient history)
        if (not self.position) and (len(self.rsi) > 20) and (self.adx[-1] < self.adx_threshold) and (self.data.Volume[-1] > self.volume_sma[-1]):
            
            entry_price = self.data.Close[-1]
            atr_val = self.atr[-1]
            risk_amount = self.equity * self.risk_per_trade
            
            # Long entry: RSI oversold but Stoch overbought (divergence for upside reversion)
            if (self.rsi[-1] < self.rsi_sma[-1]) and (self.stoch_k[-1] > self.stoch_sma[-1]):
                sl_price = entry_price - (self.atr_multiplier_sl * atr_val)
                tp_price = entry_price + (self.atr_multiplier_tp * atr_val)
                risk_distance = entry_price - sl_price
                
                position_size = risk_amount / risk_distance
                position_size = int(round(position_size))
                
                # Check validity for long
                if position_size > 0 and not np.isnan(sl_price) and not np.isnan(tp_price) and sl_price < entry_price < tp_price:
                    self.buy(size=position_size, limit=entry_price, sl=sl_price, tp=tp_price)
                    print(f"🌙 Moon Dev: Long Entry at {entry_price:.2f}, Size: {position_size}, SL: {sl_price:.2f}, TP: {tp_price:.2f} ✨")
                else:
                    print("🌙 Moon Dev: Invalid position size or SL/TP levels for long, skipping entry ⚠️")
                return
            
            # Short entry: RSI overbought but Stoch oversold (divergence for downside reversion)
            elif (self.rsi[-1] > self.rsi_sma[-1]) and (self.stoch_k[-1] < self.stoch_sma[-1]):
                sl_price = entry_price + (self.atr_multiplier_sl * atr_val)
                tp_price = entry_price - (self.atr_multiplier_tp * atr_val)
                risk_distance = sl_price - entry_price
                
                position_size = risk_amount / risk_distance
                position_size = int(round(position_size))
                
                # Check validity for short
                if position_size > 0 and not np.isnan(sl_price) and not np.isnan(tp_price) and tp_price < entry_price < sl_price:
                    self.sell(size=position_size, limit=entry_price, sl=sl_price, tp=tp_price)
                    print(f"🌙 Moon Dev: Short Entry at {entry_price:.2f}, Size: {position_size}, SL: {sl_price:.2f}, TP: {tp_price:.2f} ✨")
                else:
                    print("🌙 Moon Dev: Invalid position size or SL/TP levels for short, skipping entry ⚠️")

# Run backtest
bt = Backtest(df, DivergentReversion, cash=1000000, commission=0.002, exclusive_orders=True, trade_on_close=True)

print("🌙 Moon Dev: Running backtest... 🚀")
stats = bt.run()
print(stats)