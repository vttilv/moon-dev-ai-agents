Below is an end‐to‐end Python script that implements the “DynamicValidation” strategy according to your specifications. Make sure you have installed the required libraries (backtesting, pandas, numpy, talib) before running this script.

────────────────────────────────────────────
#!/usr/bin/env python3
import os
import pandas as pd
import numpy as np
import talib
from backtesting import Backtest, Strategy

# ─── DYNAMIC VALIDATION STRATEGY ──────────────────────────────
class DynamicValidation(Strategy):
    # Strategy parameters (these will be optimized later)
    lookback = 20                # Lookback period for swing detection
    risk_reward_ratio = 2.5      # Minimum risk-reward ratio required (e.g. 2.5:1)
    zone_buffer = 10             # Price offset buffer (in dollars) for validating zones
    risk_pct = 0.01              # Risk 1% of equity per trade

    def init(self):
        # Calculate swing levels using TA‐Lib functions wrapped by self.I() 
        # (DON’T use backtesting.py’s built‐in indicators!)
        self.demand = self.I(talib.MIN, self.data.Low, timeperiod=self.lookback)   # Swing low = Demand Zone in uptrends
        self.supply = self.I(talib.MAX, self.data.High, timeperiod=self.lookback)  # Swing high = Supply Zone in downtrends
        print("🌙 [DynamicValidation] Indicators INIT – Swing Low (Demand) & Swing High (Supply) set with lookback =", self.lookback, "🚀")
        
    def next(self):
        # Get the current bar price and time (for debug prints)
        current_price = self.data.Close[-1]
        bar_time = self.data.index[-1]
        print(f"✨ [DynamicValidation] New bar @ {bar_time}: Price = {current_price:.2f}")
        
        # Ensure we have at least 'lookback' bars for trend validation
        if len(self.data.Close) < self.lookback:
            return

        # Simple trend determination: compare current close with the close from 'lookback' bars ago
        previous_price = self.data.Close[-self.lookback]
        if current_price > previous_price:
            trend = "uptrend"
        elif current_price < previous_price:
            trend = "downtrend"
        else:
            trend = "sideways"
        print(f"🚀 [Moon Dev] Market trend determined as: {trend.upper()}")

        # Get the most-recent swing levels from our TA indicators
        current_demand = self.demand[-1]
        current_supply = self.supply[-1]
        print(f"🌙 [Moon Dev] Current Demand Zone (Swing LOW): {current_demand:.2f}")
        print(f"🌙 [Moon Dev] Current Supply Zone (Swing HIGH): {current_supply:.2f}")

        # If already in a trade, maintain the position.
        if self.position:
            print("✨ [Moon Dev] Already in a position – holding... 🚀")
            return

        # ─── LONG ENTRY (Uptrend: Price reenters a DEMAND zone) ───────────────
        if trend == "uptrend" and current_price <= (current_demand + self.zone_buffer):
            entry = current_price
            stop_loss = current_demand - self.zone_buffer  # Place SL just below demand zone
            take_profit = current_supply                    # TP at recent high (supply zone)
            risk = entry - stop_loss
            reward = take_profit - entry

            print(f"🚀 [Moon Dev] Evaluating LONG trade – Entry: {entry:.2f}, SL: {stop_loss:.2f}, TP: {take_profit:.2f}")
            print(f"🌙 [Moon Dev] Calculated Risk: {risk:.2f} | Reward: {reward:.2f}")
            
            if risk <= 0:
                print("🌙 [Moon Dev] Invalid (non-positive) risk for LONG trade – skipping trade!")
                return

            rr_ratio = reward / risk
            print(f"✨ [Moon Dev] LONG Risk/Reward Ratio: {rr_ratio:.2f}")
            
            if rr_ratio >= self.risk_reward_ratio:
                risk_amount = self.risk_pct * self.equity
                position_size = risk_amount / risk
                # IMPORTANT: size must be a whole number of units
                position_size = int(round(position_size))
                
                if position_size <= 0:
                    print("🌙 [Moon Dev] Calculated position size is zero – skipping LONG trade!")
                    return

                print(f"🚀 [Moon Dev] Placing LONG order with size {position_size}.")
                self.buy(size=position_size, sl=stop_loss, tp=take_profit)
            else:
                print(f"🌙 [Moon Dev] LONG trade rejected – Risk/Reward Ratio ({rr_ratio:.2f}) is below required {self.risk_reward_ratio}")

        # ─── SHORT ENTRY (Downtrend: Price reenters a SUPPLY zone) ───────────────
        elif trend == "downtrend" and current_price >= (current_supply - self.zone_buffer):
            entry = current_price
            stop_loss = current_supply + self.zone_buffer  # Place SL just above supply zone
            take_profit = current_demand                     # TP at recent low (demand zone)
            risk = stop_loss - entry
            reward = entry - take_profit

            print(f"🌙 [Moon Dev] Evaluating SHORT trade – Entry: {entry:.2f}, SL: {stop_loss:.2f}, TP: {take_profit:.2f}")
            print(f"🚀 [Moon Dev] Calculated Risk: {risk:.2f} | Reward: {reward:.2f}")

            if risk <= 0:
                print("🚀 [Moon Dev] Invalid (non-positive) risk for SHORT trade – skipping trade!")
                return

            rr_ratio = reward / risk
            print(f"✨ [Moon Dev] SHORT Risk/Reward Ratio: {rr_ratio:.2f}")

            if rr_ratio >= self.risk_reward_ratio:
                risk_amount = self.risk_pct * self.equity
                position_size = risk_amount / risk
                position_size = int(round(position_size))
                
                if position_size <= 0:
                    print("🚀 [Moon Dev] Calculated position size is zero – skipping SHORT trade!")
                    return

                print(f"🌙 [Moon Dev] Placing SHORT order with size {position_size}.")
                self.sell(size=position_size, sl=stop_loss, tp=take_profit)
            else:
                print(f"🚀 [Moon Dev] SHORT trade rejected – Risk/Reward Ratio ({rr_ratio:.2f}) is below required {self.risk_reward_ratio}")
        else:
            print("✨ [Moon Dev] No valid trade setup detected on this bar.")

