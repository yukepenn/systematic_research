# O2_NUMERIC_PROVENANCE_AUDIT — REPORT

**Disposition: DOCUMENTATION AUDIT COMPLETE.** 3 canonical documents (4 distinct correction
sites) were found citing the old hand-arithmetic Product-A owner-utility figures
(J=+0.1241 mixture / J=−0.1259 Γ-minimax, and their rounded form +0.124/−0.126) as if they were
current `primary_objective_v2` module output, with no note that the real module output differs
materially. All 4 sites have been corrected in place with additive `[SUPERSEDED 2026-08-09: ...]`
annotations — **no original text was deleted or altered**; every fix only appends a note
immediately after the pre-existing figure, per the campaign's "do not rewrite history" discipline.
4 further hits of the same number were reviewed and correctly left untouched as properly-scoped
historical record. `research/system_master/RESEARCH_FRONTIER.md` — one of the directive's named
candidates — has zero hits and needed no action.

## Method

1. Repo-wide grep (unrestricted, all file types) for `0\.1241|0\.1259|\+0\.124|-0\.126|J=\+0\.12|J=-0\.13`
   found matches in ~150 files. Inspection showed almost all are **incidental digit-substring
   coincidences** inside raw backtest/feature-data CSVs and JSONs (`EntryEfficiency`,
   `TotalEfficiency`, LOYO year-by-year deltas, diagnostic confidence intervals, etc.) — unrelated
   to the owner-utility objective and not "documents" in the sense the directive means.
2. Restricting the same pattern set to `*.md`/`*.txt`/`*.yaml`/`*.yml` — the file classes the
   directive named — narrowed this to **9 files**, a tractable and precise candidate set.
3. A follow-up literal-phrase search for `"daily objective"` across the same file-type set was
   run to catch any citing document that used different rounding and so evaded the numeric
   patterns. It returned the same 4 files already identified — no document was missed.
4. Every one of the 9 numeric-pattern files, plus the directive's explicitly named candidates
   (`runs/W17_C4_COMPLIANCE/O1_OBJECTIVE.md`, `research/system_master/RESEARCH_FRONTIER.md`), was
   read in context to classify per the directive's four-way scheme.

**Reproduce:**
```bash
# Candidate file list (the pass this audit is based on):
rg -n "0\.1241|0\.1259|\+0\.124|-0\.126|J=\+0\.12|J=-0\.13|J = \+0\.12|J = -0\.13" \
   -g "*.md" -g "*.txt" -g "*.yaml" -g "*.yml" .

# Follow-up phrase check (confirms no rounding-variant document was missed):
rg -n "daily objective" -g "*.md" -g "*.txt" -g "*.yaml" -g "*.yml" .
```
Full spec: `runs/O2_NUMERIC_PROVENANCE_AUDIT/spec.yaml`.

## Classification table

