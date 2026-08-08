# W8-4 — ROLE-B feasibility: entry-time micro-state vs Solar per-trade P&L

MEASUREMENT only. Frozen spec: `research/scalping_lab/specs/W8_programs_final.md` (cf7041f), W8-4.
Code: `research/scalping_lab/src/python/w8_roleb.py`. All numbers below appear in
`artifacts/w8_roleb/stdout.txt` and the CSVs in this directory. Seed 20260808; 1,000
day-clustered bootstrap reps; no data at/after 2026-06-01 used (hard guard in code:
1,457 fills and the truncated 2026-06-01 session dropped at load).

**Scope distinction (required):** day-level regime axes (vol/trend/day-type conditioning
of Solar) were falsified in prior waves and REMAIN CLOSED. The features here are
TRADE-level micro-state sampled at each entry minute — a different object. Nothing in
this study reopens day-level conditioning, and NO FILTER IS ADOPTED from this wave; any
rule would need a new spec + walk-forward + the falsified-axes review.

## 1. Trade reconstruction and verification (FACT)

- Fills: `runs/E10MASTER_V2/out/e10m_v2_fills.csv` (E10 master v2, MNQ, minute-stamped ET).
  Position tracked via signed qty; a trade = flat-to-flat episode (entry fill(s) to flat;
  the strategy scales 0–10 MNQ via targets; zero reversal fills exist — asserted).
- P&L per trade = signed sum(price×qty) cash flow minus commission, expressed in NQ ticks
  per 1-NQ-equivalent (qty/10; $5/tick): `pnl_t = (2·Σ side·price·qty − comm)/5`.
- 5,564 closed episodes over 1,139 sessions (2022-01-03 → 2026-05-29); **zero episodes
  span a session boundary** (v2 flattens by 16:44–16:45 every session), so the
  position-carry mismatch allowed for in the spec is exactly zero.
- **Verification vs `daily_v1_v2.csv` net_v2: exact.** Per-session reconstructed sum
  matches net_v2 on all 1,139 sessions (max |diff| $0.0000; sum $112,814.60 both sides)
  and on all 37 substrate dates (table: `verify_sessions37.csv`).
- 37 substrate sessions (2025-08-14 → 2026-05-20): **183 trades** (4.95/session);
  3 dropped from feature analyses (entry within first 60 s of session) → **180 trades**
  with features, 37 sessions.

Context (FACT): E10 v2 is a scale-out strategy with structurally low win rate — all-sample
win rate 0.233, mean +4.06 t/trade; the 37-session window is a modestly losing stretch
(net_v2 total −$2,934.60; 14/37 positive sessions; trade win rate 0.246, mean −3.21 t,
median |pnl| 38.2 t, range −567 t … +2,150 t). Quintile results below are conditioned on
this window.

## 2. Entry-minute micro features (definitions)

From `substrate/grid1s/NQ` + `sechilo/NQ` merged on the 1-s grid (sechilo mid_* already in
NQ ticks = price×4; grid1s bid/ask are prices, spread_t already ticks). Sampled at the
entry minute's :00 second; rolling windows use the 60 **strictly prior** seconds
(rows t−60…t−1), so nothing from the entry-stamp second leaks in. All 183 entries matched
the grid :00 second exactly.

spread60 (mean spread_t, ticks) · sflow60 (Σ signed flow) · upd60 (Σ bid_upd+ask_upd) ·
rv60 (std of 1-s mid diffs, ticks) · eff60 (|Δ60 mid|/Σ|Δ1 mid|) · dist_hi / dist_lo
(ticks from running session high/low, sechilo cummax/cummin) · mins_open (minutes since
18:00 ET open). Supplementary (not in frozen list, labeled): sflow60_signed = side×sflow60.

## 3. Quintile tables (IN-SAMPLE CHARACTERIZATION)

Full table: `quintiles.csv` (per-quintile mean pnl_t, day-clustered 95% CI, win rate,
mean max position). Compact view — Q5−Q1 mean-P&L spread and Spearman ρ(feature, pnl_t),
both with day-clustered bootstrap CIs:

