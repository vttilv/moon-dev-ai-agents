import pandas as pd
import numpy as np
from datetime import datetime
import talib as ta
from backtesting import Backtrader, BTLog, Strategy
from backtesting indicators import I

# Step 1: Load and clean data
def load_data(data_path):
    data = pd.read_csv(data_path)
    
    # Clean column names by removing spaces and making lowercase
    data.columns = data.columns.str.strip().str.lower()
    
    # Remove any unnamed columns
    data = data.drop(columns=[col for col in data.columns if 'unnamed' in col.lower()])
    
    # Convert datetime to proper format
    data['datetime'] = data['datetime'].apply(lambda x: datetime.fromisoformat(x))
    
    # Set datetime as index and sort it
    data.set_index('datetime', inplace=True)
    data.sort_index(inplace=True)
    
    return data

# Step 2: AdaptiveSynergy Strategy Implementation
class AdaptiveSynergy(Strategy):
    def __init__(self):
        # Initialize indicators with proper parameters
        self.ama_period = 14
        self.rsi_period = 14
        self.sto_period = 14
        
        # Calculate necessary indicators using TA-Lib within I() wrapper
        self.data.I(ama=ta.MA(self.data.close, timeperiod=self.ama_period), name="AMA")
        self.data.I(rsi=ta.RSI(self.data.close, timeperiod=self.rsi_period), name="RSI")
        self.data.I(sto=ta.STOCH(self.data.close, timeperiod=self.sto_period), name="STO")
        
    def next(self):
        # Check if indicators are available (only after at least 14 periods)
        if self.position.size == 0:
            # Entry logic
            if (self.rsi.last() < 30 and self.ama.last() > self.ama.last()) or \
               (self.sto.last() < 20 and self.ama.last() > self.ama.last()):
                # Potential bullish divergence - consider entry
                BTLog(f"Potential bullish divergence detected: RSI={self.rsi.last():.2f}, STO={self.sto.last():.2f}")
                
                # Close any existing positions to reduce risk
                self.position.close()
                
                # Define stop-loss and take-profit levels (example values)
                stop_loss = 0.5  # 50% of position size as stop loss
                
                # Calculate position size based on risk tolerance percentage (e.g., 2% risk per trade)
                position_size = self.broker.equity * 0.02 / abs(self.sto.last() - 1) if abs(self.sto.last() - 1) > 0 else 0
                # Ensure position size is rounded to avoid floating point issues
                position_size = round(position_size, 4)
                
                self.position = self.buy()
        
        elif self.position.size != 0:
            # Exit logic based on divergence reversal or other conditions
            if (self.rsi.last() > 30 and self.ama.last() < self.ama.last()) or \
               (self.sto.last() > 20 and self.ama.last() < self.ama.last()):
                BTLog(f"Potential bearish divergence detected: RSI={self.rsi.last():.2f}, STO={self.sto.last():.2f}")
                
                # Close position before significant price movement
                self.position.close()
        
        # Print current balance and log activity for debugging
        self.broker.print_balance()
        BTLog(f"Strategy status: {self.status.__name__}")

# Step 3: Backtest Execution
def backtest-adaptivesynergy():
    data = load_data("data/ADAPTIVE_SYNERGY_DATA.csv")
    
    # Initialize the strategy and broker
    cerebro = Backtrader()
    cerebro.addstrategy(AdaptiveSynergy)
    cerebro.broker.setcommission(commission=0.0)

    # Run backtest
    cerebro.run(data, plot=True, faststart=False)
    
    # Print full statistics
    cerebro.broker.print_stats()

if __name__ == '__main__':
    backtest-adaptivesynergy()