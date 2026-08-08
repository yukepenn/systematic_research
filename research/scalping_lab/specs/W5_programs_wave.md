# W5 — three-program parallel wave (Amendment 6; frozen before readout, 2026-08-08)

Common (Programs C, on tick substrate): 37 L2 discovery sessions, sechilo+grid1s, 1s
clock, RTH, quote-alive, conservative same-second→adverse barrier, sequential episode
simulation, C1=2.872t/C2=4.872t, day-clustered 95% CIs seed 20260808, neighbors reported
never selected on. Pass rule: net C1 > 0 AND CI_lo > −0.5t; family verdict = plateau.
Per Amendment 6 §7C: no W4-loser retuning — each spec below states its mechanical
distinction from killed relatives.

## A1 — Robust sizing FRONTIER for R5-E10 v2 (Program A; ledger-only)
Inputs: existing Family-A daily P&L ledgers (runs/E10MASTER_V2 + V1 daily equity; find
actual parquet/CSV in runs/). Method: stationary block bootstrap (mean block 10 days,
2000 paths, seed 20260808) of daily P&L per 1-NQ; for Kelly fraction c ∈ {0.15, 0.25,
0.35, 0.5, 0.75, 1.0} with MNQ-granular scaling (contracts = round(c·W·μ/σ² / notional,
MNQ)), report: geometric growth, median terminal wealth, P(maxDD > 20/30/40%), time
under water. Scenarios (each full grid): (i) empirical; (ii) edge haircut μ×0.75 and
μ×0.5 (variance unchanged); (iii) tail stress: top-5 profit days removed; (iv) both.
Deliverable: the FRONTIER TABLE + the c range that keeps P(DD>40%)<5% across ALL
scenarios. Explicitly: no single c is "the answer"; no claim of alpha creation.

## B1 — Overnight 16:44→09:30 premium, first pass (Program B)
Data: runs/AUDIT03_BARS/nq_3m_2022_2026.csv (3-min closes, 2022-01→2026-07-31; NOTE
per contamination ledger, minute-history studies dev window = →2026-05-31: TRUNCATE to
2026-05-31, do not read June/July). Position: long 1 NQ at the 16:42-16:45 bar close,
exit at next session's 09:30 bar open/close (state which; frozen: first bar with time
≥ 09:30, its close... use 09:30 bar CLOSE consistently). Friction: 2.0t RT (liquid-edge
entries) primary, 2.872t stress. Report: per-night expectancy (ticks), by year, by
post-2024 subsample, down-prior-day conditional (prior RTH ret < 0) as ONE frozen
conditional, day-clustered CI. THEN measured correlation: overnight nightly P&L vs
Solar daily P&L (E10 ledger, overlapping dates), full + losing-day corr. Verdict frozen:
promising iff unconditional ≥ +4t/night after 2.0t friction with CI_lo > 0 AND |ρ| < 0.3;
2005+ extension only then.

## B2 — Intraday-momentum correlation pre-gate (Program B; no new alpha claims)
Compute Gao-style predictor daily P&L from the same 3-min CSV (dev window): sign of
(15:30 close − prior 16:45 close... frozen: rest-of-day return 09:30→15:30) traded into
15:30→16:45, 1 NQ, C1. Correlate ITS daily P&L with Solar daily P&L. Deliverable: ρ
(full + losing-day). Frozen rule: ρ ≥ 0.5 → family rejected as diversifier (build
nothing); ρ < 0.3 → a build spec may be written next wave. (H-A1's kill of the
standalone effect stands; this measures correlation structure only.)

## C1 — W5-1 CLEAN/deep entry (distinct from killed W3-1: adds depth+efficiency+flow
interaction AND recovery-confirmation entry instead of raw-drop immediate fade)
LONG: ret30 ≤ −D (D=12 primary; 16 neighbor; from clean-move contrast median −15) AND
eff60 ≥ 0.12 AND sflow10 ≤ 0; entry NOT at trigger: wait for recovery tick = mid_last
≥ (trailing-30s low + 2t), within 60s of trigger, else cancel. SHORT symmetric.
Brackets (20,6),(24,8),(32,10); cap 300s; cooldown 30s.

## C2 — fast FSS-2 breakout-acceptance (distinct from killed 1-min S2a: 15s/30s clocks,
acceptance-close logic, different pullback grammar)
Build 15s and 30s completed bars from sechilo (O/H/L/C of mid). LONG: bar closes above
prior 20-bar high with close-location ≥ 0.7; ACCEPTANCE: next 1-2 completed bars close
above the broken level; entry: 1s mid crosses above the acceptance-phase high +1t,
strictly after acceptance bar close. Brackets (24,8),(32,10); cap 300s; cooldown 60s;
one trade per breakout.

## C3 — FSS-3 failed-opposite-probe (new state machine, never tested)
Context: ret120 ≥ +16t (up). Probe: subsequent counter-move ≥ 6t within ≤30s reaching
probe-low L. Failure: within 30s of L being set, mid recovers ≥ 50% of the probe depth
without L being undercut by > 2t. Entry LONG at the ≥50% recovery crossing. SHORT
symmetric. Brackets (24,8),(32,10); cap 300s; cooldown 60s. Neighbors: context 12/24t,
probe 4/8t.

## C4 — FSS-6/7 compression→expansion + velocity/low-retracement (never tested)
FSS-6: compression = trailing 120s range ≤ 8t; expansion trigger = 10s |ret| ≥ 6t
breaking the compression range boundary; enter in expansion direction. FSS-7 secondary:
enter when ret20 ≥ 12t AND max-retracement ratio ≤ 0.25 (retrace since move start /
displacement). Brackets (24,8),(32,10); cap 300s; cooldown 60s.

## C5 — Predictability-ceiling test (Amendment 6 §8; measurement, not a strategy)
Decision clock every 30s RTH; features = census causal library (~25, from grid1s+
sechilo trailing windows only); labels: target-first for (+24,−8) and (+32,−10), long
and short (4 sets, per-second hi/lo evaluation). Models: L2 logistic, sklearn
HistGradientBoosting (shallow: max_depth ≤ 3, early stopping), optional GAM if pyGAM
present. Validation: chronological session-grouped 5-fold (train on earlier sessions
only — expanding), ALL preprocessing inside folds. Report per label: calibration curve,
Brier, baseline P(target), top-decile-confidence bucket P(target) with day-clustered CI,
lift vs baseline, vs the C1 gap (~8.7-9.1pp for 24/8, ~7.0-7.4pp for 32/10), stability
across folds, permutation feature importance. Frozen interpretation: if NO model/label
reaches top-decile lift ≥ 5pp with CI excluding 0, the information set is declared
insufficient (major input to §9 closure); if ANY reaches ≥ 7pp stable, freeze that
model form and convert to a sequential trade sim in a NEW spec next wave.

Artifacts: `artifacts/w5_<id>/`. Code: `src/python/w5_<id>.py`. Registry rows S14-S21.
