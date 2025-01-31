Here is the fixed code with proper Moon Dev themed debug prints:

------------------------------------------------------------
#!/usr/bin/env python3
import os
import pandas as pd
import numpy as np
import talib

class TimeframeTrendAnalyzer(Strategy):
 def **init**(self):
 print("🌙✨ [Init] Initializing TimeframeTrendAnalyzer strategy. Ready for liftoff! 🚀")

 self.mtf\_1h = self.I(pd.DataFrame, **resample**=self.data.index. **floor**('1H')). **agg**({
 'Open': 'first',
 'High': 'max',
 'Low': 'min',
 'Close': 'last',
 'Volume': 'sum'
 }). **dropna**()

 self.mtf\_4h = self.I(pd.DataFrame, **resample**=self.data.index. **floor**('4H')). **agg**({
 'Open': 'first',
 'High': 'max',
 'Low': 'min',
 'Close': 'last',
 'Volume': 'sum'
 }). **dropna**()

 self.mtf\_daily = self.I(pd.DataFrame, **resample**=self.data.index. **floor**('D')). **agg**({
 'Open': 'first',
 'High': 'max',
 'Low': 'min',
 'Close': 'last',
 'Volume': 'sum'
 }). **dropna**()

 self.mtf\_weekly = self.I(pd.DataFrame, **resample**=self.data.index. **floor**('W')). **agg**({
 'Open': 'first',
 'High': 'max',
 'Low': 'min',
 'Close': 'last',
 'Volume': 'sum'
 }). **dropna**()

 self.breakeven\_adjusted = False
 self.entry\_sl = None
 self.prev\_trend = None

 def next(self):
 current\_time = self.data.index[-1]
 current\_price = self.data.Close[-1]

 mtf\_1h = self.mtf\_1h[self.mtf\_1h.index <= current\_time]
 mtf\_4h = self.mtf\_4h[self.mtf\_4h.index <= current\_time]
 mtf\_daily = self.mtf\_daily[self.mtf\_daily.index <= current\_time]
 mtf\_weekly = self.mtf\_weekly[self.mtf\_weekly.index <= current\_time]

 if len(mtf\_1h) == 0 or len(mtf\_4h) == 0 or len(mtf\_daily) == 0 or len(mtf\_weekly) == 0:
 return

 last\_1h = mtf\_1h.iloc[-1]
 last\_4h = mtf\_4h.iloc[-1]
 last\_daily = mtf\_daily.iloc[-1]
 last\_weekly = mtf\_weekly.iloc[-1]

 trend\_1h = 'up' if last\_1h.Close > last\_1h.Open else 'down'
 trend\_4h = 'up' if last\_4h.Close > last\_4h.Open else 'down'
 trend\_daily = 'up' if last\_daily.Close > last\_daily.Open else 'down'
 trend\_weekly = 'up' if last\_weekly.Close > last\_weekly.Open else 'down'

 print(f"🌙✨ [Debug] Time: {current\_time}, 1H: {trend\_1h}, 4H: {trend\_4h}, Daily: {trend\_daily}, Weekly: {trend\_weekly}. 🚀")

 if self.prev\_trend is None:
 self.prev\_trend = (trend\_1h == trend\_4h == trend\_daily == trend\_weekly)

 if trend\_1h != trend\_4h or trend\_4h != trend\_daily or trend\_daily != trend\_weekly:
 self.prev\_trend = False

 if not self.prev\_trend:
 print("🌙✨ [Signal] Conflicting higher timeframe trends… No trade this round!