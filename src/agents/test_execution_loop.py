"""
🌙 Moon Dev's Execution Loop Test
Simplified version to demonstrate the execution loop
"""

import subprocess
import json
import os
import time
from datetime import datetime
from pathlib import Path
from termcolor import cprint

# Configuration
CONDA_ENV = "tflow"
MAX_DEBUG_ITERATIONS = 3
EXECUTION_TIMEOUT = 300

# Test directory
TEST_DIR = Path(__file__).parent / "test_execution"
TEST_DIR.mkdir(exist_ok=True)

def execute_backtest(file_path: str) -> dict:
    """Execute a backtest file and capture output"""
    cprint(f"\n🚀 Executing: {file_path}", "cyan")
    
    cmd = ["conda", "run", "-n", CONDA_ENV, "python", str(file_path)]
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=EXECUTION_TIMEOUT
        )
        
        output = {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
        }
        
        if output['success']:
            cprint("✅ Execution successful!", "green")
            if output['stdout']:
                print("\n📊 OUTPUT:")
                print(output['stdout'])
        else:
            cprint("❌ Execution failed!", "red")
            if output['stderr']:
                print("\n🐛 ERROR:")
                print(output['stderr'])
        
        return output
        
    except Exception as e:
        cprint(f"💥 Error: {str(e)}", "red")
        return {"success": False, "error": str(e)}

def create_test_backtest_v1():
    """Create a backtest with intentional error (from your example)"""
    code = '''Here's the complete implementation of the FibCloudTrend strategy for backtesting.py:

```python
import pandas as pd
import talib
from backtesting import Backtest, Strategy

class TestStrategy(Strategy):
    def init(self):
        self.sma = self.I(talib.SMA, self.data.Close, timeperiod=20)
    
    def next(self):
        if self.data.Close[-1] > self.sma[-1]:
            self.buy()

# Load data
data = pd.read_csv('/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv')
data['datetime'] = pd.to_datetime(data['datetime'])
data.set_index('datetime', inplace=True)
data.columns = ['Open', 'High', 'Low', 'Close', 'Volume']

bt = Backtest(data, TestStrategy, cash=1000000)
stats = bt.run()
print(stats)
```'''
    
    file_path = TEST_DIR / "test_backtest_v1.py"
    with open(file_path, 'w') as f:
        f.write(code)
    return file_path

def create_test_backtest_v2():
    """Create a fixed version (simulating debug agent output)"""
    code = '''import pandas as pd
import talib
from backtesting import Backtest, Strategy

class TestStrategy(Strategy):
    def init(self):
        self.sma = self.I(talib.SMA, self.data.Close, timeperiod=20)
    
    def next(self):
        if self.data.Close[-1] > self.sma[-1]:
            if not self.position:
                self.buy()
        elif self.position:
            self.position.close()

# Load data
print("🌙 Moon Dev's Test Strategy Loading...")
data = pd.read_csv('/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv')
data['datetime'] = pd.to_datetime(data['datetime'])
data.set_index('datetime', inplace=True)
data.columns = ['Open', 'High', 'Low', 'Close', 'Volume']

print("🚀 Running backtest...")
bt = Backtest(data, TestStrategy, cash=1000000)
stats = bt.run()
print("✨ Backtest complete!")
print(stats)'''
    
    file_path = TEST_DIR / "test_backtest_v2.py"
    with open(file_path, 'w') as f:
        f.write(code)
    return file_path

def main():
    """Demonstrate the execution loop"""
    cprint("\n🌙 Moon Dev's Execution Loop Demo", "yellow")
    cprint("=" * 50, "yellow")
    
    # Test 1: Execute code with syntax error
    cprint("\n📝 Test 1: Code with syntax error", "cyan")
    v1_file = create_test_backtest_v1()
    result1 = execute_backtest(v1_file)
    
    if not result1['success']:
        cprint("\n🔧 Simulating Debug Agent fixing the code...", "yellow")
        time.sleep(2)
        
        # Test 2: Execute fixed code
        cprint("\n📝 Test 2: Fixed code", "cyan")
        v2_file = create_test_backtest_v2()
        result2 = execute_backtest(v2_file)
        
        if result2['success']:
            cprint("\n🎉 SUCCESS! The execution loop works!", "green")
            cprint("📊 This proves we can:", "green")
            cprint("1. ✅ Execute backtest code", "green")
            cprint("2. ✅ Capture errors", "green")
            cprint("3. ✅ Fix and retry", "green")
            cprint("4. ✅ Get successful results", "green")
    
    cprint("\n🚀 Ready to integrate into full RBI system!", "yellow")

if __name__ == "__main__":
    main()