"""Check which FMP endpoints the FMP_API_KEY plan can use.

Results are printed as GitHub Actions notices so they show on the run page.
The key itself is never printed.
"""
import os
import requests

KEY = os.environ.get("FMP_API_KEY", "")
BASE = "https://financialmodelingprep.com"
CHECKS = [
    ("quote AAPL", "/stable/quote", {"symbol": "AAPL"}),
    ("quote 5 symbols", "/stable/quote", {"symbol": "AAPL,MSFT,NVDA,AMZN,META"}),
    ("quote QQQ", "/stable/quote", {"symbol": "QQQ"}),
    ("quote ^GSPC", "/stable/quote", {"symbol": "^GSPC"}),
    ("quote ADBE", "/stable/quote", {"symbol": "ADBE"}),
    ("quote DVN", "/stable/quote", {"symbol": "DVN"}),
    ("history DVN", "/stable/historical-price-eod/full", {"symbol": "DVN"}),
    ("v3 quote DVN", "/api/v3/quote/DVN", {}),
    ("profile DVN", "/stable/profile", {"symbol": "DVN"}),
    ("income DVN", "/stable/income-statement", {"symbol": "DVN", "period": "quarter", "limit": 4}),
    ("earnings calendar", "/stable/earnings-calendar", {}),
]

if not KEY:
    print("::error title=FMP check::FMP_API_KEY secret is not set")
for name, path, params in CHECKS:
    if not KEY:
        break
    try:
        r = requests.get(BASE + path, params={**params, "apikey": KEY}, timeout=30)
        body = r.text.replace(KEY, "***")
        try:
            data = r.json()
            size = len(data) if isinstance(data, list) else ("object" if isinstance(data, dict) else "?")
        except ValueError:
            size = "not JSON"
        msg = f"HTTP {r.status_code} · items {size} · {body[:160]}"
    except Exception as e:
        msg = f"request failed: {str(e).replace(KEY, '***')[:200]}"
    level = "notice" if "HTTP 200" in msg and "items 0" not in msg else "warning"
    print(f"::{level} title=FMP {name}::{msg}".replace("\n", " "))
