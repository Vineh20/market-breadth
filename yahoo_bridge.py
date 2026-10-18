"""Run a claude-trading-skills script with Yahoo Finance supplying its price data.

The FMP free plan only serves quotes and price history for a small sample of
symbols, and never for several symbols in one request. This wrapper intercepts
the skills' FMP quote and price-history requests and answers them from Yahoo
Finance in FMP's JSON format. Every other FMP request (earnings calendar,
profiles, ...) still goes to FMP with the real key.

Usage: python yahoo_bridge.py path/to/skill_script.py [args...]
"""
import json
import os
import pickle
import runpy
import sys
from datetime import date, timedelta
from urllib.parse import urlparse

import pandas as pd
import requests
import yfinance as yf

TICKER_CSV = "https://raw.githubusercontent.com/Ate329/top-us-stock-tickers/main/tickers/sp500.csv"
CACHE_PATH = os.environ.get("YAHOO_BRIDGE_CACHE", "pro-out/yahoo_cache.pkl")
HISTORY = "2y"

_frames = {}       # symbol -> DataFrame of daily OHLCV, oldest first
_profiles = {}     # symbol -> {"name", "marketCap", "sector"}
_loaded = False
_original_get = requests.Session.get


def _load():
    global _loaded
    if _loaded:
        return
    _loaded = True
    if os.path.exists(CACHE_PATH):
        try:
            with open(CACHE_PATH, "rb") as fh:
                cached = pickle.load(fh)
            if cached.get("day") == date.today().isoformat():
                _frames.update(cached["frames"])
                _profiles.update(cached["profiles"])
                return
        except Exception:
            pass
    try:
        df = pd.read_csv(TICKER_CSV)
        for _, r in df.iterrows():
            sym = str(r["symbol"]).strip().replace("/", "-").replace(".", "-")
            _profiles[sym] = {
                "name": str(r.get("name", "") or ""),
                "marketCap": float(r.get("marketCap") or 0),
                "sector": str(r.get("industry", "") or ""),
            }
    except Exception as e:
        print(f"[yahoo-bridge] could not load ticker list: {e}", file=sys.stderr)
    _download(list(_profiles) + ["SPY", "QQQ", "^GSPC", "^IXIC", "^VIX", "IWM", "DIA"])
    _save()


def _save():
    try:
        os.makedirs(os.path.dirname(CACHE_PATH) or ".", exist_ok=True)
        with open(CACHE_PATH, "wb") as fh:
            pickle.dump({"day": date.today().isoformat(), "frames": _frames, "profiles": _profiles}, fh)
    except Exception as e:
        print(f"[yahoo-bridge] cache not saved: {e}", file=sys.stderr)


def _download(symbols):
    symbols = [s for s in dict.fromkeys(symbols) if s and s not in _frames]
    for i in range(0, len(symbols), 100):
        batch = symbols[i:i + 100]
        try:
            raw = yf.download(batch, period=HISTORY, progress=False, auto_adjust=True,
                              threads=True, group_by="ticker")
        except Exception as e:
            print(f"[yahoo-bridge] download failed for {len(batch)} symbols: {e}", file=sys.stderr)
            continue
        for sym in batch:
            try:
                frame = raw[sym] if isinstance(raw.columns, pd.MultiIndex) else raw
                frame = frame[["Open", "High", "Low", "Close", "Volume"]].dropna()
                if not frame.empty:
                    _frames[sym] = frame
            except Exception:
                pass


def _frame(sym):
    _load()
    key = sym.replace(".", "-")
    if key not in _frames:
        _download([key])
        if key in _frames:
            _save()
    return _frames.get(key)


