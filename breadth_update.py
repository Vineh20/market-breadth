import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import os, sys, json, time

CSV_PATH = "market_breadth_200d_REAL.csv"
LOG_PATH = "update_log.json"

# This is an S&P 500 proxy for the much broader US common-stock universe
# used by Pradeep Bonde's original Market Monitor.
REFERENCE_UNIVERSE = 3500.0


def get_tickers():
    url = "https://raw.githubusercontent.com/Ate329/top-us-stock-tickers/main/tickers/sp500.csv"
    try:
        df = pd.read_csv(url)
        tickers = (
            df["symbol"]
            .dropna()
            .astype(str)
            .str.strip()
            .str.replace("/", "-", regex=False)
            .str.replace(".", "-", regex=False)
            .tolist()
        )
        tickers = list(dict.fromkeys(tickers))
        if len(tickers) < 450:
            raise RuntimeError(f"Only {len(tickers)} S&P 500 tickers found")
        print(f"Got {len(tickers)} S&P 500 tickers")
        return tickers
    except Exception as e:
        raise RuntimeError(f"Could not obtain the S&P 500 ticker list: {e}")


def get_prices(tickers, days):
    end = datetime.today()
    start = end - timedelta(days=days)
    close_parts = []
    volume_parts = []

    for i in range(0, len(tickers), 100):
        batch = tickers[i:i + 100]
        try:
            raw = yf.download(
                batch,
                start=start,
                end=end,
                progress=False,
                auto_adjust=True,
                threads=True,
                group_by="column",
            )
            if raw.empty:
                continue

            # yfinance returns a MultiIndex for multi-ticker downloads.
            if isinstance(raw.columns, pd.MultiIndex):
                close = raw["Close"]
                volume = raw["Volume"]
            else:
                # Single-ticker fallback.
                symbol = batch[0]
                close = raw[["Close"]].rename(columns={"Close": symbol})
                volume = raw[["Volume"]].rename(columns={"Volume": symbol})

            close_parts.append(close)
            volume_parts.append(volume)
            time.sleep(0.5)
        except Exception as e:
            print(f"Batch {i // 100 + 1} failed: {e}")

    if not close_parts:
        raise RuntimeError("No data downloaded")

    close_data = pd.concat(close_parts, axis=1)
    volume_data = pd.concat(volume_parts, axis=1)

    # Remove duplicate ticker columns and columns with no price data.
    close_data = close_data.loc[:, ~close_data.columns.duplicated()]
    volume_data = volume_data.loc[:, ~volume_data.columns.duplicated()]
    common = close_data.columns.intersection(volume_data.columns)
    close_data = close_data[common]
    volume_data = volume_data[common]

    valid = close_data.notna().any(axis=0)
    close_data = close_data.loc[:, valid]
    volume_data = volume_data.loc[:, close_data.columns]

    print(f"Downloaded {close_data.shape[1]} stocks x {close_data.shape[0]} days")
    return {"close": close_data, "volume": volume_data}


