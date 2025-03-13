def _calculate_indicators(data):
    # Calculate balance manually without backtest indicators
    data['equity_value'] = (data['volume'] * data['close'].shift(1)) / \
                          (data['volume'].shift(1) * data['close'])
    
    # Add more indicators using pandas_ta
    data['rsi_14'] = ta.RSI(data, length=14)
    balance_indicator = ta.Indicator('balance', data)
    
    return data

def _triggers(indicators):
    balance = indicators['balance']
    rsi_14 = indicators['rsi_14']
    
    # Simple example triggers
    overbought = rsi_14 < 30
    oversold = rsi_14 > 70
    
    return {'balance': balance, 'rsi_14': rsi_14,
            'overbought': overbought, 'oversold': oversold}

def _execute_trades(triggers):
    current_balance = triggers['balance']
    overbought = triggers['overbought']
    
    if not overbought:
        print(f"\nEntering long position with {current_balance:.2f} units at", 
              current_balance[-1])
        
    return {"equity_value": current_balance}

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
    current_balance = triggers['balance']
    overbought = triggers['overbought']
    
    if not overbought:
        print(f"\nEntering long position with {current_balance:.2f} units at", 
              current_balance[-1])
        
    return {"equity_value": current_balance}