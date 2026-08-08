# SM05_BMOM_PORTFOLIO — B-MOM / B1 portfolio measurement vs SOLAR (dev window)

Spec: `runs/SM05_BMOM_PORTFOLIO/spec.yaml` (frozen 2026-08-08). Type: MEASUREMENT — full grid reported, no selection.
Window: union session calendar 2022-01-03 .. 2026-05-29 (1139 sessions), zero-filled.
Seed 20260808, block 5, B=10000. Metrics: `src/analytics/sm_metrics.py` (ann 252, ddof 1, logG base $100k).

## Legs and normalization (FACT)
- SOLAR = E10 daily (`runs/SM01_SUBSTRATE/out/e10_daily_py.csv`), 1139 sessions <= 2026-05-31; dev daily sd = $2,338.66.
- BMOM = W8-1 frozen rule daily net_c1_usd (`w8bmom_w14_daily.csv`), 1122 active sessions; sd $3,549.90; vol-match scale x0.6588.
- B1 = W9-1 nightly net at 2.0t (`w9b1_nightly.csv`, net2.0_usd = net2.0_t x $5), keyed by exit session; 1093 dev nights -> 1093 exit sessions (0 sessions with >1 night); sd $2,827.97; vol-match scale x0.8270.
- Sessions in union calendar not in SOLAR ledger: 0.
- Every portfolio = (1-w)*SOLAR + w*(vol-matched challenger), then the whole portfolio rescaled to SOLAR dev vol before metrics (CONVENTIONS 6.7 risk-normalized growth).

## (1) Standalone legs (see `standalone_metrics.csv`)
| leg | scaling | net | logG_100k | sharpe | calmar | max_dd | worst_month | pos_day_frac |
|---|---|---|---|---|---|---|---|---|
| SOLAR | unscaled | 119,009 | 0.7839 | 0.709 | 0.655 | -40,208 | -18,212 | 0.410 |
| SOLAR | vol_matched_to_solar | 119,009 | 0.7839 | 0.709 | 0.655 | -40,208 | -18,212 | 0.410 |
| BMOM | unscaled | 319,123 | 1.4330 | 1.253 | 1.630 | -43,325 | -20,226 | 0.502 |
| BMOM | vol_matched_to_solar | 210,236 | 1.1322 | 1.253 | 1.630 | -28,542 | -13,325 | 0.502 |
| B1 | unscaled | 94,980 | 0.6677 | 0.468 | 0.242 | -86,870 | -25,510 | 0.504 |
| B1 | vol_matched_to_solar | 78,546 | 0.5797 | 0.468 | 0.242 | -71,839 | -21,096 | 0.504 |

