# MS01 — microstructure standalone feasibility: the lane is OPEN, and the bar is high

| | |
|---|---|
| **run class** | **FEASIBILITY + POWER** — no model, no feature, no hypothesis, nothing promoted |
| date | 2026-08-27 |
| preregistration | `spec.yaml`, committed at **`0b6a088`, before any number was computed** |
| code | `src/feasibility.py` · reproduction `out/feasibility.txt` · `out/feasibility.csv` |
| population | `data_microstructure_v2`, 58 sessions, v2 only — the 15 truncated v1 files excluded by spec |
| seal | untouched |

> ### **Break-even needs 58.4 % directional accuracy at 15 s, 54.2 % at 60 s, 51.8 % at 300 s.**
> ### **The lane is OPEN at 15–60 s — but only under a dependence assumption the study cannot settle.**

---

## 1. Why this is not the order-flow gate

`DATAGATE_ORDERFLOW_V2` closed **P1 full-horizon action-value routing** on power: sd $2,193 per
decision against a $112 mean, needing 998 sessions when 713 exist. Directive §8/§40 is explicit that
this must not lower the prior for the **standalone** question, and it does not — **the standalone
target is a different object with far lower variance.** The order-flow null closed **one mapping**,
not a data surface.

## 2. The spread — measured, and it validates against the campaign's own number

| | median | mean | p90 | p99 | share exactly 1 tick |
|---|---:|---:|---:|---:|---:|
| all session | 4.000 | 4.811 | 7.000 | 11.000 | 0.2 % |
| **RTH only** | **3.000** | 3.567 | 5.000 | 11.000 | 0.6 % |

> **Cross-check I did not arrange:** the frozen cost convention charges P1 a **modelled spread of
> $14.44/ctrRT = 2.888 ticks**, derived in W82 from a per-minute *fill* audit. This study measures
> **3.000 ticks** from raw quoted BBO, on a different session set, by a completely different route.
> **Agreement to 0.112 ticks.** That is a real check that the measurement is sound.

I flagged the 3-tick median as implausible on sight — NQ is normally 1 tick wide — and verified the
`bip` assignment before trusting it (mean bid 30,688.6 < mean ask 30,692.2; raw interleaving shows
genuine 1.25-point quotes). **The spread is genuinely wide because this market is genuinely
violent:** observed NQ daily ranges reach 977 points. The per-15s sd of 33.6 ticks scales to an
expected daily range of ~530 points, which sits inside the observed range — the numbers are
internally consistent.

## 3. The move versus the toll

**All-in round-turn friction = 3.000 (cross the spread both sides) + 0.872 (commission) = 3.872 ticks**,
rising to 5.872 at 1 tick of slippage per side.

| horizon | raw N | E&#124;move&#124; | sd | friction @0 | **break-even accuracy** | @0.5 slip | @1.0 slip |
|---|---:|---:|---:|---:|---:|---:|---:|
| 15 s | 90,454 | 22.94 | 33.62 | 3.872 | **58.44 %** | 60.62 % | 62.80 % |
| 30 s | 45,227 | 32.90 | 47.85 | 3.872 | **55.88 %** | 57.40 % | 58.92 % |
| 60 s | 22,610 | 46.50 | 66.95 | 3.872 | **54.16 %** | 55.24 % | 56.31 % |
| 180 s | 7,536 | 80.87 | 116.50 | 3.872 | 52.39 % | 53.01 % | 53.63 % |
| 300 s | 4,519 | 107.22 | 153.24 | 3.872 | 51.81 % | 52.27 % | 52.74 % |

`p* = 0.5 + friction / (2·E|move|)` — a forecaster right with probability `p` nets
`(2p−1)·E|move|` gross.

**This is not a cheap bar.** Sustained 54–58 % net directional accuracy on liquid index futures at
sub-minute horizons is exactly what most microstructure research fails to deliver. But it is **not
absurd** either, and that is the finding: **friction does not close this lane by arithmetic.**

## 4. ⚠️ The verdict depends on an assumption this study cannot settle

MDE at ~80 % power under three dependence assumptions:

| horizon | friction | MDE if all obs independent | MDE, session design-effect | MDE if **1 obs/session** |
|---|---:|---:|---:|---:|
| 15 s | 3.872 | 0.313 | **0.426 → OPEN** | 12.360 → underpowered |
| 30 s | 3.872 | 0.630 | **0.849 → OPEN** | 17.591 → underpowered |
| 60 s | 3.872 | 1.247 | **1.681 → OPEN** | 24.615 → underpowered |
| 180 s | 3.872 | 3.757 | 5.119 → underpowered | 42.831 → underpowered |
| 300 s | 3.872 | 6.383 | 8.581 → underpowered | 56.339 → underpowered |

**Under the maximally conservative assumption the verdict flips at every horizon.** I am reporting
that rather than quoting the number that suits the conclusion.

**Which end is defensible.** The `1-obs/session` floor is a genuine bound but a poor model of a
*trading* strategy: a strategy taking `k` roughly-independent trades per session accumulates
information at `√(k·S)`, not `√S`. The design-effect estimate is the more reasonable one and it
already discounts raw N by ~46 %. **But the honest statement is that this is a range, and where
inside it the truth lies is an empirical property of a specific candidate's trade-level
autocorrelation — measurable only once a candidate exists, not assumable now.**

## 5. Verdict

| horizon | verdict |
|---|---|
| **15 s / 30 s / 60 s** | ✅ **OPEN** — friction is payable, break-even is 54–58 %, and a break-even-sized edge is detectable under the session design effect |
| **180 s / 300 s** | ⚠️ **UNDERPOWERED vs break-even** — accuracy bar is easiest here (51.8–52.4 %) but 58 sessions cannot verify an edge that merely breaks even |

**The owner thesis in §40 survives this test.** Directive §40 asserted the standalone question "may
be far easier" than the closed router question. It is: the router needed 998 sessions and had none
to spare, while this lane is arithmetically payable at 15–60 s on the data already held. **That was
an owner intuition and it was tested, not assumed** — it could have come back CLOSED_BY_FRICTION and
did not.

**What this does NOT say.** It says **nothing** about whether an edge exists. No feature was built,
no model fitted, no threshold chosen. A passing feasibility gate means the question is worth asking
under preregistration — nothing more.

**Also not established:** the friction figure assumes **crossing the spread on both sides**. A
passive/limit strategy pays less but inherits fill probability and adverse selection, which is an
execution question (§49) and would need its own break-even analysis, not an optimistic assumption.

## 6. Continuation

Next is a **preregistered Stage-A microstructure wave** at **60 s** — the horizon with the best
combination of a payable accuracy bar (54.16 %) and detectability. Per §10 it must declare a
**small** primitive family, decision-event construction, direction, and a **same-trigger mirror
control** (continuation vs reversal) before any outcome, and per §12 carry session-level block
permutation with the entire procedure repeated inside the null.

**Evidence class if it ever promotes: `MICROSTRUCTURE-CURRENT` / `REGIME-LOCAL`.** 58 sessions is
not, and will never be, a structural claim.
