# G3_EVENT_CL_20260906 — CL native EVENT diagnostic

**Ledger:** G00068, family GENESIS3_EVENT · **Campaign:** GENESIS III Wave D · **Executed:** 2026-09-06
**Stage:** DIAGNOSTIC / DISCOVERY — event → conditional-forward-path tables with matched unconditional controls. No strategy object tested; no gate can pass into promotion.
**Evidence status:** DISCOVERY · **Basis:** POINTS only (additively back-adjusted substrate, DELEV01) · **Cost basis:** MODELED / ALL_IN ($4.36 RT commission + modeled spread {1,2,3} ticks × $10; conservative $34.36; screen 2× = $68.72 = 0.06872 pts)
**Data:** `runs/SM1M_CL_SUBSTRATE/out/cl_1m_2022_2026.parquet` (sha256 `e587486c…` verified), 1,182 sessions 2022-01-03 → 2026-07-31, seal < 2026-08-01 asserted.

## Verdict

**All seven events are DEAD. 0 LEAD, 0 DESCRIPTIVE.** Across the 52-cell preregistered family, 1/52 cells reached uncorrected p<0.05 (~2.6 expected by pure chance); nothing approached the K_eff-corrected screen threshold p<0.00180. The result is consistent with the CL autopsy that motivated the run: pit returns ≈ random walk; structure lives in volatility, and none of the seven displacement-event conditionings recovers a direction-conditional forward path.

| Event | Verdict | Cells | min p_shift | max \|Δ$\| | n range |
|---|---|---|---|---|---|
| E1_eia_response_path | **DEAD** | 12 | 0.05432 | $330 | 35–44 |
| E2_settlement_transition | **DEAD** | 12 | 0.06500 | $94 | 171–209 |
| E3_overnight_pit_handoff | **DEAD** | 8 | 0.04987 | $328 | 34–94 |
| E4_shock_day_next_path | **DEAD** | 9 | 0.13268 | $2556 | 2–18 |
| E5_compression_break | **DEAD** | 4 | 0.54230 | $129 | 67–108 |
| E6_multisession_extreme | **DEAD** | 6 | 0.16385 | $792 | 52–78 |
| E7_expansion_failure | **DEAD** | 1 | 0.06589 | $1414 | 8 |

Verdict rule (operationalized in code before results): DEAD = no cell clears the K_eff-corrected p<0.05; DESCRIPTIVE = clears corrected p but fails the cost or n leg; LEAD = full screen (corrected p<0.05 AND |Δ$| ≥ $68.72 AND n ≥ 30).

## Method as executed (spec-exact)

- **Controls:** every cell has a matched unconditional control in the same wave — same horizon over all (eligible) sessions, time-matched for the time-locked windows (E1/E2/E3); E5 break-day remainder uses a time-**distribution**-matched control (close − price@t averaged over the event breach-time distribution). 52/52 control rows in `out/controls.csv`.
- **CIs:** session-block bootstrap on delta, circular blocks L=10, B=1000, one shared draw matrix for the family, seed 20260906.
- **LEAD null:** circular session-shift decoupling each event's conditioning from the outcome series — **exhaustive** shared offset set S=1122 (all offsets 30…N−31), one draw for the whole family. p_raw = P(|shifted delta| ≥ |observed delta|), two-sided.
- **Family correction:** K=52, ρ̄(null)=0.0172 (measured from the shared null draws), **K_eff = 27.71**, corrected threshold p < 0.05/K_eff = **0.00180**. Minimum achievable p = 1/1123 = 0.00089 < threshold, so the screen was reachable, not vacuous.
- **Probability meaning (CLAUDE.md ⭐):** p_raw_shift is the probability, over the exhaustive shared set of 1122 circular session-shifts, that the shifted conditional-mean-minus-control delta is ≥ the observed |delta| (two-sided). It is a per-cell alignment-null probability — NOT P(profit) and NOT family-corrected; the correction is the separate 0.00180 threshold. Second, independent computation (gate G9): block-bootstrap sign test p_boot printed for every cell; for the min-p cell E3_1.5x_up_0900-1430 the two ways agree (p_shift=0.04987, p_boot=0.072 — both non-significant).
- **Units:** all internal arithmetic on the exact $0.01 integer-cent grid; points only at output. Gate G4 proves exact translation invariance (+1000.00 pts → identical event sets, max delta deviation 0.0).

## EIA calendar (E1)

