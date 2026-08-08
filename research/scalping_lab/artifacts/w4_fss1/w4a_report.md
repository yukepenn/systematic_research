# W4-A — FSS-1: impulse -> shallow pullback -> rebreak — readout

- Spec: `research/scalping_lab/specs/W4_alpha_wave1.md` section W4-A (frozen before readout).
- Code: `research/scalping_lab/src/python/w4a_fss1.py`. Seed 20260808, 1000 bootstrap reps,
  session (day-clustered) resampling. Data: 37 discovery sessions, sechilo+grid1s merge,
  RTH + quote-alive decision seconds, sequential episode simulation, conservative
  same-second-both-crossed -> adverse barrier rule.
- Artifacts: `w4a_by_session.csv` (2,664 rows = 37 sessions x 72 configs),
  `w4a_pooled.csv` (72 configs), `w4a_stdout.txt` (full run log), `w4a_verify.txt`
  (verification pass; every number quoted below appears there or in the CSVs/stdout).

## VERDICT: DEFINITIVE KILL (KPI outcome B)

FACT: **0 of 48** market+passive configs pass the frozen rule (net(C1 or C1p) > 0 AND
CI lower bound > -0.5t). Every one of the 72 simulated configs (incl. stress) has a
negative point estimate AND a negative bootstrap CI **upper** bound:

- market (C1=2.872t): 38,572 episodes; net range [-3.945, -2.170] t/trade; max CI_hi = -1.290t.
- passive (C1p=1.872t): 67,493 episodes; net range [-3.808, -2.971] t/trade; max CI_hi = -2.240t.
- passive_stress (C2p_lite): 68,155 episodes; net range [-4.853, -3.886] t/trade; max CI_hi = -3.169t.

Plateau logic: there are no isolated positives to flag as FRAGILE — the entire
(w x I x dir x bracket) surface is uniformly and significantly negative in both entry
styles. This is a robust kill, not a fragile one. At session granularity only 79 of 864
market session-config cells have positive net C1 (FACT, w4a_verify.txt).

## FACT — market variant (pooled; * = primary w=30, I=12)

```
=== W4-A pooled — market (net_main uses C1=2.872t; net_sec C2=4.872t) ===
  w   I   dir   A   B |   imp    pb   epi   e/d days  fill% |  P(tgt)  cap |     net   CI_lo   CI_hi | net_sec PASS
 30  12  long  24   8 |  2465  1704   778 21.61   36   45.7 |  0.2211    0 |  -3.797  -4.751  -2.792 |  -5.797 fail *
 30  12  long  32  10 |  2432  1678   768 21.33   36   45.8 |  0.2074   11 |  -3.945  -5.223  -2.704 |  -5.945 fail *
 30  12 short  24   8 |  2303  1489   675 18.75   36   45.3 |  0.2333    2 |  -3.370  -4.140  -2.547 |  -5.370 fail *
 30  12 short  32  10 |  2292  1481   670 18.61   36   45.2 |  0.2192    4 |  -3.565  -4.491  -2.670 |  -5.565 fail *
 30   8  long  24   8 |  2958  1208   460 12.78   36   38.1 |  0.2227    2 |  -3.708  -4.831  -2.652 |  -5.708 fail
 30   8  long  32  10 |  2917  1193   454 12.61   36   38.1 |  0.2054   11 |  -3.895  -5.376  -2.479 |  -5.895 fail
 30   8 short  24   8 |  2775  1041   375 10.42   36   36.0 |  0.2351    5 |  -3.195  -4.220  -2.119 |  -5.195 fail
 30   8 short  32  10 |  2766  1038   374 10.39   36   36.0 |  0.2120    6 |  -3.733  -4.985  -2.483 |  -5.733 fail
 30  16  long  24   8 |  2211  1833   935 25.97   36   51.0 |  0.2259    1 |  -3.643  -4.518  -2.774 |  -5.643 fail
 30  16  long  32  10 |  2175  1800   917 25.47   36   50.9 |  0.2128   10 |  -3.791  -5.019  -2.640 |  -5.791 fail
 30  16 short  24   8 |  2069  1608   809 22.47   36   50.3 |  0.2290    1 |  -3.526  -4.284  -2.741 |  -5.526 fail
 30  16 short  32  10 |  2056  1596   805 22.36   36   50.4 |  0.2147    4 |  -3.786  -4.858  -2.732 |  -5.786 fail
 15  12  long  24   8 |  9705  6504  2880 80.00   36   44.3 |  0.2457    2 |  -2.998  -3.545  -2.439 |  -4.998 fail
 15  12  long  32  10 |  9410  6271  2788 77.44   36   44.5 |  0.2351   19 |  -2.893  -3.528  -2.171 |  -4.893 fail
 15  12 short  24   8 |  9525  6294  2805 77.92   36   44.6 |  0.2510    4 |  -2.835  -3.316  -2.403 |  -4.835 fail
 15  12 short  32  10 |  9256  6088  2721 75.58   36   44.7 |  0.2395   15 |  -2.769  -3.343  -2.208 |  -4.769 fail
 15   8  long  24   8 | 12227  4926  1804 50.11   36   36.6 |  0.2490    5 |  -2.871  -3.494  -2.251 |  -4.871 fail
 15   8  long  32  10 | 11936  4750  1761 48.92   36   37.1 |  0.2394   23 |  -2.660  -3.353  -1.999 |  -4.660 fail
 15   8 short  24   8 | 12080  4661  1728 48.00   36   37.1 |  0.2664    9 |  -2.311  -2.963  -1.714 |  -4.311 fail
 15   8 short  32  10 | 11837  4531  1682 46.72   36   37.1 |  0.2526   19 |  -2.170  -3.170  -1.290 |  -4.170 fail
 15  16  long  24   8 |  8158  6489  3200 88.89   36   49.3 |  0.2470    1 |  -2.964  -3.439  -2.480 |  -4.964 fail
 15  16  long  32  10 |  7929  6288  3098 86.06   36   49.3 |  0.2344    9 |  -2.974  -3.546  -2.347 |  -4.974 fail
 15  16 short  24   8 |  8082  6355  3090 85.83   36   48.6 |  0.2444    1 |  -3.046  -3.467  -2.620 |  -5.046 fail
 15  16 short  32  10 |  7854  6159  2995 83.19   36   48.6 |  0.2395    5 |  -2.798  -3.337  -2.287 |  -4.798 fail
(* = primary w=30, I=12; fill% = entries/valid-pullbacks; PASS = net_main>0 AND CI_lo>-0.5t)
```

