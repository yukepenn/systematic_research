# SPEC — `BBO_COMPLETENESS_RECENSUS_V1` · reconciling 99 vs 123. **DATA-ONLY.**

**Committed BEFORE the crosswalk is computed.** No prices read. No outcomes read. No model.

| | |
|---|---|
| **question** | Do the 99-session and 123-session counts describe the same population under different rules, or does a genuinely unread pre-seal BBO pool exist? |
| **forbidden** | ⛔ **Subtracting 99 from 116 and calling the remainder a blind pool.** They are different definitions |
| verdict must be | **A** no historical blind BBO pool · **B** a genuine pool exists (freeze immediately) · **C** ambiguity, provenance not certifiable |
| **if B** | hash and freeze the manifest **immediately**. **Do not inspect its returns. Do not spend it.** Its existence changes future experimental design; it authorizes no model |

---

## 1. The two criteria, recovered exactly — not approximated

**OLD** — `runs/ORDERFLOW_EXPAND_20260827/src/bbo_hourly_truth.py`, producing
`out/bbo_hourly_truth.csv` (310 pre-seal rows: **99 FULL**, 47 PARTIAL, 164 NONE).

An NQ session `sD` spans **18:00 D−1 → 17:00 D ET** and draws on **two calendar dates** of `.ncd`
files. That file established empirically that **file hour label = ET hour + 1** (Last files are
missing label 18 on every date because the maintenance break is 17:00–18:00 ET). So per series it
requires **23 hour labels**: `19..23` on D−1, plus `00` on D, plus `01..17` on D.

```
quote_frac = min(bid_frac, ask_frac)          cls = FULL  iff  quote_frac > 0.90
```

**NEW** — `runs/ESNQ00_CAPABILITY_20260828/src/esnq00_census.py`: Bid **and** Ask **and** Last
present for labels `9..16` on date D only. **8 hour labels, RTH-scoped.**

> ### These are not competing measurements of one quantity. **OLD measures FULL-SESSION (23 h)
> ### completeness; NEW measures an RTH window.** A session with complete RTH quotes and a missing
> ### overnight leg is `PARTIAL` under OLD and complete under NEW — and is **perfectly usable for an
> ### RTH-only strategy**, which is what every BBO object here has been.

⚠️ **A defect in NEW, declared before the crosswalk.** Under `label = ET hour + 1`, the RTH window
10:00–15:30 ET with a 30 s warmup and a 15:31 exit needs labels **10..16**. `esnq00_census.py` used
**9..16**, which demands an extra early hour (ET 08:00). It is therefore **stricter than necessary at
the bottom** and never over-counts. Both windows are computed and reported; neither is chosen after
seeing which gives a friendlier answer.

## 2. SOURCE-PROVENANCE GATE — what "consumed" is allowed to mean

**File enumeration does not consume a session. Timestamp-only capability inspection does not consume
a session. Computing forward returns or price outcomes on it DOES.**

Every `consumed` flag must name the artifact chain that exposed prices:

```
session -> materialized into substrate S -> run R globs S -> R computes forward returns
```

The two substrates and their consumers, established by reading the consuming code, not assumed:

| substrate | path | consumers |
|---|---|---|
| **OLD** | `research/scalping_lab/substrate/raw/NQ` | `AUCTION01`–`04`, `ACTIONMAP01`, `FLOW01`, `U9`, `U9B` |
| **v2** | `research/data_microstructure_v2/raw/NQ` | `MS01`, `MS01A`, `MSBBO_V1`, `MSBBO_DEPLOYMENT_FREEZE` |

**Conservative direction, declared now:** a session present in **either** substrate is marked
**CONSUMED**, without attempting to prove that a specific run's execution predated the file's
arrival. Over-counting consumption shrinks any claimed blind pool, which is the only safe direction
to err for this question.

## 3. The six states, kept strictly separate

```
1  file exists                  any NQ .ncd for that date
2  RTH-complete (NEW)           labels 9..16 (as-run) and 10..16 (label-corrected)
3  quote-FULL (OLD)             >90 % of the 23 required session-hour labels, both sides
4  previously materialized      present in the OLD or v2 substrate
5  outcome-consumed             materialized AND a consumer run reads that substrate
6  genuinely unread             pre-seal, quote-complete under a stated rule, NOT materialized
```

**State 6 is the only one that can support a blind pool**, and only under a rule stated **before**
the count is seen.

## 4. Crosswalk columns — fixed now

`session_date` · `contract` · `file_presence` · `old_quote_class` · `old_quote_frac` ·
`new_rth_complete_9_16` · `new_rth_complete_10_16` · `bid_coverage` · `ask_coverage` ·
`last_coverage` · `rth_span_labels` · `previously_exported_v2` · `previously_exported_old` ·
`outcome_consumed_by_run` · `consumption_provenance` · `eligible_blind_old_rule` ·
`eligible_blind_new_rule` · `reason_for_disagreement`

## 5. Seal

`>= 2026-08-01` may be **inventoried by metadata only** (file names and hour labels). **No price or
outcome in the sealed pool may be read**, and the crosswalk's eligibility columns are `False` for
every sealed date by construction.

## 6. Continuation — fixed before the count

| verdict | action |
|---|---|
| **A** no genuinely-unread quote-complete pre-seal sessions | record it; the BBO lane's claim ceiling stays **discovery-grade**; re-rank EVI |
| **B** a genuine pool exists | **freeze + hash the manifest in the same commit as the finding.** Do **not** read its returns. Do **not** design a model against it in this wave |
| **C** provenance cannot be certified | say so; name exactly what would certify it. **Do not default to B** |

**A larger blind pool is an ASSET, not a licence.** Its existence does not authorize a BBO V2, does
not un-void `MS-BBO-CANDIDATE-1`, and does not permit re-running the corrected feature set — that
formulation has already paid its discovery budget.