| file | line/section | quoted number | classification | action taken |
|---|---|---|---|---|
| `runs/O2_OWNER_UTILITY_READJUDICATION/REPORT.md` | line 14, "Precondition (ii) satisfied" section | J=+0.1241 mixture / J=−0.1259 Γ-minimax (quoted for comparison, immediately followed by the real v2 output and an explicit "hand arithmetic" / "should not be cited" disclosure) | **OLD_HAND_ARITHMETIC** | none — this is the doc that discovered and correctly discloses the issue |
| `runs/O2_OWNER_UTILITY_READJUDICATION/REPORT.md` | line 16, same section | J=+0.0549 (mixture) / J=−0.2220 (Γ-minimax) | **CURRENT_CODE_OUTPUT** | none — correct; the figure all other docs should cite going forward |
| `runs/W17_C4_COMPLIANCE/O1_REPAIR_PREREGISTRATION.md` | lines 634-673, Table 1 / Table 2 / "Answers to the questions the task asks" worked example | +0.1241 (mixture, λ=1.368) / −0.1259 (Γ-minimax / `J_worst`) / per-method `J_m` breakdown | **OLD_HAND_ARITHMETIC** | none — this **is** the original worked example that produced the number; properly scoped, historical, not cited as current from here |
| `runs/W17_C4_COMPLIANCE/O1_BLIND_REVIEW_OUTCOME.md` | lines 8, 89-93, blind-review body | +0.0210→+0.1241; +0.124 (mixture) / −0.126 (Γ-minimax); daily +0.124 vs intraday −0.140 | **OLD_HAND_ARITHMETIC** | none — append-only dated (2026-08-09) historical review record, not a current-truth citation surface |
| `runs/W17_C4_COMPLIANCE/O1_OBJECTIVE.md` | lines 404-433, 617-628 (v1 per-method CE_g/P_ruin tables) | no combined J=+0.1241/−0.1259 figure present — only raw v1-era per-method components (λ=1.0) | **OLD_HAND_ARITHMETIC** (source data only) | none — correctly published raw v1 components; never itself asserts a current combined figure |
| `research/system_master/RESEARCH_FRONTIER.md` | n/a | no match for owner-utility / mixture / Γ-minimax / `J=` anywhere in the file | **N/A** | none — file does not discuss this topic |
| `research/system_master/CURRENT_TRUTH.md` | lines ~215-216 (pre-edit), "Wave-19 verdict" §7 (R3 blind aggregation review), plain prose, **not** blockquoted | +0.124 under one convention / −0.126 under the other | **STALE_SUPERSEDED** | **FIXED** — appended inline `[SUPERSEDED 2026-08-09]` note pointing to `runs/O2_OWNER_UTILITY_READJUDICATION/` and J=+0.0549/−0.2220 |
| `research/system_master/CURRENT_TRUTH.md` | lines ~1081-1091 (pre-edit), Wave-2 §, "CORRECTION APPENDED 2026-08-09, after the M5 red team and the O1 blind repair" blockquote ("O1 BLIND REPAIR — done, and O2 stays BLOCKED") | +0.0210→+0.1241; J=+0.124 while `J_worst`=−0.126 | **STALE_SUPERSEDED** | **FIXED** — appended a further blockquoted `[SUPERSEDED 2026-08-09]` correction within the same blockquote |
| `BASELINE_MODELS.md` | lines ~331-333 (pre-edit), "Performance battery — CURRENT `_v4` EXACT BATTERY" section, explicitly the section the file calls "the number to cite for Product A going forward" | O1a daily objective: INCONCLUSIVE (+0.124 equal-weight-mixture vs −0.126 Γ-minimax) | **STALE_SUPERSEDED** | **FIXED** — appended inline `[SUPERSEDED 2026-08-09]` note; this file self-declares as THE authoritative source, so this was the highest-priority fix |
| `research/system_master/FINAL_CAMPAIGN_BASELINE.md` | lines ~48-51 (pre-edit), "Objective-function status" section | O1a daily objective is INCONCLUSIVE — +0.124 under mixture, −0.126 under Γ-minimax | **STALE_SUPERSEDED** | **FIXED** — appended inline `[SUPERSEDED 2026-08-09]` note pointing to the real v2 output and its source |
| `research/registry/tested_configs.csv` and ~140 other `runs/*/out/*.csv`\|`*.json` (e.g. `FLOW01_AGGRESSIVE_PARTICIPATION/out/checkpoint_features.csv`, `FH_tf*_[AB]/raw_result.json`, `SW*/raw_result.json`) | various | digit substrings matching `0.124x`/`0.126x`/`0.125...9` inside unrelated numeric columns (e.g. `EntryEfficiency=0.1259259259259259`, LOYO deltas, diagnostic CIs) | **INCIDENTAL_NUMERIC_COINCIDENCE** (not a real hit) | none — raw data artifacts, not canonical documents; sampled several and confirmed unrelated |