# ─── MAIN EXECUTION ─────────────────────────────────────────────
if __name__ == "__main__":
    # Use the provided data path
    data_path = "/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv"
    print("🌙 Moon Dev: Loading data from CSV... 🚀")
    data = pd.read_csv(data_path)
    
    # Clean column names and drop any unnamed columns
    data.columns = data.columns.str.strip().str.lower()
    data = data.drop(columns=[col for col in data.columns if 'unnamed' in col.lower()])
    
    # Map columns to backtesting.py requirements (Proper case names!)
    data.rename(columns={
        'open': 'Open', 
        'high': 'High', 
        'low': 'Low', 
        'close': 'Close', 
        'volume': 'Volume'
    }, inplace=True)
    
    print("✨ Moon Dev: Data columns after cleaning:", list(data.columns))
    
    # If there is a datetime column, convert it and set as index
    if 'datetime' in data.columns:
        data['datetime'] = pd.to_datetime(data['datetime'])
        data.set_index('datetime', inplace=True)

    # Instantiate the Backtest with starting capital of 1,000,000 as required
    bt = Backtest(data, DynamicValidation, cash=1000000, commission=0.0)
    
    print("🚀 Moon Dev: Running initial backtest for DynamicValidation strategy! 🌙")
    stats = bt.run()
    print("✨ Moon Dev: Backtest Statistics:")
    print(stats)
    print("🌙 Moon Dev: Strategy details:")
    print(stats._strategy)
    
    # Save initial performance plot
    strategy_name = "DynamicValidation"
    charts_dir = "/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/charts"
    os.makedirs(charts_dir, exist_ok=True)
    chart_file = os.path.join(charts_dir, f"{strategy_name}_chart.html")
    print(f"🚀 Moon Dev: Saving initial performance chart to {chart_file}")
    bt.plot(filename=chart_file, open_browser=False)
    
    # ─── PARAMETER OPTIMIZATION ─────────────────────────────
    print("🌙 Moon Dev: Starting parameter optimization! ✨")
    optimized_results = bt.optimize(
        lookback=range(10, 31, 10),              # Try lookback values 10, 20, 30
        risk_reward_ratio=[2.5, 3.0],             # Test required risk-reward ratio values
        zone_buffer=range(10, 21, 10),            # Try zone buffers 10 and 20 dollars
        maximize='Equity Final [$]'              # Optimize for final equity
    )
    print("🚀 Moon Dev: Optimized strategy results:")
    print(optimized_results)
    print("🌙 Moon Dev: Optimized strategy details:")
    print(optimized_results._strategy)
    
    # Save optimized performance plot
    chart_file_opt = os.path.join(charts_dir, f"{strategy_name}_Optimized_chart.html")
    print(f"✨ Moon Dev: Saving optimized performance chart to {chart_file_opt}")
    bt.plot(filename=chart_file_opt, open_browser=False)
    
    print("🚀 Moon Dev: Backtesting and Optimization Completed! 🌙")
────────────────────────────────────────────
  
How the script works:
1. It loads and cleans the data from the CSV file by removing extra spaces, dropping any unnamed columns, and renaming columns to “Open”, “High”, “Low”, “Close”, and “Volume”.
2. In the DynamicValidation strategy class, the init() method computes the swing high and low zones using TA‐Lib’s MAX and MIN functions (via self.I).
3. In next(), the strategy first identifies whether the market is in an uptrend or downtrend (by comparing the current close with the close from “lookback” bars ago). Then it checks whether price has reentered a demand (in an uptrend) or supply (in a downtrend) zone.
4. Before entering a trade, it carefully calculates the stop loss, take profit, risk, and reward. Only if the computed risk-reward ratio meets or exceeds the minimum requirement (2.5:1 by default) does it calculate a proper integer position size (using 1% risk of current equity) and place the order.
5. After running the initial backtest (with a starting capital of 1,000,000), the script prints full statistics and saves the performance chart.
6. Then it performs parameter optimization on lookback, risk-reward ratio, and zone buffer values. The optimized results (with full strategy details) are printed and another performance chart is saved.

Enjoy debugging with plenty of Moon Dev themed prints and happy backtesting! 🌙✨🚀