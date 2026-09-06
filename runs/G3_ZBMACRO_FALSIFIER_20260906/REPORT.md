# G3_ZBMACRO_FALSIFIER_20260906 — graduation falsifier for the G00067 E1 LEAD (ledger G00072, family GENESIS3_EVENT)

**Verdict (mechanical, preregistered decision rule): `ZBMACRO01 ENGINE CANDIDATE` — G2+G3+G4+G5+G8 all PASS (ledger PASS).**
**Evidence status: DISCOVERY_CONSUMED** — same substrate as the G00067 screen; nothing here is forward evidence.

**Frozen object (zero free parameters):** on NFP_DAY/CPI_DAY sessions (GENESIS_H2_CALENDAR_20260828, the exact E1 calendar), if close(08:45)−close(08:30) < 0 in points, SHORT 1 ZB at the 08:45 close, exit at the 15:00 close. No entry on UP or zero first response.

**Data:** `runs/SM1M_ZB_SUBSTRATE/out/zb_1m_2023_2026.parquet`, 923 sessions 2022-12-27→2026-07-31, POINTS basis (DELEV01), end-stamped bars, ET sessions 18:00→17:00. Seal asserted: max session = 2026-07-31. 1/32-grid share 1.000000.
**Cost arms (BASIS=MODELED ALL_IN = comm $4.36 + spread):** PRIMARY 1 tick/side = $66.86 RT (0.06686 pt); STRESS 2 ticks/side = $129.36 RT (0.12936 pt). No spread-only figure is called all-in anywhere in this run.
**Convention (used in every gate):** x = (c1500−c0845) + cost_pts; x < 0 = profitable short; profit_$ = −x·1000.
**Code:** `src/run_falsifier.py` (executable preregistration; all ambiguity resolutions fixed in its header before results). Artifacts: `out/trades.csv` (the 40 events with dates), `out/neighborhood.csv` (18 cells), `out/dropk.csv`, `out/gate_table.txt`, `out/run_log.txt`.

## Gate table (program-printed; full version in `out/gate_table.txt`)

| GATE | SPEC | OBSERVED | PASS/FAIL |
|---|---|---|---|
| G0_seal_identity | seal ≤2026-07-31; reproduce E1 n=40 event set exactly (identity vs artifact) | max sess 2026-07-31; 9/9 constraining E1 cell stats exact (n exact, mean <1e-9); n_down=40 | PASS |
| G1_MDE_first | MDE (block-bootstrap SE) printed BEFORE observed | MDE_sig 0.1849 pt ($185/ct), MDE_80 0.2641 pt ($264/ct); printed first | PASS |
| G2_aftercost_edge ⛔ | PRIMARY after-cost mean < 0 AND block-bootstrap CI95 excludes 0 | mean −0.1777 pt (+$177.7/ct profit), CI95 [−0.4113, −0.0449] | **PASS** |
| G3_null ⛔ | shift-null percentile ≤ 5.0 AND \|pct1−pct2\| ≤ 5.0 (sign-permutation 2nd computation) | pct1 0.50, pct2 1.55, \|diff\| 1.05 | **PASS** |
| G4_chronology ⛔ | after-cost mean < 0 in BOTH halves; both-wrong-sign = FAIL | first-20 (2023-01-12..2024-06-07) −0.2191; last-20 (2024-08-14..2026-06-05) −0.1363; both negative | **PASS** |
| G5_tail_honesty ⛔ | drop-k curve printed; after-cost mean < 0 at k=2 | k=2 mean −0.0910 pt (+$91.0/ct); full curve in dropk.csv | **PASS** |
| G6_neighborhood | 3×2×3 grid, ALL cells reported; headline stays frozen object; plateau statement | 18/18 reported; net>0 in 15/18; all-down 6/6; adjacent-entry 2/2 → PLATEAU | PASS |
| G7_release_split | NFP-only and CPI-only after-cost means printed | NFP n=23 −0.0744 (+$74.4); CPI n=17 −0.3173 (+$317.3); both negative — strengthens | PASS |
| G8_cost_stress ⛔ | after-cost mean < 0 at 2-tick STRESS arm | mean −0.1152 pt (+$115.2/ct) | **PASS** |
| G9_battery | weekly-vol lead; no unguarded fixed-DD figure; UP mirror; rho-to-P1 | Sharpe_wk 0.86; no DD-normalized income quoted; UP-long +$27.7/ct; ρ_d −0.006, ρ_w +0.100 | PASS |

