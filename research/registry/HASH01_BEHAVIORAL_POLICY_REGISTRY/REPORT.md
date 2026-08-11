# HASH01 — Behavioral Policy Registry: Reconciliation + Representational-Duplication Check

**Status:** bookkeeping / audit task only (campaign directive sec22–27). **Not alpha research.**
**Does not modify** `tested_configs.csv`, `tested_configs_backfill.csv`, or `REGISTRY_GAP_NOTE.md`.

## 0. What this task is and is not

Per sec25/sec66 of the campaign directive: **"Statistical tools cannot restore lost
preregistration."** This report does two separate things, neither of which changes that fact:

1. **Reconciliation** (`src/01_reconcile.py`) — an honest count of how many trial-slots exist
   across the campaign's three separate registries *today*, whether they double-count each other,
   and whether the post-gap-note work restored the preregistration discipline the gap note called
   for.
2. **Behavioral policy-hash dedup** (`src/02_policy_hash_dedup.py`) — for **one** family of
   parameter-sweep trials (the VolMult-grid family), a check of whether numerically distinct raw
   configurations collapse to the same discrete trading behavior ("representational duplication")
   or are genuinely behaviorally distinct.

**Neither activity shrinks the campaign's selection-bias burden, resolves the registry gap, or
reconstructs lost preregistration.** The dedup pass in particular covers **7 raw configurations
out of a registry that today totals somewhere between 499 and 653 trial-slots** — well under 2%
of the total. No number in Part 2 of this report should be read as applying to the registry as a
whole. This scoping is restated at every point in this report where a specific count is given.

---

## Part 1 — Registry reconciliation (today, 2026-08-10)

### 1.1 Three separate registries, zero conflation

| Registry | Rows | Seq coverage | Governance status |
|---|---|---|---|
| `research/registry/tested_configs.csv` | 227 data rows (seq expands to 270 distinct trial-slots for seq≥230) | seq {0,1} infra + 2–90 (Wave1/1b) + clean gap 91–229 + 230–498 (post-gap-note) | seq 0–90 contemporaneous; seq 230–498 mixed prereg (see §1.3) |
| `research/registry/tested_configs_backfill.csv` | 296 data rows | seq 91–229 exactly (139 distinct seq, ALL `reconstructed=yes`) | reconstructed, not contemporaneous — per `REGISTRY_GAP_NOTE.md`, does not restore preregistration |
| `research/system_master/TESTING_LEDGER.csv` | 59 families (family-level unit of account, no seq numbers) | 2026-08-09/10 work, never logged into either CSV above | reported separately below — see §1.2 |

**Headline finding: the seq overlap between `tested_configs.csv` and `tested_configs_backfill.csv`
is EMPTY**, verified by full expansion of every seq / seq-range token in both files.
`tested_configs.csv` holds `{0,1}` infra placeholders, then 2–90 (Wave 1/1b, one seq per trial),
then a clean gap at 91–229 (zero rows), then resumes at 230 through 498 (with skips at
392/407–409 and letter-suffixed sub-ids `392a`/`392b`/`423b`/`437b`/`437c`).
`tested_configs_backfill.csv` fills exactly and only that 91–229 gap. Zero double-counting
risk between the two CSVs.

### 1.2 A third registry, confirmed non-overlapping

`research/system_master/TESTING_LEDGER.csv` is a wholly separate registry — zero name overlap
(by exhaustive grep) with either CSV above — covering 59 additional families (2026-08-09/10
work) using a fundamentally different unit of account: `n_candidate_constructions` /
`n_parameter_cells` (family-level self-reported summary stats), not per-config seq rows. Summed
across those 59 families: 57 candidate constructions / 49 parameter cells. This is reported
separately, not folded into the row-level trial-count bound below, because it cannot be
reconciled to the `tested_configs.csv` "one seq = one trial" rule without first being
re-expressed at row level — a task this report does not attempt.

### 1.3 Trial-count bounds, extended to today

The 2026-08-07 gap note gave an honest bracket of 229–383 (R1 basis: 90 contemporaneous +
139 reconstructed-distinct-param, up to every ledger row including reruns). That bracket is
entirely superseded, not because it was wrong, but because 270 additional trial-slots have
been logged into `tested_configs.csv` since it was written (seq 230–498, post-gap-note), none
of which the gap note's own bracket could have covered.

