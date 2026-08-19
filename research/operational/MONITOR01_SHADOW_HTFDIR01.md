# MONITOR-01 SHADOW LEDGER — HTFDIR01 ARM_LONGONLY candidate (FROZEN 2026-08-19)

**Owner authorization**: 2026-08-19, verbatim: "授权并且给你随意权限。全速马力出动" — in direct
response to the HTFDIR01 REPORT recommendation ("owner-authorized candidate shadow ledger at
MONITOR-01 readings"). Committed BEFORE any forward reading exists (MONITOR-01 #2 due
≥ 2026-11-01). Frozen after the first reading like every read protocol; owner may amend until then.

## What is read

At each MONITOR-01 reading (same fresh engine-exact 1-min NQ export the protocol already
requires, consuming nothing extra), extend TWO Product-B ledgers over the newly available
forward window (≥ 2026-08-01, evaluation-only):

1. **Incumbent** — `solve_B` SYM (the certified construction, byte-frozen in
   `research/system_master/HTFDIR01_DIRECTIONAL_TILT/src/01_htfdir01_construction.py`).
2. **Candidate** — `solve_B` ARM_LONGONLY, same file, zero changes permitted.

Both are EVALUATION reads of frozen constructions — no parameter may be touched at any point.
Record per reading: forward-window daily ledgers (both), Δnet, ΔSharpe, per-session table
appended to `monitor01_shadow_htfdir01_ledger.csv` (this directory).

## Frozen decision rule

- **Primary read**: at the first reading where the accumulated forward window has ≥ 120
  sessions (~2 quarterly readings), and again at each subsequent reading:
  - **ADVANCE** (candidate goes to the NT8-parity + promotion battery step, which still needs
    its own preregistration): forward Δnet > 0 AND day-clustered P(ΔSharpe > 0) ≥ 0.75
    (10,000 reps, seed 20260819) AND no incumbent top-5 forward winning day retained < 95%.
  - **KILL** (candidate CLOSED as regime-local, permanently): accumulated forward Δnet
    ≤ −$5,000 at any reading, OR P(ΔSharpe > 0) < 0.50 once ≥ 250 forward sessions exist.
  - Otherwise **CONTINUE** (stay in shadow; re-read next quarter).
- The dev-window result (PASS-SCREEN with binding cautions, see
  `HTFDIR01_DIRECTIONAL_TILT/REPORT.md`) contributes NO further evidence — forward data only.
- Context flag (reported, not gated): the red team showed the trimmed-short toxicity is
  regime-dependent (sign flipped in 2024 and Jun–Jul 2026); each reading reports the forward
  regime split (up-tilt vs down-tilt session Δ) so a KILL/ADVANCE can be read mechanistically.

## Bookkeeping

Readings recorded in `monitor01_log.csv` alongside the champion reading; registry row per
reading in `research/system_master/TESTING_LEDGER.csv` (evaluation, zero alpha budget).
This shadow does not touch, and is not evidence about, Product A (that side is CLOSED) or the
B-MNQ adapter (shared decision core; inherits any eventual promotion decision only after its
own genuine-MNQ-price-basis rebuild, per ONE_CONTRACT_FRONTIER).
