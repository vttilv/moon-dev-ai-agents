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
    adx_threshold = 20  # 🌙 Moon Dev Optimization: Tightened ADX threshold from 25 to 20 for stronger ranging market filter to avoid weak signals
    risk_per_trade = 0.01  # 1% risk kept for controlled exposure
    atr_multiplier_sl = 1.5  # 🌙 Moon Dev Optimization: Reduced SL multiplier from 2 to 1.5 for tighter stops, improving RR
    atr_multiplier_tp = 4.5  # 🌙 Moon Dev Optimization: Increased TP multiplier from 4 to 4.5 for better 1:3 RR to boost returns on winners

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
        
        # 🌙 Moon Dev Optimization: Added volume SMA for confirmation filter to avoid low-volume fakeouts
        self.vol_sma = self.I(talib.SMA, self.data.Volume, timeperiod=20)
        
        # 🌙 Moon Dev Optimization: Added 200-period EMA as a loose trend filter to bias longs in uptrends/shorts in downtrends for BTC's overall bias
        self.ema_200 = self.I(talib.EMA, self.data.Close, timeperiod=200)
        
        print("🌙 Moon Dev: Indicators initialized ✨")

    def next(self):
        # 🌙 Moon Dev Optimization: Added trailing stop logic for positions (trail after 1.5x ATR profit to lock in gains)
        if self.position:
            current_profit = abs(self.position.pl_pnl) / self.position.size if self.position.size != 0 else 0
            atr_val = self.atr[-1]
            trail_trigger = 1.5 * atr_val
            if current_profit > trail_trigger:
                # Trail SL to entry + 1 ATR for longs, entry - 1 ATR for shorts
                if self.position.is_long:
                    new_sl = self.position.avg_entry_price + atr_val
                    if new_sl > self.position.sl:
                        self.position.sl = new_sl
                else:
                    new_sl = self.position.avg_entry_price - atr_val
                    if new_sl < self.position.sl:
                        self.position.sl = new_sl
                print(f"🌙 Moon Dev: Trailing SL updated to {self.position.sl:.2f} 🔒")
        
        # Check for exits if in position
        if self.position.is_long:
            if (self.rsi[-1] > self.rsi_sma[-1]) or (self.stoch_k[-1] < self.stoch_sma[-1]):
                self.position.close()
                print(f"🌙 Moon Dev: Long Exit on Reversion Signal at {self.data.Close[-1]:.2f} 🚀")
            return
        elif self.position.is_short:
            if (self.rsi[-1] < self.rsi_sma[-1]) or (self.stoch_k[-1] > self.stoch_sma[-1]):
                self.position.close()
                print(f"🌙 Moon Dev: Short Exit on Reversion Signal at {self.data.Close[-1]:.2f} 🚀")
            return
        
        # Entry conditions only if no position and sufficient data
        if (not self.position) and (len(self.rsi) > 200):  # 🌙 Moon Dev Optimization: Increased data length check to 200 for EMA maturity
            if self.adx[-1] < self.adx_threshold and self.data.Volume[-1] > self.vol_sma[-1]:  # Added volume filter for higher quality entries
                
                entry_price = self.data.Close[-1]
                atr_val = self.atr[-1]
                
                # 🌙 Moon Dev Optimization: Added symmetric long entries for balance in BTC's uptrending nature
                # Long entry: RSI oversold (below SMA) + Stoch divergence (K above SMA) + above EMA200 bias
                if (self.rsi[-1] < self.rsi_sma[-1]) and (self.stoch_k[-1] > self.stoch_sma[-1]) and (entry_price > self.ema_200[-1]):
                    sl_price = entry_price - (self.atr_multiplier_sl * atr_val)
                    tp_price = entry_price + (self.atr_multiplier_tp * atr_val)
                    risk_distance = entry_price - sl_price
                    
                    equity = self.equity
                    risk_amount = equity * self.risk_per_trade
                    position_size = risk_amount / risk_distance
                    # 🌙 Moon Dev Optimization: Allow fractional sizing (0-1) for precision in crypto backtesting
                    position_size = min(position_size / entry_price, 1.0)  # Normalize to fraction of equity, cap at 100%
                    
                    if position_size > 0.01 and not np.isnan(sl_price) and not np.isnan(tp_price) and sl_price < entry_price < tp_price:
                        self.buy(size=position_size, limit=entry_price, sl=sl_price, tp=tp_price)
                        print(f"🌙 Moon Dev: Long Entry at {entry_price:.2f}, Size: {position_size:.4f}, SL: {sl_price:.2f}, TP: {tp_price:.2f} ✨")
                    else:
                        print("🌙 Moon Dev: Invalid long position size or SL/TP levels, skipping entry ⚠️")
                    return
                
                # Short entry: RSI overbought (above SMA) + Stoch divergence (K below SMA) + below EMA200 bias
                if (self.rsi[-1] > self.rsi_sma[-1]) and (self.stoch_k[-1] < self.stoch_sma[-1]) and (entry_price < self.ema_200[-1]):
                    sl_price = entry_price + (self.atr_multiplier_sl * atr_val)
                    tp_price = entry_price - (self.atr_multiplier_tp * atr_val)
                    risk_distance = sl_price - entry_price
                    
                    equity = self.equity
                    risk_amount = equity * self.risk_per_trade
                    position_size = risk_amount / risk_distance
                    position_size = min(position_size / entry_price, 1.0)  # Normalize to fraction
                    
                    if position_size > 0.01 and not np.isnan(sl_price) and not np.isnan(tp_price) and tp_price < entry_price < sl_price:
                        self.sell(size=position_size, limit=entry_price, sl=sl_price, tp=tp_price)
                        print(f"🌙 Moon Dev: Short Entry at {entry_price:.2f}, Size: {position_size:.4f}, SL: {sl_price:.2f}, TP: {tp_price:.2f} ✨")
                    else:
                        print("🌙 Moon Dev: Invalid short position size or SL/TP levels, skipping entry ⚠️")

# Run backtest
bt = Backtest(df, DivergentReversion, cash=1000000, commission=0.002, exclusive_orders=True, trade_on_close=True)

print("🌙 Moon Dev: Running backtest... 🚀")
stats = bt.run()
print(stats)