Extending the gap note's own methodology (lower = contemporaneous + reconstructed-distinct-param;
upper = every ledger row minus non-trial parity gates) to include that post-gap-note bucket:

| Component | Count |
|---|---|
| Wave 1/1b contemporaneous (seq 0–90) | 90 |
| Backfill, distinct-param R1 basis (seq 91–229) | 139 |
| Backfill, all rows minus parity gates (upper-bound basis) | 293 |
| Post-gap-note `tested_configs.csv` (seq 230–498, distinct seq/letter-id slots) | 270 |
| Lower bound, TODAY | 90 + 139 + 270 = 499 |
| Upper bound, TODAY | 90 + 293 + 270 = 653 |
| (previously published 2026-08-07 bracket, for reference — now superseded) | (229–383) |

`TESTING_LEDGER.csv`'s 59 families / 57 constructions / 49 parameter cells are not folded
into either bound above (see §1.2) — they would need their own row-level ledger before combining
with the `tested_configs.csv` R1 rule.

### 1.4 Preregistration discipline for post-gap-note work: MIXED, not a clean restoration

Git-history analysis of all 187 `runs/<id>/` directories (comparing the commit that first adds
`spec.yaml` against the commit that first adds any other file in the same directory):

| Category | Count | Meaning |
|---|---|---|
| `SPEC_BEFORE_RESULTS_genuine_prereg` | 109 | spec.yaml committed in a separate, earlier commit — genuine, git-verifiable preregistration |
| `SAME_COMMIT_spec_and_results` | 44 | spec.yaml and results land in one atomic commit — not independently verifiable |
| `NO_SPEC_EVER` | 30 | no spec.yaml ever committed |
| `SPEC_ONLY_NO_RESULTS_DETECTED` | 4 | spec.yaml committed, no results file detected in that directory |

Finding: the 2026-08-07/08 recovery period genuinely does NOT inherit the Wave 1c–3
governance-failure caveat. B01C_ORB_FAIL, PORT01_SWEEPS, DM01, and SM03 through SM14 all show
explicit "preregister X before any result read" commits strictly preceding their "X: result"
commits — the campaign did honor its own remediation rule for that stretch (spanning
2026-08-06 through 2026-08-09).

But the 2026-08-09/10 wave does carry a caveat of its own — better documented and
contemporaneously logged than Waves 1c–3 (no after-the-fact reconstruction was needed;
`REPORT.md`/`out/` were written the same day as the work), but not git-verifiably
preregistered. Concentrated almost entirely in that wave: AUCTION01/02/03/04, ADD01, FLOW01,
VAR01, REL01, GAMMA00, O2, PRICE01, COMBO01, and every
`research/system_master/{GRID01,GRID02,PERT01,EQV01,EQV02,EQV03,PLACEBO01}/` directory (which sit
outside `runs/` entirely and show `src`+`out`+`REPORT.md` landing in one atomic commit). Notably,
this includes the GRID01/GRID02 substrate that Part 2 of this report reuses — that caveat is
carried forward unchanged into Part 2, not resolved by it.

### 1.5 Distinct-experiment classification: 178 distinct labels, four categories

Across all three registries, 178 distinct experiment/family values were classified:

| Category | Count | Definition |
|---|---|---|
| (a) Parameter sweep, same finite controller | 18 | genuine dedup candidates — the category Part 2 investigates |
| (b) Distinct architecture/mechanism/data-source decision | 61 | never dedup candidates — a genuinely new decision, not a numeric setting |
| (N) Not an architecture-search trial | 91 | infra / diagnostic / audit / validation / governance — a category the (a)/(b) dichotomy does not cover and should not be forced into either |
| (U) Mixed / unclassifiable as filed | 8 | the registry's own single experiment label bundles rows from more than one category above; would need sub-splitting before any dedup pass could safely apply |

Full row-level detail: `out/reconciliation.csv` / `out/reconciliation.json`
(`q4_experiment_classification.rows`).

The 18 "(a)" labels are the universe Part 2 draws from — not all 18 were processed (see §2.1
for why only one was).

---