## FACT — passive variant (limit at IH - 0.4*I, strict trade-through fill)

```
=== W4-A pooled — passive (net_main uses C1p=1.872t; net_sec flat 2.872t) ===
  w   I   dir   A   B |   imp    pb   epi   e/d days  fill% |  P(tgt)  cap |     net   CI_lo   CI_hi | net_sec PASS
 30  12  long  24   8 |  2440  1718  1358 37.72   36   79.0 |  0.1997   11 |  -3.370  -4.089  -2.622 |  -4.370 fail *
 30  12  long  32  10 |  2410  1689  1340 37.22   36   79.3 |  0.1863   25 |  -3.773  -4.657  -2.784 |  -4.773 fail *
 30  12 short  24   8 |  2294  1508  1219 33.86   36   80.8 |  0.1987    1 |  -3.507  -4.396  -2.708 |  -4.507 fail *
 30  12 short  32  10 |  2269  1489  1205 33.47   36   80.9 |  0.1967   10 |  -3.527  -4.407  -2.692 |  -4.527 fail *
 30   8  long  24   8 |  2828  1155   972 27.00   36   84.2 |  0.1948    7 |  -3.544  -4.452  -2.552 |  -4.544 fail
 30   8  long  32  10 |  2780  1124   951 26.42   36   84.6 |  0.1905   27 |  -3.506  -4.706  -2.240 |  -4.506 fail
 30   8 short  24   8 |  2594   980   846 23.50   36   86.3 |  0.2069    5 |  -3.196  -4.158  -2.272 |  -4.196 fail
 30   8 short  32  10 |  2562   963   833 23.14   36   86.5 |  0.1944   15 |  -3.431  -4.523  -2.429 |  -4.431 fail
 30  16  long  24   8 |  2405  2023  1461 40.58   36   72.2 |  0.1915    4 |  -3.711  -4.400  -2.977 |  -4.711 fail
 30  16  long  32  10 |  2368  1989  1440 40.00   36   72.4 |  0.1881   15 |  -3.808  -4.518  -3.025 |  -4.808 fail
 30  16 short  24   8 |  2218  1744  1272 35.33   36   72.9 |  0.1918    0 |  -3.734  -4.492  -2.963 |  -4.734 fail
 30  16 short  32  10 |  2189  1722  1259 34.97   36   73.1 |  0.1901    7 |  -3.793  -4.759  -2.853 |  -4.793 fail
 15  12  long  24   8 |  9393  6340  5067 140.75   36   79.9 |  0.2080    4 |  -3.201  -3.577  -2.815 |  -4.201 fail
 15  12  long  32  10 |  8959  5987  4792 133.11   36   80.0 |  0.1912   28 |  -3.752  -4.240  -3.233 |  -4.752 fail
 15  12 short  24   8 |  9189  6098  4928 136.89   36   80.8 |  0.2078    4 |  -3.219  -3.604  -2.825 |  -4.219 fail
 15  12 short  32  10 |  8777  5762  4663 129.53   36   80.9 |  0.2004   23 |  -3.389  -3.881  -2.951 |  -4.389 fail
 15   8  long  24   8 | 11352  4470  3759 104.42   36   84.1 |  0.2020   11 |  -3.382  -3.796  -2.953 |  -4.382 fail
 15   8  long  32  10 | 10865  4187  3534 98.17   36   84.4 |  0.1939   43 |  -3.583  -4.084  -3.109 |  -4.583 fail
 15   8 short  24   8 | 11028  4215  3607 100.19   36   85.6 |  0.2147   11 |  -2.971  -3.496  -2.469 |  -3.971 fail
 15   8 short  32  10 | 10655  4021  3438 95.50   36   85.5 |  0.2081   36 |  -3.017  -3.681  -2.405 |  -4.017 fail
 15  16  long  24   8 |  8528  6872  5110 141.94   36   74.4 |  0.2018    1 |  -3.412  -3.763  -3.041 |  -4.412 fail
 15  16  long  32  10 |  8177  6549  4870 135.28   36   74.4 |  0.1916   16 |  -3.771  -4.208  -3.291 |  -4.771 fail
 15  16 short  24   8 |  8307  6583  4886 135.72   36   74.2 |  0.2041    1 |  -3.340  -3.707  -3.002 |  -4.340 fail
 15  16 short  32  10 |  7987  6309  4683 130.08   36   74.2 |  0.2081    7 |  -3.117  -3.694  -2.621 |  -4.117 fail
(* = primary w=30, I=12; fill% = entries/valid-pullbacks; PASS = net_main>0 AND CI_lo>-0.5t)
```

