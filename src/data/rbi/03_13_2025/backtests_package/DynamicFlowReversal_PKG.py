# Updated imports
from pandas_ta import indicator as ta

def _calculate_indicators(data):
    # Calculate balance manually without backtest indicators
    data['balance'] = (data['volume'] * data['close'].shift(1)) / \
                     (data['volume'].shift(1) * data['close'])
    
    # Add more indicators using pandas_ta
    data['rsi_14'] = ta.RSI(data, length=14)
    data['balance'] = ta.Indicator('balance', data)
    
    return data

# Example trigger logic (no backtest indicator usage here)
def _triggers(indicators):
    balance = indicators['balance']
    rsi_14 = indicators['rsi_14']
    
    # Simple example triggers
    overbought = rsi_14 < 30
    oversold = rsi_14 > 70
    
    return {'balance': balance, 'rsi_14': rsi_14,
            'overbought': overbought, 'oversold': oversold}

def _execute_trades(triggers):
    balance = triggers['balance']
    overbought = triggers['overbought']
    
    if not overbought:
        print("Entering long position at", balance[-1])
        
    return {"balance": balance}