Machine-readable copy: `runs/O2_NUMERIC_PROVENANCE_AUDIT/out/classification_table.csv`.

## The 4 fixes, verbatim (diff excerpts)

**`BASELINE_MODELS.md`** (line ~333, appended after the existing "...may not be quoted as one number).")
```
**[SUPERSEDED 2026-08-09: the +0.124/−0.126 figures above are HAND ARITHMETIC on
already-published v1 per-method components (`runs/W17_C4_COMPLIANCE/O1_REPAIR_PREREGISTRATION.md`),
not `primary_objective_v2` module output — that module had never been run end-to-end on real P&L
until `runs/O2_OWNER_UTILITY_READJUDICATION/`. Running the real module on the certified Product-A
legacy-proxy daily series gives J=+0.0549 (mixture) / J=−0.2220 (Γ-minimax) — same sign pattern,
still INCONCLUSIVE, but materially different magnitude. See
`runs/O2_OWNER_UTILITY_READJUDICATION/REPORT.md` and
`runs/O2_OWNER_UTILITY_READJUDICATION/out/o2_scoring_summary.csv`. Cite the v2 module figures, not
this hand-computed pair, going forward.]**
```

**`research/system_master/FINAL_CAMPAIGN_BASELINE.md`** (line ~51, appended after "...may not be quoted as a single number.")
```
**[SUPERSEDED 2026-08-09: the +0.124/−0.126 pair above is HAND ARITHMETIC on already-published
v1 per-method components (`runs/W17_C4_COMPLIANCE/O1_REPAIR_PREREGISTRATION.md`), not actual
`primary_objective_v2` module output — the module had never been executed end-to-end on real P&L
until `runs/O2_OWNER_UTILITY_READJUDICATION/`. The real module output on the same Product-A series
is J=+0.0549 (mixture) / J=−0.2220 (Γ-minimax) — same sign pattern, still INCONCLUSIVE, materially
different magnitude. See `runs/O2_OWNER_UTILITY_READJUDICATION/REPORT.md` and
`runs/O2_OWNER_UTILITY_READJUDICATION/out/o2_scoring_summary.csv`.]**
```

**`research/system_master/CURRENT_TRUTH.md`** (site 1, Wave-19 §7, appended after "...inject a selection bias no aggregation rule touches).")
```
**[SUPERSEDED 2026-08-09: the +0.124/−0.126 pair above is HAND ARITHMETIC on already-published
v1 per-method components, not actual `primary_objective_v2` module output — see
`runs/O2_OWNER_UTILITY_READJUDICATION/REPORT.md`. The real module output on the certified
Product-A series is J=+0.0549 (mixture) / J=−0.2220 (Γ-minimax) — same sign pattern, still
INCONCLUSIVE, materially different magnitude. Source:
`runs/O2_OWNER_UTILITY_READJUDICATION/out/o2_scoring_summary.csv`.]**
```

**`research/system_master/CURRENT_TRUTH.md`** (site 2, Wave-2 "CORRECTION APPENDED" blockquote, appended as a further blockquoted paragraph after "...no result was produced from the un-justified state.")
```
> **[SUPERSEDED 2026-08-09: the +0.1241/−0.1259 (rounded +0.124/−0.126) pair disclosed above was
> HAND ARITHMETIC on the already-published v1 per-method components — `primary_objective_v2` had
> still never been run end-to-end on real candidate P&L at the time this was written. It has now
> been run, in `runs/O2_OWNER_UTILITY_READJUDICATION/`: the real module output on the certified
> Product-A legacy-proxy daily series is J=+0.0549 (mixture) / J=−0.2220 (Γ-minimax) — same sign
> pattern (still INCONCLUSIVE), but materially different magnitude from the hand-computed pair
> above. See `runs/O2_OWNER_UTILITY_READJUDICATION/REPORT.md` and
> `runs/O2_OWNER_UTILITY_READJUDICATION/out/o2_scoring_summary.csv`. Do not cite the hand-computed
> pair as current v2 output going forward.]**
```

