# C01 T0-1 — Short-side regime structure (SOLAR-01)

_Executed 2026-08-07 against frozen constants in `C01_WAVE_SPEC.md` §2 T0-1. No constant was
adjusted after any result was read. Tier-0 instrumentation; consumes 0 R1 trials._

## Verdict: **REJECT** — record "shorts are crisis insurance; keep symmetric" and close SOLAR-01.

Both halves of the frozen gate fail, the first one with the **wrong sign**:

| Gate condition (Bonferroni α = 0.05/3) | Required | Observed | Result |
|---|---|---|---|
| Ungated-state (G3 false) pooled short P&L | negative, t ≤ −2 | **+$204,626** pooled, t_session = **+0.35** (608 active sessions; per-trade t +1.01, n = 11,220) | **FAIL** |
| G3-true retention of 2022+2025 pooled short net | ≥ 80% | strict flag-True cell: **40.6%** ($311,168 / $767,037). Deployment rule (warm-up = baseline): 94.1% — but only because 2022 flags are undefined (see Caveat) | **FAIL** (strict) |

Per-flag out-state t (all positive, none approaches −2): G1 +0.32, G2 +0.60, G3 +0.35.
The fallback continuous arm is licensed only when "separability holds but retention fails";
separability does **not** hold, so arm C below is instrumentation, not a candidate.

## Data and validation

- Daily session closes built from `runs/AUDIT03_BARS/nq_3m_2022_2026.csv` (18:00 ET roll):
  1,184 sessions, 2022-01-03 → 2026-07-31.
- Flags at PRIOR close (shift-1, no lookahead): G1 = close < 200d SMA; G2 = 20d realized vol
  (std of daily log returns, ddof 1, ×√252) > rolling-756d 70th pct (min 250); G3 = G1 OR G2
  (three-valued OR). volz20 = z of vol20 vs rolling 756d (min 250).
- 13 member ledgers `runs/AUDIT02_V3_SWEEP_B/ledgers/b2v3__*.csv`: 34,148 round-trip episodes
  (19,077 short), qty = 1 throughout, every ledger ends flat, **zero** episodes cross a session
  close. Episode-decomposed daily P&L equals fill-based daily cashflow for all 13 members to
  < $1e-6. Arm A reproduces the untouched pooled ledgers exactly (max daily deviation < $1e-9)
  — verified **before** arms B/C were read.

## Caveat frozen before results: flag warm-up

With only 2022+ closes, G1/G3 are undefined for the first 200 sessions (through 2022-10-10)
and G2 until 2023-01-18. Pre-registered handling: cell statistics use defined flags only;
replay arms fall back to baseline (shorts kept, w = 1) where undefined. The undefined stretch
is exactly the 2022 bear: **$410,845 of the $657,879 total pooled short net (62%) sits in the
warm-up cell** and can never be attributed to a flag state with this data window. With real
pre-2022 history, early 2022 would almost certainly flag G1-true (NQ crossed its 200d SMA in
Jan 2022), which strengthens — not rescues — the "crisis insurance" reading: the reject verdict
does not depend on the warm-up, because the gate's t-condition fails on sign in the defined
region regardless.

## Cell structure (pooled across 13 members; G3; full table in `c01_t01_short_regime_cells.csv`)

| Year | G3-in net | n_ep | t_sess | G3-out net | n_ep | t_sess |
|---|---|---|---|---|---|---|
| 2022 | −$4,569 | 908 | −0.03 | — | 0 | — |
| 2023 | −$57,009 | 384 | −0.80 | +$44,154 | 3,693 | +0.19 |
| 2024 | +$21,174 | 405 | +0.18 | −$37,384 | 3,869 | −0.13 |
| 2025 | +$315,737 | 1,527 | +0.79 | +$45,024 | 2,662 | +0.14 |
| 2026 | −$232,924 | 1,579 | −0.70 | +$152,832 | 996 | +0.50 |
| ALL | +$42,409 | 4,803 | +0.08 | +$204,626 | 11,220 | +0.35 |

The in-state cell **flips sign year to year** (2023 strongly negative, 2025 strongly positive,
2026 strongly negative — G2-in 2026 alone is −$289,507, per-trade t −2.45). There is no stable
"shorts only work in bear/high-vol regimes" structure at the trade level; if anything, 2026
high-vol shorts were the worst cell in the study while ungated shorts stayed positive.

## Counterfactual ledger replay (13-member equal-weight, per-member-average $; valid because the
signal path is position-independent)

| Arm | Net | Sharpe | maxDD | MAR | Worst yr | 2022 ret | 2025 ret |
|---|---|---|---|---|---|---|---|
| A symmetric (= untouched ledgers, exact) | $198,059 | 1.064 | −$39,853 | 1.087 | $12,160 (2023) | 100% | 100% |
| B shorts only if G3 | $182,318 | 1.104 | −$30,062 | 1.326 | $8,763 (2023) | 100%* | 94.3% |
| C w_short = clip(volz20,0,2)/2 | $174,757 | 1.159 | −$23,202 | 1.647 | $11,474 (2023) | 100%* | 63.9% |

\* 2022 untouched only because flags are undefined there (warm-up = baseline). Yearly: arm B
gives back −$3.4k (2023), −$3.5k (2025), −$11.8k (2026) and gains +$2.9k (2024); arm C fails
the 80% crisis-retention bar outright in 2025 (63.9%).

B and C do improve Sharpe/DD/MAR — but that is generic short-exposure reduction paying with net
(−8% and −12%) and with crisis participation, exactly the trade the spec pre-declared
unacceptable below 80% crisis retention, and it rests on a regime signal whose in/out cells are
sign-unstable. Right-tail indicator (point estimate): top-1% short-episode P&L share in the
G3-out (down-weighted) state = 33.8% vs 68.4% session share — the tail constraint is not the
binding objection; sign instability and the failed t-gate are.

## Disposition

- SOLAR-01 closes at Tier 0. No Tier-1 NT8 confirmation run is licensed; 0 of the wave's
  10-trial budget consumed.
- Registry: record C01-T0-1 as REJECT with note **"shorts are crisis insurance; keep
  symmetric"** (hypotheses.md + seq-0 instrumentation row, counts_as_trial: no).
- Files: `c01_t01_short_regime_cells.csv` (all flags × states × years),
  `c01_t01_replay_arms.csv` (arm metrics). Analysis script archived in the session scratchpad
  (`c01_t01_analysis.py`); deterministic given the two committed inputs.
