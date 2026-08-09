# RESEARCH_FRONTIER — navigation table for the post-parity RESEARCH campaign

Started 2026-08-09 (MEGA RESEARCH DIRECTIVE, same day the parity/repo-consolidation campaign
closed — see `/RESEARCH_HANDOFF.md`). Superseded/absorbed same day by the SYSTEM ARCHITECTURE
SCIENCE + ALPHA OPTIMIZATION MEGA DIRECTIVE, which reprioritizes the queue to
SA0 → R3 → R2B → R4 → R5 → R6 → PA0 → PA1 → SYN (see that section below). This is navigation, not
a report: one row per family, kept current after every run. Full evidence lives in each
`runs/<FAMILY>/REPORT.md`.

| Family | Hypothesis | Status | Best candidate | Evidence | Why alive/dead | Next action |
|---|---|---|---|---|---|---|
| P0 | Owner's April-2026 "Solar reversed, B-MOM/M kept a stale short hold" hypothesis, generalized trade-state autopsy | **CLOSED** | n/a (diagnostic) | `runs/P0_TRADESTATE_AUTOPSY/REPORT.md` | Literal hypothesis REFUTED (B-MOM flat 0.0 in both flagged trades); stronger giveback/decay mechanism found and generalized (Spearman -0.656, 100%/0% separation at bottom/top decile) | Motivated R1; no further action, diagnostic complete |
| R1 (adaptive exit / giveback) | Giveback-conditioned early exit reduces catastrophic losers without destroying right-tail winners | **CONFIRMED-NOT-BENEFICIAL** | C03 (giveback>=0.65, floor $300) — still not promotable | `runs/R1_ADAPTIVE_EXIT/REPORT.md` | Every candidate (12 + 3 ATR-stop benchmarks) has lower Sharpe/Sortino than incumbent on both NQ/MNQ; best candidate is net tail-dollar-negative (-$80k winners vs +$32k losers), MNQ-divergent, chronologically unstable (2023 outlier) | Closed. Do not re-tune this grid. A materially different state variable (distinguishing true reversal from in-trend consolidation) would need its own new preregistration, not this family reopened |
| R2 (entry timing/pullback) | Conditional entry confirmation (persistence, pullback-then-reclaim) improves entry quality without suppressing rare right-tail entries | **CLOSED — NOT PROMOTED** | confirm_bars=2 entry-confirmation overlay (`SolarWaveOneContractNQ_v6_R2CONFIRM.cs`, archived as rejected evidence) | `runs/R2_ENTRY_TIMING/R2V1_VERDICT.md` (binding), `REPORT.md`/`NT8_VALIDATION.md` (superseded first-pass) | Full-history headline (+8.6% net, Sharpe+11%) is ENTIRELY a 2026-stub artifact: 2022-2025-only delta is -$4,431 (a wash), LOYO-2026 confirms exactly, and confirm_bars=1 shows the identical pattern (not candidate-specific). True mechanism: 93% of entries are a pure 2-bar delay (net COST -$81.6k), net improvement comes only from the 7% of entries the delay redirects/cancels (+$106.8k) -- a thin, concentrated edge. Early NT8 parity PASSED (149/149) but that only confirms faithful implementation, not a real edge. | None -- closed, do not re-tune ConfirmBars without new information |
| **SA0 (system structure / failure-mode science)** | Explanatory: why does Product B work, where does it fail, which components are load-bearing/redundant | **CLOSED — diagnostic complete, no candidate** | n/a (diagnostic) | `runs/SA0_SYSTEM_STRUCTURE/REPORT.md`, `research/system_master/STRUCTURE_MAP.md` | Structural ablation (SOLAR_ONLY/BMOM_ONLY/NO_HTF_TILT/NO_HYSTERESIS_GAP), score-mixing sensitivity (no fragile point found), Solar13 ensemble diversity (participation ratio 3.66/13, local not global redundancy), HTF/B-MOM attribution (B-MOM structurally cannot solo-enter, |WBMOM·B|<3.0 always, but has standalone Sharpe 1.26), failure-mode atlas (C4-forced exits win 75% vs voluntary M-driven exits' 24%), long/short asymmetry (shorts Sharpe 0.18 vs longs 1.54, 9.7x higher tail concentration), April/top-20-loser matched-control science (matched-winner-rate ≈ unconditional rate — no entry-state signal separates these losers) | Motivates R3 (session×state, not blanket window) and flags 2 new facts (C4-exit superiority, short weakness) for a POSSIBLE future family — not acted on this run |
| R3 (liquidity-conditioned eligibility) | Time-of-day as continuous state (x signal strength/volatility), not a blanket exclusion like closed S2 | **IN PROGRESS** | — | — | — | Immediately after SA0 |
| R2B (pullback→reclaim) | Shallow adverse pullback + directional reclaim, distinct from the closed fixed-delay R2 axis | QUEUED — audit existing R2 evidence first | — | — | — | After R3 |
| R4 (new-info diagnostics: slope, explosive candle) | Regression slope / range-over-ATR contain residual information beyond Solar/HTF/B-MOM/vol | QUEUED | — | — | — | After R2B |
| R5 (microstructure/order-flow scout) | Volume/range-based proxies add information conditional on incumbent decision state | QUEUED | — | — | — | Data inventory first (3-min OHLCV only, confirmed no L2/tick order-flow in this campaign's data — see scalping_lab substrate, which is a SEPARATE, unrelated campaign) |
| R6 (orthogonal Engine-3) | A genuinely low-correlation, non-price-momentum mechanism exists | QUEUED, low priority | — | Prior wave: 15 candidates/5 slates/0 survivors (`research/system_master/COMPLEMENTARY_ENGINE_FRONTIER.md`) | Bar is high; only test if a genuinely new idea surfaces | Do not manufacture a candidate merely to fill the slot |
| PA0/PA1 (Product A structure + sizing) | Alpha-vs-sizing decomposition, exposure-path science; sizing candidate only if diagnostics support one | QUEUED | — | — | — | After R3-R6 |

## Campaign stop condition (directive sec40 [MEGA RESEARCH DIRECTIVE] / sec60 [SYSTEM ARCHITECTURE SCIENCE DIRECTIVE])

Not yet met. Continue through SA0 → R3 → R2B → R4 → R5 → R6 → PA0 → PA1 → SYN until either a
candidate is PROMOTED, or every family closes as REJECTED / CONFIRMED-NOT-BENEFICIAL /
INCONCLUSIVE / CLOSED. No families beyond this list without new information per the standing
discipline.

## Standing constraints (do not re-litigate)

- Incumbents (`SolarWaveSMMaster_v4`, `SolarWaveOneContractNQ_v5`, `SolarWaveOneContractMNQ_v5`)
  are frozen controls during exploratory research; only a formally promoted candidate replaces one.
- Product B (BEST_ONE_NQ/MNQ) is one shared decision core (`theta_NQ = theta_MNQ`) — every
  candidate is evaluated as one decision sequence priced on both instruments' genuine economics.
- S2_SELTIME's exact frozen construction (02:00-08:00 ET blanket block) is CLOSED, NOT PROMOTED —
  not to be rerun with a shifted window and called new; R3 studies time as continuous state instead.
- No live trading authorization exists or is implied by any research in this campaign.
