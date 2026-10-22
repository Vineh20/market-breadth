# IBD Distribution Day Monitor Report

- **As of:** 2026-10-21
- **Overall Risk Level:** **SEVERE**
- **Primary Signal Symbol:** QQQ
- **Generated At:** 2026-10-22T01:39:57+00:00

## Index Results

### QQQ — risk: **SEVERE**

- Today is Distribution Day: False
- d5 / d15 / d25 = 2 / 5 / 6
- Cluster: within 5/15/25 sessions: 2/5/6
- Trend filters: close_above_21ema=False, close_above_50sma=False, market_below_21ema_or_50ma=True

> QQQ had no Distribution Day today. Active Distribution Days within the last 5/15/25 sessions: 2/5/6. Risk level: SEVERE.

#### Active Distribution Days

| date | close | pct_change | volume_change_pct | age | expires_in | high_since | invalidation_price |
|------|-------|------------|-------------------|-----|------------|------------|---------------------|
| 2026-10-16 | 709.8 | -2.50% | 34.31% | 3 | 22 | 727.95 | 745.29 |
| 2026-10-14 | 728.95 | -1.97% | 82.28% | 5 | 20 | 740.53 | 765.3975 |
| 2026-10-13 | 743.57 | -0.33% | 14.28% | 6 | 19 | 744.2 | 780.7485 |
| 2026-10-12 | 746.04 | -0.70% | 18.83% | 7 | 18 | 749.79 | 783.342 |
| 2026-10-08 | 747.58 | -1.34% | 95.13% | 9 | 16 | 757.18 | 784.9590000000001 |
| 2026-09-28 | 736.53 | -1.07% | 37.95% | 17 | 8 | 762.86 | 773.3565 |

### SPY — risk: **SEVERE**

- Today is Distribution Day: False
- d5 / d15 / d25 = 2 / 4 / 7
- Cluster: within 5/15/25 sessions: 2/4/7
- Trend filters: close_above_21ema=True, close_above_50sma=True, market_below_21ema_or_50ma=False

> SPY had no Distribution Day today. Active Distribution Days within the last 5/15/25 sessions: 2/4/7. Risk level: SEVERE.

#### Active Distribution Days

| date | close | pct_change | volume_change_pct | age | expires_in | high_since | invalidation_price |
|------|-------|------------|-------------------|-----|------------|------------|---------------------|
| 2026-10-16 | 763.25 | -1.11% | 48.83% | 3 | 22 | 774.44 | 801.4125 |
| 2026-10-14 | 769.6 | -1.08% | 115.55% | 5 | 20 | 776.35 | 808.08 |
| 2026-10-08 | 773.93 | -0.42% | 30.47% | 9 | 16 | 779.42 | 812.6265 |
| 2026-09-30 | 762.63 | -0.21% | 68.27% | 15 | 10 | 781.62 | 800.7615000000001 |
| 2026-09-28 | 765.61 | -0.74% | 16.44% | 17 | 8 | 781.62 | 803.8905000000001 |
| 2026-09-23 | 767.81 | -0.72% | 57.84% | 20 | 5 | 781.62 | 806.2004999999999 |
| 2026-09-16 | 752.1822 | -0.44% | 28.19% | 25 | 0 | 781.62 | 789.79131 |

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