## (2) Full risk-share grid (`portfolio_grid.csv`) — FULL GRID, NO SELECTION
| portfolio | w | logG_100k | sharpe | calmar | max_dd | worst_month | roll60_min | tuw | dSharpe | p(dSh<=0) | dlogG | p(dlogG<=0) | dlogG_H1 | dlogG_H2 | PASS |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| SOLAR+BMOM w=0.000 (baseline=SOLAR) | 0 | 0.7839 | 0.709 | 0.655 | -40,208 | -18,212 | -29,810 | 0.949 | — | — | — | — | — | — | — |
| SOLAR+BMOM w=0.200 | 0.2 | 0.9337 | 0.920 | 0.944 | -36,192 | -16,689 | -28,174 | 0.938 | 0.211 | 0.0136 | 0.1498 | 0.0147 | 0.0849 | 0.1220 | PASS |
| SOLAR+BMOM w=0.250 | 0.25 | 0.9681 | 0.973 | 1.040 | -34,734 | -16,112 | -27,468 | 0.933 | 0.264 | 0.0155 | 0.1842 | 0.0168 | 0.1051 | 0.1505 | PASS |
| SOLAR+BMOM w=0.333 | 0.333 | 1.0206 | 1.058 | 1.222 | -32,145 | -14,951 | -25,978 | 0.923 | 0.349 | 0.0202 | 0.2367 | 0.0211 | 0.1362 | 0.1945 | PASS |
| SOLAR+BMOM w=0.400 | 0.4 | 1.0572 | 1.119 | 1.351 | -30,763 | -14,633 | -24,497 | 0.918 | 0.410 | 0.0256 | 0.2733 | 0.0267 | 0.1582 | 0.2255 | PASS |
| SOLAR+BMOM w=0.500 | 0.5 | 1.1012 | 1.197 | 1.558 | -28,514 | -14,242 | -21,829 | 0.910 | 0.487 | 0.0359 | 0.3173 | 0.0381 | 0.1848 | 0.2633 | PASS |
| SOLAR+B1 w=0.000 (baseline=SOLAR) | 0 | 0.7839 | 0.709 | 0.655 | -40,208 | -18,212 | -29,810 | 0.949 | — | — | — | — | — | — | — |
| SOLAR+B1 w=0.200 | 0.2 | 0.8503 | 0.799 | 0.768 | -38,623 | -15,331 | -28,395 | 0.933 | 0.090 | 0.1944 | 0.0664 | 0.1992 | -0.0664 | 0.1316 | fail |
| SOLAR+B1 w=0.250 | 0.25 | 0.8634 | 0.817 | 0.797 | -38,053 | -14,397 | -27,781 | 0.924 | 0.108 | 0.2119 | 0.0795 | 0.2158 | -0.0916 | 0.1638 | fail |
| SOLAR+B1 w=0.333 | 0.333 | 0.8785 | 0.839 | 0.850 | -36,617 | -14,846 | -26,232 | 0.915 | 0.129 | 0.2480 | 0.0946 | 0.2565 | -0.1437 | 0.2132 | fail |
| SOLAR+B1 w=0.400 | 0.4 | 0.8822 | 0.844 | 0.899 | -34,871 | -15,769 | -25,602 | 0.914 | 0.135 | 0.2888 | 0.0982 | 0.2949 | -0.1950 | 0.2462 | fail |
| SOLAR+B1 w=0.500 | 0.5 | 0.8699 | 0.826 | 0.744 | -41,210 | -16,740 | -27,209 | 0.924 | 0.117 | 0.3524 | 0.0859 | 0.3563 | -0.2874 | 0.2799 | fail |
| SOLAR+BMOM+B1 thirds | 0.333 | 1.1330 | 1.255 | 1.375 | -33,868 | -11,513 | -15,089 | 0.878 | 0.545 | 0.0508 | 0.3491 | 0.0523 | 0.0086 | 0.4189 | PASS |
| SOLAR+BMOM+B1 0.5/0.3/0.2 | 0.5 | 1.0915 | 1.179 | 1.527 | -28,677 | -10,259 | -20,841 | 0.903 | 0.470 | 0.0209 | 0.3076 | 0.0221 | 0.0732 | 0.3300 | PASS |

## (3) Diversification scorecard (`diversification_scorecard.csv`)
| challenger | rho_full | rho Solar-losing days | rho Solar-losing weeks | frac worst-20 Solar days challenger>=0 | dd-series corr | top-20-day overlap |
|---|---|---|---|---|---|---|
| BMOM | 0.3444 | 0.0430 (n=672) | 0.0520 (n=124) | 0.45 (19/20 active) | 0.0539 | 8/20 |
| B1 | 0.0150 | 0.1574 (n=672) | 0.1363 (n=124) | 0.40 (19/20 active) | -0.2802 | 3/20 |
| BMOM+B1_equal_risk_sleeve | 0.2520 | 0.1368 (n=672) | 0.1377 (n=124) | 0.45 (20/20 active) | 0.0657 | 6/20 |

## (4) Preregistered gates — mechanical application (FACT)
Gate (spec): cell passes iff portfolio improves risk-normalized logG AND Calmar AND worst-month vs SOLAR-only, H1/H2 dlogG same (positive) sign, bootstrap P(dSharpe<=0)<0.10 AND P(dlogG<=0)<0.10. Plateau = >=3 adjacent passing cells.
- BMOM: cell passes at w=[0.2,0.25,0.333,0.4,0.5] -> [True, True, True, True, True]; max adjacent run 5; plateau MET.
- B1: cell passes at w=[0.2,0.25,0.333,0.4,0.5] -> [False, False, False, False, False]; max adjacent run 0; plateau NOT met.
- Three-way thirds cell_pass = True; 0.5/0.3/0.2 cell_pass = True (single points, no plateau concept).