| feature | Q5−Q1 (t) | CI | Spearman ρ | CI | CI excl. 0? |
|---|---|---|---|---|---|
| rv60 | **−63.4** | [−113.8, −27.8] | **−0.255** | [−0.365, −0.129] | **yes (both)** |
| dist_hi | −25.6 | [−74.3, +41.6] | **−0.264** | [−0.380, −0.133] | ρ yes |
| spread60 | +45.5 | [−65.2, +225.2] | **−0.216** | [−0.333, −0.089] | ρ yes |
| upd60 | −18.2 | [−102.4, +67.5] | −0.147 | [−0.290, −0.009] | ρ marginal |
| dist_lo | −50.7 | [−137.2, +36.3] | −0.002 | [−0.136, +0.141] | no |
| mins_open | −62.6 | [−208.8, +54.2] | +0.029 | [−0.128, +0.176] | no |
| sflow60 | −7.1 | [−78.9, +61.5] | +0.008 | [−0.148, +0.150] | no |
| eff60 | −1.4 | [−47.3, +50.6] | −0.018 | [−0.142, +0.103] | no |
| sflow60_signed (suppl.) | +26.7 | [−36.6, +100.9] | −0.024 | [−0.167, +0.121] | no |

Reading (IN-SAMPLE CHARACTERIZATION): the only cluster with CIs clear of zero is the
**volatility/activity family** — high entry-minute rv60 (and its correlates spread60,
upd60, dist_hi = entering far below the session high) associates with worse subsequent
trade P&L. rv60 Q5 (>6.97 t/s) is the one quintile whose own CI excludes zero
(mean −58.9 t, CI [−79.9, −33.2], win rate 0.167). Spearman significance with
non-significant Q5−Q1 spreads (dist_hi, spread60) reflects the heavy-tailed P&L (rank vs
mean disagreement) — treat magnitudes as unstable. Directional/flow features (sflow60,
signed flow, eff60) carry no measurable information. Note rv60/spread60/upd60/dist_hi are
mutually correlated; this is roughly ONE axis, not four independent signals — and it
rhymes with the W4/W5 census finding that vol/activity was the dominant separating axis.

## 4. Leakage-guarded logistic (out-of-fold MEASUREMENT)

L2 logistic (C=1.0 fixed, no tuning), win/loss label, the 8 frozen features, scaler fit
on train only, chronological session folds (5 blocks of the 37 sessions, expanding train,
folds 2–5 tested; `logistic_folds.csv`, `oof_predictions.csv`):

- Per-fold AUC: 0.481 / 0.393 / 0.417 / 0.538 (test n = 26/37/41/40)
- **Pooled out-of-fold AUC = 0.447**, day-clustered CI **[0.362, 0.530]** (n=144, base
  win rate 0.236)
- Top-decile predicted-win trades (n=14): win rate 0.286, **lift +0.050,
  CI [−0.174, +0.258]**
- Top-quintile (n=29, supplementary): win rate 0.172, lift −0.064, CI [−0.158, +0.099]
- Full-sample standardized coefficients (descriptive only, `logistic_coefs_insample.csv`):
  rv60 −0.50, dist_hi −0.39, upd60 +0.32, spread60 +0.22, … — the vol cluster again, with
  unstable signs among its collinear members.

## 5. Verdict (INFERENCE)

Role-B feasibility on this sample is **weak-negative**: there is a real in-sample,
day-cluster-robust association between entry-minute volatility state and per-trade P&L
(rv60 is the single defensible axis), but a leakage-guarded chronological model converts
none of it into out-of-fold win/loss discrimination (AUC 0.447, CI spanning 0.5; decile
lift CI spans 0). With 180 trades / 37 sessions the study is powered for large effects
only; the win/loss label also discards the P&L magnitude where the rv60 effect lives.
If role-B is revisited, the only candidate worth a NEW spec is a high-rv60 entry-state
study on a larger trade sample with a magnitude-aware target — subject to walk-forward
and the falsified-axes review. **No filter is adopted; day-level regime axes remain
closed.**

Artifacts: stdout.txt, trades_all_sessions.csv, trades_features.csv,
verify_sessions_all.csv, verify_sessions37.csv, quintiles.csv, logistic_folds.csv,
oof_predictions.csv, logistic_coefs_insample.csv, w8roleb_report.md.
