#!/usr/bin/env python3
"""
Moon Dev's Backtest AI 🌙 - StochasticPhaseTrader Strategy Backtesting Script
---------------------------------------------------------------------------
This script implements the StochasticPhaseTrader strategy using backtesting.py.
It uses the TA‐Lib library for indicator calculations and includes:
  • Data cleaning & mapping
  • Indicator calculations via self.I() wrapper
  • Entry/exit logic with Moon Dev themed debug prints 🚀✨
  • Risk management with proper position sizing (always converting to integer!)
  • Parameter optimization (breaking down list parameters into ranges)
  
Data source: /Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv
Charts will be saved to the charts directory.
"""

import os
import pandas as pd
import numpy as np
from backtesting import Backtest, Strategy
from backtesting.lib import crossover
import talib

# ---------------------------------------------------------------------------
# Define the StochasticPhaseTrader Strategy
# ---------------------------------------------------------------------------
class StochasticPhaseTrader(Strategy):
    # ----------------------------------------------------------------------------
    # Strategy optimization & risk parameter defaults (these can be optimized)
    # ----------------------------------------------------------------------------
    rsi_period = 14             # Period for RSI calculation
    stoch_period = 14           # Period for rolling min/max of RSI (StochRSI calc)
    stoch_d_period = 3          # SMA period for %D line of StochRSI
    oversold_threshold = 20     # Below this value, market is oversold → potential BUY
    overbought_threshold = 80   # Above this value, market is overbought → potential SELL
    stop_loss_pct = 0.01        # Stop Loss: 1% risk relative to entry price
    risk_reward_ratio = 2       # Risk-reward ratio (TP = entry + risk*ratio)
    risk_percentage = 0.01      # Risk 1% of current equity per trade

    def init(self):
        # ----------------------------------------------------------------------------
        # Calculate RSI using TA-Lib and then use it to compute the Stochastic RSI.
        # We MUST use the self.I() wrapper for all indicator calculations.
        # ----------------------------------------------------------------------------
        # (We could store RSI separately but since our compute function uses the close prices,
        # we define a helper function that handles it.)
        
        def compute_stoch_rsi(close):
            # Compute RSI from Close prices
            r = talib.RSI(close, timeperiod=self.rsi_period)
            # Compute rolling minimum and maximum on RSI using TA-Lib functions
            rmin = talib.MIN(r, timeperiod=self.stoch_period)
            rmax = talib.MAX(r, timeperiod=self.stoch_period)
            # Compute Stochastic RSI: scaled between 0 and 100
            return (r - rmin) / (rmax - rmin + 1e-10) * 100
        
        # Calculate the fast (%K) line of the StochRSI using our compute function
        self.stoch_rsi = self.I(compute_stoch_rsi, self.data.Close)
        # Calculate the slow (%D) line as the SMA of the %K line
        self.stoch_d = self.I(talib.SMA, self.stoch_rsi, timeperiod=self.stoch_d_period)
        
        print("🌙✨ [INIT] Indicators initialized: RSI period =", self.rsi_period,
              "| Stoch Period =", self.stoch_period,
              "| Stoch %D period =", self.stoch_d_period)

    def next(self):
        # ----------------------------------------------------------------------------
        # This method is called on every new bar.
        # It checks for entry (BUY) or exit (SELL) conditions based on the StochRSI indicator.
        # ----------------------------------------------------------------------------
        current_price = self.data.Close[-1]
        stochk = self.stoch_rsi[-1]
        stochd = self.stoch_d[-1]
        
        # Ensure we have sufficient history to check for a crossover (need at least two data points)
        if len(self.stoch_rsi) < 2:
            return
        prev_stochk = self.stoch_rsi[-2]
        prev_stochd = self.stoch_d[-2]
        
        # --------------------------------------------------------------------
        # Entry Rule: Enter long position when:
        #  • The fast StochRSI line (stochk) is below the oversold threshold
        #  • A bullish crossover occurs (stochk crosses above stochd)
        # --------------------------------------------------------------------
        if not self.position:
            if (prev_stochk < prev_stochd) and (stochk > stochd) and (stochk < self.oversold_threshold):
                entry_price = current_price
                stop_loss_price = entry_price * (1 - self.stop_loss_pct)
                take_profit_price = entry_price * (1 + self.risk_reward_ratio * self.stop_loss_pct)
                # Calculate risk per unit and compute position size based on risk amount = equity * risk_percentage
                risk_per_unit = entry_price - stop_loss_price
                risk_capital = self.equity * self.risk_percentage
                position_size = risk_capital / risk_per_unit if risk_per_unit > 0 else 0
                # IMPORTANT: Always use integer position sizes for backtesting.py!
                position_size = int(round(position_size))
                if position_size <= 0:
                    position_size = 1  # Minimal fallback size
                
                print(f"🌙✨🚀 Moon Dev BUY Signal triggered!")
                print(f"   [BUY] stochrsi_k crossed above stochrsi_d: {prev_stochk:.2f} -> {stochk:.2f} (threshold < {self.oversold_threshold})")
                print(f"   Entry Price: {entry_price:.2f}, Stop Loss: {stop_loss_price:.2f}, Take Profit: {take_profit_price:.2f}")
                print(f"   Calculated Position Size (int): {position_size}\n")
                
                self.buy(size=position_size, sl=stop_loss_price, tp=take_profit_price)
        
        # --------------------------------------------------------------------
        # Exit Rule: Exit (close position) when:
        #  • In position, and the fast StochRSI line (stochk) is above the overbought threshold
        #  • A bearish crossover occurs (stochk crosses below stochd)
        # --------------------------------------------------------------------
        elif self.position:
            if (prev_stochk > prev_stochd) and (stochk < stochd) and (stochk > self.overbought_threshold):
                print(f"🌙✨🚀 Moon Dev SELL Signal triggered!")
                print(f"   [SELL] stochrsi_k crossed below stochrsi_d: {prev_stochk:.2f} -> {stochk:.2f} (threshold > {self.overbought_threshold})")
                print(f"   Exiting position at Price: {current_price:.2f}\n")
                self.position.close()
                
        # Additional Moon Dev debug info (plenty of debug prints for tracing)
        print(f"🌙 [DEBUG] Price = {current_price:.2f} | stochrsi_k = {stochk:.2f} | stochrsi_d = {stochd:.2f}")

