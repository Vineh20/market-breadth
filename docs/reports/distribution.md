# IBD Distribution Day Monitor Report

- **As of:** 2026-10-16
- **Overall Risk Level:** **SEVERE**
- **Primary Signal Symbol:** SPY
- **Generated At:** 2026-10-18T18:44:47+00:00

## Index Results

### SPY — risk: **SEVERE**

- Today is Distribution Day: True
- d5 / d15 / d25 = 2 / 5 / 8
- Cluster: 5/15/25セッション経過以内: 2/5/8
- Trend filters: close_above_21ema=False, close_above_50sma=False, market_below_21ema_or_50ma=True

> SPYは本日Distribution Day該当。 5/15/25セッション経過以内の有効Distribution Dayはそれぞれ 2/5/8 件。 リスク判定: SEVERE。

#### Active Distribution Days

| date | close | pct_change | volume_change_pct | age | expires_in | high_since | invalidation_price |
|------|-------|------------|-------------------|-----|------------|------------|---------------------|
| 2026-10-16 | 763.25 | -1.11% | 48.83% | 0 | 25 | 773.25 | 801.4125 |
| 2026-10-14 | 769.6 | -1.08% | 115.55% | 2 | 23 | 776.35 | 808.08 |
| 2026-10-08 | 773.93 | -0.42% | 30.47% | 6 | 19 | 779.42 | 812.6265 |
| 2026-09-30 | 762.63 | -0.21% | 68.27% | 12 | 13 | 781.62 | 800.7615000000001 |
| 2026-09-28 | 765.61 | -0.74% | 16.44% | 14 | 11 | 781.62 | 803.8905000000001 |
| 2026-09-23 | 767.81 | -0.72% | 57.84% | 17 | 8 | 781.62 | 806.2004999999999 |
| 2026-09-16 | 754.05 | -0.44% | 28.19% | 22 | 3 | 781.62 | 791.7524999999999 |
| 2026-09-15 | 757.39 | -0.46% | 5.01% | 23 | 2 | 781.62 | 795.2595 |

## Portfolio Action

- **Instrument:** TQQQ
- **Recommended Action:** CLOSE_TQQQ_OR_HEDGE
- **Exposure:** current 100% → target 25% (delta -75%)
- **Trailing Stop:** 3%
- **Alternative:** SWITCH_TO_QQQ_OR_CASH

> TQQQ targets 3x daily Nasdaq returns. Distribution Day clusters amplify drawdown risk via daily compounding, so exposure is cut faster than for unleveraged QQQ.

## Audit

- **Data Source:** fmp
- **Symbols:** SPY
- **Audit Flags:** ['no_data_returned']
- **Rule Version:** ibd_dd_v1.0

