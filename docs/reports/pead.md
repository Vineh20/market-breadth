# PEAD Screener Report - Post-Earnings Announcement Drift
**Generated:** 2026-11-15 19:37:52
**Mode:** A (FMP Earnings Calendar)
**Lookback:** 14 days
**Watch Window:** 5 weeks

---

## Summary

| Stage | Count |
|-------|-------|
| Total Screened | 6 |
| BREAKOUT | 0 |
| SIGNAL_READY | 2 |
| MONITORING | 4 |
| EXPIRED | 0 |
| Timing unknown | 0 of 14 |

---

## BREAKOUT (0 stocks)
*Price has broken above the red candle high on a green weekly candle*

No stocks in this stage.

---

## SIGNAL_READY (2 stocks)
*Red candle pullback identified, awaiting breakout*

### 1. SONY [DEVELOPING]
**Price:** $27.07 | **Earnings:** 2026-11-05 (bmo) | **Gap:** +6.2% | **Weeks Since:** 1
**PEAD Score:** 61.5/100 (Developing)

| Component | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| Setup Quality | 75 | 30% | 22.5 |
| Breakout Strength | 0 | 25% | 0.0 |
| Liquidity | 100 | 25% | 25.0 |
| Risk/Reward | 70 | 20% | 14.0 |

**Red Candle:** Week of 2026-11-09 | High: $27.32 | Low: $26.25

**Trade Setup:**
- Trigger: Close above $27.32 on green weekly candle
- Stop (if triggered): $26.25
- Action: Set alert at red candle high
- Guidance: Watchlist, wait for cleaner breakout

---

### 2. SHOP [DEVELOPING]
**Price:** $147.09 | **Earnings:** 2026-11-03 (bmo) | **Gap:** -12.7% | **Weeks Since:** 1
**PEAD Score:** 55.5/100 (Developing)

| Component | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| Setup Quality | 55 | 30% | 16.5 |
| Breakout Strength | 0 | 25% | 0.0 |
| Liquidity | 100 | 25% | 25.0 |
| Risk/Reward | 70 | 20% | 14.0 |

**Red Candle:** Week of 2026-11-09 | High: $152.59 | Low: $142.10

**Trade Setup:**
- Trigger: Close above $152.59 on green weekly candle
- Stop (if triggered): $142.10
- Action: Set alert at red candle high
- Guidance: Watchlist, wait for cleaner breakout

---

---

## MONITORING (4 stocks)
*Post-earnings gap-up, no red candle yet*

### 1. RIOT 
**Price:** $17.52 | **Earnings:** 2026-11-04 (bmo) | **Gap:** +11.4% | **Weeks Since:** 1
**PEAD Score:** 52.5/100 (Weak)

| Component | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| Setup Quality | 75 | 30% | 22.5 |
| Breakout Strength | 0 | 25% | 0.0 |
| Liquidity | 100 | 25% | 25.0 |
| Risk/Reward | 25 | 20% | 5.0 |

**Red Candle:** Not yet formed

**Trade Setup:**
- Action: Monitor for red candle formation
- Guidance: Not actionable

---

### 2. AAPL 
**Price:** $356.27 | **Earnings:** 2026-11-02 (amc) | **Gap:** -3.8% | **Weeks Since:** 1
**PEAD Score:** 40.5/100 (Weak)

| Component | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| Setup Quality | 35 | 30% | 10.5 |
| Breakout Strength | 0 | 25% | 0.0 |
| Liquidity | 100 | 25% | 25.0 |
| Risk/Reward | 25 | 20% | 5.0 |

**Red Candle:** Not yet formed

**Trade Setup:**
- Action: Monitor for red candle formation
- Guidance: Not actionable

---

### 3. PLTR 
**Price:** $167.99 | **Earnings:** 2026-11-02 (amc) | **Gap:** -5.7% | **Weeks Since:** 1
**PEAD Score:** 40.5/100 (Weak)

| Component | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| Setup Quality | 35 | 30% | 10.5 |
| Breakout Strength | 0 | 25% | 0.0 |
| Liquidity | 100 | 25% | 25.0 |
| Risk/Reward | 25 | 20% | 5.0 |

**Red Candle:** Not yet formed

**Trade Setup:**
- Action: Monitor for red candle formation
- Guidance: Not actionable

---

### 4. SNAP 
**Price:** $5.26 | **Earnings:** 2026-11-04 (amc) | **Gap:** -10.6% | **Weeks Since:** 1
**PEAD Score:** 25.5/100 (Weak)

| Component | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| Setup Quality | 35 | 30% | 10.5 |
| Breakout Strength | 0 | 25% | 0.0 |
| Liquidity | 40 | 25% | 10.0 |
| Risk/Reward | 25 | 20% | 5.0 |

**Red Candle:** Not yet formed

**Trade Setup:**
- Action: Monitor for red candle formation
- Guidance: Not actionable

---

---

## EXPIRED (0 stocks)
*Beyond the monitoring window*

No stocks in this stage.

---

## API Usage
- **API Calls Made:** 29
- **Budget Remaining:** 171
- **Cache Entries:** 29

---

## Methodology

This screener identifies Post-Earnings Announcement Drift (PEAD) setups:

1. **Setup Quality** (30%) - Earnings gap quality and weekly pattern formation
2. **Breakout Strength** (25%) - Price breakout above red candle high with volume
3. **Liquidity** (25%) - ADV20, average volume, and price thresholds
4. **Risk/Reward** (20%) - Entry/stop/target risk-reward ratio

For detailed methodology, see the PEAD strategy reference in the pead-screener skill directory.

---

**Disclaimer:** This screener is for educational and informational purposes only. Not investment advice. Always conduct your own research and consult a financial advisor before making investment decisions. Past patterns do not guarantee future results.
