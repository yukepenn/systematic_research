# SMV2Q_DIAGNOSTICS — Statistical Red Team Notes (V4 §48 mandatory pass)

Reviewer: statistical red team subagent, 2026-08-08.
Scope: spec letter-exactness, independent recomputation, lookahead/leakage scan,
report language, policy-creep check. No fixes applied; measurement only.

## Verdict: CONFIRMED

## 1. Spec applied letter-exact

- spec.yaml frozen in commit 58dc2d2 ("wave-3 specs FROZEN before any read, seq 372-388")
  and byte-identical at review time (git diff empty). Results files are untracked
  (post-spec), i.e., spec committed BEFORE results were read. PASS.
- Class DIAGNOSTIC: the spec defines **no gates, no grids, no seeds** — nothing to move.
  No selection, ranking, or thresholding anywhere in the executors; the only quantile
  computed (top-decile SOLAR_DUAL threshold) is the spec's own winner-drought definition.
- All six specced curves loaded from the specced sources. SM14 reuse of the SMV2H2 regen
  column is explicitly permitted by the spec ("or reuse SMV2H2 regen curves") and was
  crosschecked against SMV2H daily_curves (max diff 0.0).
- Window discipline: dev ≤ 2026-05-31 primary everywhere; June–July 2026 appears ONLY in
  recency_2026.csv, ONLY for MASTER_EXEC_NT, every row carrying label=CONSUMED. Verified
  in code and artifact. PASS.
- All five deliverable blocks present with the specced feature lists (sigma460, rv20 pct,
  range/friction, ER150, DC flip rate, HTF mix, side-of-loss split, B-MOM activation;
  concurrent + prior; Welch t per feature). Extra artifacts (worst_periods.csv,
  master_week_cell_overlap.csv, leg_daily.csv) are supporting measurement outputs of the
  specced questions, not extra cells or new selections.
- One documented interpretation, not a deviation: the attribution ratio
  KS·Tpp/(KS·Tpp+KB·B) is evaluated on the signal bar that generated the position
  (share shifted 1 bar) because pos[t] = tgt_ops[t-1]. The spec fixes the formula, not
  the bar alignment. I verified from twin_bar_ledger.parquet: pos[t]==tgt_ops[t-1] at
  99.9926% of 540,232 bars; flat-signal bars with nonzero carried position = 2,334
  exactly as reported; whenever the signal is flat the target is 0 (flat & tgt≠0 = 0),
  so the ffill/0.5 start-fill is inert for MTM attribution. The binding invariant —
  legs rebuild the twin exactly — holds (my recompute: max abs daily err 9.1e-13 vs
  upstream tw). The concurrent-bar rejection is documented in REPORT methods with
  measured evidence (leg positions to 596). Acceptable.

## 2. Independent recomputation — 65/65 PASS

Recomputed with independent code from UPSTREAM inputs (parity_daily_aligned.csv,
solar_dual_htf_daily.csv, ledger_E2_next_open.parquet, twin_bar_ledger.parquet), not the
run's intermediates. Script: scratchpad rt_recompute.py (session-local). Highlights:

| claim | run value | red-team recompute | match |
|---|---|---|---|
| MASTER_EXEC_NT pos day/wk/mo/qtr % | .4411/.5609/.6415/.8333 | identical | PASS |
| worst wk/mo/qtr | −10,307.2 / −7,523.0 / −14,300.3 | identical | PASS |
| maxDD_eod / TUW / med / p95 recovery | 18,894.3 / 131 / 5 / 61.8 | identical | PASS |
| roll20/60/120 floors | −12,795.8/−16,610.0/−3,453.8 | identical | PASS |
| JL weeks 50/230, JL months 7/53 | 50, 7 | 50, 7 | PASS |
| JL weeks 100% master-neg; 49.50% of 101 master-neg; sum −159,638.4 | all | identical | PASS |
| drought: thr 2,494.18, n=114, med 6, p90 21.8, p95 32.4, max 47 | all | identical | PASS |
| Q4 drought: mean uw 23.35d, mean depth 7,667.4, max 18,894.3 | all | identical | PASS |
| LEG_SOLAR 96,583.3 (Shp 0.875) / LEG_BMOM 82,705.4 (Shp 1.138); recon ≤1e-12 | all | identical | PASS |
| r120 devend 1.1224 = 41.3 pct; CONSUMED Jun +20,616.7 / Jul +14,380.4 / ex-edge +7,013.3; r120@07-31 1.0288 = 36.1 pct | all | identical | PASS |
| Welch t (er150 −6.468, flip +3.007, sigma460 +0.266, mtm_short −7.463, mtm_long −6.739, prior mtm_long +2.425, monthly mtm_short −2.862) | all | reproduced from moments to ≤2e-3 | PASS |
| SHORT×HTF_UP only negative side×HTF cell (−4,118); RTH 09:33–12:00 gross loss −2.934M; ON 00:00–09:33 −2.072M | all | identical | PASS |
| conflict bars −309,879.5, 30.65% of both-active; friction 39,966.3; gross 219,255 | all | identical | PASS |