## Part 2 — Behavioral policy-hash deduplication: the VolMult-grid family

### 2.1 Scope: 1 of 18 flagged sweep labels, disclosed reason

Of the 18 labels flagged in §1.5 as pure numeric-parameter sweeps of one finite controller, this
task processed exactly one family: the VolMult-grid family, comprising

- `GRID01_SOLAR_RESOLUTION_CONVERGENCE` (grid density: G7 / G13 / G25 / G49 — 4 raw configs)
- `GRID02_ENDPOINT_PERTURBATION` (grid endpoint: `endpoint_5_29` / `endpoint_6_30` /
  `endpoint_7_31` — 3 raw configs)

Why only this one: it is the only one of the 18 labels that (a) varies the literal VolMult
(`vms`) axis, and (b) already has a self-checked, re-executable Python substrate
(`research/system_master/GRID01_SOLAR_RESOLUTION_CONVERGENCE/src/grid_core.py`) this session could
reuse verbatim (`build_pend` / `member_states` / `member_trades` / `sm.sigma_series`, unmodified)
without reimplementing or re-deriving anything. The other 16 flagged labels use structurally
different, non-interchangeable finite controllers and were deliberately not folded into this
hash space:

- vendor NT8 RKReplica TM/SM/Slowdown/WWS grids: `W1_S1`, `W1_S3`, `W1_S2`, `W1b`, `W1C`
- the SMV2 python-decoder family's own numeric ladders: `SW01c`, `DM01`, `SMV2B`, `SMV2C`,
  `SMV2E-ext`, `SMV2H2`, `SMV2S`, `SMV2AA`, `SMV2AE`, `SMV2Z`
- `PERT01_STRUCTURAL_INVARIANCE`'s own 3-axis (VolPeriod/BAND_DAYS/TiltSma) one-at-a-time
  perturbation, on its own standalone substrate

Folding non-interchangeable controllers into one hash space would manufacture false equivalence —
exactly what sec25/sec66 warns against. This is a disclosed scope decision, not a silent
extrapolation to "the whole registry."

Neither `GRID01` nor `GRID02` is itself a seq row in `tested_configs.csv` or
`tested_configs_backfill.csv` (confirmed by grep, zero matches) — both sit in the post-gap-note,
same-commit (non-git-verifiably-preregistered) bucket flagged in §1.4. That caveat is
unchanged, not resolved, by this dedup pass.

### 2.2 Methodology (four levels, all thresholds disclosed before computation)

