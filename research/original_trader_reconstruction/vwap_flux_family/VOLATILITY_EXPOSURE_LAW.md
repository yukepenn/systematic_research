# VOLATILITY / EXPOSURE LAW — 2026

> ## ⚠ IDENTIFICATION WITHDRAWN 2026-08-25 (OTR_R31 amendment 2, Part E)
>
> The exit-class identification below — *"his discretionary exit is a fixed-point trailing stop of
> 20–30 NQ points"* — is **WITHDRAWN**, by the falsifier registered in advance.
>
> **Why.** The Jan-2023 era's exit is *known* to be a stop-and-reverse on Solar flips with **no
> trailing stop** (established by the unique 89-trade inverse). Measured on that already-recovered
> path, 2023 gives `hold ~ ATR^−0.844`, R² = 0.606. A demonstrably **state-based** exit produces a
> steep law too, so **the ATR-hold law is not diagnostic of exit class.**
>
> Also failed: **I2** — the two right-tail weeks (6/21–6/26, 7/12–7/31) are high-ATR with holds
> *above* the curve (+13.2, +5.1 residual), which I registered as directly contrary to a fixed
> trail.
>
> **What survives:** the law itself is real and robust (23 windows: b = −1.369, R² = 0.868), but is
> most economically read as a generic property of intraday systems — moves complete faster at
> higher volatility — rather than a fingerprint of any mechanism.
>
> The text below is retained verbatim as the record of what was measured and claimed.
> See `runs/OTR_R31_JOINT_MECHANISM/REPORT.md`.

Directive R31 §8, §17. Run `OTR_R31_JOINT_MECHANISM` Part A + amendment 1, preregistered before
each readout. Code: `run_r31a_volatility_law.py`.

---

## 1. The measurement that started this

His holding time is almost deterministically governed by volatility:

| | corr(ATR, hold) | power-law exponent `hold ~ ATR^b` | R² |
|---|---|---|---|
| **the trader** | **−0.883** | **−1.636** | **0.923** |
| our incumbent (130-pt stop, state exit) | −0.438 | −0.338 | 0.169 |
| our incumbent at 65 pt | −0.498 | −0.405 | 0.238 |
| our incumbent at 32.5 pt | −0.467 | −0.439 | 0.214 |

**A benchmark I got wrong, corrected.** I first asserted that "fixed distances, no ATR logic"
predicts an exponent of −1. That is only true for *ballistic* motion. Under *diffusion* a fixed
distance D is traversed in time ~ (D/σ)², giving **−2**. Real price sits between, so a
fixed-distance exit predicts **b ∈ [−2, −1]**. His −1.636 is inside that band; ours is not.

---

## 2. The ATR-hold law identifies the EXIT CLASS

All 26 R30 exit families re-scored on the law (entry path frozen throughout):

| exit class | n | exponent range | mean b | mean R² |
|---|---|---|---|---|
| **DISTANCE-based** (trail-in-points, fixed target) | 12 | −1.871 … −0.700 | **−1.205** | **0.759** |
| TIME-based (bar timeout) | 5 | −0.182 … −0.063 | −0.125 | 0.110 |
| STATE-based (signal / trend / FV / band) | 4 | −0.338 … +0.312 | +0.084 | 0.107 |
| VOLATILITY-SCALED (ATR trail) | 5 | −0.062 … +0.162 | +0.068 | 0.056 |

**Only distance-based exits produce a steep, tight law. Everything else is flat and loose.**

Nearest to his (b = −1.636, R² = 0.923):

| family | b | R² | \|Δb\| |
|---|---|---|---|
| **X_TRAIL_PTS 20** | **−1.740** | **0.912** | 0.104 |
| **X_TRAIL_PTS 25** | **−1.546** | **0.881** | 0.090 |
| X_TRAIL_PTS 30 | −1.500 | 0.864 | 0.137 |
| X_TARGET 40 | −1.155 | 0.729 | 0.482 |

> **IDENTIFIED (LEVEL B, behavioural): his discretionary exit is DISTANCE-based — a trailing
> stop denominated in FIXED POINTS, in the region of 20–30 NQ points.**

