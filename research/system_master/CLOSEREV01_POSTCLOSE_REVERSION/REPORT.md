# CLOSEREV01 — REPORT (readout 2026-08-19; spec frozen at be9b993 BEFORE the run)

**Verdict: FAIL — the post-cash-close pressure-reversion family is CLOSED on this substrate
(one shot, per spec). First alpha hypothesis of the new wave (1 of 2).**

## Numbers (N=325 triggers over 20 years, audited cost model 1.5t/side + $4.36/RT)

- Net **−$2,117** (−$6.5/trade); iid CI [−57, +41]; episode CI [−58, +43] — G2 FAIL.
- **G3-SPLIT (the new primary gate) FAIL**: pre-2020 −$25.4/t (n=219, CI [−50.6, +0.7] — nearly
  significantly NEGATIVE); post-2020 +$32.5/t (n=106, CI spans zero widely).
- G6 plateau FAIL: 6 of 9 cells negative (only z2.0×15:30-window at +$27/t; sign-scatter, no
  plateau). G7 tails degenerate (|net|≈0 makes shares meaningless — fails as constructed).
  G9 stress (2t/side + 3× comm) FAIL: −$20/t.
- **G5 placebo is itself significantly NEGATIVE** (n=3,624, −$12.5/t, CI [−22.7, −2.3]): fading
  ordinary impulses into the post-close loses steadily — the fade direction has no general edge
  and the audited spread cost eats everything at the margin.
- Era trend: 2006-2015 −$33.8/t → 2016-2026 +$19.6/t. The literature's direction (rising closing-
  auction pressure) is weakly visible but two orders of magnitude short of economics — and
  entirely non-significant. G8 orthogonality was as predicted (corr −0.15) — irrelevant now.

## Interpretation (honest, one paragraph)

The genuinely virgin 16:00-16:14 window was worth exactly one shot, and the answer is that
index-level netting plus the audited 2-3-tick post-close spread leaves nothing tradable at
retail latency: the point estimate is a rounding error either side of zero in every era. The
scout's viability arithmetic assumed a 15% reversion of the impulse; the measured reversion is
~0. No red team needed for a FAIL of this magnitude (nothing is being adopted; the frozen
one-shot rule closes the family). The BBO feasibility-audit machinery (pre-outcome cost-model
freeze) worked exactly as designed and is retained for future execution-sensitive specs.

Artifacts: `out/closerev01_{results.json,trades.csv,placebo_trades.csv}`. Substrate ends
2026-05-29; seals untouched. Registry row this commit.