def calc_row(data, i):
    close = data["close"]
    volume = data["volume"]

    if i < 1:
        return None

    current = close.iloc[i]
    previous = close.iloc[i - 1]
    vol_today = volume.iloc[i]
    vol_prev = volume.iloc[i - 1]

    daily_change = (current / previous - 1).replace([float("inf"), -float("inf")], pd.NA)
    daily_change = daily_change.dropna()

    # Bonde's 4% daily scan requires a 4% move AND volume >= 100,000
    # shares AND volume greater than the prior day.
    eligible_volume = (vol_today >= 100000) & (vol_today > vol_prev)
    eligible_volume = eligible_volume.reindex(current.index).fillna(False)

    up4 = (daily_change >= 0.04) & eligible_volume.reindex(daily_change.index).fillna(False)
    down4 = (daily_change <= -0.04) & eligible_volume.reindex(daily_change.index).fillna(False)

    # Primary 25% quarter scans use the 65-day low/high as the reference,
    # matching Bonde's published Market Monitor scan rather than simply
    # comparing today's close with the close 65 days ago.
    q_start = max(0, i - 65)
    q_window = close.iloc[q_start:i + 1]
    q_min = q_window.min(axis=0, skipna=True)
    q_max = q_window.max(axis=0, skipna=True)
    q_up = (current / q_min - 1)
    q_down = (current / q_max - 1)

    # Bonde's primary scans include an average-dollar-volume filter.
    vol_start = max(0, i - 19)
    avg_dollar_volume = (close.iloc[vol_start:i + 1] * volume.iloc[vol_start:i + 1]).mean(axis=0)
    liquidity = avg_dollar_volume >= 2_500_000

    q_up_count = (q_up >= 0.25) & liquidity
    q_down_count = (q_down <= -0.25) & liquidity

    # Secondary monthly scans use approximately 21 trading days.
    m_start = max(0, i - 20)
    month_ref = close.iloc[m_start]
    month_change = current / month_ref - 1
    month_ok = (month_ref >= 5) & liquidity

    # Primary fast 34/13 scans use 34-day low/high and the same liquidity idea.
    fast_start = max(0, i - 34)
    fast_window = close.iloc[fast_start:i + 1]
    fast_min = fast_window.min(axis=0, skipna=True)
    fast_max = fast_window.max(axis=0, skipna=True)
    fast_up = current / fast_min - 1
    fast_down = current / fast_max - 1

    # Approximation of T2108: percentage of stocks above their 40-day SMA.
    ma_start = max(0, i - 39)
    sma40 = close.iloc[ma_start:i + 1].mean(axis=0, skipna=True)
    above40 = (current > sma40).sum()
    valid40 = current.notna().sum()

    return {
        "Date": close.index[i].strftime("%Y-%m-%d"),
        "Up_4pct_Daily": int(up4.sum()),
        "Down_4pct_Daily": int(down4.sum()),
        "Up_2pct_Daily": int((daily_change >= 0.02).sum()),
        "Down_2pct_Daily": int((daily_change <= -0.02).sum()),
        "Up_25pct_Quarter": int(q_up_count.sum()),
        "Down_25pct_Quarter": int(q_down_count.sum()),
        "Up_50pct_Quarter": int(((q_up >= 0.50) & liquidity).sum()),
        "Up_25pct_Month": int((month_change >= 0.25).where(month_ok, False).sum()),
        "Down_25pct_Month": int((month_change <= -0.25).where(month_ok, False).sum()),
        "Up_50pct_Month": int((month_change >= 0.50).where(month_ok, False).sum()),
        "Up_13pct_34d": int((fast_up >= 0.13).where(liquidity, False).sum()),
        "Down_13pct_34d": int((fast_down <= -0.13).where(liquidity, False).sum()),
        "34_13D": int((fast_up >= 0.13).where(liquidity, False).sum() - (fast_down <= -0.13).where(liquidity, False).sum()),
        "T2108_Approx": round(100 * above40 / valid40, 1) if valid40 else 0,
        "Total_Stocks": int(current.notna().sum()),
    }


def add_metrics(df):
    df = df.copy()

    # Core Stockbee/Pradeep Bonde 5-day and 10-day breadth ratios.
    df["5Day_Bulls"] = df["Up_4pct_Daily"].rolling(5, min_periods=3).sum().round(0).astype("Int64")
    df["5Day_Bears"] = df["Down_4pct_Daily"].rolling(5, min_periods=3).sum().round(0).astype("Int64")
    df["5Day_Ratio"] = (df["5Day_Bulls"] / df["5Day_Bears"].replace(0, 1)).round(2)

    df["10Day_Bulls"] = df["Up_4pct_Daily"].rolling(10, min_periods=5).sum().round(0).astype("Int64")
    df["10Day_Bears"] = df["Down_4pct_Daily"].rolling(10, min_periods=5).sum().round(0).astype("Int64")
    df["10Day_Ratio"] = (df["10Day_Bulls"] / df["10Day_Bears"].replace(0, 1)).round(2)

    # Bonde's 34/13D = 34/13 bullish count - 34/13 bearish count.
    df["DCR"] = df["34_13D"]

    def primary_trend(row):
        up = int(row["Up_25pct_Quarter"])
        down = int(row["Down_25pct_Quarter"])
        if up > down:
            return "BULL"
        if up < down:
            return "BEAR"
        return "NEUTRAL"

    df["Primary_Trend"] = df.apply(primary_trend, axis=1)

    # The original Bonde material uses ~200 and ~500 as reference levels
    # for a much larger US common-stock universe. These are scaled here only
    # as a transparent S&P 500 approximation, not as official Bonde thresholds.
    df["Q25_Bull_Extreme_Threshold"] = (200.0 / REFERENCE_UNIVERSE * df["Total_Stocks"]).round(0)
    df["Q25_Dip_Toe_Threshold"] = (500.0 / REFERENCE_UNIVERSE * df["Total_Stocks"]).round(0)

    def thrust(row):
        r = float(row["10Day_Ratio"]) if pd.notna(row["10Day_Ratio"]) else 0
        if r >= 2.0:
            return "BULLISH_THRUST"
        if r <= 0.50:
            return "BEARISH_THRUST"
        return "NO_THRUST"

    df["Thrust"] = df.apply(thrust, axis=1)

    def extreme_zone(row):
        up = int(row["Up_25pct_Quarter"])
        down = int(row["Down_25pct_Quarter"])
        bull_extreme = float(row["Q25_Bull_Extreme_Threshold"])
        toe = float(row["Q25_Dip_Toe_Threshold"])
        if up <= bull_extreme:
            return "EXTREME_BULLISH_ZONE"
        if down <= bull_extreme:
            return "EXTREME_BEARISH_WARNING"
        if up <= toe:
            return "DIP_TOE_ZONE"
        return "NORMAL"

    df["Extreme_Zone"] = df.apply(extreme_zone, axis=1)

    # Practical action label using only the documented Bonde relationships:
    # >2 = bullish thrust, <0.5 = bearish thrust; primary trend is the
    # relationship between Q25 gainers and Q25 losers. Intermediate readings
    # are deliberately labelled SELECTIVE/WAIT rather than forced into CASH.
    def get_signal(row):
        r = float(row["10Day_Ratio"]) if pd.notna(row["10Day_Ratio"]) else 0
        primary = row["Primary_Trend"]
        zone = row["Extreme_Zone"]

        if zone == "EXTREME_BULLISH_ZONE":
            return "BUY_ZONE"
        if primary == "BULL" and r >= 2.0:
            return "TRADE"
        if primary == "BEAR" and r >= 2.0:
            return "RE-ENTRY_WATCH"
        if primary == "BULL" and r <= 0.50:
            return "REDUCE"
        if primary == "BEAR" and r <= 0.50:
            return "DEFENSIVE"
        if primary == "BULL" and r >= 1.0:
            return "SELECTIVE"
        if primary == "BULL":
            return "WAIT"
        if primary == "BEAR":
            return "DEFENSIVE"
        return "WAIT"

    df["Market_Regime"] = df["Primary_Trend"]
    df["Swing_Signal"] = df.apply(get_signal, axis=1)
    return df


