🪨 Moon Dev's Debug AI 🌙

Here is the step-by-step explanation of the fixes made to ensure compliance with backtest requirements:

1. **Position Sizing Compliance**:
   - Ensured that position sizing uses either fractions (0 < size < 1) for percentage equity or positive integers for units without floating points.

2. **Variable Scoping and Naming**:
   - Improved variable names for clarity, ensuring no variables are shadowed or misused across different scopes.

3. **Stop Loss and Take Profit Handling**:
   - Converted stop loss and take profit parameters from relative distances to absolute price levels by using the current instrument's price as a reference.

4. **Data Handling Corrections**:
   - Replaced `data_array` with `current_data_price` in the fractals method for accurate calculation of RSI based on absolute prices.
   
5. **Imports and Function Calls**:
   - Ensured that pandas_ta functions return scalar values when used within the strategy, avoiding array operations where single-value results are expected.

6. **Rounding for Units**:
   - Added rounding logic to ensure position sizes using units are converted from floating-point numbers to integers by rounding down or up as needed.

These fixes maintain the original strategy's functionality while adhering strictly to the backtest requirements.