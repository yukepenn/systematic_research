
# OTR_R31_JOINT_MECHANISM — report

Spec + amendments 1–2 preregistered before each readout. Owner continuation directive R31,
2026-08-25. Code: `run_r31a_volatility_law.py`, `run_r31b_ext_and_era.py`.

**Headline: my own falsifiers fired. The exit-class identification announced earlier in this
session is WITHDRAWN, and one of R30's structural findings is withdrawn with it.** Details below,
recorded rather than rewritten.

---

## 0. Platform-boundary correction (directive §1) — already in force

Verified, not assumed:

| artifact | state |
|---|---|
| `2026_PANEL_TOPOLOGY.md` (committed 2026-08-24) | six trailing groups already identified as the NT8 standard tail, counted as **26 platform rows** |
| `ALL_VISIBLE_PARAMETER_ORIGIN_MATRIX.csv` | **29 slots** `IDENTIFIED_PLATFORM_SETTING`, **0** treated as author modules |
| `PARAMETER_COVERAGE_REPORT.md` | custom rows computed as `523 − 26 = ~497` — exactly the boundary rule |
| this session | head `[SEP] enum enum` additionally reclassified as NT8's own **General** group |

`VF13 sits immediately above Data Series` was already a committed FACT. **Outstanding:** older
artifacts predating the correction (`CURRENT_TRUTH.md`, `FAMILY_MAP.md`, `2026_VARIANT_LEDGER.csv`,
several `per_image/*.md`) — Part D sweep, marked superseded, never deleted.

---

## 1. Data correction — June/July bars were in the repo all along

R30's spec and report stated June/July 2026 bars were not local and would need a fresh export.
**That was wrong.** `data/nq0626_jun2026_1m.csv` (2026-05-24→06-18) and
`data/nq0926_junjul2026_1m.csv` (2026-06-14→07-31) already existed. With the parquet this gives
continuous 1-minute coverage to **2026-07-31**. August remains sealed and untouched.

Recorded as an error of mine, not silently fixed. It cost R30 its out-of-sample check.

---

## 2. Part A — the ATR-hold law, and why it is NOT an exit fingerprint

**The law itself is robust.** Extending from 17 to 23 windows:

| | exponent `b` | R² |
|---|---|---|
| 17 windows (to 2026-05-29) | −1.636 | 0.923 |
| **23 windows (to 2026-07-31)** | **−1.369** | **0.868** |

**I1 PASS** — inside the preregistered band [−2.0, −1.2] with R² > 0.75.

**But E2 FAILED, and it is decisive.** The Jan-2023 era's exit mechanism is *known* — a
stop-and-reverse on Solar flips, with **no trailing stop**, established by the unique 89-trade
inverse. I predicted it would therefore show a flat law (|b| < 0.6, low R²). Measured on the
already-recovered path:

> **2023: `hold ~ ATR^−0.844`, R² = 0.606** — over 11 days, alignment self-checked
> (entry price = `open[ei]` for **89/89** trades).

A demonstrably **state-based** exit produces a steep law too.

> **Therefore the ATR-hold law is NOT diagnostic of exit class, and the identification
> "his exit is a fixed-point trailing stop of 20–30 points" is WITHDRAWN** under the decision rule
> I registered in amendment 2.

The honest residual reading: 2023 (−0.844, R² 0.606) *is* shallower and looser than 2026
(−1.369, R² 0.868), which is *consistent with* an exit-mechanism difference between eras but does
not establish one. The law is most economically read as a generic property of intraday systems —
moves complete faster when volatility is higher, so holds shorten — rather than a fingerprint.

**I2 also FAILED.** I predicted the right-tail weeks would be low-ATR, continuing the law. They
are not: 6/21–6/26 has ATR 19.28 (well above median) with hold 40.0 where the law predicts 26.8
(residual **+13.2**), and 7/12–7/31 has ATR 15.85 with residual **+5.1**. The two best weeks of
2026 sit *above* the curve — long holds at high volatility, which I registered in advance as
directly contrary to a fixed-trail mechanism.

---

