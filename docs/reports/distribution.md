# IBD Distribution Day Monitor Report

- **As of:** 2026-11-04
- **Overall Risk Level:** **SEVERE**
- **Primary Signal Symbol:** QQQ
- **Generated At:** 2026-11-05T03:36:51+00:00

## Index Results

### QQQ — risk: **SEVERE**

- Today is Distribution Day: False
- d5 / d15 / d25 = 2 / 5 / 8
- Cluster: within 5/15/25 sessions: 2/5/8
- Trend filters: close_above_21ema=False, close_above_50sma=False, market_below_21ema_or_50ma=True

> QQQ had no Distribution Day today. Active Distribution Days within the last 5/15/25 sessions: 2/5/8. Risk level: SEVERE.

#### Active Distribution Days

| date | close | pct_change | volume_change_pct | age | expires_in | high_since | invalidation_price |
|------|-------|------------|-------------------|-----|------------|------------|---------------------|
| 2026-10-30 | 690.49 | -3.47% | 122.85% | 3 | 22 | 701.45 | 725.0145 |
| 2026-10-29 | 715.34 | -1.42% | 25.38% | 4 | 21 | 718.07 | 751.1070000000001 |
| 2026-10-22 | 704.47 | -2.86% | 98.77% | 9 | 16 | 726.14 | 739.6935000000001 |
| 2026-10-16 | 709.8 | -2.50% | 34.31% | 13 | 12 | 727.95 | 745.29 |
| 2026-10-14 | 728.95 | -1.97% | 82.28% | 15 | 10 | 740.53 | 765.3975 |
| 2026-10-13 | 743.57 | -0.33% | 14.28% | 16 | 9 | 744.2 | 780.7485 |
| 2026-10-12 | 746.04 | -0.70% | 18.83% | 17 | 8 | 749.79 | 783.342 |
| 2026-10-08 | 747.58 | -1.34% | 95.13% | 19 | 6 | 757.18 | 784.9590000000001 |

### SPY — risk: **SEVERE**

- Today is Distribution Day: False
- d5 / d15 / d25 = 2 / 5 / 7
- Cluster: within 5/15/25 sessions: 2/5/7
- Trend filters: close_above_21ema=True, close_above_50sma=True, market_below_21ema_or_50ma=False

> SPY had no Distribution Day today. Active Distribution Days within the last 5/15/25 sessions: 2/5/7. Risk level: SEVERE.

#### Active Distribution Days

| date | close | pct_change | volume_change_pct | age | expires_in | high_since | invalidation_price |
|------|-------|------------|-------------------|-----|------------|------------|---------------------|
| 2026-10-30 | 755.72 | -1.77% | 92.80% | 3 | 22 | 775.64 | 793.5060000000001 |
| 2026-10-29 | 769.36 | -0.38% | 33.74% | 4 | 21 | 775.64 | 807.8280000000001 |
| 2026-10-22 | 763.96 | -1.18% | 69.41% | 9 | 16 | 775.64 | 802.158 |
| 2026-10-16 | 763.25 | -1.11% | 48.83% | 13 | 12 | 775.64 | 801.4125 |
| 2026-10-14 | 769.6 | -1.08% | 115.55% | 15 | 10 | 776.35 | 808.08 |
| 2026-10-08 | 773.93 | -0.42% | 30.47% | 19 | 6 | 779.42 | 812.6265 |
| 2026-09-30 | 762.63 | -0.21% | 68.27% | 25 | 0 | 781.62 | 800.7615000000001 |

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

