# UNIVERSE_ADJUDICATION — which Solar event universe can reproduce the visible days

Run `runs/OTR_R11_INVERSE/` (spec + amendments 1–3 preregistered before each readout).
Directive v4.0 sections 7–10. Raw matrix: `FEASIBLE_PATH_SUMMARY.csv`,
invariants: `EVENT_INVARIANTS.csv`, log: `runs/OTR_R11_INVERSE/out/r11b_log.txt`.

Design: 6 event universes × 2 exit-comparison rules × 11 visible Jan-2023 days = 132 cells.
Each cell enumerates **all** single-position trade paths satisfying **nine exact
constraints simultaneously** — trade count, winner count, loser count, gross profit, gross
loss, largest winner, largest loser, **sum MAE**, **sum MFE** — with cropped screenshot cells
recovered on the $5-tick lattice and never fabricated. Selection is by FEASIBILITY only;
no P&L objective exists anywhere in this run.

## Result matrix (days explained / 11)

| exit rule | U1 T1 | U2 T1+T2E | U3 T1+T2L | U4 T1+T3 | U5 T1+T2E+T3 | U6 T1+T2L+T3 |
|---|---|---|---|---|---|---|
| **STRICT** | **8** | 8 | 8 | 8 | 8 | 8 |
| INCLUSIVE | 5 | 5 | 5 | 5 | 5 | 5 |

Every feasible cell returns **exactly one** path. Not "a path that fits" — the *only* path
that fits, cent-exact on economics and tick-exact on excursions.

## Finding 1 — the exit comparison is STRICT

Changing `close <= TrailingStop` to `close < TrailingStop` moves 5/11 → **8/11**, gaining
2023-01-06, 2023-01-13 and 2023-01-16.

This was **predicted before it was tested** (amendment_1) from two independent days whose
only defect was a single trade's exit price, with sum-MAE and sum-MFE already exact — which
proved the *entries* were already right:

| day | our exit | trader's implied exit | our next entry |
|---|---|---|---|
| 2023-01-06 | L 15:52 @ 14264.25 | 14260.75 | S 15:56 @ **14260.75** |
| 2023-01-16 | S 06:16 @ 14704.50 | 14704.00 | L 06:21 @ **14704.00** |

He reversed where we exited early. Structurally, given the Solar ladder recurrence, for a
long in an uptrend `close <= TS` can occur **only** on a flip bar or on a bar where
`close == anchor − S` exactly. So STRICT ≡ **"exit only on a genuine trend flip"**, and the
two rules differ only on exact-touch bars — which is why no aggregate statistic could ever
have separated them and why cent-level daily labels were required.

> Caveat recorded honestly: at the **master-window** level (R13,
> `out/r13_master_exitrule.csv`) the preregistered prediction **FAILED** — STRICT moves
> trade count from +5.2 % to +7.8 % and hold from +1.4 % to +2.8 % *away* from the
> EARLY_LONG target. That comparison is confounded: the D-gate constants were fitted under
> INCLUSIVE, and R14 shows they are partly falsified. Per directive section 48
> (CENT-LEVEL TRADE MATCH > PNL SIMILARITY) the day-level evidence dominates the
> approximate, screenshot-derived master aggregate — but the failure is on record.

## Finding 2 — T2 and T3 entries are NOT USED by the early flagship

Every feasible day in **every** universe solves with **`min_extra = 0`**: the unique path
never contains a T2 (pullback) or T3 (strengthening) entry, however many are made available,
under either PullbackEarly setting. Adding those signal classes:

- never produces a *new* explanation for a solvable day, and
- never rescues an unsolvable one.

This is a direct, non-circular refutation of "his early build has an active pullback entry
layer". Combined with R12 — which showed the A3/A4/A5 retune moves T3 by +38.6 % and T2 by
only +3.0 %, while all three are *exactly* invisible to T1 (Jaccard 1.000000) — the standing
story ("A3-A5 changed, T1 can't see it, therefore a pullback entry layer exists") loses its
entry-layer conclusion entirely.

**Scope limit, stated explicitly:** the solvable days are all Jan-2023. This establishes that
the **2023 build enters on T1 only**. It says nothing directly about the late-2025 build, in
which the retune actually occurred. The two are separate objects and must not be blended.

## Finding 3 — three days are unexplained by any tested mechanism

2023-01-04, 2023-01-12 and 2023-01-17 are IMPOSSIBLE in every universe under both exit
rules, with the search running to **exhaustion** (not merely to the node budget) in the
completed cells. Mechanisms tested and eliminated:

| mechanism | test | verdict |
|---|---|---|
| T2 entries (Early and Late) | U2, U3, U5, U6 with up to 3 extra entries | **does not rescue** |
| T3 entries | U4, U5, U6 | **does not rescue** |
| Fixed intrabar initial stop | R15: 70, 72.5, 75, 80, 85, 90, 100, 110, 125, 150, 175, 200 pts × both exit rules | **FALSIFIED** — 0 solutions in all 26 configurations |
| Contract / merge policy | analytic | **cannot be the cause**: a back-adjusted merge shifts all prices by a constant within Jan-2023 (no roll in the window), and P&L, MAE and MFE are all *differences*, so a constant offset cancels identically |

Localisation (R16, `out/r16_log.txt`), relaxing one constraint at a time:

- **2023-01-17: the trade COUNT itself is unreachable.** The session admits at most 5 trades
  under T1; the report says 6. Achievable counts {2,3,4,5}.
- **2023-01-04 and 2023-01-12: the count is reachable** (14 ∈ {10…18}, 16 ∈ {12…17}) but
  *both* the economics and the excursion statistics fail independently — relaxing gross
  profit + gross loss + largest winner + largest loser still yields nothing, and so does
  relaxing MAE + MFE. The trade set is structurally wrong, not merely mispriced.

## Event invariants

For the 8 uniquely-solved days the labels are **INVARIANT_LABELS** (see
`../CAND2_REAUDIT.md`): 16 flat T1 decision points, of which 1 is platform warm-up
(`BarsRequiredToTrade = 20`, bar 10 of the backtest) and 15 are strategy decisions —
10 TAKE, 5 SKIP, no AMBIGUOUS entries, because each day's solution is unique.

They remain conditional on (universe = T1-only, exit rule = STRICT). They are **not**
observed original trade labels, and they replace — they do not vindicate — the retired R1e
"42/42 cent-exact ground-truth labels", whose removal-only formulation was structurally
incapable of explaining 2023-01-13 and 2023-01-17 in the first place.

## What this changes

| object | before | after |
|---|---|---|
| exit test | inclusive touch (inherited from campaign-1 V0) | **STRICT / flip-only** (8/11 vs 5/11) |
| T2/T3 entry layer in the 2023 build | assumed present | **ruled out** (min_extra = 0 everywhere) |
| early-era fixed stop | open | **FALSIFIED** over 70–200 pts |
| daily trade labels | R1e conditional latent labels | **unique-path invariant labels**, 15 of them |
| 2023-01-04 / 12 / 17 | assumed explicable | **UNEXPLAINED_BY_ANY_TESTED_MECHANISM** |
