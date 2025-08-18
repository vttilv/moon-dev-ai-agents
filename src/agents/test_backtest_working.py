import pandas as pd
import talib
from backtesting import Backtest, Strategy

class MoonDevStrategy(Strategy):
    def init(self):
        # Simple SMA strategy
        self.sma_fast = self.I(talib.SMA, self.data.Close, timeperiod=20)
        self.sma_slow = self.I(talib.SMA, self.data.Close, timeperiod=50)
        print("🌙 Moon Dev Strategy initialized!")
    
    def next(self):
        # Buy when fast SMA crosses above slow SMA
        if self.sma_fast[-2] < self.sma_slow[-2] and self.sma_fast[-1] > self.sma_slow[-1]:
            if not self.position:
                self.buy()
                print(f"🚀 BUY signal at {self.data.Close[-1]}")
        
        # Sell when fast SMA crosses below slow SMA
        elif self.sma_fast[-2] > self.sma_slow[-2] and self.sma_fast[-1] < self.sma_slow[-1]:
            if self.position:
                self.position.close()
                print(f"💰 SELL signal at {self.data.Close[-1]}")

# Load data
print("📊 Loading BTC data...")
data = pd.read_csv('/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv')

# Clean column names
data.columns = data.columns.str.strip()

# Convert datetime and set index
data['datetime'] = pd.to_datetime(data['datetime'])
data.set_index('datetime', inplace=True)

# Rename columns to match backtesting.py requirements
data.rename(columns={
    'open': 'Open',
    'high': 'High', 
    'low': 'Low',
    'close': 'Close',
    'volume': 'Volume'
}, inplace=True)

# Drop any extra columns
data = data[['Open', 'High', 'Low', 'Close', 'Volume']]

print("🚀 Running backtest on Moon Dev Strategy...")
bt = Backtest(data, MoonDevStrategy, cash=1000000, commission=.002)
stats = bt.run()

print("\n✨ BACKTEST COMPLETE! ✨")
print("=" * 60)
print(stats)
print("=" * 60)
print(f"\n🌙 Final Portfolio Value: ${stats['Equity Final [$]']:,.2f}")
print(f"📈 Total Return: {stats['Return [%]']:.2f}%")
print(f"💎 Sharpe Ratio: {stats['Sharpe Ratio']:.2f}")
print(f"📊 Total Trades: {stats['# Trades']}")
print("\n🚀 TO THE MOON! 🚀")