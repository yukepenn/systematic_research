# SYSTEM_MASTER — Frozen Evaluation Conventions

**Frozen 2026-08-08, committed BEFORE any new experimental result was read.**
Everything below is binding for the whole program. Changes require a new dated section
appended here with justification; nothing may be edited after a result that depends on it
has been read.

## 1. Data windows (frozen)

| window | range | role |
|---|---|---|
| **CURRENT (dev)** | 2022-01-01 → **2026-05-31** | primary economic lens; all development, all selection |
| **JOINT-READ HOLDOUT** | 2026-06-01 → 2026-07-31 | ONE read, only after the joint finalist package is frozen (§8) |
| TRANSITION | 2018-01-01 → 2021-12-31 | diagnostic: fragility/decay only, never selection |
| HISTORICAL | 2006-01-05 → 2017-12-31 | diagnostic: stress, mechanism, null calibration |
| VIRGIN | ≥ 2026-08-01 | untouchable (LOCKED_FORWARD; MONITOR-01 only) |

**Recency weighting: NONE.** Primary ranking uses the CURRENT window unweighted; TRANSITION
and HISTORICAL are reported separately and never pooled into a headline metric. This is the
frozen answer to the directive's "freeze any recency weighting before ranking" — the scheme
is *no weights, current-window primary*, chosen for zero degrees of freedom.

**Honesty note on the holdout.** The Solar/E10 *baseline* has already been read through
2026-07-31 (LOCKED_FORWARD declares ≤2026-07-31 research-consumed). The holdout is therefore
**clean** for: B-MOM, B-FADE, B1, and every NEW engine developed on ≤2026-05-31 data (none of
their rules ever read June–July 2026). It is **increment-only** for Solar overlays: the
baseline's June–July P&L is known, but overlay/portfolio parameters chosen on dev have never
seen those two months, so Δ(overlay−base) and portfolio weights are the meaningful holdout
statistics there. This distinction must be stated in the joint-read report.

## 2. Daily P&L basis

- Daily vectors are keyed by **NT8 session date** (18:00 ET roll) — for flat-at-close
  engines this equals TRUE_MTM to the cent (proven, MTM_RECONCILIATION). Every engine in
  this program must be flat at session close (or earlier); if any candidate ever holds
  overnight as part of its rule (e.g. B1), its session-keyed MTM convention must be stated.
- **Program calendar (dev): all NQ sessions in `runs/AUDIT03_BARS/nq_3m_2022_2026.csv`
  with session date ≤ 2026-05-31.** Sharpe uses ALL days of this calendar (flat days = 0),
  ann = 252, std ddof=1. The calendar count is pinned in the substrate build report.
- Ensembles/portfolios are strict fixed-weight means of member daily vectors; no
  reweighting ever, except where a spec explicitly tests a frozen weighting rule.

## 3. Cost model (inherited, never softened)

| object | cost |
|---|---|
| Solar member (NQ, from ledgers) | Lifetime $2.18/side + 1 tick/execution embedded |
| E10 executable (MNQ) | $0.65/side + 1 tick/execution on net target changes |
| New minute-bar engines (NQ) | **C1 = 2.872 t/RT** primary; **C2 = 4.872 t/RT** stress |
| Slip stress for Solar variants | slip-2 re-run (retention reported) |

A result that is positive only below these frictions does not exist.

## 4. Metric suite (every candidate, computed by one committed driver)

Net; **logG on $100k base** (geometric growth, the risk-normalized primary); Sharpe
(all-days, §2); Sortino; Calmar; max DD; median/95th-pct DD depth; Ulcer index; TUW and
longest recovery; ES5 (daily); worst day/week/month/quarter; % positive days/weeks/months;
longest losing streak in days/weeks/months; rolling 20/60/120-session minimum cumulative
P&L; top-1% trade share of net; top-10 day share; and for any Solar modification:
**top-1% trade retention, top-10 day retention, largest-winner table vs baseline**.

## 5. Statistical protocol (frozen)

- Bootstrap: circular **session-block bootstrap, block = 5, B = 10,000, seed 20260808**.
- Multiple arms within a family: Romano–Wolf stepdown, one-sided, non-studentized.
- Split-half stability: **H1 = 2022-01-01→2024-03-31, H2 = 2024-04-01→2026-05-31**
  (equal halves of the dev window; frozen here before any read).
- Chronological CV where used: day-grouped folds, ≥2-session embargo; no shuffling.
- Trial accounting: `research/registry/TRIAL_ACCOUNTING_RULE.md` continues to apply;
  every tested config gets a registry row (seq 291+). DSR is reported, never a gate
  (per its ABANDONED-as-criterion status).

## 6. Promotion gates (inherited from C01 §1, extended)

Any promoted overlay/engine/portfolio must satisfy ALL of:

1. Positive after base costs on CURRENT dev; survives stress cost (C2 / slip-2).
2. ≥ 3 of 5 dev years positive (2022, 2023, 2024, 2025, 2026-partial counts if ≥4 months).
3. Split-half same sign (H1/H2 of §5).
4. No single month > 40% of the candidate's net.
5. Complementary engines: **losing-day correlation with Family A ≤ +0.25**
   (full correlation is reported but is NOT a gate — owner directive §15/§19; this
   supersedes the scalping-lab ρ_full < 0.3 gate for portfolio-purpose evaluation).
6. **HARD RIGHT-TAIL GATE** for anything that modifies Solar exposure or exits:
   top-1% trade P&L retention ≥ 90% AND top-10 day retention ≥ 90% vs baseline; any
   state down-weighted below baseline must hold top-1% P&L share ≤ its session share.
7. Risk-normalized improvement: at matched realized dev vol (scalar on daily P&L),
   candidate logG must exceed baseline logG — leverage itself is never the improvement.
8. Nothing promoted may be a single selected parameter cell; plateaus/ensembles only.

## 7. Run governance

Every experiment: `runs/SM<nn>_<name>/spec.yaml` committed before results are read;
immutable run dirs; outputs referenced from the track's frontier doc. Zero-burn
instrumentation (reconstruction, parity, feature measurement with no trade rule) is
labeled INSTRUMENTATION in the spec and consumes no R1 trial, per audit precedent.

## 8. Finalist / holdout protocol

When the tracks converge: freeze `FINAL_PACKAGE_SPEC.md` naming every finalist (Solar
baseline; best Solar-overlay variant; B-MOM exact; qualified complementary engines; final
portfolio rules with frozen weights) — commit — then run the ONE joint read on
2026-06-01→2026-07-31, report all finalists jointly, and mark the holdout CONSUMED in
this file and in `research/scalping_lab/CONTAMINATION_LEDGER.md`. No iteration afterward:
post-read changes create a new candidate class that cannot claim the holdout.

## 9. Anti-hallucination labels

Every conclusion in every program document carries FACT (computed from committed data),
INFERENCE (derived, stated logic), HYPOTHESIS (untested), or EXTERNAL PRIOR (literature /
deep research, unverified locally). Recent-regime success is never converted to permanent
edge; drawdown reduction is never called alpha; leverage is never called improvement.
