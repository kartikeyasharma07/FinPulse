"""
Raw NSE quote-equity test with a manual browser-style cookie handshake -
no library abstraction involved. Run with: python -m app.debug_nse_raw
"""
import requests

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.nseindia.com/",
}

session = requests.Session()
session.headers.update(headers)

print("Step 1: visiting nseindia.com homepage to collect cookies...")
homepage_resp = session.get("https://www.nseindia.com", timeout=10)
print(f"  status: {homepage_resp.status_code}, cookies collected: {list(session.cookies.keys())}")

print("\nStep 2: calling quote-equity endpoint with those cookies...")
resp = session.get("https://www.nseindia.com/api/quote-equity?symbol=RELIANCE", timeout=10)
print(f"  status: {resp.status_code}")

try:
    data = resp.json()
    print(f"  parsed JSON OK. Top-level keys: {list(data.keys())}")
    if data:
        print(f"\n  Sample - lastPrice: {data.get('priceInfo', {}).get('lastPrice')}")
    else:
        print("  Result: empty JSON object {}")
except ValueError:
    print(f"  NOT valid JSON. Raw response (first 300 chars):\n{resp.text[:300]}")