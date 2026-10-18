"""Daily chart data for the Charts page, with TA-Lib indicators and candlestick patterns.

Writes one JSON file per S&P 500 stock (plus SPY and QQQ) into chart-data/,
and chart-data/list.json with a one-line summary per stock. The workflow
publishes that folder to the `chart-data` branch, replacing the previous day,
so the repository history does not grow.
"""
import json
import os
import sys
from datetime import datetime, timezone

import numpy as np
import pandas as pd
import talib

from breadth_update import get_tickers
import swing_screener
from swing_screener import download, get_names

OUT_DIR = "chart-data"
EXTRA = ["SPY", "QQQ"]
EXTRA_NAMES = {"SPY": "SPDR S&P 500 ETF", "QQQ": "Invesco QQQ (Nasdaq-100)"}
BARS = 500               # about two years of daily bars
PATTERN_LOOKBACK = 120   # bars scanned for candlestick-pattern markers
# TA-Lib flags these dojis with +100 regardless of direction; use the usual reading.
FIXED_DIRECTION = {"CDLGRAVESTONEDOJI": "bear", "CDLDRAGONFLYDOJI": "bull"}

# TA-Lib candlestick functions shown on the chart, with plain names.
# TA-Lib returns +100 for a bullish signal and -100 for a bearish one.
PATTERNS = {
    "CDLENGULFING": "Engulfing",
    "CDLHAMMER": "Hammer",
    "CDLINVERTEDHAMMER": "Inverted hammer",
    "CDLSHOOTINGSTAR": "Shooting star",
    "CDLHANGINGMAN": "Hanging man",
    "CDLMORNINGSTAR": "Morning star",
    "CDLEVENINGSTAR": "Evening star",
    "CDLPIERCING": "Piercing line",
    "CDLDARKCLOUDCOVER": "Dark cloud cover",
    "CDL3WHITESOLDIERS": "Three white soldiers",
    "CDL3BLACKCROWS": "Three black crows",
    "CDLHARAMI": "Harami",
    "CDLDRAGONFLYDOJI": "Dragonfly doji",
    "CDLGRAVESTONEDOJI": "Gravestone doji",
}


def rnd(x, n=2):
    if x is None or not np.isfinite(x):
        return None
    return round(float(x), n)


def indicators(o, h, l, c, v):
    rsi = talib.RSI(c, 14)
    macd, signal, hist = talib.MACD(c, 12, 26, 9)
    adx = talib.ADX(h, l, c, 14)
    plus_di = talib.PLUS_DI(h, l, c, 14)
    minus_di = talib.MINUS_DI(h, l, c, 14)
    atr = talib.ATR(h, l, c, 14)
    sma50 = talib.SMA(c, 50)
    sma200 = talib.SMA(c, 200)
    stoch_k, stoch_d = talib.STOCH(h, l, c, 14, 3, 0, 3, 0)
    obv = talib.OBV(c, v)
    close = c[-1]
    return {
        "rsi": rnd(rsi[-1], 1),
        "macd": rnd(macd[-1], 3),
        "macd_signal": rnd(signal[-1], 3),
        "macd_hist": rnd(hist[-1], 3),
        "macd_cross": ("up" if hist[-1] > 0 >= hist[-2] else "down" if hist[-1] < 0 <= hist[-2] else None)
        if np.isfinite(hist[-2]) else None,
        "adx": rnd(adx[-1], 1),
        "plus_di": rnd(plus_di[-1], 1),
        "minus_di": rnd(minus_di[-1], 1),
        "atr": rnd(atr[-1], 2),
        "atr_pct": rnd(atr[-1] / close * 100, 2),
        "stoch_k": rnd(stoch_k[-1], 1),
        "stoch_d": rnd(stoch_d[-1], 1),
        "obv_trend": ("up" if obv[-1] > obv[-21] else "down") if len(obv) > 21 else None,
        "vs_sma50": rnd((close / sma50[-1] - 1) * 100, 1),
        "vs_sma200": rnd((close / sma200[-1] - 1) * 100, 1),
    }


def patterns(o, h, l, c, dates):
    found = []
    start = max(0, len(c) - PATTERN_LOOKBACK)
    for fn, label in PATTERNS.items():
        out = getattr(talib, fn)(o, h, l, c)
        for i in np.nonzero(out[start:])[0] + start:
            found.append({"i": int(i), "d": dates[i], "name": label,
                          "dir": FIXED_DIRECTION.get(fn) or ("bull" if out[i] > 0 else "bear")})
    found.sort(key=lambda p: (p["i"], p["name"]))
    return found


def main():
    swing_screener.HISTORY_DAYS = 760  # about 520 trading days
    tickers = get_tickers() + EXTRA
    names = get_names()
    data = download(tickers)
    last_date = data["Close"].dropna(how="all").index[-1]
    as_of = last_date.strftime("%Y-%m-%d")
    os.makedirs(OUT_DIR, exist_ok=True)

    summary = []
    for sym in data["Close"].columns:
        frame = pd.DataFrame({f: data[f][sym] for f in data}).dropna()
        frame = frame[frame["Volume"] > 0]
        if len(frame) < 60 or frame.index[-1] != last_date:
            continue
        o, h, l, c, v = (frame[f].to_numpy(dtype=float) for f in ("Open", "High", "Low", "Close", "Volume"))
        dates = [d.strftime("%Y-%m-%d") for d in frame.index]
        try:
            ind = indicators(o, h, l, c, v)
            pats = patterns(o, h, l, c, dates)
        except Exception as e:
            print(f"{sym}: {e}")
            continue

        keep = slice(-BARS, None)
        offset = max(0, len(c) - BARS)
        info = names.get(sym, {})
        name = info.get("name") or EXTRA_NAMES.get(sym, "")
        doc = {
            "t": sym,
            "name": name,
            "sector": info.get("sector", "ETF" if sym in EXTRA else ""),
            "as_of": as_of,
            "d": dates[keep],
            "o": [rnd(x) for x in o[keep]],
            "h": [rnd(x) for x in h[keep]],
            "l": [rnd(x) for x in l[keep]],
            "c": [rnd(x) for x in c[keep]],
            "v": [int(x) for x in v[keep]],
            "ind": ind,
            "patterns": [{**p, "i": p["i"] - offset} for p in pats if p["i"] >= offset],
        }
        with open(os.path.join(OUT_DIR, f"{sym}.json"), "w") as fh:
            json.dump(doc, fh, separators=(",", ":"))

        today = [p for p in pats if p["i"] == len(c) - 1]
        summary.append({
            "t": sym,
            "name": name,
            "close": rnd(c[-1]),
            "day": rnd((c[-1] / c[-2] - 1) * 100, 2),
            "rsi": ind["rsi"],
            "adx": ind["adx"],
            "today": [f'{p["name"]} ({p["dir"]})' for p in today],
        })

    if len(summary) < 300:
        raise RuntimeError(f"Only {len(summary)} stocks processed; data looks incomplete")
    summary.sort(key=lambda r: r["t"])
    with open(os.path.join(OUT_DIR, "list.json"), "w") as fh:
        json.dump({
            "as_of": as_of,
            "generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "stocks": summary,
        }, fh, separators=(",", ":"))
    print(f"As of {as_of}: wrote {len(summary)} charts to {OUT_DIR}/")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Chart data failed: {e}")
        sys.exit(1)