Standard schedule implemented: Wednesdays 10:30 ET; a federal holiday (observed) on Mon/Tue/Wed shifts that week's release to Thursday. 239 releases 2022-01 → 2026-07, **36 Thursday-shifted**, all matched to substrate sessions, 0 unmatched, max date 2026-07-29 (seal-clean). Spot-checked shifts: MLK, Presidents, Memorial, Juneteenth, July-4, Labor, Columbus, Christmas, New-Year weeks; Thanksgiving (Thursday holiday) correctly does not shift. Caveat: per spec all events anchor at 10:30, but real EIA practice for holiday-delayed releases is typically 11:00 ET — the 36 shifted events (15%) may condition ~30 min before the true release (dilutive only). Ad-hoc delays (EIA systems outages) not modeled.

## Full cell table (all 52 preregistered cells; means/deltas in points; d$ per contract; P/C/N = screen legs p/cost/n)

```
cell                          n     mean  ctlmean    delta      d$   ci95lo   ci95hi  p_shift  p_boot P C N  LEAD
-----------------------------------------------------------------------------------------------------------------
E1_up_t1_1045-1200           36  -0.0053  -0.0009  -0.0043      -4  -0.1869   0.1897  0.96438  0.9980 . . Y
E1_up_t1_1045-1430           36  -0.0944  -0.0476  -0.0469     -47  -0.3672   0.2858  0.78807  0.8320 . . Y
E1_up_t2_1045-1200           44   0.1123  -0.0009   0.1132     113  -0.1321   0.3328  0.27337  0.3480 . Y Y
E1_up_t2_1045-1430           44  -0.3777  -0.0476  -0.3302    -330  -0.9689   0.1846  0.05432  0.2620 . Y Y
E1_up_t3_1045-1200           39   0.0954  -0.0009   0.0963      96  -0.1906   0.3863  0.39181  0.5100 . Y Y
E1_up_t3_1045-1430           39   0.0731  -0.0476   0.1206     121  -0.1459   0.3956  0.47818  0.3820 . Y Y
E1_dn_t1_1045-1200           41  -0.0090  -0.0009  -0.0081      -8  -0.1773   0.1548  0.94390  0.9760 . . Y
E1_dn_t1_1045-1430           41   0.1334  -0.0476   0.1810     181  -0.1619   0.6116  0.34372  0.3340 . Y Y
E1_dn_t2_1045-1200           36  -0.0753  -0.0009  -0.0743     -74  -0.2880   0.1180  0.51558  0.4940 . Y Y
E1_dn_t2_1045-1430           35   0.0960  -0.0476   0.1436     144  -0.1535   0.4443  0.46037  0.3480 . Y Y
E1_dn_t3_1045-1200           40  -0.1283  -0.0009  -0.1273    -127  -0.3765   0.1066  0.26892  0.2420 . Y Y
E1_dn_t3_1045-1430           40  -0.3463  -0.0476  -0.2987    -299  -0.7554   0.1323  0.09795  0.1600 . Y Y
E2_up_t1_1430-close         204   0.0582   0.0443   0.0139      14  -0.0420   0.0670  0.68299  0.6020 . . Y
E2_up_t1_next0900-1030      204  -0.0012  -0.0274   0.0263      26  -0.0758   0.1258  0.62778  0.6060 . . Y
E2_up_t2_1430-close         173   0.0732   0.0443   0.0289      29  -0.0269   0.0946  0.46572  0.3180 . . Y
E2_up_t2_next0900-1030      173   0.0603  -0.0274   0.0878      88  -0.0343   0.2230  0.14248  0.1700 . Y Y
E2_up_t3_1430-close         171  -0.0191   0.0443  -0.0634     -63  -0.1441   0.0190  0.10775  0.1440 . . Y
E2_up_t3_next0900-1030      171  -0.1211  -0.0274  -0.0937     -94  -0.2474   0.0543  0.11932  0.2140 . Y Y
E2_dn_t1_1430-close         200  -0.0221   0.0443  -0.0664     -66  -0.1755   0.0087  0.06500  0.1040 . . Y
E2_dn_t1_next0900-1030      200  -0.0816  -0.0274  -0.0542     -54  -0.1554   0.0305  0.32591  0.2400 . . Y
E2_dn_t2_1430-close         188   0.0618   0.0443   0.0175      17  -0.0451   0.0744  0.64470  0.5900 . . Y
E2_dn_t2_next0900-1030      187   0.0631  -0.0274   0.0905      91  -0.0132   0.1963  0.12556  0.0900 . Y Y
E2_dn_t3_1430-close         209   0.1048   0.0443   0.0605      60  -0.0023   0.1350  0.07836  0.0660 . . Y
E2_dn_t3_next0900-1030      209  -0.0352  -0.0274  -0.0077      -8  -0.1313   0.1209  0.87801  0.9140 . . Y
E3_1.5x_up_0900-1030         75  -0.0744  -0.0280  -0.0464     -46  -0.2185   0.1174  0.63134  0.5760 . . Y
E3_1.5x_up_0900-1430         74  -0.4022  -0.0744  -0.3278    -328  -0.7403   0.0226  0.04987  0.0720 . Y Y
E3_1.5x_dn_0900-1030         94  -0.0243  -0.0280   0.0038       4  -0.1612   0.1773  0.96349  0.9460 . . Y
E3_1.5x_dn_0900-1430         94   0.0593  -0.0744   0.1336     134  -0.2216   0.4723  0.39181  0.4440 . Y Y
E3_2.0x_up_0900-1030         34  -0.0238  -0.0280   0.0042       4  -0.2610   0.2516  0.98041  0.9780 . . Y
E3_2.0x_up_0900-1430         34  -0.2209  -0.0744  -0.1465    -146  -0.5831   0.2564  0.57792  0.4400 . Y Y
E3_2.0x_dn_0900-1030         41  -0.0605  -0.0280  -0.0325     -32  -0.2634   0.2244  0.80410  0.8420 . . Y
E3_2.0x_dn_0900-1430         41  -0.1915  -0.0744  -0.1171    -117  -0.7752   0.4458  0.60908  0.7080 . Y Y
E4_bottom_next1              18  -0.7239   0.0324  -0.7563    -756  -1.7899   0.3296  0.13268  0.1640 . Y .
E4_bottom_next2              18   0.0356   0.0627  -0.0271     -27  -1.6052   1.3359  0.97596  0.9960 . . .
E4_bottom_next3              18   0.7728   0.0939   0.6789     679  -1.5212   3.1302  0.43010  0.5940 . Y .
E4_mid_next1                  2   0.2550   0.0324   0.2226     223  -1.8165   2.2564  0.86109  0.6960 . Y .
E4_mid_next2                  2   1.7550   0.0627   1.6923    1692   1.2924   2.0921  0.35352  0.0020 . Y .
E4_mid_next3                  2   2.6500   0.0939   2.5561    2556   1.0427   4.0527  0.28762  0.0020 . Y .
E4_top_next1                  9  -0.8578   0.0324  -0.8902    -890  -2.8539   1.1046  0.21193  0.3400 . Y .
E4_top_next2                  9  -0.9800   0.0627  -1.0427   -1043  -3.0271   0.9585  0.28940  0.3080 . Y .
E4_top_next3                  9  -0.8411   0.0939  -0.9350    -935  -3.5523   2.1663  0.43633  0.4760 . Y .
E5_upbrk_remainder          108  -0.0419  -0.0047  -0.0373     -37  -0.2760   0.2153  0.80588  0.7700 . . Y
E5_upbrk_next1              108   0.0190   0.0170   0.0020       2  -0.2830   0.3126  0.99644  0.9800 . . Y
E5_dnbrk_remainder           67  -0.1355  -0.0062  -0.1293    -129  -0.4548   0.2002  0.54230  0.4640 . Y Y
E5_dnbrk_next1               67  -0.0361   0.0170  -0.0531     -53  -0.4433   0.3640  0.83348  0.7780 . . Y
E6_up_next1                  78   0.3610   0.0324   0.3286     329  -0.0432   0.7311  0.17275  0.0780 . Y Y
E6_up_next2                  78   0.0709   0.0627   0.0082       8  -0.6177   0.5753  0.98219  1.0000 . . Y
E6_up_next3                  78   0.1438   0.0939   0.0500      50  -0.7438   0.8641  0.91184  0.9420 . . Y
E6_dn_next1                  52  -0.1400   0.0324  -0.1724    -172  -0.6672   0.2534  0.54497  0.4540 . Y Y
E6_dn_next2                  52   0.3173   0.0627   0.2546     255  -0.5110   0.9954  0.57614  0.4600 . Y Y
E6_dn_next3                  52   0.8854   0.0939   0.7915     792  -0.1004   1.7257  0.16385  0.0760 . Y Y
E7_all_next1                  8   1.4463   0.0324   1.4138    1414  -1.5494   3.8081  0.06589  0.3200 . Y .
```

