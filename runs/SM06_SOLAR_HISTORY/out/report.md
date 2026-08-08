# SM06 — Frozen Champion on Unseen 2006-2021: REGIME_LOCAL

_2026-08-08. Spec + interpretation rule frozen and committed BEFORE this read
(`runs/SM06_SOLAR_HISTORY/spec.yaml`). Exact SM01-certified code, exact champion
parameters, zero tuning. Data: nq1m_2005_202605.parquet (< 2022-01-01) resampled 3-min
via the GATE_D-verified exact aggregator. First 20 sessions excluded (warmup)._

## Verdict (frozen rule): **REGIME_LOCAL**

- Pooled 2006-2021: net **−$8,970** over 4,110 sessions; mean −$2.18/day,
  95% CI [−$22.30, +$18.68] — fails STRUCTURAL (CI_lo ≤ 0) and fails
  REGIME_SENSITIVE_POSITIVE (pooled net < 0). Not CONTRADICTED (CI_hi > 0). FACT
- Positive years: **4 of 16** (2008 +$1.5k, 2017 +$9.0k, 2020 +$36.1k, 2021 +$11.1k). FACT
- Blocks: 2006-09 **−$19.6k (CI_hi < 0)**, 2010-13 **−$20.4k (CI_hi < 0)**,
  2014-17 −$8.6k (n.s.), 2018-21 **+$39.6k** (n.s., CI [−32.7, +112.2] per-day). FACT
- Sharpe −0.051; max DD −$62,588 (research-basis MNQ×10 scale, same as dev champion). FACT

## What this changes

1. **The Solar edge is itself a late-regime phenomenon** (economically 2020+; the dev
   window 2022-2026 sits inside it). The engine's mechanism (vol-normalized close-basis
   persistence harvesting) had no positive expectancy for at least 2006-2017. FACT
2. **B-MOM symmetry.** B-MOM was parked partly because its 2022+ edge "shares Solar's
   regime fuel" (pre-2022 PF 1.013). Solar now shows the SAME shape (pre-2022 net < 0).
   Neither engine is structural; both are current-regime engines. The portfolio question
   (SM05) is therefore between peers, exactly as the owner directive framed it. INFERENCE
3. **Frozen consequence applied:** stop/exposure overlay *calibration* is dev-only.
   The 2006-2017 stretch is retained as an adversarial STRESS diagnostic for overlay
   candidates (a live regime-death simulation: any DD-protection layer should shrink the
   historical −$62.6k DD without being fit to it). INFERENCE/rule
4. **Regime identification rises in EVI.** The difference between dead (2006-2017) and
   alive (2020+) epochs is the single most valuable state variable for the final system.
   MONITOR-01's overshoot ratio r is the designated statistic; computing banded r over
   2006-2021 (zero burn, dc_overshoot.py) is queued as SM06b to test whether r would have
   flagged the dead regime ex ante. HYPOTHESIS to test
5. The program's current-regime framing (CONVENTIONS §1: dev-primary, history as
   fragility lens) is now evidence-backed, not just mandated. FACT+INFERENCE

## Caveats (preregistered)

Modern cost model held constant (2006-2010 commissions were higher; slip-1 likely
optimistic in thin pre-2010 overnight hours — the negative verdict is thereby, if
anything, understated). Pre-2012 session structure differs (gap-based session detection).
Back-adjustment offsets cancel in the difference-based engine. MNQ scalar anachronistic
pre-2019 (research basis only).

Outputs: `e10_daily_hist.csv` (4,130 sessions), `member_trades_hist.parquet` (~114k
trades), `vote_state_3m_hist.parquet`, `result.json`.
