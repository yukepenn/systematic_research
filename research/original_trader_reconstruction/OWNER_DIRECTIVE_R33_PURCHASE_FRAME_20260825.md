# OWNER DIRECTIVE R33 — PURCHASE FRAME CORRECTION (2026-08-25)

Recorded verbatim in substance from the owner's message following delivery of
`FINAL_ANSWER_20260825.md` / `PURCHASE_GATE_v3.md`. This directive AGREES with the action
conclusion (buy VWAP Flux, nothing else) but CORRECTS its justification and installs the
post-purchase protocol. It supersedes the *reasoning* sections of PURCHASE_GATE_v3 where they
conflict; the action verdict stands.

---

## 1. The corrected justification for the purchase

> **NOT** because we have proven the late-2026 system is "Solar + VWAP Flux".
>
> **BUT** because VWAP Flux is the only product where $300 materially collapses the core
> hypothesis space, and the only one with very strong direct linkage to the 2026 screenshots.

The $300 is to be understood as **buying an experimental instrument (a signal oracle)**, not as
"buying a profitable indicator". Research spend to reverse-engineer VF already exceeds $300 many
times over. The information value requires only that official VF can export per-bar
`Fair Value / rails / Signal_Trend / Signal_Trade / Signal_Cum_Delta`.

Supporting argument the owner highlights (good component-identification evidence): the VF-style
parameter tail `95/75/50/25/5/3/10/5` is present in the 3/22 **catastrophe** week too (92 trades,
28.26 % WR, avg win ≈ $909, avg loss ≈ $998, largest loss −$2,600). **The VF-style object was not
selected into winning weeks after the fact — it lived through the disaster week.**

## 2. Model ranking for the mature 2026 system (do NOT collapse to one)

1. **M1 (most likely):** VF-compatible core + author custom strategy wrapper
   (entry acceptance; re-entry; exit; hard risk; time/session; long/short handling; possibly
   volatility/exposure scaling; possibly extra internal state).
