# G3_XPASS01 — P1 passive-entry policy replay (join-bid limit + T-second timeout)

**Ledger G00082 · family GENESIS3_EXECUTION / EXEC_PASSIVE_ENTRY (3 T-variants = one family) · run date 2026-09-06 · Class-X EXECUTION · DISCOVERY-grade by construction · NEVER alpha evidence.**

NOTE: the harness refused writing this REPORT.md into runs/G3_XPASS01_PASSIVE_ENTRY_REPLAY_20260906/ (subagent write policy); per instructions it is returned here instead of being tunneled to disk. All program-printed artifacts ARE on disk in the run's out/.

## Verdict

**LEDGER: NULL — no candidate, no kill.** Mechanically applied per DESIGN_FROZEN §5: no T-variant cleared G2 (Bonferroni) — all three lower CIs span zero — so nothing is a CANDIDATE; and neither KILL fired — the policy engages the book easily (strict fill rate 73.8–91.0 %, far above the 20 % mechanism floor) and the upper 95 % CIs (+$11.86 to +$17.54/ctr-entry) sit well above the $2.50 materiality floor, so the powered-kill clause cannot close the question either. **The trial is honestly indeterminate at n = 127**: point estimates are small and positive at short timeouts (+$3.97 at T=5, +$4.66 at T=30, −$3.28 at T=120, per contract-entry) but the chase-drift variance that G1's spread proxy explicitly does not cover makes the CIs ±$10–27 wide.

## Headline table (accounting A — CHASE, powered primary; strict-through fills; δ = 250 ms)

All figures **$/ctr-entry, BASIS SPREAD_ONLY (entry side, vs baseline first-valid-ask fill), EVIDENCE MEASURED (tick replay)**. N = 127 measurable entry events / 145 contract-entries / 53 sessions; contract-weighted; session-level block bootstrap (B = 10,000, shared resample); Bonferroni α = 0.05/3.

| T | fill % | mean Δ | CI-Bonferroni | CI-95 | sav\|fill | chase cost\|unfilled |
|---|---|---|---|---|---|---|
| 5 s | 73.8 % | **+3.97** | [−7.32, +13.23] | [−4.90, +11.86] | +24.35 | 53.42 |
| 30 s | 87.6 % | **+4.66** | [−12.57, +19.07] | [−9.21, +16.92] | +25.59 | 143.06 |
| 120 s | 91.0 % | **−3.28** | [−36.57, +20.38] | [−29.73, +17.54] | +25.53 | 295.77 |

+1-tick stress (G3, barrier B−1 tick on both clauses): fill 67.6/83.4/88.3 %, means +0.48/+1.34/−8.38 — all G3 FAIL. At-touch upper-bound diagnostic: +8.10/+12.79/+3.93 (T=30 CI-95 lower +2.37 — suggestive but a diagnostic only, not the primary). Latency sensitivity (100 ms / 1 s) leaves T=5/30 signs unchanged; T=120 flips sign across latencies (noise, consistent with its CI). Time-to-fill (strict): p50 0.9 s, p90 11.4 s.

## What was measured, and the facts worth keeping

1. **The join-bid policy DOES engage the book at P1's entry instants** — 74 % filled inside 5 seconds, median fill 0.9 s. The prior "momentum entries run away from a passive bid" is wrong at second scale; KILL-2's premise did not survive contact.
2. **Adverse selection behaves exactly as the mechanism prior said, and grows with T**: incumbent all-in P&L of unfilled vs filled entries = −$31 vs +$86 (T=5), +$58 vs +$55 (T=30), **+$339 vs +$28 (T=120)** — at long timeouts the entries you fail to improve are precisely the winners, and the chase pays $296/ctr average drift. Short timeouts cap that; T=120 is the wrong shape.
3. **Anchor quoted spread at P1's entry instants: mean $26.26/ctr (5.25 ticks), SD $13.45** — wider than the RTH-median 3 ticks and the all-hours 4 ticks, consistent with P1's 63 % non-RTH entry share and bar-open timing. The realistic per-entry savings pool is ~$25, not $15.

## Accounting B (CANCEL) — UNPOWERED-BY-DESIGN, components only

