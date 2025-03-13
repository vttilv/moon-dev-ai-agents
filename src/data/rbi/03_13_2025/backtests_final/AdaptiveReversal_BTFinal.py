# Debugging variable: Print current volatility indicator value
print(f"Current Volatility Indicator Value: {self.volatility_indicator}")

# Calculate position size based on strategy logic
if self.position_size > 0 and self.spread <= 2:
    # Ensure proper rounding for integer-based units or fractional percentages
    if isinstance(self.position_size, float):
        print(f"Rounding position size from {self.position_size} to nearest integer.")
        self.position_size = round(self.position_size)
    
    if self.volatility_indicator is not None:
        print(f"Volatility Indicator is valid: {self.volatility_indicator}")