def _quote(sym):
    f = _frame(sym)
    if f is None or len(f) < 2:
        return None
    last, prev = f.iloc[-1], f.iloc[-2]
    year = f.iloc[-252:]
    close = float(last["Close"])
    prof = _profiles.get(sym.replace(".", "-"), {})
    change = close - float(prev["Close"])
    pct = change / float(prev["Close"]) * 100 if prev["Close"] else 0.0
    return {
        "symbol": sym,
        "name": prof.get("name") or sym,
        "price": round(close, 4),
        "change": round(change, 4),
        "changePercentage": round(pct, 4),
        "changesPercentage": round(pct, 4),
        "open": round(float(last["Open"]), 4),
        "dayHigh": round(float(last["High"]), 4),
        "dayLow": round(float(last["Low"]), 4),
        "previousClose": round(float(prev["Close"]), 4),
        "volume": int(last["Volume"]),
        "avgVolume": int(f["Volume"].iloc[-63:].mean()),
        "yearHigh": round(float(year["High"].max()), 4),
        "yearLow": round(float(year["Low"].min()), 4),
        "priceAvg50": round(float(f["Close"].iloc[-50:].mean()), 4),
        "priceAvg200": round(float(f["Close"].iloc[-200:].mean()), 4),
        "marketCap": prof.get("marketCap") or None,
        "exchange": "NASDAQ" if sym in ("QQQ",) else "NYSE",
        "timestamp": int(pd.Timestamp(f.index[-1]).timestamp()),
    }


def _history_rows(sym, start=None, end=None):
    f = _frame(sym)
    if f is None:
        return []
    if start:
        f = f[f.index >= pd.Timestamp(start)]
    if end:
        f = f[f.index <= pd.Timestamp(end)]
    rows = []
    prev_close = None
    for ts, r in f.iterrows():
        close = float(r["Close"])
        change = close - prev_close if prev_close else 0.0
        rows.append({
            "symbol": sym,
            "date": ts.strftime("%Y-%m-%d"),
            "open": round(float(r["Open"]), 4),
            "high": round(float(r["High"]), 4),
            "low": round(float(r["Low"]), 4),
            "close": round(close, 4),
            "adjClose": round(close, 4),
            "volume": int(r["Volume"]),
            "change": round(change, 4),
            "changePercent": round(change / prev_close * 100, 4) if prev_close else 0.0,
            "vwap": round((float(r["High"]) + float(r["Low"]) + close) / 3, 4),
        })
        prev_close = close
    rows.reverse()  # FMP returns newest first
    return rows


def _response(url, payload):
    r = requests.models.Response()
    r.status_code = 200 if payload not in (None, [], {}) else 404
    r._content = json.dumps(payload if payload is not None else []).encode()
    r.headers["Content-Type"] = "application/json"
    r.encoding = "utf-8"
    r.url = url
    return r


def _route(url, params):
    """Return a fake Response for price endpoints, or None to pass through."""
    u = urlparse(url)
    if "financialmodelingprep.com" not in u.netloc:
        return None
    path = u.path.rstrip("/")
    params = params or {}
    if path == "/stable/quote" or path.startswith("/api/v3/quote/"):
        syms = params.get("symbol") or path.rsplit("/", 1)[-1]
        quotes = [q for q in (_quote(s.strip()) for s in str(syms).split(",")) if q]
        return _response(url, quotes)
    if path == "/stable/historical-price-eod/full" or path == "/stable/historical-price-eod/light":
        sym = str(params.get("symbol", ""))
        return _response(url, _history_rows(sym, params.get("from"), params.get("to")))
    if path.startswith("/api/v3/historical-price-full/"):
        sym = path.rsplit("/", 1)[-1]
        rows = _history_rows(sym, params.get("from"), params.get("to"))
        n = params.get("timeseries")
        if n:
            rows = rows[:int(n)]
        hist = [{k: v for k, v in row.items() if k != "symbol"} for row in rows]
        return _response(url, {"symbol": sym, "historical": hist} if hist else {})
    return None


def _patched_get(self, url, params=None, **kwargs):
    try:
        fake = _route(url, dict(params) if params else {})
    except Exception as e:
        print(f"[yahoo-bridge] error answering {urlparse(url).path}: {e}", file=sys.stderr)
        fake = None
    if fake is not None:
        return fake
    return _original_get(self, url, params=params, **kwargs)


def main():
    if len(sys.argv) < 2:
        sys.exit("usage: yahoo_bridge.py SCRIPT [args...]")
    script = os.path.abspath(sys.argv[1])
    requests.Session.get = _patched_get
    sys.argv = [script] + sys.argv[2:]
    sys.path.insert(0, os.path.dirname(script))
    runpy.run_path(script, run_name="__main__")


if __name__ == "__main__":
    main()
