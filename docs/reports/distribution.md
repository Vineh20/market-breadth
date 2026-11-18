# IBD Distribution Day Monitor Report

- **As of:** 2026-11-17
- **Overall Risk Level:** **SEVERE**
- **Primary Signal Symbol:** QQQ
- **Generated At:** 2026-11-18T04:35:59+00:00

## Index Results

### QQQ — risk: **SEVERE**

- Today is Distribution Day: True
- d5 / d15 / d25 = 3 / 5 / 9
- Cluster: within 5/15/25 sessions: 3/5/9
- Trend filters: close_above_21ema=False, close_above_50sma=False, market_below_21ema_or_50ma=True

> QQQ had a Distribution Day today. Active Distribution Days within the last 5/15/25 sessions: 3/5/9. Risk level: SEVERE.

#### Active Distribution Days

| date | close | pct_change | volume_change_pct | age | expires_in | high_since | invalidation_price |
|------|-------|------------|-------------------|-----|------------|------------|---------------------|
| 2026-11-17 | 656.95 | -0.73% | 26.34% | 0 | 25 | 663.36 | 689.7975000000001 |
| 2026-11-16 | 661.75 | -2.67% | 3.51% | 1 | 24 | 672.15 | 694.8375 |
| 2026-11-13 | 679.89 | -1.20% | 13.11% | 2 | 23 | 688.75 | 713.8845 |
| 2026-10-30 | 690.49 | -3.47% | 122.85% | 12 | 13 | 701.45 | 725.0145 |
| 2026-10-29 | 715.34 | -1.42% | 25.38% | 13 | 12 | 718.07 | 751.1070000000001 |
| 2026-10-22 | 704.47 | -2.86% | 98.77% | 18 | 7 | 726.14 | 739.6935000000001 |
| 2026-10-16 | 709.8 | -2.50% | 34.31% | 22 | 3 | 727.95 | 745.29 |
| 2026-10-14 | 728.95 | -1.97% | 82.28% | 24 | 1 | 740.53 | 765.3975 |
| 2026-10-13 | 743.57 | -0.33% | 14.28% | 25 | 0 | 744.2 | 780.7485 |

### SPY — risk: **SEVERE**

- Today is Distribution Day: True
- d5 / d15 / d25 = 3 / 6 / 9
- Cluster: within 5/15/25 sessions: 3/6/9
- Trend filters: close_above_21ema=False, close_above_50sma=False, market_below_21ema_or_50ma=True

> SPY had a Distribution Day today. Active Distribution Days within the last 5/15/25 sessions: 3/6/9. Risk level: SEVERE.

#### Active Distribution Days

| date | close | pct_change | volume_change_pct | age | expires_in | high_since | invalidation_price |
|------|-------|------------|-------------------|-----|------------|------------|---------------------|
| 2026-11-17 | 732.44 | -1.01% | 3.18% | 0 | 25 | 739.76 | 769.0620000000001 |
| 2026-11-16 | 739.95 | -1.91% | 78.74% | 1 | 24 | 749.82 | 776.9475000000001 |
| 2026-11-13 | 754.37 | -0.36% | 3.36% | 2 | 23 | 760.12 | 792.0885000000001 |
| 2026-11-05 | 733.0 | -4.41% | 102.64% | 8 | 17 | 765.97 | 769.65 |
| 2026-10-30 | 755.72 | -1.77% | 92.80% | 12 | 13 | 775.64 | 793.5060000000001 |
| 2026-10-29 | 769.36 | -0.38% | 33.74% | 13 | 12 | 775.64 | 807.8280000000001 |
| 2026-10-22 | 763.96 | -1.18% | 69.41% | 18 | 7 | 775.64 | 802.158 |
| 2026-10-16 | 763.25 | -1.11% | 48.83% | 22 | 3 | 775.64 | 801.4125 |
| 2026-10-14 | 769.6 | -1.08% | 115.55% | 24 | 1 | 776.35 | 808.08 |

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