2. **M2:** VF-compatible core + one or more auxiliary signals (Solar / SJB / another ninZa
   component / author's own state machine) + custom wrapper. **No second product currently
   reaches VF's evidence strength.**
3. **M3 (fully possible):** mature VF-style strategy + a separate Solar-derived sleeve at
   account level. AS-1 (several strategies simultaneously) directly supports the plumbing.

**Standing prohibition:** never promote "Solar demonstrably existed in 2023–25" into "the August
Strategy Analyzer strategy internally uses Solar".

## 3. Owner-assessed prior structure (OWNER PRIORS — distinct from measured evidence levels)

| proposition | owner prior |
|---|---|
| VF-compatible core present in the main 2026 lineage | ~85–95 % |
| author custom wrapper is a key part | > 90 % |
| Solar still somewhere in the 2026 **account** | ~50–70 % |
| Solar inside this specific VF strategy | ~25–45 % |
| ≥ 1 additional ninZa signal inside the mature strategy | ~25–45 % |
| full DOM/L2 alpha as the main system | < 20 % |

## 4. Purchase table (current)

| product | may participate in late build? | buy now? |
|---|---|---|
| **VWAP Flux** | very high | **YES — first and only** |
| Solar Wave | 2023–25 established; 2026 unknown | NO — already researched to recovered-math depth |
| Super JumpBoo$t | interesting; leading second candidate (~30–45 %) | NOT YET — residual-driven |
| Bollinger %B Pro | downgraded from old-thread 75–80 % to **~15–30 %** | NO — build free %B proxy first (20, 2σ, 30/70 is trivial math; only the Pro momentum/resume/trend state is proprietary) |
| Multi-Osc | ~10–20 %; retire the 65/30/75/20/46/36 mapping | NO — free MFI∧RSI∧Stoch overlap proxy first |
| ApexFlow | possible, no direct evidence | NO |
| Cosmik | possible, weak | NO |
| Gravity / Entropy / DeepStack | release-date + behaviour **narratives only** | NO — low-priority pool |
| ThunderZilla | evidence declined | NO |
| Infinity / Captain | possibly meta-architecture analogues of the author's own wrapper | NO |
| King Kong RK | bundle; question malformed | void |

The old "other quant signals" thread is repositioned: **it is the 2026 vendor/module hypothesis
LIBRARY, not a fact table.** Its "buy five products for Replica V1" plan is withdrawn. Correct
statement of coverage: we may know ~60–70 % of the **functional categories** (direction, value/
location, trend quality, pullback/resumption, risk, time/session, exit, possibly flow, possibly
multiple sleeves) — we do NOT know 60–70 % of the **product identities** filling them.

## 5. Post-purchase protocol (mechanical, in order)

**Phase 1 — vendor parity.** Author's exact parameters: NQ 1-minute, `BidAskPrice_RealVolume`,
Anchor 60, VWAP Amount 5, Trend Period 20 EMA, levels 95/75/50/25/5, then 3/10/5. Run the
author's key windows. Export per bar: Fair Value, Max, Upper, Median, Lower, Min, `Signal_Trend`,
`Signal_Trade`, `Signal_Cum_Delta`.

**Phase 2 — retire the clean-room Layer A.** Official output becomes the oracle. Stop debating
anchor style, percentile vs linear, CloseThreshold semantics.

**Phase 3 — wrapper-only inverse problem.** Starting from official `Signal_Trade`, test: entry
immediately vs next bar; trend-state required; resumption required; per-trend allowance and its
reset; reverse vs flat; exit on opposite / on trend change / at Fair Value; fixed stop; any other
visible custom state. **This is the correct inverse problem.**

**Residual-driven second purchase rule.** Only if official-VF parity still leaves a large,
structured mismatch:
- missing trades concentrate at value/zone locations → raise SJB;
- concentrate in order-flow states → raise ApexFlow;
- concentrate in legacy trend direction → raise Solar/Cosmik;
- no vendor state explains them → author custom logic.
Never buy a basket up front; the search space must be paid down one residual at a time.

## 6. The frozen-build test (the eventual decisive experiment)

If/when a `MATURE_AUGUST_2026` candidate is recovered: **freeze it**, then run 2022–2026
uniformly with real commission, slippage, rollover and NT8 fill semantics; report annual net,
PF, Sharpe, DD, worst week, both tails, regime dependence.

- Still strong → a genuinely tradeable object has been found.
- Not strong → what we reconstructed is **the author's evolving research process shown
  retrospectively, not a fixed persistent edge** — and that answer must be accepted.

Three selection caveats forbid reading "many positive screenshot weeks" as "the frozen August
build wins weekly": (1) the author continuously changed versions (Class A); (2) multiple
strategies ran simultaneously (Class A); (3) the screenshots are not a pre-frozen forward record.

## 7. Where the alpha probably is not

The money structure across 2026 is **positive skew** (WR ≈ 35–45 %, E[win] ≫ E[loss], a few
right-tail winners of $11.7k/$13k/$15k/$18k/$22.5k class), not high WR. So the residual gap is
more plausibly **context + entry location + position management + exits + risk cap + exposure by
market state + parallel sleeves** than "four more alpha indicators". Consistent with R29/R30.

Campaign-side nuance retained (audit): the ATR–hold power law is **not diagnostic even of exit
class** (a known state-based 2023 exit also yields b ≈ −0.84), and `corr(ATR, avg_loss) = −0.51`
is a pooled feature with **no out-of-sample support**. These remain flags, not foundations.

## 8. Standing verdict on the session's epistemics

Owner concurs with the audit's diagnosis — "arithmetic right nearly everywhere, quantifiers too
strong nearly everywhere" — and instructs that conclusions of the form "therefore 2026 is
definitely Solar + VF" or "the other ninZa are all excluded" are exactly the relapse to avoid.
