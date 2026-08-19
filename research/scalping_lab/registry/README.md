# Scalping Lab registry — file status map (written 2026-08-18, consolidation pass)

| File | Status | What it actually holds |
|---|---|---|
| `tested_configs.csv` | **OPERATIVE record** | 41 rows, seq S1–S35 (+S0-* instrumentation sub-ids, S9p), 2026-08-07→08-08. Every tested config of the campaign. |
| `hypothesis_ledger.csv` | **OPERATIVE record** | 26 rows; per-hypothesis terminal verdicts incl. the three parked Program-B candidates. |
| `experiments.yaml` | **EMPTY since creation — never used** | The mandated per-experiment registry was fulfilled in practice by `specs/` (15 frozen wave specs, committed before readouts) + `tested_configs.csv` + `CAMPAIGN_STATE.md`. Kept as-is per append-only convention; do not read its emptiness as "no experiments". |
| `candidate_registry.csv` | **HEADER-ONLY — no candidate ever registered** | The one adopted operational candidate (E10 Flatten1644 v2, CONFIRMED_ADOPT, live-ops default) is recorded in `CAMPAIGN_STATE.md` and `runs/E10MASTER_V2/results.md`, not here. Zero *alpha* candidates ever reached freeze (Program B = 3 parked / 0 frozen), so the emptiness is substantively correct for alpha. |

If the campaign resumes: either register new experiments here properly or formally deprecate
these two files in the mandate — do not let the split recur silently.
