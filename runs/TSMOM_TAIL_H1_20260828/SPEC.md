# TSMOM-TAIL-H1 · PREREGISTRATION — committed before any 2023+ TSMOM P&L was read

| | |
|---|---|
| **status** | **SPEC COMMITTED BEFORE THE READ** |
| date | 2026-08-28 |
| authorized by | owner directive §5 — exactly **ONE** new hypothesis |
| window | **2023-01-01 → 2026-05-30, one shot** |
| seal | **≥ 2026-08-01 blocked by a hard cap in the substrate builder and an assertion in the runner** |

---

## 1. ⚠️ Evidence provenance — permanent, and attached to every number H1 produces

```
HYPOTHESIS MOTIVATED BY THE FAILED 2019–2022 VALIDATION
2019–2022 IS DISCOVERY FOR THIS NEW CLAIM, NOT EVIDENCE
NOT A CLEAN EX-ANTE HYPOTHESIS
2023–2026 TSMOM OUTCOMES REMAIN UNREAD BEFORE THIS SPEC IS COMMITTED
```

**And the holdout is ONE-SIDED.** The TSMOM leg is genuinely blind on 2023–2026 — its outcomes have
never been read. **The incumbent leg is not**: `P1/PCT` and `XM_CONFLICT` were discovered using
modern data covering much of this window. So this is a

> ### **ONE-SIDED BLIND TSMOM HISTORICAL HOLDOUT**

It is **not** prospective, **not** a fully pristine portfolio out-of-sample, and **not** forward
evidence. That asymmetry travels with every result.

## 2. What changes, and what emphatically does not

| | V2 (failed) | **H1** |
|---|---|---|
| trading object | 252d slow trend | **byte-identical** |
| **scientific claim** | "a sufficiently stable standalone slow-trend premium" | **"valuable portfolio diversification / tail behaviour despite uneven yearly returns"** |

**Only the claim changes.** Inherited unchanged: 21 CORE roots · `sign(R252)` · roll machinery and
pre-expiry fallback · eligibility · 252-day warmup · 63-day lagged vol · inverse-vol / equal-risk
sizing · daily rebalance · long/short symmetry · $4.36 commission · PRIMARY 1-tick / STRESS 2-tick ·
fractional research sizing.

**Explicitly NOT done** (these would be V2.1, which is forbidden): 126d, 126+252, 189d, 300d,
long-only, sector deletion, sector caps, trend-strength weighting, carry, breakout, new rebalancing,
new volatility estimator.

## 3. The allocator — ONE causal rule, frozen

**Expanding inverse-volatility**, standard deviations estimated **only from weeks strictly before**
the allocation week, **one-week lag**, **26-week warmup** (the same constant already declared in
`PORTFOLIO_B_RECONCILIATION_20260827`, not a new choice). Weights normalised to sum to 1.

**No optimizer. No Markowitz. No Sharpe-weighting. No weight search. No best-of-{10,20,30,40,50 %}.
No use of holdout volatility.** Prior weeks from before 2023 may inform the estimate — they are
past data, not future.

Objects: **incumbent `P1+XM`** · **`P1+XM+TSMOM`** · **`P1+TSMOM`** (secondary, to separate XM).

## 4. Primary utility and inference

**Primary: `Δ fixed-DD $/week`** = combined − incumbent, each normalised to its **own** $20,245
drawdown so the comparison is risk-normalised and extra exposure cannot masquerade as alpha.

**Inference (frozen form):** circular block bootstrap on the **paired weekly** series
`combined·k_combined − incumbent·k_incumbent`, block length `round(n^(1/3))` (the same rule
`FWD_BOOTSTRAP_V2` uses), **B = 20,000**, seed 20260828, **one-sided lower 95 % bound**.

## 5. Gates — all must pass. Fixed here.

| gate | rule |
|---|---|
| **H1-G1** | `Δ fixed-DD $/week > 0` |
| **H1-G2** | the paired bootstrap **lower 95 % bound > 0** |
| **H1-G3** | `Δ fixed-DD $/week > 0` at **STRESS** cost |
| **H1-G4** | **mean TSMOM P&L in the incumbent's worst-decile weeks > 0** |
| **H1-G5** | combined **ES5 %** (fixed-DD normalised) **not worse** than the incumbent's |

**H1-G4 is chosen now, before the read.** The directive offered "positive in worst-decile weeks
**OR** materially reduces ES". Choosing after seeing which passes would be selection, so the
**worst-decile mean is the primary tail criterion** — it is the more direct test of the crisis
claim — and **ES reduction is reported as a diagnostic only**.

**"Positive in ≥3 of 4 years" is deliberately NOT a gate here.** It answered the old steady-premium
claim, and re-using it against a hypothesis explicitly about uneven yearly returns would be
incoherent.

**Reported regardless of gates:** weekly ρ, ρ | P1<0, mean TSMOM | P1<0, mean TSMOM in the bottom
decile, worst-decile overlap, combined maxDD, ES, positive weeks, t, yearly result.

## 6. Verdict rules — fixed

**If H1 FAILS:** TSMOM is **CLOSED for this campaign** — steady-premium role failed, tail-diversifier
role failed. **Do not invent H2.** Do not spend more history on another TSMOM formulation.

**If H1 PASSES:** the claim is exactly *"frozen 252d TSMOM is **supported as a HISTORICAL
TAIL-DIVERSIFIER CANDIDATE** under a one-sided-blind holdout; clean portfolio confirmation still
requires prospective time."* **Not** "validated alpha". Freeze immediately; it may enter prospective
shadow. **LIVE remains NO.**

## 7. Frozen hashes

| artifact | sha256 |
|---|---|
| `ncd_day.py` | `17603bdc722d30f386b013d35a33f8b2cb510d8b7ea6fdbc07f0274bf01baec9` |
| `roll.py` | `b88a5176f8ed1dbc3903e300f6238993099046437c4b921293c9ba1d2eda837f` |
| `build_substrate.py` | `c6ce1a431109a35df9879fb4fc73960bb80d1f2b484e1a2503e30216a176548d` |
| `tsmom_v2.py` (the frozen object) | `9da123e6fae7dd367cdbd320ccd0a4b571991a1016de9e9863b7f7099a9db6b8` |
| **`tail_h1.py`** | `5421118fba84b556ff3ef0177d5c6e7310e3d472dbdbb020ef82902b4e1620e3` |
| `economic_returns.parquet` | `30dfa053595dc38b8be590628da2fef7f93fa5b410f239f223eb87397cc2b9c9` |
| `weekly.csv` (incumbent) | `442ffe9d826f3eb7a13aaa0db618dc27d3daffdc808552ca4e40e9b0a782dffc` |

**Substrate**: 89,843 root-days, 21 roots, 2009-03-31 → 2026-07-31; holdout carries **17,631
eligible root-days across all 21 roots**. Extended from expiry years 2023 → 2027 for holdout
coverage — **data only**, verified by re-running V1 on the extended substrate and reproducing the
committed development figures **exactly** (days 2,265, net $10,167, Sharpe 0.226, maxDD $17,129).
A **hard `SEAL_CAP = 2026-08-01`** now drops any row at or beyond the global seal at build time.
