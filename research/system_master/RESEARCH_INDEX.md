# RESEARCH_INDEX — map of the evidence base (2026-08-08)

> **⚠️ Staleness note (added 2026-08-09, no rows below edited):** this index was written early
> in wave-1 (registry seq ~357) and its "V2 wave-1" / "V1 record" split has NOT been updated for
> waves 2-15 (seq now 442+). Some entries below are themselves now wrong as a result — e.g.
> `CONVENTIONS.md` and `SM13_BMOM_DECAY_RULE.md` are listed under "V1 record (superseded
> framing)" but are in fact still ACTIVE, binding documents (verified directly against this
> session's own wave-11-15 work, which cites both). **Do not trust this file's categorization
> over `CURRENT_TRUTH.md`** — if the two disagree about whether something is current, believe
> `CURRENT_TRUTH.md`. Left uncorrected here rather than silently re-edited, per the "append,
> don't rewrite" convention — see `MAP.md` at repo root for a version-independent map instead.

## Read first
START_HERE.md → CURRENT_TRUTH.md → SYSTEM_SCORECARD.md

## V2 wave-1 results (2026-08-08)
- DRAWDOWN_RECONCILIATION.md — the −27.2k vs −58.5k answer (SMV2A)
- BMOM_EXECUTION_AUDIT.md — causal fills, E2 canonical (SMV2B, seq 320-323)
- B1_ABLATION.md — B1 demoted (SMV2C, 324-327)
- LONG_SHORT_FRONTIER.md — c1_50 promoted, DUAL_HTF core (SMV2E, 328-334+343-346)
- LEVERAGE_ROBUSTNESS.md — method-robust frontier (SMV2F)
- INDICATOR_FRONTIER.md §SMV2G — HTF mechanism plateau (335-342)
- ONE_CONTRACT_FRONTIER.md — policy rebuild + autopsy + LOYO (SMV2H, 347-357)
- DAY_ONLY_FRONTIER.md — DAYONLY_DUAL6040 champion candidate
- NINJATRADER_PARITY.md — OneLot v1 Analyzer parity PASSED
- KNOWN_ERRORS_AND_CORRECTIONS.md / SUPERSEDED_CONCLUSIONS.md / CLAIM_LEDGER.md
- NEXT_RESEARCH_QUEUE.md — priority queue

## V1 record (2026-08-08, superseded framing but intact evidence)
FINAL_NQ_SYSTEM.md, FINAL_NQ_SYSTEM_RED_TEAM.md, FINAL_PACKAGE_SPEC.md,
NINJATRADER_MASTER_SPEC.md, SOLAR_DRAWDOWN_ATLAS.md, STOP_OVERLAY_FRONTIER.md,
RECENT_REGIME_BMOM.md, PORTFOLIO_FRONTIER.md, LEVERAGE_FRONTIER.md,
ALPHA_THROUGHPUT.md, SM13_BMOM_DECAY_RULE.md, EVIDENCE_MAP_RAW.md, CONVENTIONS.md,
OWNER_DIRECTIVE_20260808.txt, OWNER_DIRECTIVE_V2_20260808.txt, CURRENT_STATE.md.

## Machine state
SYSTEM_FRONTIER.yaml (verdicts) · research/registry/tested_configs.csv (seq ledger,
at 357) · runs/SM*/spec.yaml (frozen specs) · runs/*/out (immutable results).

## Certified tooling
src/analytics/sm01_solarsim.py (member+E10 twin, 4/4 gates) · sm_bmom.py (1333/1333) ·
sm_metrics.py · smv2_common.py (V2 batteries) · runs/SMV2A_DD_RECONCILE/smv2a.py
(canonical OneLot replay + 7-object accounting).
