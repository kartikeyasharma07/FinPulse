from nselib import capital_market

attempts = [
    {"period": "1Y", "fo_sec": True, "fin_period": "Quarterly"},
    {"period": "1Y", "fo_sec": False, "fin_period": "Quarterly"},
    {"period": "1Y", "fo_sec": True, "fin_period": "Annual"},
]

for params in attempts:
    print(f"\n{'='*60}")
    print(f"Trying financial_results_for_equity({params})...\n")
    try:
        df = capital_market.financial_results_for_equity(**params)
        if df is None or df.empty:
            print("Result: empty")
            continue
        print(f"Success! Got {len(df)} rows.\n")
        print("All columns:")
        for col in df.columns:
            print(f"  - {col}")
        print("\nSample row:")
        for k, v in df.iloc[0].items():
            print(f"  {k}: {v}")
        break  # stop at the first attempt that returns something
    except Exception as e:
        print(f"Exception: {type(e).__name__}: {e}")