## FACT — passive stress sensitivity (C2p_lite: entry shifted 1t adverse via price, friction 1.872t)

```
=== W4-A pooled — passive_stress (net_main uses C1p=1.872t on 1t-adverse-shifted entry (C2p_lite ~2.872t); net_sec n/a) ===
  w   I   dir   A   B |   imp    pb   epi   e/d days  fill% |  P(tgt)  cap |     net   CI_lo   CI_hi | net_sec PASS
 30  12  long  24   8 |  2452  1729  1367 37.97   36   79.1 |  0.1647    7 |  -4.524  -5.303  -3.740 |      -- fail *
 30  12  long  32  10 |  2418  1696  1344 37.33   36   79.2 |  0.1710   22 |  -4.464  -5.288  -3.446 |      -- fail *
 30  12 short  24   8 |  2301  1513  1223 33.97   36   80.8 |  0.1718    1 |  -4.366  -5.249  -3.580 |      -- fail *
 30  12 short  32  10 |  2282  1498  1211 33.64   36   80.8 |  0.1661    7 |  -4.807  -5.664  -4.000 |      -- fail *
 30   8  long  24   8 |  2837  1158   975 27.08   36   84.2 |  0.1674    7 |  -4.422  -5.260  -3.492 |      -- fail
 30   8  long  32  10 |  2788  1131   957 26.58   36   84.6 |  0.1626   22 |  -4.696  -5.830  -3.460 |      -- fail
 30   8 short  24   8 |  2604   986   851 23.64   36   86.3 |  0.1751    6 |  -4.205  -5.108  -3.366 |      -- fail
 30   8 short  32  10 |  2567   965   834 23.17   36   86.4 |  0.1744   14 |  -4.269  -5.433  -3.169 |      -- fail
 30  16  long  24   8 |  2412  2030  1467 40.75   36   72.3 |  0.1696    5 |  -4.401  -5.064  -3.738 |      -- fail
 30  16  long  32  10 |  2374  1994  1445 40.14   36   72.5 |  0.1692   15 |  -4.601  -5.332  -3.790 |      -- fail
 30  16 short  24   8 |  2226  1751  1276 35.44   36   72.9 |  0.1716    0 |  -4.380  -5.103  -3.715 |      -- fail
 30  16 short  32  10 |  2201  1730  1264 35.11   36   73.1 |  0.1653    6 |  -4.853  -5.760  -3.942 |      -- fail
 15  12  long  24   8 |  9473  6399  5117 142.14   36   80.0 |  0.1758    4 |  -4.231  -4.611  -3.849 |      -- fail
 15  12  long  32  10 |  9053  6059  4859 134.97   36   80.2 |  0.1692   25 |  -4.685  -5.131  -4.250 |      -- fail
 15  12 short  24   8 |  9256  6153  4978 138.28   36   80.9 |  0.1801    2 |  -4.107  -4.469  -3.743 |      -- fail
 15  12 short  32  10 |  8861  5838  4724 131.22   36   80.9 |  0.1768   18 |  -4.390  -4.872  -3.948 |      -- fail
 15   8  long  24   8 | 11445  4521  3800 105.56   36   84.1 |  0.1715   11 |  -4.353  -4.714  -3.973 |      -- fail
 15   8  long  32  10 | 10995  4255  3584 99.56   36   84.2 |  0.1685   40 |  -4.646  -5.113  -4.164 |      -- fail
 15   8 short  24   8 | 11160  4281  3660 101.67   36   85.5 |  0.1821    8 |  -4.022  -4.504  -3.563 |      -- fail
 15   8 short  32  10 | 10730  4065  3481 96.69   36   85.6 |  0.1875   31 |  -3.886  -4.500  -3.338 |      -- fail
 15  16  long  24   8 |  8601  6936  5155 143.19   36   74.3 |  0.1731    1 |  -4.332  -4.669  -3.971 |      -- fail
 15  16  long  32  10 |  8261  6624  4931 136.97   36   74.4 |  0.1666   15 |  -4.825  -5.255  -4.370 |      -- fail
 15  16 short  24   8 |  8356  6632  4921 136.69   36   74.2 |  0.1776    0 |  -4.189  -4.537  -3.872 |      -- fail
 15  16 short  32  10 |  8063  6367  4731 131.42   36   74.3 |  0.1814    7 |  -4.237  -4.715  -3.778 |      -- fail
(* = primary w=30, I=12; fill% = entries/valid-pullbacks; PASS = net_main>0 AND CI_lo>-0.5t)
```