| Level | What is hashed | Window |
|---|---|---|
| 1 — raw parameter identity | the literal `vms` tuple | n/a (already known, read from the scripts' own `GRIDS` dicts) |
| 2 — finite-state policy identity | SHA256 of discrete `(T, ProductA bar_pos, ProductB bar_pos)` integer arrays | CLAUDE.md canonical window, 2023-01-01 → 2025-02-02 |
| 3 — full-history target-vector identity | same triple, SHA256'd | full loaded history, every bar through 2026-07-31 |
| 4 — full-history P&L-vector identity | SHA256 of the exact daily P&L array per product (ticks=1, canonical commission) | full history |

Where Level 4 hashes differ, pairwise Pearson correlation of the daily P&L vectors is reported
against a threshold fixed in the script before any result was computed: r ≥ 0.99 = "near-
identity." An eigenvalue participation ratio (PR) over the 7×7 full-history daily-P&L correlation
matrix is also reported, per product, as a continuous companion statistic — not a replacement
trial count.

### 2.3 Results

N_raw = 7 raw configurations processed (GRID01's G7/G13/G25/G49 + GRID02's
endpoint_5_29/endpoint_6_30/endpoint_7_31).

| Level | Unique count | Out of |
|---|---|---|
| N_raw (raw parameter tuples) | 6 unique | 7 |
| N_unique_finite_policy (Level 2 — canonical-window discrete policy) | 6 unique | 7 |
| N_unique_target_vector (Level 3 — full-history discrete target vector) | 6 unique | 7 |
| N_unique_pnl_vector (Level 4 — full-history P&L hash, Product A / Product B / combined) | 6 / 6 / 6 unique | 7 |

Exactly one pair is a genuine representational duplicate: GRID02's `endpoint_6_30` is the
byte-identical raw `vms` tuple `[6, 8, 10, ..., 30]` as GRID01's `G13` incumbent — same numbers,
tested under two different experiment labels/directories. That pair collapses to an exact
SHA256 match at every level (1 through 4, both products), as expected since they are literally
the same input. All other 5 raw configs remain behaviorally distinct at every hash level — no
two of the remaining 6 configurations produce an identical discrete position sequence or an
identical daily P&L array, despite being drawn from a deliberately dense/narrow VolMult-scale
neighborhood (7–49 members spanning `[5, 31]`). SHA256 hashing finds no additional hidden
duplicates beyond the one literal repeat.

### 2.4 The complementary near-identity view

The exact-hash result above is one story; the continuous correlation view tells a different,
complementary one. 14 of the 21 raw pairs clear r ≥ 0.99 on at least one product's
full-history daily P&L, and the participation ratio over the 7×7 correlation matrix is:

- Product A: PR = 1.0151 (out of a maximum of 7)
- Product B: PR = 1.0699 (out of a maximum of 7)

I.e. this family's 7 raw configurations behave, P&L-wise, as barely more than one effective
independent dimension. This is not a hidden-duplication finding — it is the expected signature
of a deliberate density/robustness probe around one incumbent policy (GRID01/GRID02's own
stated purpose was diagnostic convergence-checking, explicitly zero-alpha-budget). The one-only
exact-hash duplicate (§2.3) and the near-total P&L correlation here are two different measurements
of the same underlying fact: this family was never exploring 7 meaningfully different strategies.

Net reading: exact-hash dedup finds only the trivial literal-repeat duplicate (6/7 unique
raw); the continuous PR view shows the family's effective footprint was closer to 1 dimension by
construction — not by concealed duplication. PR is reported alongside, not instead of, the
raw/behavioral counts, and must not be read as "the campaign really only ran ~1 trial here."

---

## Part 3 — Explicit scope statement (sec25/sec66 compliance)

Restated plainly, because this is the point of the task:

1. Behavioral deduplication is supplementary. It distinguishes representational duplication
   (many numeric settings collapsing to the same discrete behavior) from genuine
   architecture-search decisions — nothing more.
2. It does not rewrite `REGISTRY_GAP_NOTE.md`. That document is unmodified and remains the
   authoritative record of the Wave 1c–3 preregistration failure.
3. It does not reconstruct lost preregistration. No amount of post-hoc hashing turns a
   reconstructed or same-commit trial into a contemporaneously preregistered one. Statistical
   tools cannot restore lost preregistration (sec25/sec66, verbatim).
4. It does not reduce selection bias to zero, or by any specific quantified amount for the
   registry as a whole. The Harvey–Liu-style haircut referenced in the gap note is unaffected by
   anything in this report.
5. Coverage is narrow and must not be extrapolated. The dedup pass in Part 2 covers 7 raw
   configurations — under 1.4% of the lower-bound 499-trial-slot registry, and under
   1.1% of the upper-bound 653-trial-slot registry, as reconciled in Part 1. No "N_unique"
   figure in this report should ever be quoted as if it describes the full ~499–653-trial-slot
   registry; it describes only the VolMult-grid family.
6. The 16 other flagged parameter-sweep labels (§2.1) remain unprocessed. They are not
   asserted to dedup the same way, or differently — they are simply out of scope for this task's
   available substrate, and that is disclosed rather than silently generalized from the one
   family that was processed.

---

## Output files

- `src/01_reconcile.py` — registry reconciliation (seq-overlap check, trial-count bounds,
  preregistration git-history audit, experiment classification)
- `src/02_policy_hash_dedup.py` — behavioral policy-hash dedup for the VolMult-grid family
  (reuses `grid_core.py`'s `build_pend`/`member_states`/`member_trades` verbatim)
- `out/reconciliation.json`, `out/reconciliation.csv` — full reconciliation detail (per-directory
  preregistration audit, per-experiment classification rows)
- `out/policy_hash_results.json`, `out/policy_hash_results.csv` — full dedup detail (per-config
  hashes at all 4 levels, pairwise correlation matrices, participation-ratio eigenvalues)
- `REPORT.md` — this file
