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
    adx_threshold = 20  # 🌙 Moon Dev: Tightened ADX threshold for stricter ranging market filter to avoid weak trends
    risk_per_trade = 0.01  # 1% risk kept for solid risk management
    atr_multiplier_sl = 2
    atr_multiplier_tp = 6  # 🌙 Moon Dev: Increased TP multiplier to 6 for 1:3 RR, allowing winners to run longer for higher returns

    def init(self):
        # RSI(20)
        self.rsi = self.I(talib.RSI, self.data.Close, timeperiod=20)
        self.rsi_sma = self.I(talib.SMA, self.rsi, timeperiod=20)
        
        # Stochastic %K(8) - kept fast params but now used symmetrically
        self.stoch_k, _ = self.I(talib.STOCH, self.data.High, self.data.Low, self.data.Close,
                                  fastk_period=8, slowk_period=1, slowd_period=1)
        self.stoch_sma = self.I(talib.SMA, self.stoch_k, timeperiod=20)
        
        # ATR(14) for dynamic stops
        self.atr = self.I(talib.ATR, self.data.High, self.data.Low, self.data.Close, timeperiod=14)
        
        # ADX(14) for trend filter
        self.adx = self.I(talib.ADX, self.data.High, self.data.Low, self.data.Close, timeperiod=14)
        
        # 🌙 Moon Dev: Added volume SMA for confirmation filter to enter only on above-average volume setups
        self.vol_sma = self.I(talib.SMA, self.data.Volume, timeperiod=20)
        
        print("🌙 Moon Dev: Indicators initialized ✨")

    def next(self):
        # 🌙 Moon Dev: Improved exit logic - check both long and short positions separately for symmetric reversion signals
        if self.position.is_long:
            if (self.rsi[-1] > self.rsi_sma[-1]) or (self.stoch_k[-1] < self.stoch_sma[-1]):
                self.position.close()
                print(f"🌙 Moon Dev: Long Exit on Reversion Signal at {self.data.Close[-1]:.2f} 🚀")
        
        if self.position.is_short:
            if (self.rsi[-1] < self.rsi_sma[-1]) or (self.stoch_k[-1] > self.stoch_sma[-1]):
                self.position.close()
                print(f"🌙 Moon Dev: Short Exit on Reversion Signal at {self.data.Close[-1]:.2f} 🚀")
        
        # 🌙 Moon Dev: Entry conditions - added symmetric long side for balanced trading in ranging markets
        # No 'return' after exits to allow potential opposite entry on same bar if conditions align (rare but possible)
        if (not self.position) and (len(self.rsi) > 20) and (self.adx[-1] < self.adx_threshold):
            
            # Long entry: Bearish RSI divergence with bullish Stoch, plus RSI <45 filter and volume confirmation
            if (self.rsi[-1] < self.rsi_sma[-1]) and (self.stoch_k[-1] > self.stoch_sma[-1]) and (self.rsi[-1] < 45) and (self.data.Volume[-1] > self.vol_sma[-1]):
                # Calculate entry, SL, TP
                entry_price = self.data.Close[-1]
                atr_val = self.atr[-1]
                sl_price = entry_price - (self.atr_multiplier_sl * atr_val)
                tp_price = entry_price + (self.atr_multiplier_tp * atr_val)
                risk_distance = entry_price - sl_price
                
                # Position sizing: risk 1% of equity, using float for precise sizing (no int rounding)
                risk_amount = self.equity * self.risk_per_trade
                position_size = risk_amount / risk_distance  # Float for better precision in crypto units (BTC)
                
                # Check if size and SL/TP levels are valid for long
                if position_size > 0 and not np.isnan(sl_price) and not np.isnan(tp_price) and sl_price < entry_price < tp_price:
                    self.buy(size=position_size, sl=sl_price, tp=tp_price)  # Removed unnecessary limit=entry_price
                    print(f"🌙 Moon Dev: Long Entry at {entry_price:.2f}, Size: {position_size:.4f}, SL: {sl_price:.2f}, TP: {tp_price:.2f} ✨")
                else:
                    print("🌙 Moon Dev: Invalid long position size or SL/TP levels, skipping entry ⚠️")
            
            # Short entry: Bullish RSI divergence with bearish Stoch, plus RSI >55 filter and volume confirmation
            elif (self.rsi[-1] > self.rsi_sma[-1]) and (self.stoch_k[-1] < self.stoch_sma[-1]) and (self.rsi[-1] > 55) and (self.data.Volume[-1] > self.vol_sma[-1]):
                # Calculate entry, SL, TP
                entry_price = self.data.Close[-1]
                atr_val = self.atr[-1]
                sl_price = entry_price + (self.atr_multiplier_sl * atr_val)
                tp_price = entry_price - (self.atr_multiplier_tp * atr_val)
                risk_distance = sl_price - entry_price
                
                # Position sizing: risk 1% of equity, using float for precise sizing
                risk_amount = self.equity * self.risk_per_trade
                position_size = risk_amount / risk_distance  # Float for better precision
                
                # Check if size and SL/TP levels are valid for short
                if position_size > 0 and not np.isnan(sl_price) and not np.isnan(tp_price) and tp_price < entry_price < sl_price:
                    self.sell(size=position_size, sl=sl_price, tp=tp_price)  # Removed unnecessary limit=entry_price
                    print(f"🌙 Moon Dev: Short Entry at {entry_price:.2f}, Size: {position_size:.4f}, SL: {sl_price:.2f}, TP: {tp_price:.2f} ✨")
                else:
                    print("🌙 Moon Dev: Invalid short position size or SL/TP levels, skipping entry ⚠️")

# Run backtest
bt = Backtest(df, DivergentReversion, cash=1000000, commission=0.002, exclusive_orders=True, trade_on_close=True)

print("🌙 Moon Dev: Running backtest... 🚀")
stats = bt.run()
print(stats)