Adjudicated at G1 **before any outcome was read**: MDE_B = $338.70/ctr-entry at 80 % power vs a $20 ceiling (16.9×) ⇒ components-only, can neither adopt nor kill. Components: savings|fill $24–26 [SPREAD_ONLY, MEASURED]; unfilled entries' incumbent all-in P&L −$31/+$58/+$339 per ctr at T=5/30/120 [ALL_IN approx = commission-in + $14.44/ctrRT modelled spread, DISCOVERY_CONSUMED]. No net headline is quoted.

## Governance record (the one failed gate)

- **G0b-i FAIL (recorded): the GOVERNANCE_PRECHECK premise "pool ∩ extracted = 0 across all four registers" is FALSE for the W5 register.** Mechanical re-intersection of the 104-session union against `confirmation_pool_168_dates.txt` found **21 members** (other 3 registers: 0), decomposing exactly as the BBO_GOVERNANCE_MEMO footnote implies: 8 batch-1-consumed + 13 W5 protected members whose tick content was later materialized by MS01/ESNQ dev. **Remediation (conservative, applied before any tick file was opened): all 21 excluded; replay set = 83 strictly-clean sessions; final replay-set ∩ (all four registers) = ∅ re-asserted (G0b-ii PASS); 2026-05-05 absent (G0b-iii PASS).** No pool member's price content was read by this run. Cost: 40 of 168 in-union entry events excluded (~24 % of n).
- G0c bench parity: xinst_bench reproduced P1/PCT at **0.0000 % on all 5 committed metrics** before any timestamp was emitted (weekly 1393.573663, maxDD 22930.665853, t 4.163612, trades 2401, rate 14.436483).
- Seals: 1-min substrate max session 2026-07-31, 0 bars dropped; every tick file load-time asserted < 2026-08-01. Censoring: 1 of 128 entries unmeasurable (NO_VALID_ANCHOR_BBO; incumbent P&L +$3,526/ctr — censused, excluded symmetrically). Crossed-BBO instants at anchors: 0. G4 semantic identity recomputed independently from per_entry.csv: max |diff| 1.6e-14. G6: 53 sessions tagged (31 BURNED-WINDOW, 22 DISCOVERY-CONSUMED); substrate mix of the 83-session set v2 45 / ESNQ 32 / v1 6.

## Disclosed interpretation choices (none decision-relevant)

1. **+1-tick stress wording**: DESIGN §2's two phrases ("strict-through shifted one tick" vs "fill requires a print ≤ B − 1 tick") diverge on the tick grid. Implemented the **more conservative barrier-shift on both clauses** (trade < B−1tk or ask ≤ B−1tk) as the G3 primary and printed the literal reading as a sensitivity — both fail G3 at every T, so the choice decides nothing.
2. **Chase instant**: "first valid ask after anchor+T" implemented as the prevailing valid quote at/after anchor+T — the same standing-quote convention as the baseline's "at/after anchor".
3. Optional minute-BBO cross-check surface: not used (optional in the pre-check; avoids the 5 exposed pool dates entirely).

## Why NULL and what would move it

The G1 caveat printed in advance is the whole story: the spread-distribution proxy gives MDE_A = $3.86, but realized CI half-widths are $10–27 because unfilled entries' chase drift ($53–296/ctr on 9–26 % of entries) dominates the variance. A decision at the observed effect size (~+$4/ctr ≈ $40/wk ≈ 3 % of P1 net — point-estimate arithmetic, NOT a claim) needs several-fold more entries; the full 168-entry union would NOT have sufficed either, so this is not a pool-exclusion artifact. Honest paths, all owner-gated: (a) more sessions (frozen-pool spend under the pools' own protocols, or provider-side history), (b) depth/queue data (Databento MBO) to replace the strict/at-touch bracket with a point estimate, (c) a forward shadow measurement. **No FAILURE_MEMORY closure is recorded — neither kill fired.** No live change, no sizing change, no promotion; this run prices execution and is never alpha evidence.

## Artifacts (on disk, program-written)

`out/gate_table.txt` (program-printed GATE/SPEC/OBSERVED/PASS-FAIL), `out/replay_table.csv`, `out/per_entry.csv`, `out/fill_curves.csv`, `out/censoring_census.csv`, `out/censoring_by_substrate.csv`, `out/session_evidence_tags.csv`, `out/mde_barrier.txt` (written before outcomes), `out/run_log.txt`, `src/xpass_replay.py`.