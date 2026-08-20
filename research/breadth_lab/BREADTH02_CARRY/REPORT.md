# BREADTH02 — REPORT (readout 2026-08-19; spec frozen at dd8f08e BEFORE any statistic)

**Verdict: FAIL — genuinely, not by power. The free-data carry construction is dead in the
modern regime. CLOSED one-shot (no tenor/window/universe re-skins).**

## Numbers

- Book: Sharpe **0.136**, ann +0.97% at 7.2% vol, 2003-2026. G2 year-block CI
  [−1.67%, +3.77%] — spans zero → FAIL.
- **G3-ERA (the corrected gate, working exactly as designed)**: pre-2020 +2.88%/yr
  (CI [−0.37, +6.07]) but post-2020 **−4.08%/yr** (CI [−10.1, +2.2]); halves Sharpe
  **0.36 / −0.09 opposite signs** → FAIL. Five consecutive losing years 2022-2026
  (−8.5% / −6.8% / −4.1% / −6.2% / −6.8% ann-rate). This is a sign failure, not a CI
  technicality — the spec's own §7 prediction ("equity D/P−rf shorts equities in bull
  markets; the 2022 inversion is the acid test") fired in full.
- G5 complementarity: ρ_full 0.014 / ρ_losing −0.010 fine, but the book LOSES on Solar
  losing days (−1.47%/yr) → FAIL.
- G7 stress: CI spans zero → FAIL. G6 blend passed (diversification arithmetic — moot).
- Sleeves: bond slope carry Sharpe 0.23, equity div-yield carry 0.09, sleeve ρ −0.15;
  correlation to the closed BREADTH01 trend book −0.12 (the style-diversification premise
  itself was real; the sleeves just don't pay post-2020 in this form).

## Interpretation

Koijen et al's per-class carry Sharpes (FI slope 1.03, equity 0.91) came from futures-implied
carry across many countries in a 1983-2012-heavy sample. The free-data US-heavy proxy
version — treasury slope + realized D/P−rf — is a rates-level bet that the 2022-2026 regime
inverted. An honest carry book would need futures term-structure data across many markets
(the owner-gated breadth-funding decision). On free data, the carry family is closed.
No red team needed (FAIL, nothing adopted). Artifacts: `out/breadth02_results.json`,
`out/book_daily_carry.csv`, `data/MANIFEST.json`. Mask ≤2026-05-31 held.
