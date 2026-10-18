"""Daily swing-trade screener for the S&P 500.

Finds stocks in a Mark Minervini style Stage 2 uptrend (Trend Template),
ranks them by IBD-style relative strength, and flags common swing setups:
breakouts, stocks near their pivot, tight VCP-like bases, volume dry-ups
and pocket pivots.

Writes two files for the dashboard in docs/:
  screener.json         one row per stock, plus summary counts
  screener_charts.json  recent daily bars for the trend-template stocks
"""
import json
import os
import sys
import time
from datetime import datetime, timezone

import numpy as np
import pandas as pd
import yfinance as yf

from breadth_update import get_tickers

TICKER_CSV = "https://raw.githubusercontent.com/Ate329/top-us-stock-tickers/main/tickers/sp500.csv"
OUT_PATH = "docs/screener.json"
CHARTS_PATH = "docs/screener_charts.json"
BREADTH_LOG = "update_log.json"

HISTORY_DAYS = 430      # calendar days: enough for a 200-day average plus a 52-week range
CHART_BARS = 130        # daily bars sent to the chart view
PIVOT_LOOKBACK = 20     # prior bars that define the breakout pivot
NEAR_PIVOT = 0.05       # within 5% below the pivot
BREAKOUT_VOLUME = 1.4   # breakout volume must be 1.4x the 50-day average
TIGHT_RANGE = 0.08      # 10-day high-low range under 8% of price
DRY_UP = 0.75           # 10-day volume under 75% of the 50-day average
MAX_RISK = 0.10         # stops more than 10% away are flagged as too wide


def get_names():
    """Company name and industry for each ticker, keyed like get_tickers()."""
    try:
        df = pd.read_csv(TICKER_CSV)
        df["symbol"] = (
            df["symbol"].astype(str).str.strip()
            .str.replace("/", "-", regex=False)
            .str.replace(".", "-", regex=False)
        )
        names = {}
        for _, r in df.iterrows():
            name = str(r.get("name", "") or "")
            for suffix in (" Common Stock", " Class A", " Class B", " Class C",
                           " Ordinary Shares", " Inc.", " Inc", " Corporation", " Corp."):
                name = name.replace(suffix, "")
            names[r["symbol"]] = {
                "name": name.strip(" ,"),
                "sector": str(r.get("industry", "") or ""),
            }
        return names
    except Exception as e:
        print(f"Could not load company names: {e}")
        return {}


def download(tickers):
    """Daily OHLCV for every ticker as a dict of DataFrames (one per field)."""
    fields = ["Open", "High", "Low", "Close", "Volume"]
    parts = {f: [] for f in fields}
    for i in range(0, len(tickers), 100):
        batch = tickers[i:i + 100]
        for attempt in range(3):
            try:
                raw = yf.download(
                    batch,
                    period=f"{HISTORY_DAYS}d",
                    progress=False,
                    auto_adjust=True,
                    threads=True,
                    group_by="column",
                )
                if raw.empty:
                    raise RuntimeError("empty response")
                for f in fields:
                    parts[f].append(raw[f])
                break
            except Exception as e:
                print(f"Batch {i // 100 + 1} attempt {attempt + 1} failed: {e}")
                time.sleep(5)
        time.sleep(0.5)

    if not parts["Close"]:
        raise RuntimeError("No price data downloaded")
    data = {f: pd.concat(parts[f], axis=1).sort_index() for f in fields}
    data = {f: df.loc[:, ~df.columns.duplicated()] for f, df in data.items()}
    print(f"Downloaded {data['Close'].shape[1]} tickers x {data['Close'].shape[0]} days")
    return data


def pct(a, b):
    return (a / b - 1.0) if b else np.nan


def rnd(x, n=2):
    if x is None or (isinstance(x, float) and not np.isfinite(x)):
        return None
    return round(float(x), n)


