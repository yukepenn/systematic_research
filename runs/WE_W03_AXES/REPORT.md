# WE_W03 — AXES · REPORT (run 2 of record, after amendment 1 look-ahead correction)

Spec preregistered; **amendment 1**: the first run's context gates used the entry bar's CLOSE
to admit fills at its OPEN (one-bar look-ahead), caught in self-review before any freeze.
Masks lagged; full rerun. Run-1 numbers (incl. a headline dev Sharpe 0.355) are VOID and
preserved only in `out/run1.log`.

## Corrected headline

**1 config clears the dev tail bar**: `S4.all13.h1300.gdl` — dev $1,233/wk · 56.5 % ·
worst **−$12,915** · Sharpe 0.217 · **$110.5/trade (above his $103)** · stress-positive.
Holdout confirm **FAIL** (0.151 < 0.30) → **no champion**, per prereg.

## What the correction changed, and what survived

| finding | pre-correction | post-correction |
|---|---|---|
| delta gate | transformative (0.355 member) | **real but modest**: +0.02–0.03 Sharpe on portfolios (0.253 vs 0.226 baseline); best gated rows still outrank ungated |
| session halt (h1300) | works | **unchanged — works** (causal by construction); still the only mechanism that gets a config under −$15k |
| per-trade expectancy | $143.9/trade | **$110.5/trade — still above his $103** |
| narrow6 members | best family | ordinary; the fast-member glow was mostly the look-ahead |
| MO / CD standalone | dead / marginal | unchanged (no gates involved) |

Top corrected portfolio: `S1.none+S4.all13.h1300.gdl` dev 0.253 · $2,631/wk · 60.0 % ·
worst −$26,968; holdout 0.589. The ungated W01-era P2 (0.226) is beaten but not crushed.

## Lessons entered into the campaign record

1. **The one-bar close-vs-open trap**: any mask indexed at the fill bar must carry only
   decision-bar information. Now a standing check for every new gate.
2. The self-review that caught this was triggered by the owner's question "赚的钱可以解释吗" —
   *explainability review before freeze* is now a mandatory step (it just paid for itself).
3. Post-correction, the campaign's mechanism ranking is: **session halts (strong, causal) >
   delta context gate (modest, real) > everything else tried**.

## Next
W05A explainability diagnostics on the corrected candidates; freeze decisions only after it.
Holdout is exhausted (4 reads); arbiter = virgin ≥ 2026-11-01 read.