⛔ = blocking. **Blocking set G2+G3+G4+G5+G8: 5/5 PASS → `ZBMACRO01 ENGINE CANDIDATE` (ledger PASS).**

## Key numbers

- **n = 40** down-response events (23 NFP, 17 CPI), 2023-01-12 → 2026-06-05, reproduced EXACTLY from the G00067 E1 artifact (G0: 9/9 constraining cell statistics; the artifact carries no per-event dates, so identity is via the identical deterministic constructor + exact statistic match; the dates are now materialized in `out/trades.csv`).
- **After-cost edge (PRIMARY):** +$177.7/ct per trade (gross +$244.5, cost $66.86); CI95 of profit [+$44.9, +$411.3]. **STRESS (2 tk/side):** +$115.2/ct.
- **Null:** circular-shift of the release flag puts the observed after-cost total (+$7,107) at the **0.50th percentile**; the sign-permutation second computation reads **1.55** — agreement 1.05 pts (clause ≤ 5). The shift-null mean is *positive* (+1.01 pt = short loses on non-release down responses): the effect is release-specific, not generic momentum.
- **Chronology:** profitable in both halves (+$219.1 / +$136.3 per trade).
- **Tails:** drop-k curve +177.7 / +132.7 / **+91.0** / +64.9 / +40.8 / +18.0 $/ct at k=0..5 — tail-carried but survives its preregistered k=2 clause; at k=5 it is nearly gone (honesty: 60% hit rate, magnitude-driven).
- **Neighborhood (report-only, headline unchanged):** all six all-down cells positive net (entry 08:40/08:45/08:50 × exit 14:00/15:00: $79/$100/$174/$178/$14/$18) — a plateau, though decaying fast at 08:50. The below-median-down and terc1-aligned cells at 08:45 are larger ($394–$421, $314–$325) but remain non-headline per prereg (n-floor/selection); terc1-aligned flips negative at 08:50 (−$253/−$258), so the small-response reading is entry-fragile.
- **Asymmetry:** UP-long mirror nets only +$27.7/ct with CI spanning zero [−$252, +$218] — direction-concentrated, as screened.
- **Orthogonality preview:** ρ to P1 (source: `runs/WE_W56_BREADTH/out/p1_daily.csv` — the preregistered alternative to re-running G3_ESMR_PORTFOLIO's substrate rebuild; zero-filled common calendar 2022-12-27..2026-05-29, 878 sessions, 39/40 trades in overlap): **daily −0.006, weekly +0.100.**
- **Honest annual economics (weekly-vol lead):** weekly-vol annualized Sharpe **0.86** on the 188-week grid; native **~$1,966/yr per contract** on 11.1 trades/yr; weekly maxDD $1,799, CDaR95 $1,510 (path descriptives ONLY — no fixed-DD/CDaR-normalized income is quoted anywhere in this run, so no thinning placebo is owed).

## Caveats (binding)

1. **DISCOVERY_CONSUMED.** Same substrate as the screen that found it. The pass graduates the lead to ENGINE CANDIDATE; it does not create forward evidence and does not touch any baseline.
2. **Underpowered vs its own MDE.** |observed| 0.1777 pt < MDE_80 0.2641 pt: at n=40 this design had <80% power to detect the effect it measured. The G2 CI excludes zero, but the margin is real-but-thin (CI low edge +$44.9/ct).
3. **Small dollars.** ~13 preregistered trades/yr in expectation (11.1 realized), ~$2k/yr/ct. Per the decision rule, the CLASS-S/P assessment (portfolio question, when-does-it-pay profile) decides whether construction proceeds. No deploy, no promotion, no baseline change.
4. **One trade (2026-06-05) sits inside the globally BURNED 2026-05-31→07-31 window** — labeled per spec; this window cannot serve as a clean sub-holdout.
5. The tercile/below-median sub-cells stay non-headline; quoting them standalone would be selection (the E1 n-floor failure stands).

## Next step per decision rule

Class-S/P assessment: honest annual economics ~13 trades/yr — small dollars, so the CLASS-P portfolio question (ρ_w ~0.10 to P1, event-locked payout profile) and the when-does-it-pay profile decide whether construction proceeds. No deploy, no promotion.
