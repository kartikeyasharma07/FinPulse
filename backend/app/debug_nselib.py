"""
Standalone diagnostic for nselib - not part of the app.
Run with: python -m app.debug_nselib
"""
from nselib import capital_market

print("Trying capital_market.price_volume_data(symbol='SBIN', period='1M')...\n")

try:
    df = capital_market.price_volume_data(symbol="SBIN", period="1M")
    if df is None or df.empty:
        print("Result: empty (no rows returned)")
    else:
        print(f"Success! Got {len(df)} rows.\n")
        print("Columns:", list(df.columns))
        print("\nFirst few rows:")
        print(df.head())
except Exception as e:
    print(f"Request raised an exception: {type(e).__name__}: {e}")