Also verified: BMOM zero-fill arithmetic (101 zero days; 572/1,038 = 55.1% among active),
dd_ownership 9-of-10 shared-loss episodes (2022-06 episode is the exception, B-MOM +3,681),
median solar share of top-10 windows = 0.608 ("~60%" in REPORT).

## 3. Lookahead / leakage scan — CLEAN

- HTF state: sign(close − MA50) **shift(1)** — no same-session outcome use (matches smv2h def).
- er150 / sigma460 / rv20 / flip rate: strictly backward-looking constructions.
- Attribution share: shift(1) (backward); costs allocated within-session by |Δ leg target| —
  descriptive, no decision depends on it.
- Full-sample descriptive statistics exist (rv20_pct percentile rank over dev; top-decile
  drought threshold over dev) — both are the spec's own definitions for measurement and feed
  no rule, gate, or selection. Noted, not leakage.
- Data hygiene: input max dates = 2026-07-31 (parity nt/tw, ledger), 2026-05-29 (dual,
  BMOM ledger sessions). **No data ≥ 2026-08-01 anywhere.** CONSUMED confined to
  master-exec Jun–Jul rows, labeled.
- No RNG anywhere (no bootstrap deliverables in spec); qcut/quantile deterministic.
- Burn-in: r120 dropna (first window complete), MA50 HTF NaN masked via where(notna).

## 4. Report language — PASS

- Claims labeled FACT / INFERENCE / HYPOTHESIS throughout (23 label instances); recency
  section uses the V4 §56 mandated phrasing verbatim in substance ("path evidence, not
  proof of death"; MONITOR-01/SM13 load-bearing; "No tuning, no gate, no selection follows
  from this read").
- Caveats honest and material: mixed dollar units across curves; n=7 monthly JL sample
  flagged as thin with weekly n=50 load-bearing; BMOM zero-fill convention disclosed;
  2026-07-30/31 window-edge days split out; open DD episode at dev end flagged as
  CONSUMED-window observation.
- No kills to record (nothing killable in a measurement track); no BLOCKED items claimed.

## 5. Policy/adoption creep — NONE

Grep for adopt/promote/deploy/recommend/select/gate-pass over REPORT.md: no hits beyond
the "no gates, no selection" disclaimers. Engine-3 material is framed as HYPOTHESIS
("for Engine-3 targeting, not a rule") and is explicitly within spec scope
("input to 11-14"). The recency read draws no action.

## Minor notes (non-blocking, no action required by this pass)

1. Registry lag: research/registry/tested_configs.csv ends at seq 371; the seq-380 row and
   CAMPAIGN_STATE/frontier updates are not yet written (presumably pending post-red-team).
   Should land with the run commit.
2. q_addendum.py np.select cell labeling would tag a week with solar sum exactly 0.0 and
   bmom < 0 as "S-B0"; no such week exists (cells reconcile exactly with smv2q.py:
   71/45/62/50/2/0 = 230). Cosmetic only.
3. Worst-quarter values include partial edge quarters (2026Q2-partial is the worst for
   most curves) — disclosed in REPORT; keep the "-partial" tag if these numbers migrate
   to the permanent scorecard.
4. REPORT rounds p95 recovery 61.8→62 and r120 1.1224→1.12 — within normal presentation.

Verdict: **CONFIRMED** — spec letter-exact, 65/65 independent recomputations match,
no leakage, language compliant, no policy creep.