## Reading the table honestly

- **Closest miss (min p in family):** E3_1.5x_up_0900-1430 — after an up overnight gap ≥1.5× trailing-20 overnight σ, the pit session (09:00→14:30) fades −0.33 pts (−$328) vs control, p_shift=0.0499, p_boot=0.072. Sign-consistent at the 2.0× threshold (−0.15 pts) but weaker there — the opposite of what a real dose-response would do — and an order of magnitude away from the corrected 0.00180 bar. With 52 cells, one cell at p≈0.05 is exactly the noise expectation (observed 1 raw-significant vs ~2.6 expected).
- **E1 (EIA realized-response conditioning, the one open EIA representation):** flat in all 12 cells; neither continuation nor reversal of the 10:30→10:45 response at either horizon. The largest deltas (±$300) carry p≈0.05–0.5 and are sub-noise for the family.
- **E4/E7 large deltas are tiny-n artifacts:** E4_mid (n=2, +$2556 at next3) and E7 (n=8, +$1414) look big but are LEAD-ineligible by the preregistered n≥30 leg and statistically nothing (p 0.29/0.066). Shock days close bimodally (18 bottom / 9 top / 2 mid of 29 shocks) — the mid-tercile cell is structurally near-empty.
- **E5/E6:** compression breaks and 20-session extremes show no follow-through or fade in any direction/horizon.

