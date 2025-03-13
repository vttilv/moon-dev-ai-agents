import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import talib as ta
from typing import Dict, List, Optional

class Backtester:
    """Backtester class with data handling and backtesting functionality."""
    
    def __init__(self, data_path: str = '/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv'):
        self.data_path = data_path
        self.data = self._load_data()
        self.data = self._clean_data()
        
    def _load_data(self) -> pd.DataFrame:
        """Load and clean the data."""
        df = pd.read_csv(self.data_path)
        df.set_index('datetime', inplace=True)
        return df
    
    def _clean_data(self) -> pd.DataFrame:
        """Clean the data by removing spaces in column names and dropping unnamed columns."""
        # Clean column names
        df = self.data.rename(
            lambda x: x.strip() if x.strip().replace('.', '', 1).strip() else None,
            axis=1
        )
        
        # Drop any unnamed columns
        df.dropna(axis=1, inplace=True)
        
        return df
    
    def _calculate_indicators(self) -> Dict[str, pd.DataFrame]:
        """Calculate necessary indicators."""
        data = self.data
        indicators = {}
        
        # Calculate the relative strength of buys vs sells (example indicator)
        data['balance'] = (data['volume'] * data['close'].shift(1)) / (
            data['volume'].shift(1) * data['close']
        )
        
        # Add other indicators as needed
        
        return {
            'balance': data['balance'],
            # Add more indicators...
        }
    
    def _triggers(self, indicators: Dict[str, pd.DataFrame]) -> Dict[str, pd.Series]:
        """Generate entry and exit triggers based on indicators."""
        triggers = {}
        
        # Example trigger logic (buy signal)
        indicators['balance'].where(
            indicators['balance'] > self.params['reversal_threshold'],
            inplace=True
        )
        
        # Example sell signal
        indicators['balance'].where(
            indicators['balance'] < -self.params['reversal_threshold'],
            inplace=True
        )
        
        triggers['entry'] = (indicators['balance'] > 0).cumsum()
        triggers['exit'] = (indicators['balance'] < 0).cumsum()
        
        return triggers
    
    def _execute_trades(self, triggers: Dict[str, pd.Series]) -> Optional[Dict]:
        """Execute trades based on triggers."""
        trades = {}
        position = {
            'BTC-USD': {'size': 0.0, 'entered_at': None}
        }
        
        for i, (index, trigger) in enumerate(triggers.items()):
            if i > self.params['window']:
                break
            
            if trigger['entry'] == 1 and 'exit' not in trades:
                size = abs(position['BTC-USD']['size']) * self.params['holding_period']
                position['BTC-USD']['size'] = size
                print(f"Entering long position at {index}: {position}")
                
                # Take profit logic
                take_profit = size * (1 + self.params['take_profit_pct'] / 100)
                stop_loss = size * (1 - self.params['stop_loss_pct'] / 100)
                
                order = {
                    'type': 'take_profit',
                    'order_type': 'limit',
                    'price': take_profit,
                    'amount': size
                }
                
                print(f"Taking profit at {take_profit}")
                
                # Stop loss logic
                if stop_loss < 0:
                    stop_loss = abs(stop_loss)
                    
                order_stop = {
                    'type': 'stop_loss',
                    'order_type': 'limit',
                    'price': stop_loss,
                    'amount': size
                }
                
                print(f"Setting stop loss at {stop_loss}")
                
            elif trigger['exit'] == -1 and 'exit' in trades:
                position['BTC-USD']['size'] = 0.0
                
        return position

# Example usage
params = {
    'window': 20,
    'reversal_threshold': 0.5,
    'holding_period': 10,
    'take_profit_pct': 2,
    'stop_loss_pct': 2
}

backtester = Backtester()
indicators = backtester._calculate_indicators()
triggers = backtester._triggers(indicators)

# Execute trades based on triggers and print results
print(backtester._execute_trades(triggers))