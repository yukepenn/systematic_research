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

## [ADDENDUM 2026-08-10 — the same failure mode recurred, in a milder form, on 2026-08-09/10]

`research/registry/HASH01_BEHAVIORAL_POLICY_REGISTRY/REPORT.md`, auditing the registry as part of
a structural-invariance campaign, ran a git-history check across all `runs/<id>/` directories
(comparing the commit that first adds `spec.yaml` against the commit that first adds any other file
in the same directory) plus every `research/system_master/<id>/` directory created since. Result:
**109 directories genuinely show `spec.yaml` committed in an earlier, separate commit before
results** (2026-08-06 through 2026-08-09, including the immediate post-remediation window this
note's own rule produced — B01C_ORB_FAIL, PORT01_SWEEPS, DM01, SM03 through SM14 all show explicit
"preregister X" commits strictly preceding "X: result" commits). But **44 directories show
`spec.yaml` and results landing in the same commit**, and **30 never had a `spec.yaml` at all** —
concentrated almost entirely in the 2026-08-09/10 wave: `AUCTION01/02/03/04`, `ADD01`, `FLOW01`,
`VAR01`, `REL01`, `GAMMA00`, `O2`, `PRICE01`, `COMBO01`, and every `research/system_master/
{GRID01,GRID02,PERT01,EQV01,EQV02,EQV03,PLACEBO01,HASH01,SIMPLE01}/` directory (the last several —
all of this same day's structural-invariance work, including this HASH01 audit itself — bundle
`src`+`out`+`REPORT.md` into one atomic commit, same pattern this note originally flagged).

**This is not the same failure as the original one, and should not be read as identical.** The
2026-08-09/10 wave's specs were genuinely written and, in most cases, methodologically frozen
*before* their own results were interpreted (e.g. bounded M1–M5 slates declared before running;
`SIMPLE01`'s SPEC-agent role structurally cannot see performance data before writing its manifest,
enforced by which information reaches which subagent call, not by commit timing) — this is
contemporaneous, disclosed, machine-readable work, not after-the-fact reconstruction the way Waves
1c–3 were. But it shares the original defect's *auditability* gap: a same-commit `spec.yaml` is,
from git history alone, indistinguishable from a `spec.yaml` written to match an already-known
result. The convention this note established (spec committed **separately and first**) was not
followed for this wave, and "the methodology says it was blind" is not independently checkable the
way a git timestamp is.

**Going forward:** phases still open in the current structural-invariance campaign (EQV04 and
later) should commit their frozen spec/preregistration artifacts in a separate, first commit before
the commit containing results — closing this gap prospectively rather than attempting to rewrite
the history of what has already landed. No history rewrite is being performed for the 2026-08-09/10
wave's existing commits.
