# IBD Distribution Day Monitor Report

- **As of:** 2026-11-13
- **Overall Risk Level:** **SEVERE**
- **Primary Signal Symbol:** QQQ
- **Generated At:** 2026-11-14T03:26:13+00:00

## Index Results

### QQQ — risk: **SEVERE**

- Today is Distribution Day: True
- d5 / d15 / d25 = 1 / 3 / 8
- Cluster: within 5/15/25 sessions: 1/3/8
- Trend filters: close_above_21ema=False, close_above_50sma=False, market_below_21ema_or_50ma=True

> QQQ had a Distribution Day today. Active Distribution Days within the last 5/15/25 sessions: 1/3/8. Risk level: SEVERE.

#### Active Distribution Days

| date | close | pct_change | volume_change_pct | age | expires_in | high_since | invalidation_price |
|------|-------|------------|-------------------|-----|------------|------------|---------------------|
| 2026-11-13 | 679.89 | -1.20% | 12.30% | 0 | 25 | 688.75 | 713.8845 |
| 2026-10-30 | 690.49 | -3.47% | 122.85% | 10 | 15 | 701.45 | 725.0145 |
| 2026-10-29 | 715.34 | -1.42% | 25.38% | 11 | 14 | 718.07 | 751.1070000000001 |
| 2026-10-22 | 704.47 | -2.86% | 98.77% | 16 | 9 | 726.14 | 739.6935000000001 |
| 2026-10-16 | 709.8 | -2.50% | 34.31% | 20 | 5 | 727.95 | 745.29 |
| 2026-10-14 | 728.95 | -1.97% | 82.28% | 22 | 3 | 740.53 | 765.3975 |
| 2026-10-13 | 743.57 | -0.33% | 14.28% | 23 | 2 | 744.2 | 780.7485 |
| 2026-10-12 | 746.04 | -0.70% | 18.83% | 24 | 1 | 749.79 | 783.342 |

### SPY — risk: **SEVERE**

- Today is Distribution Day: True
- d5 / d15 / d25 = 1 / 4 / 7
- Cluster: within 5/15/25 sessions: 1/4/7
- Trend filters: close_above_21ema=False, close_above_50sma=False, market_below_21ema_or_50ma=True

> SPY had a Distribution Day today. Active Distribution Days within the last 5/15/25 sessions: 1/4/7. Risk level: SEVERE.

#### Active Distribution Days

| date | close | pct_change | volume_change_pct | age | expires_in | high_since | invalidation_price |
|------|-------|------------|-------------------|-----|------------|------------|---------------------|
| 2026-11-13 | 754.37 | -0.36% | 2.48% | 0 | 25 | 760.12 | 792.0885000000001 |
| 2026-11-05 | 733.0 | -4.41% | 102.64% | 6 | 19 | 765.97 | 769.65 |
| 2026-10-30 | 755.72 | -1.77% | 92.80% | 10 | 15 | 775.64 | 793.5060000000001 |
| 2026-10-29 | 769.36 | -0.38% | 33.74% | 11 | 14 | 775.64 | 807.8280000000001 |
| 2026-10-22 | 763.96 | -1.18% | 69.41% | 16 | 9 | 775.64 | 802.158 |
| 2026-10-16 | 763.25 | -1.11% | 48.83% | 20 | 5 | 775.64 | 801.4125 |
| 2026-10-14 | 769.6 | -1.08% | 115.55% | 22 | 3 | 776.35 | 808.08 |

## Portfolio Action

- **Instrument:** TQQQ
- **Recommended Action:** CLOSE_TQQQ_OR_HEDGE
- **Exposure:** current 100% → target 25% (delta -75%)
- **Trailing Stop:** 3%
- **Alternative:** SWITCH_TO_QQQ_OR_CASH

> TQQQ targets 3x daily Nasdaq returns. Distribution Day clusters amplify drawdown risk via daily compounding, so exposure is cut faster than for unleveraged QQQ.

## Audit

- **Data Source:** fmp
- **Symbols:** QQQ, SPY
- **Audit Flags:** []
- **Rule Version:** ibd_dd_v1.0