def analyse(sym, o, h, l, c, v):
    """Metrics for one stock. Series are aligned and NaN-free."""
    n = len(c)
    if n < 220:
        return None

    close = c.iloc[-1]
    sma50 = c.rolling(50).mean()
    sma150 = c.rolling(150).mean()
    sma200 = c.rolling(200).mean()
    s50, s150, s200 = sma50.iloc[-1], sma150.iloc[-1], sma200.iloc[-1]
    s200_month_ago = sma200.iloc[-22]

    window = min(252, n)
    hi52 = h.iloc[-window:].max()
    lo52 = l.iloc[-window:].min()

    def ret(bars):
        return pct(close, c.iloc[-bars - 1]) if n > bars else np.nan

    r63, r126, r189, r252 = ret(63), ret(126), ret(189), ret(252)
    if not np.isfinite(r252):
        r252 = ret(n - 2)
    rs_raw = 0.4 * r63 + 0.2 * r126 + 0.2 * r189 + 0.2 * r252

    avgvol50 = v.iloc[-51:-1].mean()
    avgvol10 = v.iloc[-10:].mean()
    vol_ratio = v.iloc[-1] / avgvol50 if avgvol50 else np.nan
    dryup_ratio = avgvol10 / avgvol50 if avgvol50 else np.nan

    pivot = h.iloc[-PIVOT_LOOKBACK - 1:-1].max()
    to_pivot = pct(pivot, close)

    range10 = (h.iloc[-10:].max() - l.iloc[-10:].min()) / close
    # Three consecutive 20-day ranges, oldest first. A VCP shows each
    # pullback smaller than the last.
    ranges = []
    for start, end in ((-60, -40), (-40, -20), (-20, None)):
        hh = h.iloc[start:end].max()
        ll = l.iloc[start:end].min()
        ranges.append((hh - ll) / hh if hh else np.nan)

    prev_close = c.iloc[-2]
    day_chg = pct(close, prev_close)
    tr = pd.concat([h - l, (h - c.shift()).abs(), (l - c.shift()).abs()], axis=1).max(axis=1)
    atr14 = tr.iloc[-14:].mean()
    adr20 = ((h / l) - 1).iloc[-20:].mean()

    # Pocket pivot: an up day whose volume beats every down day of the prior 10.
    prior = pd.DataFrame({"c": c, "v": v}).iloc[-11:-1]
    down_vols = prior["v"][prior["c"] < prior["c"].shift()]
    max_down_vol = down_vols.max() if len(down_vols) else 0
    pocket = bool(close > prev_close and v.iloc[-1] > max_down_vol and close > s50)

    stop = l.iloc[-10:].min()
    risk = pct(close, stop) if stop else np.nan
    if not np.isfinite(risk) or risk <= 0:
        stop, risk = close - 1.5 * atr14, 1.5 * atr14 / close

    return {
        "t": sym,
        "close": close,
        "day": day_chg,
        "s50": s50, "s150": s150, "s200": s200,
        "s200_up": s200 > s200_month_ago,
        "hi52": hi52, "lo52": lo52,
        "rs_raw": rs_raw,
        "r63": r63,
        "vol_ratio": vol_ratio,
        "dryup_ratio": dryup_ratio,
        "pivot": pivot, "to_pivot": to_pivot,
        "range10": range10,
        "ranges": ranges,
        "atr_pct": atr14 / close,
        "adr": adr20,
        "pocket": pocket,
        "stop": stop, "risk": risk,
        "dollar_vol": avgvol50 * close,
    }


def trend_template(m):
    """The eight Minervini Trend Template checks, in his order."""
    close = m["close"]
    return [
        close > m["s150"] and close > m["s200"],
        m["s150"] > m["s200"],
        m["s200_up"],
        m["s50"] > m["s150"] and m["s50"] > m["s200"],
        close > m["s50"],
        close >= 1.30 * m["lo52"],
        close >= 0.75 * m["hi52"],
        m["rs"] >= 70,
    ]


def setups(m):
    flags = []
    if m["close"] > m["pivot"] and m["vol_ratio"] >= BREAKOUT_VOLUME:
        flags.append("BREAKOUT")
    elif 0 <= m["to_pivot"] <= NEAR_PIVOT:
        flags.append("NEAR_PIVOT")
    r = m["ranges"]
    if all(np.isfinite(r)) and r[0] > r[1] > r[2] and r[2] <= 0.12 and m["dryup_ratio"] < 1.0:
        flags.append("VCP")
    if m["range10"] <= TIGHT_RANGE:
        flags.append("TIGHT")
    if m["dryup_ratio"] <= DRY_UP:
        flags.append("DRY_UP")
    if m["pocket"]:
        flags.append("POCKET_PIVOT")
    return flags


def score(m):
    """Sort key for the default view: strongest, most actionable setups first."""
    s = m["rs"]
    f = m["setups"]
    s += 25 if "BREAKOUT" in f else 0
    s += 15 if "NEAR_PIVOT" in f else 0
    s += 15 if "VCP" in f else 0
    s += 8 if "TIGHT" in f else 0
    s += 5 if "DRY_UP" in f else 0
    s += 8 if "POCKET_PIVOT" in f else 0
    s -= 15 if m["risk"] > MAX_RISK else 0
    return s


def load_previous():
    try:
        with open(OUT_PATH) as fh:
            prev = json.load(fh)
        return {r["t"]: r.get("first_seen") for r in prev.get("stocks", []) if r.get("tt_pass")}
    except Exception:
        return {}


def load_breadth():
    try:
        with open(BREADTH_LOG) as fh:
            log = json.load(fh)
        return {k: log.get(k) for k in ("signal", "regime", "ratio", "latest_date")}
    except Exception:
        return None


