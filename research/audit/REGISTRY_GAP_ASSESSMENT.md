# Registry gap — audit-grade reconciliation and consequences

_2026-08-07 · POST_CAMPAIGN_AUDIT_01 / AUDIT-01 · branch `post_campaign_audit`, parent commit
`b811a21` · campaign final HEAD `e5079e1`, campaign stop commit `0660f74`._

This document is the audit-grade counterpart to `research/registry/REGISTRY_GAP_NOTE.md`, which
discloses the governance failure. That note is not duplicated here; this document does what the
note could not: reconcile the four public trial counts computationally, quantify what the backfill
itself got wrong, and state exactly which statistical claims are weakened and by how much.
Companion machine-readable artifacts, generated with computed (not asserted) totals:

- `research/audit/reconstructed_trials.csv` — 412 normalized rows unifying both registry CSVs,
  with a computed summary block.
- `research/audit/candidate_lineage.json` — source, engine hash, members, window, costs, parent
  hypothesis and caveats for every finalist/reference.

---

## (a) What was contemporaneous, what was backfilled

| registry surface | contemporaneous through | backfilled 2026-08-07 |
|---|---|---|
| `registry/tested_configs.csv` | seq 1–90 + seq-0 machinery, 30 rows; last write `9a2fff3` 2026-08-06 21:43 | — (left untouched) |
| `runs/<run_id>/spec.yaml` convention | 36 campaign-era run dirs, ending `RE01_open_parity` (`e866c77` 2026-08-06 22:18) | 6 audit-era runs (AUDIT_GATE_R01/R02, AUDIT02_V3/V4_SWEEP and their _B supersessions) |
| `registry/experiments.yaml` | 2 entries (PARITY, SW00) | 8 entries, marked `preregistered: false/partial` |
| `registry/hypotheses.md` | append-only throughout; H-001…H-007 registered before results at commit granularity | H-008/H-011/H-012/H-013 entries landed with their verdicts |
| Waves 1c–3 evidence | — | 296 execution ledgers committed in the wave commits; `tested_configs_backfill.csv` (296 rows, seq 91–229) created at `80a1a31` 2026-08-07 07:47 |

The lapse window is exact and short: the entire Wave 1c → Wave 2 → Wave 3 program executed
between `562c426` (2026-08-06 23:36) and `0660f74` (2026-08-07 05:08) — roughly 5.5 hours in
which not one contemporaneous registry write occurred. Counts: **90** configurations
contemporaneously registered (Wave 1/1b and earlier phases), **139** reconstructed (Waves 1c–3),
**296** surviving ledgers enumerated, **3** of them unnumbered parity gates.

Hypothesis-timing from git (an AUDIT-01 work item) — the lapse was narrower than "Waves 1c–3 were
not preregistered" suggests, and also narrower than a reader of the backfill alone would infer:

| hypothesis | registered (commit) | results (commit) | commit-verifiable preregistration |
|---|---|---|---|
| H-001…H-005 | `73aa572` 20:32 / `1593ed4` 20:57 / `1b14f9c` 21:23 (08-06) | `5f9cf7e` / `25e0923` / `b9284ff` | **yes**, spec files + registry |
| H-006, H-007 | `fd4cf4b` 08-06 22:19 | `9097c04` 08-07 00:08 | **yes**, hypothesis + falsification criteria, 1h49m lead |
| H-008, H-011, H-012, H-013 | `9097c04` 08-07 00:08 | same commit | **no** |
| H-014 | criterion in `851cdef` 08-07 00:36 | `9bc3d9b` 08-07 05:01 | **criteria-level**, 4h25m lead (see (c)) |
| C2/C4/wavecond/ES | — | `9bc3d9b` / `fbe267b` | **no** |

## (b) Reconciliation of the four public counts

| figure | what it denominates | basis | audit verdict |
|--:|---|---|---|
| **90** | Wave 1 + 1b configurations, seq 1–90 | contemporaneous registry | exact |
| **229** | campaign R1-basis distinct configurations = 90 + 139 | counted from committed ledgers (`tested_configs_backfill.csv`) | **reproduced exactly** by `reconstructed_trials.csv` (139 distinct seq 91–229, one `counts_as_trial=yes` row each, no gaps) — but see the strict recount below |
| **≈316** | running asserted total: ≈255 asserted through Wave 2 (the same 255 used as `n_trials` in the withdrawn DSR figures) + 61 counted in `WAVE3_report.md` §5 | assertion, never an enumeration | superseded; happens to sit inside every honest bracket |
| **383** | every seq-assigned engine ledger including slip/cost re-runs = 90 + 293 (296 backfill rows − 3 unnumbered parity gates) | counted | **reproduced exactly** |

