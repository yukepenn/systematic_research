# RESEARCH_FRONTIER — navigation table for the post-parity RESEARCH campaign

Started 2026-08-09 (MEGA RESEARCH DIRECTIVE, same day the parity/repo-consolidation campaign
closed — see `/RESEARCH_HANDOFF.md`). This is navigation, not a report: one row per family, kept
current after every run. Full evidence lives in each `runs/<FAMILY>/REPORT.md`.

| Family | Hypothesis | Status | Best candidate | Evidence | Why alive/dead | Next action |
|---|---|---|---|---|---|---|
| P0 | Owner's April-2026 "Solar reversed, B-MOM/M kept a stale short hold" hypothesis, generalized trade-state autopsy | **CLOSED** | n/a (diagnostic) | `runs/P0_TRADESTATE_AUTOPSY/REPORT.md` | Literal hypothesis REFUTED (B-MOM flat 0.0 in both flagged trades); stronger giveback/decay mechanism found and generalized (Spearman -0.656, 100%/0% separation at bottom/top decile) | Motivated R1; no further action, diagnostic complete |
| R1 (adaptive exit / giveback) | Giveback-conditioned early exit reduces catastrophic losers without destroying right-tail winners | **CONFIRMED-NOT-BENEFICIAL** | C03 (giveback>=0.65, floor $300) — still not promotable | `runs/R1_ADAPTIVE_EXIT/REPORT.md` | Every candidate (12 + 3 ATR-stop benchmarks) has lower Sharpe/Sortino than incumbent on both NQ/MNQ; best candidate is net tail-dollar-negative (-$80k winners vs +$32k losers), MNQ-divergent, chronologically unstable (2023 outlier) | Closed. Do not re-tune this grid. A materially different state variable (distinguishing true reversal from in-trend consolidation) would need its own new preregistration, not this family reopened |
| R2 (entry timing/pullback) | Conditional entry confirmation (persistence, pullback-then-reclaim) improves entry quality without suppressing rare right-tail entries | QUEUED | — | — | — | Diagnostic phase next |
| R3 (liquidity-conditioned eligibility) | Time-of-day as continuous state (x signal strength/volatility), not a blanket exclusion like closed S2 | QUEUED | — | — | — | After R2 |
| R4 (new-info diagnostics: slope, explosive candle) | Regression slope / range-over-ATR contain residual information beyond Solar/HTF/B-MOM/vol | QUEUED | — | — | — | After R3 |
| R5 (microstructure/order-flow scout) | Volume/range-based proxies add information conditional on incumbent decision state | QUEUED | — | — | — | Data inventory first (3-min OHLCV only, confirmed no L2/tick order-flow in this campaign's data — see scalping_lab substrate, which is a SEPARATE, unrelated campaign) |
| R6 (orthogonal Engine-3) | A genuinely low-correlation, non-price-momentum mechanism exists | QUEUED, low priority | — | Prior wave: 15 candidates/5 slates/0 survivors (`research/system_master/COMPLEMENTARY_ENGINE_FRONTIER.md`) | Bar is high; only test if a genuinely new idea surfaces | Do not manufacture a candidate merely to fill the slot |

## Campaign stop condition (directive sec40)

Not yet met. Continue through R2-R6 until either a candidate is PROMOTED, or all of R1-R6 close
as REJECTED / CONFIRMED-NOT-BENEFICIAL / INCONCLUSIVE / CLOSED. No R7+ without new information
per the standing discipline.

## Standing constraints (do not re-litigate)

- Incumbents (`SolarWaveSMMaster_v4`, `SolarWaveOneContractNQ_v5`, `SolarWaveOneContractMNQ_v5`)
  are frozen controls during exploratory research; only a formally promoted candidate replaces one.
- Product B (BEST_ONE_NQ/MNQ) is one shared decision core (`theta_NQ = theta_MNQ`) — every
  candidate is evaluated as one decision sequence priced on both instruments' genuine economics.
- S2_SELTIME's exact frozen construction (02:00-08:00 ET blanket block) is CLOSED, NOT PROMOTED —
  not to be rerun with a shifted window and called new; R3 studies time as continuous state instead.
- No live trading authorization exists or is implied by any research in this campaign.