def main():
    tickers = get_tickers()
    names = get_names()
    data = download(tickers)
    last_date = data["Close"].dropna(how="all").index[-1]
    as_of = last_date.strftime("%Y-%m-%d")

    metrics, charts_src = [], {}
    for sym in data["Close"].columns:
        frame = pd.DataFrame({f: data[f][sym] for f in data}).dropna()
        frame = frame[frame["Volume"] > 0]
        if frame.empty or frame.index[-1] != last_date:
            continue
        try:
            m = analyse(sym, frame["Open"], frame["High"], frame["Low"], frame["Close"], frame["Volume"])
        except Exception as e:
            print(f"{sym}: {e}")
            continue
        if m and np.isfinite(m["rs_raw"]):
            metrics.append(m)
            charts_src[sym] = frame

    if len(metrics) < 300:
        raise RuntimeError(f"Only {len(metrics)} stocks analysed; data looks incomplete")

    ranks = pd.Series([m["rs_raw"] for m in metrics]).rank(pct=True)
    for m, r in zip(metrics, ranks):
        m["rs"] = int(max(1, min(99, round(r * 99))))

    previous = load_previous()
    stocks = []
    for m in metrics:
        checks = trend_template(m)
        m["setups"] = setups(m)
        tt_pass = all(checks)
        info = names.get(m["t"], {})
        row = {
            "t": m["t"],
            "name": info.get("name", ""),
            "sector": info.get("sector", ""),
            "close": rnd(m["close"]),
            "day": rnd(m["day"] * 100, 2),
            "rs": m["rs"],
            "tt": sum(bool(x) for x in checks),
            "tt_checks": [bool(x) for x in checks],
            "tt_pass": tt_pass,
            "from_high": rnd((m["close"] / m["hi52"] - 1) * 100, 1),
            "from_low": rnd((m["close"] / m["lo52"] - 1) * 100, 1),
            "r63": rnd(m["r63"] * 100, 1),
            "pivot": rnd(m["pivot"]),
            "to_pivot": rnd(m["to_pivot"] * 100, 1) or 0.0,
            "range10": rnd(m["range10"] * 100, 1),
            "vol_ratio": rnd(m["vol_ratio"], 2),
            "dryup": rnd(m["dryup_ratio"], 2),
            "adr": rnd(m["adr"] * 100, 1),
            "stop": rnd(m["stop"]),
            "risk": rnd(m["risk"] * 100, 1),
            "dollar_vol_m": rnd(m["dollar_vol"] / 1e6, 0),
            "setups": m["setups"] if tt_pass else [],
            "score": rnd(score(m), 1),
        }
        if tt_pass:
            row["first_seen"] = previous.get(m["t"]) or as_of
        stocks.append(row)

    stocks.sort(key=lambda r: (not r["tt_pass"], -(r["score"] or 0)))
    passers = [s for s in stocks if s["tt_pass"]]

    def count(flag):
        return sum(flag in s["setups"] for s in passers)

    out = {
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "as_of": as_of,
        "universe": len(stocks),
        "summary": {
            "trend_template": len(passers),
            "breakouts": count("BREAKOUT"),
            "near_pivot": count("NEAR_PIVOT"),
            "vcp": count("VCP"),
            "pocket_pivots": count("POCKET_PIVOT"),
            "new_today": sum(s.get("first_seen") == as_of for s in passers),
        },
        "breadth": load_breadth(),
        "stocks": stocks,
    }

    charts = {}
    for s in passers:
        f = charts_src[s["t"]]
        c = f["Close"]
        lines = {k: c.rolling(w).mean() for k, w in (("m50", 50), ("m150", 150), ("m200", 200))}
        f = f.iloc[-CHART_BARS:]
        charts[s["t"]] = {
            "d": [d.strftime("%Y-%m-%d") for d in f.index],
            "o": [rnd(x) for x in f["Open"]],
            "h": [rnd(x) for x in f["High"]],
            "l": [rnd(x) for x in f["Low"]],
            "c": [rnd(x) for x in f["Close"]],
            "v": [int(x) for x in f["Volume"]],
            **{k: [rnd(x) for x in ser.iloc[-CHART_BARS:]] for k, ser in lines.items()},
        }

    os.makedirs("docs", exist_ok=True)
    with open(OUT_PATH, "w") as fh:
        json.dump(out, fh, separators=(",", ":"))
    with open(CHARTS_PATH, "w") as fh:
        json.dump({"as_of": as_of, "charts": charts}, fh, separators=(",", ":"))

    print(f"As of {as_of}: {len(stocks)} stocks, {len(passers)} pass the Trend Template")
    print(json.dumps(out["summary"]))


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Screener failed: {e}")
        sys.exit(1)