**New audit finding — the backfill's own counting is internally inconsistent.** 126 backfill rows
carry the literal label `no (slip-N stress of seq X)` while differing from seq X's primary row in
a **non-slip** field. Five swept axes were collapsed to one trial each: H-014 (13 price-bp cells
→ 1), ES price-normalisation (13 → 1), H-007 (2 × 11 exit-multiplier cells → 2), H-012 (13
estimator-lag cells → 1), and H-008 mode-2 — the close-confirmed-HL family, a **published Pareto
finalist** — recorded as duplicates of the mode-1 seqs and contributing **zero** trials.
Identical-in-kind sweeps elsewhere (h006, esvol, fixedwide, combo, c2-adaptive) were counted
per-cell. The H-011 execution-mode variants (execmode 1/2) and the Wave-1c 16:30 timed-exit
variants are likewise distinct rules mislabeled as slip stress. Applied consistently, rule R1
gives:

| R1 applied | count |
|---|--:|
| as committed in the backfill | 229 |
| + 66 collapsed swept-parameter cells (h014 +12, esbp +12, h007 +20, h012 +12, h008am2 +10) | **295** |
| + 40 distinct exit-time / stop-execution-mode rule variants (w1c t163000 +20, h011 x1/x2 +20) | **335** |
| every seq-assigned ledger | 383 |

A related internal contradiction: `WAVE3_report.md` §5 counts H-014 as **13** trials; the backfill
counts it as **1**. The two committed records disagree. Neither is edited; the disagreement is
recorded here and enumerated row-by-row in `reconstructed_trials.csv`.

Downstream sensitivity, checked at every point of the bracket [229, 383]: the R6 Harvey–Liu
haircut Sharpe is 0.000 throughout, and DSR under the preregistered rule uses `N_eff`
(participation ratio ≈ 7), which does not depend on the raw count. **No published figure moves.**
The binding consequence is prospective: any future statement of "raw N" for this campaign must
quote the bracket 229–383 (best consistent point estimate 295–335), never a single number.

## (c) Which statistical claims are weakened, exactly

1. **PBO / "ensembles beat selection" (PBO 0.48–0.90, negative IS→OOS slopes).** The figures are
   reproducible from committed ledgers and stand *as computed*. What is lost is campaign-level
   **completeness**: without preregistration there is no committed enumeration proving that every
   evaluated configuration left a ledger — a config run, read, and discarded before the wave
   commit would be invisible. The claim is therefore downgraded from "campaign-complete" to
   "complete over the surviving committed evidence." The git record (all 296 ledgers landed inside
   the wave commits, hours apart) makes wholesale omission unlikely; it cannot prove absence.

2. **DSR / deflation trial lineage.** The raw trial count is a bracket, not a number (above), and
   the backfill's within-family counting is inconsistent. This does not rescue or further damage
   any deflation figure: all campaign DSRs were already withdrawn by the red team (`851cdef`), and
   the preregistered replacement rule deliberately keys on `N_eff`, not raw N. The conclusion
   "deflation adjudicates nothing here in either direction" is **robust to the registry gap**.
   What is *not* supportable is any future claim requiring an exact raw N or a complete trial
   lineage at run granularity for Waves 1c–3.

