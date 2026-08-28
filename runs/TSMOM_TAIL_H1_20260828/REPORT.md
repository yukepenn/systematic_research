# TSMOM-TAIL-H1 — FAILED. TSMOM is closed for this campaign.

| | |
|---|---|
| **verdict** | **4 of 5 gates FAIL. TSMOM CLOSED — steady-premium role failed, tail-diversifier role failed.** No H2 |
| spec committed | `30d7cff`, **before** the read |
| window | **2023-01-01 → 2026-05-30**, 178 evaluated weeks, one shot |
| evidence class | **ONE-SIDED BLIND TSMOM HISTORICAL HOLDOUT** — TSMOM leg blind, incumbent leg discovery-consumed |
| seal | ≥ 2026-08-01 blocked by a hard substrate cap **and** a runner assertion |

---

## 1. The gates

| gate | observed | |
|---|---:|---|
| **H1-G1** Δ fixed-DD $/wk > 0 | **−$1,602.43** | **FAIL** |
| **H1-G2** paired bootstrap lower 95 % > 0 | **−$2,115.80** | **FAIL** |
| **H1-G3** Δ fixed-DD > 0 at STRESS | **−$1,656.85** | **FAIL** |
| **H1-G4** mean TSMOM in incumbent's worst decile > 0 | **−$169.70** | **FAIL** |
| H1-G5 combined ES5 % not worse | +$3,726.11 | PASS |

## 2. What the numbers say

| object | $/wk | **fixed-DD $/wk** | maxDD | ES5 % | positive wk | t |
|---|---:|---:|---:|---:|---:|---:|
| **TSMOM standalone** | **−$4** | **−$8** | $10,466 | −$2,154 | 53.9 % | −0.07 |
| **INCUMBENT P1+XM** | $1,222 | **$3,000** | $8,249 | −$4,466 | 61.8 % | 4.83 |
| INCUMBENT + TSMOM | $373 | **$1,397** | $5,407 | −$1,932 | 65.2 % | 4.28 |
| P1 + TSMOM *(secondary)* | $271 | $740 | $7,432 | −$2,326 | 64.0 % | 3.27 |

**TSMOM earns essentially nothing on this window: −$4/week, t −0.07.** Yearly: 2023 −$4,193 ·
2024 +$2,485 · 2025 +$1,264 · 2026 −$317.

> ### **Adding it cuts the incumbent's risk-normalised income by more than half — $3,000 → $1,397
> ### per week.** Under a causal equal-risk allocator, a sleeve with no return simply takes risk
> ### budget away from one that has return.

## 3. ⚠️ The one passing gate is the trap, not the consolation

`H1-G5` passes: combined ES5 % improves by **+$3,726**. Combined maxDD is $20,245 versus the
incumbent's $20,245 — identical **by construction**, since both are normalised to the same
drawdown.

> ### **That is dilution, not diversification.**
> ρ(incumbent, TSMOM) = **0.013** — genuinely uncorrelated — but **uncorrelated and unprofitable
> is not a hedge, it is ballast.** Mixing a zero-return uncorrelated stream into a profitable one
> always improves shortfall statistics *and* always costs income. G5 was written to catch extra
> exposure disguised as alpha; here it catches the mirror error, **risk reduction disguised as
> diversification**, and G1–G4 are what expose it.
>
> **This is exactly why the primary tail criterion (G4) was fixed before the read.** Had I been
> free to choose "ES reduction" after seeing the table, H1 would have "passed" on a statistic that
> improves precisely because the sleeve earns nothing.

## 4. The tail claim itself fails on its own terms

| | |
|---|---:|
| incumbent worst-decile weeks | 18 of 178 (threshold −$2,171) |
| **mean TSMOM in those weeks** | **−$169.70** |
| mean TSMOM when incumbent < 0 | −$6.30 |
| ρ(incumbent, TSMOM), all weeks | 0.013 |
| ρ ∣ incumbent < 0 | 0.048 |
| worst-decile overlap (TSMOM also < 0) | 33.3 % |

**TSMOM does not pay when the incumbent hurts.** The 2020/2022 crisis payoff that motivated this
hypothesis **did not recur** in 2023–2026 — including 2025's genuine volatility. The hypothesis was
motivated by two macro episodes and did not generalize to the next ones.

## 5. Verdict

| | |
|---|---|
| **what was measured** | whether the frozen 252d object earns its place as a portfolio tail diversifier on a one-sided-blind window |
| **what passed** | only the ES diagnostic — and for the wrong reason |
| **what failed** | the primary utility (Δ fixed-DD **−$1,602/wk**), its bootstrap bound, the stress version, and **the tail claim itself** |
| **what changed** | **TSMOM is CLOSED for this campaign.** Both roles tested, both failed, on two separate protected windows |
| **what did NOT change** | the incumbent; the 141-session Last-only blind pool; the ≥2026-08-01 seal |
| **evidence class** | one-sided blind historical. **Not** prospective, **not** a pristine portfolio OOS |
| **what is NOT closed** | multi-market alpha as such. **Carry / term structure is a genuinely different information source**, and the expensive substrate — true unmerged contracts, contract truth, causal rolls, basis-safe P&L — **already exists and is reusable**. It would be a NEW family with its own spec, attempt budget and evidence class, **never a TSMOM rescue** |
| **not done** | no H2. No 126d, no blend, no re-weighting, no sector surgery. The window has judged the object |