**A1's exact ordering prediction FAILED** and is recorded, not rewritten: I predicted
DISTANCE < STATE < VOL-SCALED, but STATE (+0.084) and VOL-SCALED (+0.068) came out swapped. Both
are ≈ 0, so the failure is trivial; the substantive separation passed emphatically.

### H3 — the falsifier survived

If entry-side variation alone could produce the steep law, the identification would collapse.
All **12** entry variants (4 trend models × 3 rails) with a state exit were tested:

| best entry variant | b | R² |
|---|---|---|
| T_C \| P_MED | −0.338 | 0.169 |
| T_C \| P_Q75 | −0.316 | 0.152 |
| all others | −0.23 … +0.14 | ≤ 0.06 |

**None reaches b < −1.0.** The law is specific to the exit mechanism. The identification stands.

---

## 3. But an EXPOSURE law is independently required — H1 FAILED

I predicted that a fixed-point trail would also reproduce his dollar co-scaling, which would have
eliminated the owner's cause E. **It does not.**

| | corr(ATR, avg_win) | corr(ATR, avg_loss) | corr(ATR, payoff) |
|---|---|---|---|
| **the trader** | **−0.469** | **−0.509** | **−0.062** |
| our X_OPP baseline | +0.498 | +0.775 | −0.283 |
| our X_TRAIL_PTS 20 | +0.293 | +0.627 | **−0.117** |
| our X_TRAIL_PTS 25 | +0.256 | +0.658 | **−0.128** |

**His dollar amounts fall with volatility. Ours rise.** The trail barely moves it and leaves
`avg_loss` strongly positive. No exit mechanism tested closes a gap of 1.1–1.3 in correlation.

But note the **payoff ratio is matched almost exactly** (−0.117 / −0.128 against his −0.062).

> **That is the signature of a multiplicative exposure factor.** The *ratio* behaves correctly;
> only the *levels* are wrong, and a factor that multiplies wins and losses identically is
> precisely what leaves a ratio untouched while moving both levels.

**Cause E survives as an independent requirement.** My H1 prediction failed and is recorded.

---

## 4. Verdict on the four hypotheses

| | hypothesis | verdict |
|---|---|---|
| H-V1 | fixed distance, no explicit ATR logic | **PARTIAL** — explains the hold law, fails the dollar co-scaling |
| H-V2 | explicit volatility-normalised exit | **REFUTED** — ATR-scaled trails give b ≈ +0.07, R² ≈ 0.06, the opposite of his |
| H-V3 | dynamic quantity alone | **REFUTED as sufficient** — quantity cannot change holding time (A3), and constant-quantity families *do* reproduce his hold exponent |
| **H-V4** | **hybrid: distance exit + volatility-scaled exposure** | **SUPPORTED — the only hypothesis consistent with every measurement** |

The owner named H-V4 as the one worth testing. It is now the supported answer.

---

## 5. The entry constraint this implies (H2, testable)

A ~25-point trail applied to **our** entries yields avg_win ≈ $517 over ~2,126 trades. His avg_win
median is ~$1,780 over 1,214 trades. If his exit really is a 20–30 pt trail, then **his entries
must be positioned so that a tight trail is not hit before a large move develops** — he enters far
closer to the start of moves than we do.

**Measurable prediction:** his per-trade **MAE must be tightly bounded** — a trade that goes 25
points against you dies immediately under a 25-point trail. 2026 has no MAE data, but
**Feb-2025 (OTRIMG-0026) and Jan-2023 (OTRIMG-0003) do**, and the certified 90/90 NT8 MAE rule
already exists. That is the next free test and it needs no purchase.

---

## 6. Status tokens

- **REPRODUCED** — his hold obeys `hold ~ ATR^−1.636`, R² = 0.923 (17 windows).
- **IDENTIFIED (LEVEL B, behavioural)** — exit class is a fixed-point trailing stop ≈ 20–30 pts.
  Not LEVEL A: no label or class name supports it, only behaviour.
- **REQUIRED** — an exposure law inversely related to volatility, independent of the exit.
- **UNKNOWN** — the entry rule; and whether the exposure law is dynamic quantity, a
  dollar-risk-normalised stop, or something else. Kept as rivals (§6).
- **FAILED PREDICTIONS, recorded** — A1's exact class ordering; H1's cause-E elimination.