## FACT — plateau view (net_main across the (w,I) grid)

```
=== plateau view: net_main across (w,I) grid, per variant/dir/bracket ===
 market  long +24/-8: w30I12:-3.80  w30I8:-3.71  w30I16:-3.64  w15I12:-3.00  w15I8:-2.87  w15I16:-2.96
 market  long +32/-10: w30I12:-3.94  w30I8:-3.90  w30I16:-3.79  w15I12:-2.89  w15I8:-2.66  w15I16:-2.97
 market short +24/-8: w30I12:-3.37  w30I8:-3.19  w30I16:-3.53  w15I12:-2.83  w15I8:-2.31  w15I16:-3.05
 market short +32/-10: w30I12:-3.57  w30I8:-3.73  w30I16:-3.79  w15I12:-2.77  w15I8:-2.17  w15I16:-2.80
passive  long +24/-8: w30I12:-3.37  w30I8:-3.54  w30I16:-3.71  w15I12:-3.20  w15I8:-3.38  w15I16:-3.41
passive  long +32/-10: w30I12:-3.77  w30I8:-3.51  w30I16:-3.81  w15I12:-3.75  w15I8:-3.58  w15I16:-3.77
passive short +24/-8: w30I12:-3.51  w30I8:-3.20  w30I16:-3.73  w15I12:-3.22  w15I8:-2.97  w15I16:-3.34
passive short +32/-10: w30I12:-3.53  w30I8:-3.43  w30I16:-3.79  w15I12:-3.39  w15I8:-3.02  w15I16:-3.12
```

## Passive vs market economics (primary w=30, I=12, long +24/-8)

FACT: market — 778 episodes, P(tgt)=0.2211, gross/trade = -0.925t, net C1 = -3.797t.
FACT: passive — 1,358 fills (fill rate 79.05% of valid pullbacks), P(tgt)=0.1997,
gross/trade = -1.498t, net C1p = -3.370t.

INFERENCE: the passive limit saves 1.0t of friction (1.872 vs 2.872) but gives back
~0.57t of it in worse gross (-1.498 vs -0.925) via adverse selection — fills are
concentrated in flush-throughs that keep going. Net-net the passive variant is ~0.3-0.4t
better than market at the primary but still ~3.4t underwater; the owner's limit-order
intuition is directionally right about friction and wrong about the setup. The stress
row (1t worse entry via price) costs a further ~1.0-1.3t, as expected.

