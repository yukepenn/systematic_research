# EXECUTION_REALITY — what live fills actually cost (evidence, not assumptions)

_2026-08-08. Sources: grid1s L1 substrate (2025-08→2026-05, 40 sessions), SMV2B stress
arms, NT8 Analyzer parity run._

- **Modern NQ RTH spread: ~3 ticks median (0.75 pt), p90 4t** (2026-05 sample; L1
  bid/ask direct). A market order pays ≈1.5t vs mid per side. MNQ spreads are wider in
  ticks at times; MNQ fills at 10× count.
- **Research fill convention**: next-bar-open ±1 tick capped by bar range. With ~3t
  spreads, the honest live band is the SMV2B E3–E4 corridor (+1 to +2t/side beyond
  next-open): B-MOM standalone Sharpe 1.31 → plan on 1.20-1.26 live-basis.
- **Commissions (Lifetime)**: NQ $2.18/side ($4.36/RT); MNQ $0.65/side ($13.00/RT per
  10-MNQ). Per 10-MNQ-equivalent, NQ is $8.64/RT cheaper; over dev that is $17.2k on
  the one-lot strategy — effectively the whole MNQ-vs-NQ Sharpe gap. Never divide NQ
  commission by 10.
- **B-MOM artifacts carry C1 (2.872t/RT) stress friction** — $10/RT more than actual;
  reported portfolio numbers are conservative by that margin.
- **Timing**: OneLot decisions at 3-min bar close, fills next bar open (verified
  identical in NT8 Analyzer: 100% entry-price match). Day-margin flatten decided at
  the 16:39 bar close, filled 16:42 — confirmed in the NT trade log (all forced exits
  stamp 16:42). No entries 16:30→18:03. Early closes: session-close backstop.
- **Slippage sensitivity**: every +1t/side costs the one-lot NQ strategy ≈ $6.6k/yr at
  ~1,970 round trips / 4.4yr (≈450 RT/yr × $10/RT... computed: 450×$5/t×2 sides ≈
  $4.5k/yr per tick). The system survives C2 (2×C1) on all promoted objects.
