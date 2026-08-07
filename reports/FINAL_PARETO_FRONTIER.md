# FINAL PARETO FRONTIER — audited candidate set with tier labels

_DRAFT 2026-08-07 · branch `post_campaign_audit`. Tiers: **CHAMPION** (the frozen deliverable),
**PARETO_FINALIST** (non-dominated, retained), **REFERENCE** (kept for calibration/robustness,
not a deliverable), **REJECTED** (failed preregistered gates or tests; may not be revived without
a genuinely new hypothesis), **INVALIDATED** (the construct itself was shown to be an artifact).
Bases labeled REALIZED_ONLY / TRUE_MTM per constitution §10. Ranking is never by net profit
alone. Window for all rows: 2022-01-01 → 2026-07-31, NQ 3-minute (except as noted), slip-1,
Lifetime commission._

## The frontier

| tier | candidate | net | Sharpe | max DD | other key metrics | status / evidence |
|---|---|---:|---:|---:|---|---|
| **CHAMPION** | **R5-E10 executable** — 13 × SolarWaveOpenV3 virtual members (StartUp=false, ThresholdMode 1, VolPeriod 460, clamp 40–1200, VolMult 6–30), target = round(10 × mean) MNQ max 10, net-change execution, session-close flatten, MNQ $0.65/side + 1 tick | **$179,361.36** | **0.9671** session TRUE_MTM (calendar 0.8883) | **−$41,252.20** daily TRUE_MTM | ES5 −$4,028; TUW 1,120/1,184; worst day −$12,724; corr w/ theory 0.9985; top-10-day retention 98.6%; mean \|exposure\| 0.278 NQ-eq; 52,126 contracts; commission $33,882 + slippage $26,063 | Passes ALL preregistered AUDIT-04 gates; margin thin (0.003–0.012) and robust to round/floor × session/calendar (4/4). `research/audit/EXECUTABLE_ENSEMBLE.md`, `executable_ensemble_metrics.csv`, `e10_sensitivity.csv` |
| **PARETO_FINALIST** | **R5 theoretical** — same 13 members, strict 1/N, NQ $4.36/RT (research proxy of the champion, corr 0.9985) | $198,058.82 | 1.0642 session TRUE_MTM (calendar 1.0104; campaign 1,424-calendar headline 0.9771 REALIZED_ONLY) | −$39,853.39 daily / **−$42,204.42 bar-level TRUE_MTM** | Sortino 2.2246; Calmar 1.0577; ES5 −$3,983; TUW 1,112; worst qtr −$8,613; slip-2 retains 87.4%; P(Sharpe≤0)=0.0020 | STRONG_HISTORICAL_CANDIDATE — **REPRODUCED 13/13 fill-by-fill**. `research/audit/R5_REPRODUCTION.md`, `MTM_RECONCILIATION.md`, `FINALIST_SCORECARDS.md` |
| **REFERENCE** | **R4-21 theoretical** — fixed threshold, all 21 cells SM 170–880, strict 1/N | $159,423.70 | 0.9704 session TRUE_MTM (campaign 1,424-calendar 0.8922 REALIZED_ONLY) | **−$36,360.30** daily / −$39,493.63 bar-level TRUE_MTM (smallest of the set at every granularity) | Sortino 1.9586; Calmar 0.9332; ES5 −$3,865; TUW 1,110; worst day −$7,135; P(Sharpe≤0)=0.0051 | Simplicity/robustness anchor and challenger benchmark. **NOT executable at acceptable cost** — see REJECTED rows. Members not re-executed by the audit (committed ledgers + determinism gates; flagged, not certified). `FINALIST_SCORECARDS.md` |
| **REFERENCE** | **Canonical open baseline** — SolarWaveRKReplicaV0 / SolarWaveOpenV1, Type 1, 90/179, 1-minute, canonical window 2023-01-01 → 2025-02-02 | $146,440.60 (slip-0) | — | −$22,066.60 | 2,915 trades; PF 1.132213; commission $12,709.40 | Re-verified to the penny 2026-08-07, vendor and vendor-free (`runs/AUDIT_GATE_R01/R02`). Anchors all determinism claims; the mandatory gate check before any run |
| **PARETO_FINALIST (INCONCLUSIVE — NOT RE-AUDITED)** | **ccHL anchor ensemble** — close-confirmed High/Low anchor, 10 cells | $215,137.15 | 0.9119 (1,424-calendar REALIZED_ONLY; session-basis 0.9992) | −$47,697.57 | Calmar 0.798; TUW 688 d; worst qtr −$21,438; turnover 5.39 tr/session; ex-top-10-days retention 48% | Campaign-reported numbers only; **no re-execution, MTM, or executable work performed** (out of audit scope; historically "PASS but redundant with R5" — combo adds nothing: 1.011 vs 1.010). `FINALIST_SCORECARDS.md`, `reports/final_pareto.csv` |
| **REJECTED** | **C2 sleeve** — Type-1 core + one Type-3 re-entry, 8 fixed cells | $233,628.36 | 0.8499 (1,424-calendar REALIZED_ONLY) | −$47,413.26 | best point estimates in the campaign | Fails the interaction test: on the adaptive core ΔSharpe −0.402, P(Δ≤0)=0.879, 2025 turns negative. A sleeve whose sign flips with the core is an interaction, not an effect. `research/frontier.yaml` C2_SLEEVE_INTERACTION_TEST |
| **REJECTED** | **R4 discrete executables** — E13 (21 MNQ), E10, E20, E3 on the R4-21 signal set | $119,222–$131,780 | 0.7262–0.8023 session TRUE_MTM | −$39,225…−$41,726 | ΔSharpe −0.168…−0.244 vs theory | Every variant fails the preregistered Sharpe gate by 0.17–0.24 (E3 also net). The 21-member higher-turnover structure pays ~3× commission under the MNQ schedule. `executable_ensemble_metrics.csv` |
| **REJECTED** | **R5 discrete alternates** — E13 (13 MNQ, −0.116), E20 (−0.129), E3 mixed naive (−0.181) | $163,113–$176,455 | 0.8835–0.9479 session TRUE_MTM | ≈ −$41.3k | published with FAIL verdicts as part of the E10 design-choice disclosure | `executable_ensemble_metrics.csv`, `SECOND_RED_TEAM.md` §3 |
| **REJECTED** | **Family-B candidates** — B01c ORB-failure fade (seq 230); B01e/B02 gap fade (seq 231–232); DR05-H2 failed-flip fade (dead unbuilt per preregistered gate) | B01c −$22,534; B02 +$75,095 slip-1 but FAIL 3/6 gates | — | B02 worst trade −$8,544; trade-ES5 −$5,390 (stopless) | B02 top-1% = 90.1% of net; 52.7% months positive; losing-day corr with Family A −0.08 (independent, but not a system) | Family B FALSIFIED in its preregistered high-value forms on 2022–2026 NQ. `research/registry/rejected_ideas.md`, `research/04_complementary_family/` |
| **INVALIDATED** | **R4b 8-cell plateau** (as first published) | $180,479.44 | 0.7728 (1,424-calendar REALIZED_ONLY) | −$53,689.43 | — | The plateau boundary was itself an in-sample selection — the very operation CSCV shows does not travel. Superseded by R4-21, which beats it on both Sharpe and DD. `reports/final_pareto.csv`, `research/frontier.yaml` R4_REDEFINED_FULL_RANGE |
| **INVALIDATED** | **Any single cell / "best member"** (e.g. best single net $249,934, Sharpe 1.236) | — | — | −$71,395 | — | Unknowable ex ante: PBO 0.48–0.90, negative IS→OOS slope everywhere; walk-forward argmax earned $16,131 where the median config earned $121,373. `research/CAMPAIGN_STATE.md` §3 |

## Reading rules

1. **The champion and its proxy are the same signal set** at two cost/granularity layers; quote
   E10 for anything executable, E0 only as the research proxy, always labeled.
2. **R4-21 must never be quoted as a deployable alternative** without a cost-engineering
   breakthrough — its frontier position is theoretical only.
3. **ccHL is the only row whose numbers were not re-verified by the audit**; any future use
   requires re-audit (reproduction + MTM + executable) before comparison with audited rows.
4. **V4 (tick-snapped S) is not a candidate** — it is a sensitivity datapoint:
   ensembles PERFORMANCE_SIMILAR_ONLY (corr 0.9952, ΔSharpe +0.019, P = 0.33), member paths
   NOT_EQUIVALENT (up to −49%). `research/audit/V3_V4_VERDICT.md`.
5. Nothing on this table is forward-validated; no row has clean OOS; external portability is
   refuted for the family (0-for-4: ES, YM, RTY, CL). The frontier is a historical object.