# ---------------------------------------------------------------------------
# Main Backtesting & Optimization Execution
# ---------------------------------------------------------------------------
if __name__ == '__main__':
    # -------- Data Loading & Cleaning ---------------------------------------
    data_path = "/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv"
    try:
        data = pd.read_csv(data_path)
        print("🌙✨🚀 Moon Dev: Data successfully loaded from", data_path)
    except Exception as e:
        print("🌙❌ Moon Dev ERROR: Failed to load data.", str(e))
        raise

    # Clean column names: remove extra spaces and convert to lowercase
    data.columns = data.columns.str.strip().str.lower()
    # Drop any 'unnamed' columns
    data = data.drop(columns=[col for col in data.columns if 'unnamed' in col.lower()])
    
    # Ensure proper mapping to required columns with Capitalized names
    rename_map = {
        'open': 'Open',
        'high': 'High',
        'low': 'Low',
        'close': 'Close',
        'volume': 'Volume',
        'datetime': 'Datetime'
    }
    data.rename(columns=rename_map, inplace=True)
    
    # Convert Datetime column to pandas datetime and set as index if available
    if 'Datetime' in data.columns:
        data['Datetime'] = pd.to_datetime(data['Datetime'])
        data.set_index('Datetime', inplace=True)
    
    print("🌙✨🚀 Moon Dev: Data cleaning complete. Columns available:", list(data.columns))
    
    # -------- Backtest Initialization with initial size (1,000,000) ------------
    bt = Backtest(data, StochasticPhaseTrader, cash=1_000_000, commission=0.0, trade_on_close=True)
    print("🌙✨🚀 Moon Dev: Backtest initialized with cash = 1,000,000")
    
    # -------- Run Initial Backtest ------------------------------------------
    print("🌙✨🚀 Moon Dev: Running initial backtest with default parameters...")
    stats = bt.run()
    print("\n🌙✨🚀 Moon Dev: *** INITIAL BACKTEST STATS ***")
    print(stats)
    print("\n🌙✨🚀 Moon Dev: Strategy parameters:")
    print(stats._strategy)
    
    # Save the initial performance chart
    strategy_name = "StochasticPhaseTrader"
    chart_dir = "/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/charts"
    os.makedirs(chart_dir, exist_ok=True)
    chart_file = os.path.join(chart_dir, f"{strategy_name}_chart.html")
    bt.plot(filename=chart_file, open_browser=False)
    print(f"🌙✨🚀 Moon Dev: Initial performance chart saved to {chart_file}\n")
    
    # -------- Optimization --------------------------------------------------
    # Optimize the following parameters:
    #   • oversold_threshold: try values in range(15, 25, 5)  → e.g. 15, 20
    #   • overbought_threshold: try values in range(75, 85, 5)  → e.g. 75, 80
    #   • risk_reward_ratio: try values in range(1, 3, 1)         → e.g. 1, 2
    # Constraint: oversold_threshold must be strictly less than overbought_threshold.
    print("🌙✨🚀 Moon Dev: Starting optimization...")
    opt_stats = bt.optimize(oversold_threshold=range(15, 25, 5),
                            overbought_threshold=range(75, 85, 5),
                            risk_reward_ratio=range(1, 3, 1),
                            maximize='Equity Final [$]',
                            constraint=lambda p: p.oversold_threshold < p.overbought_threshold,
                            return_stats=True)
    print("\n🌙✨🚀 Moon Dev: *** OPTIMIZATION RESULTS ***")
    print(opt_stats)
    print("\n🌙✨🚀 Moon Dev: Optimal strategy parameters:")
    print(opt_stats._strategy)
    
    # -------- Re-run Backtest with Optimized Parameters ---------------------
    best_oversold = opt_stats._strategy.oversold_threshold
    best_overbought = opt_stats._strategy.overbought_threshold
    best_rr = opt_stats._strategy.risk_reward_ratio
    print(f"\n🌙✨🚀 Moon Dev: Re-running backtest with optimized parameters: oversold_threshold = {best_oversold}, "
          f"overbought_threshold = {best_overbought}, risk_reward_ratio = {best_rr}")
    
    bt_optimized = Backtest(data, StochasticPhaseTrader, cash=1_000_000, commission=0.0, trade_on_close=True)
    stats_opt = bt_optimized.run(oversold_threshold=best_oversold,
                                 overbought_threshold=best_overbought,
                                 risk_reward_ratio=best_rr)
    
    # Save the optimized performance chart
    opt_chart_file = os.path.join(chart_dir, f"{strategy_name}_optimized_chart.html")
    bt_optimized.plot(filename=opt_chart_file, open_browser=False)
    print(f"🌙✨🚀 Moon Dev: Optimized performance chart saved to {opt_chart_file}\n")
    
    print("🌙✨🚀 Moon Dev: All done! Happy trading and may the Moon light your profits! 🌕🚀✨")
    
# End of Script