def backfill(tickers):
    print("Running full 200-day backfill...")
    data = get_prices(tickers, days=320)
    rows = [calc_row(data, i) for i in range(1, len(data["close"]))]
    rows = [r for r in rows if r]
    df = pd.DataFrame(rows).tail(200).reset_index(drop=True)
    df = add_metrics(df)
    df.to_csv(CSV_PATH, index=False)
    print(f"Backfill done: {len(df)} rows")
    return df


def daily_update(tickers, existing):
    print("Running daily update...")
    data = get_prices(tickers, days=90)
    today = data["close"].index[-1].strftime("%Y-%m-%d")
    if today in existing["Date"].values:
        print(f"Already have {today}, skipping")
        return existing

    row = calc_row(data, len(data["close"]) - 1)
    if not row:
        print("Could not calculate today")
        return existing

    df = pd.concat([existing, pd.DataFrame([row])], ignore_index=True)
    df = df.tail(200).reset_index(drop=True)
    df = add_metrics(df)
    df.to_csv(CSV_PATH, index=False)
    last = df.iloc[-1]
    print(f"Updated: {today} | Primary: {last['Market_Regime']} | Ratio: {last['10Day_Ratio']} | Signal: {last['Swing_Signal']}")
    return df


def save_log(df):
    last = df.iloc[-1].to_dict()
    log = {
        "last_updated": datetime.utcnow().isoformat() + "Z",
        "latest_date": str(last.get("Date", "")),
        "ratio": float(last.get("10Day_Ratio", 0)),
        "ratio5": float(last.get("5Day_Ratio", 0)),
        "up25q": int(last.get("Up_25pct_Quarter", 0)),
        "dn25q": int(last.get("Down_25pct_Quarter", 0)),
        "up4": int(last.get("Up_4pct_Daily", 0)),
        "dn4": int(last.get("Down_4pct_Daily", 0)),
        "primary_trend": str(last.get("Primary_Trend", "")),
        "thrust": str(last.get("Thrust", "")),
        "extreme_zone": str(last.get("Extreme_Zone", "")),
        "regime": str(last.get("Market_Regime", "")),
        "signal": str(last.get("Swing_Signal", "")),
        "t2108_approx": float(last.get("T2108_Approx", 0)),
        "total_rows": len(df),
    }
    with open(LOG_PATH, "w") as f:
        json.dump(log, f, indent=2)
    print("Log saved")


if __name__ == "__main__":
    print("=" * 50)
    print(f"Market Breadth Updater - {datetime.today().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 50)
    tickers = get_tickers()
    existing = pd.read_csv(CSV_PATH) if os.path.exists(CSV_PATH) else pd.DataFrame()
    do_backfill = "--backfill" in sys.argv or existing.empty or len(existing) < 10
    df = backfill(tickers) if do_backfill else daily_update(tickers, existing)
    save_log(df)
    print(f"Done: {len(df)} rows | Primary: {df.iloc[-1]['Market_Regime']} | Signal: {df.iloc[-1]['Swing_Signal']}")
    print("=" * 50)