## 3. I3 — a R30 structural finding collapses out of sample

The correlations that drove R30's amendment-4 narrative, recomputed over 23 windows:

| | 17 windows | **23 windows** | verdict |
|---|---|---|---|
| corr(ATR, avg_loss) | −0.509 | **−0.515** | **ROBUST** |
| corr(ATR, avg_win) | −0.469 | −0.289 | weakened |
| corr(ATR, payoff) | −0.062 | +0.075 | ~zero either way |
| **corr(max_run, payoff)** | **−0.452** | **−0.050** | **COLLAPSES** |

`corr(max_run, payoff) = −0.452` was the quantity I identified in R30 amendment 4 as *"the genuine
structural effect that sizing cannot produce"* and made the primary target for Part C. Over 23
windows it is **−0.050 — nothing.** It was a 17-window artifact.

**Withdrawn:** R30 amendment 4's claim that a payoff-bearing, max_run-asymmetric structural
component exists. **Also weakened:** R30 Part B's "the market offered the most and he captured the
least" — March ranks 3rd of 23 on max_run now, not 17/17, and the two June/July weeks exceed it.

**Survives:** `corr(ATR, avg_loss) ≈ −0.51` on both samples. His average *loss* shrinks with
volatility, robustly. That single relationship is now the most durable unexplained regularity in
the 2026 record, and no entry, exit or exposure hypothesis on the table accounts for it.

---

## 4. E1 — his 2023 MAE distribution (a genuine, reusable measurement)

From the recovered 89-trade path, per-trade MAE in index points:

| p10 | p25 | p50 | p75 | p90 | p95 | max | mean |
|---|---|---|---|---|---|---|---|
| 6.00 | 14.50 | **30.00** | 42.75 | 54.65 | 60.90 | 112.75 | 30.00 |

**55.1 %** of his 2023 trades had MAE above 25 points; **49.4 %** above 30.

So a 20–30 point trailing stop would have destroyed roughly **half** of his 2023 trades before
they developed. That is fully consistent with the 2023 mechanism (no trail), and it is an
independent reason to doubt a tight trail in any era where his entry style resembles 2023's.

---

## 5. What stands, and what does not

**Withdrawn this pass:**
- Exit-class identification (fixed-point trail 20–30 pts) — killed by E2.
- `corr(max_run, payoff)` as a structural signal — killed by I3.
- R30 Part B's opportunity-capture framing — weakened by the 23-window recount.

**Unaffected and still standing:**
- **F4** (R30): no exit family reproduces the March/late-May asymmetry. Denominator-independent,
  and E2 does not touch it.
- The −$2,600 / quantity audit: q ∈ {4,5,10,13} excluded; q = 1 forced for the four odd-cell
  records; 130×1 vs 65×2 still open.
- The VF13 label finding (his own re-declarations, not the vendor grid) — LEVEL A.
- All panel/platform-boundary work.
- `corr(ATR, avg_loss) ≈ −0.51`, robust across both samples.

**Method note.** Three claims failed this pass, all to falsifiers I had registered in advance and
all before anything was built on top of them. That is the process working as intended, and it is
the third time this session that a mechanism claim has not survived its own test — the pattern
itself is now evidence about how much weight single-sample correlations deserve here.

---

## 6. Consequence for the purchase gate (directive §16)

The question is whether exact vendor `Signal_Trend` / `Signal_Trade` / `Signal_Cum_Delta` would
collapse a material fraction of surviving hypotheses.

After this pass the surviving hypothesis set is **larger, not smaller**: the exit class is no
longer identified, and the structural target that was to discriminate entry mechanisms turned out
to be noise. What remains robust is one relationship (`ATR → avg_loss`) that vendor signal series
would not address, plus a set of entry hypotheses that vendor signals **would** directly constrain.

That still points toward BUY, but the case is now weaker than it looked an hour ago, because the
thing a purchase would discriminate against — a clean structural target — is exactly what just
evaporated. Final recommendation deferred to `PURCHASE_GATE_v3` after the joint entry×exit test
(directive §13), which is the next run and needs no purchase.
