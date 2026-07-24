"""
Standalone diagnostic - not part of the app. Run this alone to see exactly
what NSE's API is sending back, so we can see the real shape of the response
instead of guessing from a library's error message.

Run with: python -m app.debug_nse
"""
import json
from nsepython import nsefetch

url = (
    "https://www.nseindia.com/api/historical/cm/equity"
    "?symbol=RELIANCE&series=[%22EQ%22]&from=01-07-2026&to=24-07-2026"
)

print(f"Requesting: {url}\n")

try:
    result = nsefetch(url)
    print(f"Type of response: {type(result)}\n")
    if isinstance(result, dict):
        print("Top-level keys:", list(result.keys()))
        print("\nFull response (truncated to 2000 chars):")
        print(json.dumps(result, indent=2)[:2000])
    else:
        print("Raw response (truncated to 2000 chars):")
        print(str(result)[:2000])
except Exception as e:
    print(f"Request raised an exception: {type(e).__name__}: {e}")

print("\n" + "=" * 60)
print("Now trying a simpler live-quote endpoint...")
quote_url = "https://www.nseindia.com/api/quote-equity?symbol=RELIANCE"
try:
    result2 = nsefetch(quote_url)
    print(f"Type of response: {type(result2)}\n")
    if isinstance(result2, dict):
        print("Top-level keys:", list(result2.keys()))
        print("\nFull response (truncated to 1000 chars):")
        print(json.dumps(result2, indent=2)[:1000])
    else:
        print(str(result2)[:1000])
except Exception as e:
    print(f"Request raised an exception: {type(e).__name__}: {e}")