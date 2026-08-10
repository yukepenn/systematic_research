# LEV02 — causal trailing leverage-effect regime: CLEAN NULL

**Disposition: CLOSED — no signal.** The non-confounded, strictly-causal version of LEV01's own
Test 2 idea finds nothing. This is an important, clarifying result: it confirms LEV01's original
compelling-looking finding (t=4.45) really was entirely a sunk-P&L artifact, not a weaker-but-real
signal that a cleaner test might have partially recovered.

## Construction (causal, verified)

`trailing_asymmetry[s]` = (mean vol_change over sessions in the trailing 120-session window,
ending 5 sessions before s, where the session's own return was negative) minus (same, where
return was non-negative). Explicit causal proof: the latest session contributing to
`trailing_asymmetry[s]` is session `s-5`, and that session's own `vol_change` label (from LEV01's
substrate) was itself realized using forward data only through session `s-5+5 = s` — so by
construction, no information later than session `s` is ever used. 1,014/1,139 canonical sessions
have a valid trailing regime value (first 125 sessions lack sufficient trailing history).

## Test A — does regime predict Product-B entry outcomes?

Raw Spearman(regime, block_net_pnl) = **0.0055** (n=1,694) — essentially zero. OLS: adding
`regime` on top of contemporaneous `sigma460` improves R² by only +0.00067 (0.00420→0.00487).
Regime coefficient t=−1.07 — not statistically distinguishable from noise.

## Test A2 — split by side

Shorts (n=913): raw ρ=0.0163. Longs (n=781): raw ρ=−0.0047. Neither meaningfully different from
zero; no side-specific pattern emerges.

## Year-by-year stability

| year | n | ρ |
|---|---:|---:|
| 2022 | 228 | −0.0038 |
| 2023 | 437 | +0.0249 |
| 2024 | 420 | +0.0698 |
| 2025 | 436 | +0.0198 |
| 2026 | 173 | −0.0328 |

No consistent sign, no discernible pattern — this is what pure noise looks like across 5 years.

## Test B — Product-A SCALE_IN forward outcomes

Raw Spearman(regime, fwd20_pnl) = **−0.0057** (n=6,997) — again essentially zero.

## Too-good-to-be-true re-check

Max |ΔR²| across this family = 0.00067, far below the 0.02 trigger — no further confound
investigation warranted (there is no surprising result to investigate).

## Verdict

**Clean null.** Once the predictor is genuinely causal and non-overlapping with trade
resolution, there is no detectable relationship between recent leverage-effect strength and
forward Product-B or Product-A performance, in either direction, at any horizon tested, in any
year. This retroactively strengthens confidence in LEV01's Test 2 confound diagnosis: the
originally compelling t=4.45/3.33 finding was not a weaker-but-real signal masked by a
measurement flaw — it was entirely the sunk-P&L artifact, full stop. The market-structure fact
from LEV01 Test 1 (NQ genuinely exhibits the leverage effect) remains true and interesting on its
own terms, but does not translate into any detectable trading-relevant regime signal for this
system. No candidate constructed. Product A and Product B remain unchanged.