## Anomalies

1. **EIA holiday anchor:** the 36 Thursday-shifted releases are anchored at 10:30 ET per spec; real EIA practice for delayed releases is typically 11:00 ET, so those events (15%) may condition ~30 min before the true release. Dilutive only; noted, not corrected post-hoc. Ad-hoc EIA delays (systems outages) not modeled.
2. **First execution failed gate G4** (points-translation invariance): +1000.0 on raw float prices flipped ~1-ulp boundary ties, slightly changing E2 tercile memberships. Fixed by moving all price arithmetic to the exact $0.01 integer-cent grid; G4 now exact (max deviation 0.0 under +1000-pt translation, identical event sets). Verdicts identical in both executions (all DEAD both times); disclosed because the first table had been printed before the fix.
3. Sign-zero conditioning moves excluded from sign cells: E1 n=3, E2 n=15. E5 same-first-bar high+low tie: 0. ~22 early-close sessions lack valid 14:00/14:30 anchors (30-min staleness tolerance) and drop from affected E2 cells and controls. E4_mid had 125/1000 degenerate bootstrap draws (no events in resample); CI from remaining draws.

## Gate table (program-printed, verbatim)

```
GATE                      SPEC                                                            OBSERVED                                                      PASS-FAIL
-----------------------------------------------------------------------------------------------------------------------------------------------------------------
G1_DATA_SHA256            e587486c23f5b611...                                             e587486c23f5b611...                                           PASS
G2_SEAL_MAX_SESSION       < 2026-08-01                                                    2026-07-31                                                    PASS
G3_SESSION_COUNT          1182                                                            1182                                                          PASS
G4_POINTS_INVARIANCE      event sets identical & max|d(delta)|=0 under +1000.00-pt price  ev_same=True, max_dev=0.00e+00 cents                          PASS
G5_CELLS_REPORTED         52 preregistered                                                52 emitted                                                    PASS
G6_CONTROLS_MATCHED       every cell has a matched control row                            52/52 control rows                                            PASS
G7_NULL_SHARED_DRAW       one exhaustive offset set for all 52 cells; K,K_eff printed     S=1122 offsets shared; K=52, rhobar=0.0172, K_eff=27.71       PASS
G8_PROB_MEANING_WORDS     p-value event stated in words in output                         printed below                                                 PASS
G9_PROB_SECOND_WAY        LEAD p recomputed via block-bootstrap sign test agrees (<0.05)  no LEAD; min-p cell E3_1.5x_up_0900-1430: p_shift=0.04987, p  PASS
G10_EIA_CAL_SEAL          all release dates < 2026-08-01                                  239 dates, max 2026-07-29                                     PASS
G11_COST_CONSTANTS        comm 4.36 + spread{1,2,3}x$10; conservative 34.36; screen 2x=6  all-in band [14.36, 24.36, 34.36]; screen 68.72 USD = 0.0687  PASS
G12_MIN_EVENTS_ENFORCED   every LEAD cell n>=30                                           vacuous (no LEAD)                                             PASS
-----------------------------------------------------------------------------------------------------------------------------------------------------------------
ALL GATES: PASS
```

## Consequence for the frontier

The CL native event/displacement axis joins the closed list: with multi-day z-MR underpowered (G00065), pre-event EIA direction closed, and now the 7-event displacement catalog DEAD, no CL directional representation remains open on the $0 1-min surface. Any further CL expenditure should target volatility representations or bought data, per the standing owner forks — not more $0 directional cards.

## Files

- `runs/G3_EVENT_CL_20260906/src/run_event_cl.py` — full pipeline (calendar, cells, controls, bootstrap, shift null, gates)
- `runs/G3_EVENT_CL_20260906/out/event_tables.csv` — all 52 cells
- `runs/G3_EVENT_CL_20260906/out/controls.csv` — 52 matched control rows with descriptions
- `runs/G3_EVENT_CL_20260906/out/gate_table.txt`, `out/console.txt` — program-printed output
- `runs/G3_EVENT_CL_20260906/out/run_extras.json` — K/K_eff/ρ̄, calendar details, verdicts, machine-readable