## (6) Worst-month / rolling-60 / TUW / streak improvement (`improvement_table.csv`)
SOLAR baseline: worst_month -18,212, roll60_min -29,810, tuw 0.949, streaks d/w/m 9/6/3, max_dd -40,208.
| portfolio | d worst_month | d roll60_min | d tuw | d day-streak | d week-streak | d month-streak | d max_dd |
|---|---|---|---|---|---|---|---|
| SOLAR+BMOM w=0.200 | 1,522 | 1,636 | -0.011 | 0 | -1 | 0 | 4,016 |
| SOLAR+BMOM w=0.250 | 2,100 | 2,342 | -0.016 | 0 | -1 | 0 | 5,474 |
| SOLAR+BMOM w=0.333 | 3,261 | 3,833 | -0.026 | 0 | -1 | 0 | 8,062 |
| SOLAR+BMOM w=0.400 | 3,578 | 5,313 | -0.031 | 0 | -2 | 0 | 9,444 |
| SOLAR+BMOM w=0.500 | 3,970 | 7,982 | -0.039 | -1 | -2 | 0 | 11,693 |
| SOLAR+B1 w=0.200 | 2,880 | 1,416 | -0.016 | 0 | 0 | 0 | 1,584 |
| SOLAR+B1 w=0.250 | 3,815 | 2,029 | -0.025 | 1 | -1 | 0 | 2,154 |
| SOLAR+B1 w=0.333 | 3,365 | 3,578 | -0.034 | 2 | -1 | 0 | 3,591 |
| SOLAR+B1 w=0.400 | 2,443 | 4,208 | -0.035 | 0 | -1 | 3 | 5,337 |
| SOLAR+B1 w=0.500 | 1,471 | 2,602 | -0.025 | -1 | 0 | 3 | -1,002 |
| SOLAR+BMOM+B1 thirds | 6,699 | 14,722 | -0.071 | 1 | -2 | 0 | 6,339 |
| SOLAR+BMOM+B1 0.5/0.3/0.2 | 7,953 | 8,970 | -0.047 | 0 | -2 | 0 | 11,530 |

## (5) TRANSITION/HISTORICAL diagnostic — pre-2022 challenger side (DIAGNOSTIC ONLY)
LIMITATION (binding): SOLAR has no pre-2022 ledger, so no pre-2022 portfolio can be formed. What is reported is the CHALLENGER SIDE of the 0.333 portfolios — the $ stream the challenger sleeve would have contributed at the dev-frozen vol-match scales — on the pre-2022 union calendar 2006-01-06..2021-12-31 (4103 sessions; BMOM 4077 active days, B1 3955 nights). Labels: TRANSITION/HISTORICAL. See `historical_diagnostic.csv`.
| series | net | logG_100k | sharpe | calmar | max_dd | worst_month |
|---|---|---|---|---|---|---|
| BMOM_hist_unscaled | 18,156 | 0.1668 | 0.066 | 0.015 | -73,738 | -58,345 |
| B1_hist_unscaled | 116,250 | 0.7713 | 0.518 | 0.165 | -43,260 | -18,095 |
| BMOM_hist_at_dev_scale | 11,961 | 0.1130 | 0.066 | 0.015 | -48,578 | -38,437 |
| B1_hist_at_dev_scale | 96,136 | 0.6736 | 0.518 | 0.165 | -35,775 | -14,964 |
| sleeve_2way_BMOM_w0.333 | 3,987 | 0.0391 | 0.066 | 0.015 | -16,193 | -12,812 |
| sleeve_2way_B1_w0.333 | 32,045 | 0.2780 | 0.518 | 0.165 | -11,925 | -4,988 |
| sleeve_3way_thirds_challenger_side | 36,032 | 0.3077 | 0.395 | 0.093 | -23,797 | -16,781 |

## (7) B-FADE appendix — daily overlay correlation ONLY
IN-SAMPLE-CHARACTERIZED (W8-2 honesty clause; W9-3 verdict UNCONFIRMED-POSSIBLY-RECENT, parked). NO portfolio arithmetic performed or permitted from this table.
| exit horizon | n release days | rho vs SOLAR (full calendar, zero-fill) | rho (active days only) |
|---|---|---|---|
| 15 min | 102 | -0.0491 | -0.1152 |
| 30 min | 102 | -0.0328 | -0.0764 |
| 60 min | 102 | -0.0530 | -0.1242 |

## Files
- portfolio_grid.csv, diversification_scorecard.csv (spec outputs)
- standalone_metrics.csv, improvement_table.csv, historical_diagnostic.csv, facts.json (supporting)
