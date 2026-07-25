"""
Standalone diagnostic for jugaad-data's live quote feature (which claims
to expose fundamentals: P/E, market cap, etc). Uses a hard timeout so it
can't hang indefinitely like it did in an earlier attempt.
Run with: python -m app.debug_jugaad
"""
import concurrent.futures as cf
from jugaad_data.nse import NSELive

TIMEOUT_SECS = 20


def fetch():
    nse = NSELive()
    return nse.stock_quote("RELIANCE")


print(f"Trying NSELive().stock_quote('RELIANCE') with a {TIMEOUT_SECS}s timeout...\n")

try:
    with cf.ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(fetch)
        data = future.result(timeout=TIMEOUT_SECS)

    if not data:
        print("Result: empty (no data returned)")
    else:
        print(f"Success! Top-level keys: {list(data.keys())}\n")
        price_info = data.get("priceInfo", {})
        metadata = data.get("metadata", {})
        security_info = data.get("securityInfo", {})
        print(f"  lastPrice: {price_info.get('lastPrice')}")
        print(f"  pdSymbolPe (P/E): {metadata.get('pdSymbolPe')}")
        print(f"  issuedSize: {security_info.get('issuedSize')}")
except cf.TimeoutError:
    print(f"Timed out after {TIMEOUT_SECS}s - request hung, did not complete.")
except Exception as e:
    print(f"Request raised an exception: {type(e).__name__}: {e}")