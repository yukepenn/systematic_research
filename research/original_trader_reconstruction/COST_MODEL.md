# COST MODEL — two strictly separated layers (§28, §44)

## LAYER 1 — SCREENSHOT PARITY (behavioral reconstruction)

Match the displayed assumptions of the screenshot being reconstructed:
- Slippage = 0 (as shown in Strategy Analyzer screenshots)
- Commission: match the screenshot (often $0 displayed; some had Include Commission
  selected, some not; Trade Performance reports show real commission — e.g. $141.20 on
  136 trades ≈ $1.04/trade side-pair → consistent with author's "~$2 RT" estimate class)
- Historical fill: Standard (Fastest); Fill limit on touch OFF unless shown otherwise
- NEVER inject realistic costs into a parity comparison and then call the mismatch a
  reconstruction failure.

## LAYER 2 — ECONOMIC REALITY (after a candidate is frozen)

Run separately, only on frozen candidates:
- Commission: author's ~$2 RT (his statement) AND our known NinjaTrader Brokerage
  Lifetime $4.36/RT (repo standard) — report both
- Slippage sensitivity: 0 / 1 tick per side / 2 ticks per side / higher stress where
  informative
- Author's rough adjustment (profit ×0.9, loss ×1.1) evaluated as a CONSISTENCY CHECK
  ONLY — never hard-coded as execution physics
- Never assume the author's real slippage was zero; he explicitly acknowledged slippage.

## Reporting rule (§44)

For each final candidate: (1) screenshot-style result → (2) realistic commission →
(3) realistic commission + slippage stress. Question 1 ("did we reconstruct the reported
behavior?") and question 2 ("what was that behavior economically worth?") are never mixed.