`git diff` confirms all four edits are pure additions — every changed line's original text is
byte-for-byte preserved before the appended note; nothing was deleted or rewritten.

## Notes on classification judgment calls

- **Why `O1_OBJECTIVE.md`, `O1_REPAIR_PREREGISTRATION.md`, and `O1_BLIND_REVIEW_OUTCOME.md` were
  left untouched.** These three documents are the literal origin chain of the number: `O1_OBJECTIVE.md`
  publishes the raw v1 per-method components; `O1_REPAIR_PREREGISTRATION.md`'s own worked example
  hand-combines them into +0.1241/−0.1259 and states so explicitly (its own §"Answers to the
  questions the task asks" walks through the arithmetic); `O1_BLIND_REVIEW_OUTCOME.md` is an
  append-only, dated record of the R3 blind review of that repair. All three are properly scoped,
  point-in-time historical/technical record — exactly the `O1_OBJECTIVE.md`-worked-example carve-out
  the directive described — and none of them is a document anyone would reasonably treat as "today's
  owner-utility number" the way `BASELINE_MODELS.md`, `CURRENT_TRUTH.md`, and
  `FINAL_CAMPAIGN_BASELINE.md` are.
- **Why the second `CURRENT_TRUTH.md` site (inside a "CORRECTION APPENDED" blockquote) was still
  treated as STALE_SUPERSEDED rather than left as historical record.** Unlike `O1_BLIND_REVIEW_OUTCOME.md`,
  this text sits inside `CURRENT_TRUTH.md` itself — a file whose own header states "single page,
  updated after every wave" and whose established convention (seen at line 448's "CORRECTION
  APPENDED 2026-08-09 (Wave 18...)" block) is to append corrective annotations directly onto
  chronology sections the moment a defect is found, not to rely solely on a top-of-file disclaimer.
  Since no such correction had been appended anywhere in the file for the O2 finding, a reader
  hitting either site would see the hand-computed figures presented as the last word. Both sites
  were fixed for consistency and completeness.
- **No `INCORRECT` (unrelated numeric error) findings were flagged.** One adjacent oddity was noted
  in passing — `BASELINE_MODELS.md` cites Product A net $177,924.40 (`_v4`) while
  `FINAL_CAMPAIGN_BASELINE.md` cites $175,798.80 (`_v3`) — but this is a disclosed, intentional
  version difference (both files explicitly flag which build version they describe and which
  document supersedes which), not a hidden error, so per the directive's scope it was not treated
  as an `INCORRECT` finding requiring a fix.

## Safety boundary compliance

No file or data dated ≥2026-08-01 was read, exported, or computed on. The AMENDMENT_3 protected
confirmation pool was not touched. No orders, strategy deployments, or connection/credential/
licensing changes were made. This was a pure text-search-and-documentation-correction pass — no
backtests were run, no `research/scalping_lab` tick or grid data was read, and every edit was
strictly additive (a correction annotation appended after the original text), per this repo's
"never delete raw research evidence, erase failed experiments, rewrite historical results" rule
and the campaign's own append-only correction convention observed elsewhere in `CURRENT_TRUTH.md`.

## Artifacts

- `runs/O2_NUMERIC_PROVENANCE_AUDIT/spec.yaml` — audit spec, method, and reproduce commands.
- `runs/O2_NUMERIC_PROVENANCE_AUDIT/out/classification_table.csv` — machine-readable classification
  table (all hits, including the incidental-noise files, for completeness).
- Edited in place: `BASELINE_MODELS.md`, `research/system_master/CURRENT_TRUTH.md`,
  `research/system_master/FINAL_CAMPAIGN_BASELINE.md`.

Nothing was committed to git as part of this pass (edits are present in the working tree; no
commit was requested).
