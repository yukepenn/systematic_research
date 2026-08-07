# Registry gap — disclosure and partial reconstruction

_2026-08-07. Written as part of the post-campaign integrity audit. This documents a governance
failure in my own process. It is not a result._

## What went wrong

The campaign constitution requires that every run get an immutable directory under
`runs/<run_id>/` with `spec.yaml` **written and committed before results are read**, and that every
tested configuration get a sequence number in `tested_configs.csv`.

Both conventions held through Wave 1b and then **lapsed**:

- `tested_configs.csv` stops at **seq 90** (Wave 1b, commit `9a2fff3`).
- `experiments.yaml` holds **2** entries (PARITY, SW00) of roughly twelve.
- `runs/` stops at **`RE01_open_parity`** (commit `e866c77`).
- Waves 1c, 2 and 3 instead wrote ~296 execution-ledger CSVs directly under `research/`.

## Why this matters

The raw evidence survives — every ledger is committed, and every published figure in this
repository was regenerated from those ledgers during the audit. Reproducibility is intact.

What is **not** intact is the *preregistration guarantee*. Because no spec was committed before
each Wave-1c/2/3 result was read, there is no record proving that the pass/fail criteria were
fixed in advance of seeing the numbers. That guarantee is the campaign's primary structural defence
against post-hoc metric selection, and for those three waves it rests on researcher discipline
rather than on the record.

**A reviewer is entitled to discount Waves 1c–3 accordingly, and should.**

Partial mitigation, worth stating: the two most consequential Wave-3 statistical decisions *were*
preregistered in committed documents before their figures existed — `TRIAL_ACCOUNTING_RULE.md`
(written before any DSR was recomputed under it, including its own expected negative conclusion)
and the H-014 pass/fail criteria. The red-team review was also run by independent agents against
results they had not produced. Those three are on the record; the rest of Waves 1c–3 are not.

## What the reconstruction does and does not do

`tested_configs_backfill.csv` enumerates all 296 surviving ledgers with their parameters, wave,
instrument, cost model and evidence path, assigned sequence numbers 91–229.

It **restores auditability of what was run.** It **does not** restore preregistration, and every
row is flagged `reconstructed=yes` so it can never be mistaken for a contemporaneous record.

## The trial count, honestly bracketed

Rule R1 counts a configuration whose daily P&L vector was computed and inspected. Re-running the
same parameter set at a different slippage assumption is a cost-stress of one trial, not a new
trial; parity gates are not trials at all.

| basis | count |
|---|--:|
| Wave 1 + 1b, contemporaneously registered | 90 |
| Waves 1c–3, distinct parameter sets | 139 |
| **campaign total, R1 basis** | **229** |
| campaign upper bound, counting every ledger including slip re-runs | 383 |
| *previously asserted in campaign documents* | *≈316* |

The asserted ≈316 sits inside the honest bracket, so no published figure was inflated by an
undercount. It was, however, an assertion rather than a count, and it is now checkable.

**This changes nothing downstream.** The R6 Harvey–Liu haircut used N_raw = 316; at either end of
the 229–383 bracket the haircut Sharpe remains **0.000**, and the deflated Sharpe under the
preregistered rule uses `N_eff` (participation ratio ≈ 7), not the raw count, so it is unaffected.

## Rule for any resumed work

Do not add a single new configuration until the `runs/<run_id>/spec.yaml` convention is restored
and demonstrated on one throwaway run. The convention exists because researcher discipline is
exactly what fails silently under time pressure — as it did here.