## Why it fails (INFERENCE from FACTs)

1. Gross is negative before any costs at the primary (-0.925t market, -1.498t passive):
   the rebreak of a 30s momentum impulse on NQ 1s data is adversely selected —
   continuation does not follow the shallow-pullback-rebreak sequence often enough.
2. P(target-first) sits at 0.19-0.27 across all configs vs required break-evens of
   0.3397 (24,8 @ C1) / 0.3065 (32,10 @ C1) / 0.3085 (24,8 @ C1p) / 0.2827 (32,10 @ C1p)
   — a 6-14pp shortfall that no cost engineering in this family closes.
3. The best cell in the whole family (market w15 I8 short +32/-10: net -2.170t,
   CI [-3.170, -1.290]) is a neighbor, not the primary, and still significantly negative.

## Implementation notes (frozen-spec interpretations)

- Impulse detect on decision seconds only; efficiency ret_w >= 0.5*TV_w (equivalent to
  ret/TV >= 0.5; TV >= |ret| > 0 whenever ret >= I).
- IH = running max of mid from the impulse second, tracked up to 30s; pullback = first
  second with depth in [3t, 0.5*I]; depth > 0.6*I cancels, enforced in BOTH the tracking
  and rebreak windows; IH frozen at pullback start.
- Market entry at the rebreak second's mid (delay 0, house convention); entries only on
  decision seconds — a crossing on a dead second kills the setup.
- Passive: limit armed from pullback start, fills checked from the NEXT second (no
  same-second lookahead), strict trade-through mid_low < L - 1t, fill check precedes
  rebreak/cancel within a second, fills only on decision seconds, barrier evaluation
  includes the fill second (conservative), entry price = L.
- Passive stress applies the 1t 'via price': entry = L + 1t adverse, brackets from the
  shifted entry, friction 1.872t (total ~2.872t). Episode counts differ slightly from
  base passive because shifted barriers change exit timing and hence the sequential
  cooldown path (e.g. primary long 24/8: 1,367 vs 1,358) — expected, documented.
- One session (s20250902) produced zero primary (w30,I12) market episodes; unique_days=36
  for those configs. Bootstrap resamples only sessions holding episodes of a config,
  weighted by episode count (house pattern).
- Neighbors were run as the full w x I grid (w in {15,30} x I in {8,12,16}), superset of
  the spec's named neighbors (w=15; I in {8,16}); reported always, never selected on.

## Verification block (w4a_verify.txt, verbatim)

```
W4-A verification pass (numbers quoted in w4a_report.md)
configs: 72 | passes under frozen rule: 0 | market+passive configs: 48
market: episodes=38572 net[-3.945,-2.170] ci_hi_max=-1.290 rate[0.3602,0.5101] p_tgt[0.2054,0.2664]
passive: episodes=67493 net[-3.808,-2.971] ci_hi_max=-2.240 rate[0.7222,0.8650] p_tgt[0.1863,0.2147]
passive_stress: episodes=68155 net[-4.853,-3.886] ci_hi_max=-3.169 rate[0.7227,0.8642] p_tgt[0.1626,0.1875]
break-evens P(tgt) needed: (24,8) C1=0.3397 C2=0.4022 C1p=0.3085 | (32,10) C1=0.3065 C2=0.3541 C1p=0.2827
check: 0.3397 0.4022 0.3085 0.3065 0.3541 0.2827
primary market nets: [-3.797, -3.945, -3.37, -3.565] ci_lo: [-4.751, -5.223, -4.14, -4.491] ci_hi: [-2.792, -2.704, -2.547, -2.67]
primary passive nets: [-3.37, -3.773, -3.507, -3.527] fill rates: [0.7905, 0.7934, 0.8084, 0.8093]
primary stress nets: [-4.524, -4.464, -4.366, -4.807]
primary long 24/8 market: gross_per_trade=-0.925 net_main=-3.797 p_tgt=0.2211 episodes=778
primary long 24/8 passive: gross_per_trade=-1.498 net_main=-3.370 p_tgt=0.1997 episodes=1358
best market: w15 I8 short +32/-10 net=-2.170 CI=[-3.170,-1.290] epi=1682
best passive: w15 I8 short +24/-8 net=-2.971 CI=[-3.496,-2.469] epi=3607
sessions with zero primary(w30,I12) market episodes: ['s20250902']
market session-config cells net>0: 79 / 864
sessions: 37 | by-session rows: 2664
```