3. **H-014 "PASS, p = 0.009, preregistered" — the careful decomposition.** Per
   `REGISTRY_GAP_NOTE.md`, the H-014 criteria were preregistered; that is true and commit-verifiable,
   but it is criteria-level, not run-level, and the distinction matters:
   - **Commit-verifiable preregistration:** `851cdef` (2026-08-07 00:36) committed the decisive
     control and its falsification logic — "run a price-proportional threshold family through NT8.
     If it matches the volatility-proportional one … H-006's mechanism claim dies" — 4h25m before
     the results commit `9bc3d9b` (05:01). The direction of the test and what would kill the
     hypothesis were on the record before the figures existed.
   - **Not preregistered:** run-level specs (no `runs/<id>/spec.yaml` for any of the 13 cells),
     the exact grid (bp 8–56 step 4), the test statistic (paired circular block bootstrap,
     L = 20, B = 10,000) and the numeric significance bar. These first appear in the same commit
     as the result.
   - **Trial accounting:** the backfill counts the 13 H-014 cells as one trial; the wave report
     counts 13 (see (b)).
   - **`TRIAL_ACCOUNTING_RULE.md`:** its full text landed in `9bc3d9b` *together with* the Wave-3
     figures, so the commit record alone cannot prove text-before-figures. What is
     commit-verifiable: `851cdef` mandated the rule's content in advance ("preregister the
     trial-counting rule (clusters-as-trials with `N_eff` from the trial correlation matrix), then
     recompute every DSR"), and the rule's self-declared expected-negative outcome was honored
     rather than negotiated. Its preregistration status rests partly on the document's own dating.

   Net position: H-014 keeps the property "criterion fixed in advance of the result, on the
   committed record" — which is more than any other Wave-1c–3 result can claim — and does **not**
   carry machine-verifiable spec-before-result preregistration at run granularity. The label
   "the campaign's only clean significance result" survives with exactly that qualifier.

4. **Everything else in Waves 1c–3** (Wave-1c plateau confirmations, H-006 through H-013 verdicts,
   ES portability, C2/C4/wavecond rejections): reproducible from committed ledgers, criteria not
   provably fixed in advance (H-006/H-007 hypotheses excepted, per the (a) table). A reviewer is
   entitled to discount accordingly — `REGISTRY_GAP_NOTE.md` says this and it stands. Note the
   asymmetry in what that discount can do: nearly all of these were *negative* verdicts
   (falsifications), and post-hoc flexibility inflates positives, not negatives. The finding most
   exposed is the campaign's central positive structural claim, "ensemble beats selection"
   (item 1); the finalist recommendation R5 already rests on H-014 plus absolute-edge evidence,
   the strongest-preregistration items on the record.

## (d) What the audit-era registry event schema adds

`runs/AUDIT_GATE_R01/spec.yaml` is the new template — written and committed (`b811a21`) before
execution, and demonstrated six times (AUDIT_GATE_R01, AUDIT_GATE_R02, AUDIT02_V3_SWEEP,
AUDIT02_V4_SWEEP, and the _B supersession sweeps whose specs record their supersession rationale
before results were read). Fields the campaign-era SW00 specs did not carry, each closing a defect
this audit actually found:

| new field | defect it closes |
|---|---|
| `source_commit` + `strategy_source_sha256` | the R5 spec named `SolarWaveOpenV4`, a class never run (`ec5a359`); source not in repo until `4887c5f` |
| `engine_version` / engine fingerprint | engine drift indistinguishable from strategy change |
| `parameter_hash` | "same params" claims become checkable |
| inline `pass_criteria` / `reject_criteria` | criteria-level preregistration becomes run-level and machine-checkable |
| `counts_as_trial` declared at spec time | the (b) mislabeling class — trial accounting decided *before* the result exists, not reconstructed after |
| `research_family_budget`, `degrees_of_freedom`, `selection_relevance` | selection pressure stated ex ante, feeding R1/R3 without reconstruction |

## (e) The binding rule going forward

`REGISTRY_GAP_NOTE.md` closes with: no new configuration until the `runs/<run_id>/spec.yaml`
convention is restored and demonstrated on one throwaway run. That demonstration exists
(AUDIT_GATE_R01). The rule is now binding in this form:

1. **No engine run of any configuration without `runs/<run_id>/spec.yaml` committed before
   results are read.** No exceptions for gates, stresses, or "just checking" runs — those get
   specs with `counts_as_trial: no` declared up front.
2. The registry row (`tested_configs.csv` schema, `reconstructed=no`) is appended in the same
   commit as the spec, with the sequence number assigned then.
3. Sweeps enumerate their cells in the spec, so the R1 count of a sweep is fixed before any
   result exists.
4. `reconstructed=yes` rows are permanently second-class: usable for reproduction, never for a
   preregistration claim. `tested_configs_backfill.csv` is not edited — its defects are
   enumerated in `reconstructed_trials.csv` and adjudicated here.

Failure mode this guards against, named plainly: researcher discipline under time pressure — the
entire gap occurred inside one 5.5-hour window of a single day.
