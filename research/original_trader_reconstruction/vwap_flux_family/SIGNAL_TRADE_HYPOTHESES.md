# SIGNAL_TRADE_HYPOTHESES — status after R7/R7b (2026-08-24)

## Pinned semantics (manual, EV-038; no longer hypotheses)
- Split=5: min bars between consecutive SAME-direction signals.
- QtyPerTrend=3: max same-direction signals per trend/zone episode (reset rule
  member-tested: episode = trend-state run; alternatives not yet separable).
- CloseThreshold=10: candle-close-location filter. Orientation readings:
  H1a (close in extreme 10% TOWARD signal — strict momentum-close),
  H1c (manual-verbatim: exclude only the 10% extreme AGAINST — nearly-open),
  H1b (extreme against) REJECTED (degenerate).

## Surviving model cluster (OTR-VF-CAND1, §6 members kept)

| member | mean §40 | worst | failure-week net (tgt −42,235) | note |
|---|---|---|---|---|
| **T_C\|P_MED\|C_DIR\|H1a\|X_OPP** | **0.476** | 0.905 | −9,730 | LOWO leader 13/17 |
| T_C\|P_MED\|C_DIR\|H1a\|X_OPP\|strong | 0.492 | 0.922 | −5,135 | 4-state variant |
| T_C\|P_Q75\|C_REC\|H1a\|X_OPP | 0.501 | 0.827 | −17,870 | |
| T_D\|P_IN\|C_REC\|H1c\|X_FLIP | 0.514 | 0.755 | **−26,535 (63%)** | best catastrophe geometry + manual-verbatim CLV |

DQ'd per §32: T_C|P_MED|C_REC|H1a|X_OPP (mean 0.479 but PROFITABLE +2,970 in
the −42k week).

Common structure across the cluster: trend episode → pullback toward the cloud
core (Median or rail) → close-quality confirmation → entry; SAR-or-flip exit;
QtyPerTrend/Split as indicator-side suppression; fixed 130-pt stop (§33).

## The plateau and what it means
Every structurally distinct member converges to mean distance 0.48-0.52 with
right-scale trade counts (~1.2-1.8k vs ~1.2k target) and right failure-week
SIGN but 23-63% magnitude. Interpretation (consistent with R3's preregistered
clone boundary): the remaining residual is the exact trigger composition, not
the architecture. On 1-min bar data with weekly aggregates as the only labels,
the members are NOT further separable — declared inseparable per §6.

## What would separate them (§45 bookkeeping)
1. Signal_Trade TIMESTAMPS for any single day (oracle or a chart frame with
   visible signal arrows + readable times) — separates all four immediately.
2. Higher-frequency labels (a per-day 2026 Analyzer table like OTRIMG-0003).
3. NOT the $300 purchase alone: per EV-039 the licensed indicator cannot
   reproduce the trader's displayed historical mode, and under the leading
   H3/H4 reading his stream comes from his OWN implementation anyway —
   the vendor oracle answers vendor semantics, not his build's.
