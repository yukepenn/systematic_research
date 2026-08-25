# THE EXPOSURE LAW — and how it resolves the 130 vs 65 ambiguity

Run `OTR_R32_JOINT_ENTRY_EXIT` amendment 1, preregistered before readout.
Code: `run_r32b_exposure.py`. No purchase, no new data, nothing from the sealed window.

---

## 1. Why this was solvable rather than searchable

R32 Part A established that **no exit mechanism** reproduces `corr(ATR, his avg_loss) = −0.51`
(0 of 9 families; all strongly positive, +0.66 to +0.87). That left an exposure/sizing law as the
only remaining candidate.

Quantity enters **multiplicatively**: it rescales every dollar figure and leaves hold, win rate,
payoff ratio and trade count untouched. So under `q ∝ ATR^(−k)` our dollar exponent becomes
`b_ours − k`, and matching his gives

> **k = b_ours − b_his** — solved from measured exponents, not fitted to minimise anything.

A single exposure law must give the **same k** from `avg_loss` and from `avg_win`, because
quantity multiplies winners and losers identically. That is a free internal consistency check.

---

## 2. The result

| configuration | b_loss | b_win | **k from loss** | **k from win** | agree? |
|---|---|---|---|---|---|
| `P_MED\|C_DIR\|X_OPP` (incumbent) | +0.997 | +0.627 | 1.423 | 1.173 | PASS |
| `P_IN\|C_REC\|X_OPP` | +0.962 | +0.754 | **1.388** | **1.300** | PASS (0.087) |
| `P_MED\|C_DIR\|X_TRAIL_PTS:25` | +0.420 | +0.325 | **0.846** | **0.871** | PASS (0.025) |
| `P_MED\|C_DIR\|X_TARGET:60` | +1.099 | +0.584 | 1.525 | 1.130 | PASS |
| `P_IN\|C_REC\|X_TRAIL_PTS:80` | +0.594 | +0.062 | 1.020 | 0.608 | FAIL |

**K1 PASS 4/5** — a single multiplicative quantity law *can* reconcile his winners and his losers
simultaneously, and in two configurations it does so to within 0.03–0.09. The exposure hypothesis
is internally consistent.

**K2: solved k across configurations = [0.61, 1.53], median 1.151.**

A **fixed dollar risk R per trade with a volatility-scaled stop** implies
`q = R / (20 · c · ATR)` — that is, **exactly k = 1**. The solved interval contains 1 and its
median sits 0.15 away.

---

## 3. What one hypothesis explains

Fixed-dollar-risk sizing accounts for **five separate observations** that had been treated as
unrelated:

| observation | how it follows |
|---|---|
| `corr(ATR, his avg_loss) = −0.51` (robust on both samples) | size falls as volatility rises |
| his winners and losers co-scale, leaving the payoff ratio untouched (−0.06) | quantity multiplies both identically |
| **largest loss is EXACTLY −$2,600 in 18 of 24 weeks** | under fixed dollar risk the worst case is R *by construction*, independent of volatility |
| the confirmed **qty-2** trade in the June Trade Performance record | size genuinely varies |
| q = 1 forced by parity in four Strategy Analyzer records | size is *sometimes* 1 |

**K3, registered in advance:** under a fixed-**point** stop with varying quantity the largest loss
would vary week to week. It does not. Only a fixed-**dollar**-risk formulation is consistent with
an exactly-repeating −$2,600.

---

## 4. It dissolves the 130-vs-65 ambiguity instead of deciding it

R30 left `130 points × qty 1` and `65 points × qty 2` separated by only 0.023, both live. Under
fixed dollar risk, **that was the wrong question**:

> `stop_points = 2600 / (20 · q)`
>
> q = 1 → **130 points.**  q = 2 → **65 points.**
> **Both are true, at different times, under one rule.**

The stop is not a fixed point distance at all. It is a fixed **$2,600**, and its point distance is
whatever quantity makes it. That is why the two candidates could never be separated on fit — they
are the same rule evaluated at two different volatilities.

Implied size variation over the observed 2026 ATR range (7.5 → 15.2): at k = 1, quantity varies by
a factor of **~2.0** across the year.

---

## 5. Status, and the caveat that matters

**INDICATED — not identified.** Held deliberately below LEVEL B:

- His own dollar-exponent fits are **loose**: `avg_loss ~ ATR^−0.426` at **R² = 0.265**, and
  `avg_win ~ ATR^−0.546` at **R² = 0.212**. The exponents carry wide uncertainty, so k does too.
  The honest statement is the **interval [0.61, 1.53]**, which contains 1 — not "k = 1".
- k ≈ 1 is *consistent with* fixed-dollar-risk sizing. Other mechanisms that scale exposure
  inversely with volatility would produce the same signature, and none is excluded.
- One configuration failed K1, so the reconciliation is not universal across entry/exit choices.
- No label, class name or panel row supports it. This is behavioural evidence only.

**What would upgrade it:** a 2026 record with per-trade quantity recoverable. The two June Trade
Performance records already yield one qty-2 trade; a third such record, or per-day rows with
MAE/MFE, would let quantity be read out per trade rather than inferred from an exponent.
The corpus is fixed at 164 images, so this is not obtainable by spending.
