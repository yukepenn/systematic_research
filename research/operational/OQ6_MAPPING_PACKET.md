# OQ-6 DECISION PACKET — integer-contract mapping for {P1/PCT + XM_v2}

> ✅ **RATIFIED 2026-08-30 by owner: 「确认 M_11」** — recorded in `OWNER_DECISION_20260830.md`;
> slot D updated in `EXECUTION_MANIFEST.md`.

**For owner ratification.** Analysis: `runs/G2_OQ6_MAPPING_20260830` (spec committed pre-result,
trial G00040). Decision frozen BEFORE the 2026-09-01 shadow start so the mapped portfolio is a
preregistered forward object from day one. **Ratifying a mapping does NOT enable anything live.**

## Recommendation: **M_11 — P1 ×1 NQ + XM ×1 NQ**

The two legs' weekly vols are nearly equal (P1 $4,879 vs XM $4,382/wk), so the inverse-vol
reference share for P1 is **0.473** — and plain 1:1 lands at 0.527, closest of any integer
mapping. It ALSO wins the tie-break outright:

| candidate | risk-share dev | net/wk (dev) | maxDD | net @ $20,245 DD | %pos wk | worst wk |
|---|---:|---:|---:|---:|---:|---:|
| **M_11 (1:1)** | **0.054** | $2,489 | **$21,740** | **$2,318** | 61.3% | −$15,281 |
| M_21 (2:1) | 0.217 | $4,063 | $39,748 | $2,070 | 63.2% | −$21,552 |
| M_12 (1:2) | 0.116 | $3,404 | $39,778 | $1,732 | 61.8% | −$29,926 |

The happy accident is real: **because the legs are naturally vol-matched, the simplest mapping IS
the inverse-vol mapping** to within 5pp of risk share. No micro-contract complexity needed
(MNQ variants stay FLAGGED-ONLY — MNQ friction is unmeasured here).

## Caveats that travel with the numbers

1. **Convention note**: weekly bucketing here (entry-date ISO weeks, 212 common weeks) differs
   from W103's session-date convention — the RELATIVE comparison between candidates is the
   deliverable; do not quote the $2,318 as superseding the recorded honest portfolio band
   ($1,750–1,800/wk); both conventions will be reconciled by the shadow's real stream.
2. **Costs**: P1 leg at modeled $14.44 (measured $20.65 ⇒ ≈ −$58/wk on this leg); **XM's spread
   has never been measured** — it owes the same EXEC01-style audit.
3. **Shape**: the combined stream inherits both legs' tail-carried profile (worst dev week
   −$15.3k; 2026-07 saw both legs lose together). The tail-aware shadow-reading frame applies to
   the portfolio too.
4. Margin/capital: two simultaneous NQ contracts at peak (plus P1's internal size-2 moments →
   up to 3 net long) — check current broker margin; no figures invented here.

## What ratification changes

Slot D upgrades from `EXECUTABLE_COMPONENT_SET` to **`EXECUTABLE_PORTFOLIO (mapping M_11)`** in
the execution manifest; the shadow's component streams combine under M_11 as the preregistered
portfolio object. **LIVE ENABLED stays NO** — live enablement remains a separate, later,
owner-recorded decision.

> **To ratify, reply: "确认 M_11"** (or name another candidate / decline — all three candidates'
> full economics are above and in `out/mapping_table.csv`).

---

## POST-HOC ROBUSTNESS CHECK (2026-08-30, after ratification — disclosed as post-hoc)

The frozen candidate set was 3 mappings (1:1, 2:1, 1:2). ⚠️ That was narrow. The full integer
grid (a:b ≤ 5 contracts) was computed AFTER ratification as a robustness check — **it does not
change the answer**, and it is recorded as a check, not a new selection:

| map | ctr | net/wk | maxDD | fixed-DD $/wk | risk share | dev vs inv-vol (0.473) |
|---|---:|---:|---:|---:|---:|---:|
| 2:3 | 5 | $5,893 | $61,518 | $1,939 | 0.426 | **0.047** (best dev) |
| **1:1 (= 2:2 ratio)** | **2** | $2,489 | $21,740 | **$2,318** | 0.527 | 0.054 |
| 3:2 | 5 | $6,552 | $56,643 | **$2,342** (best) | 0.625 | 0.152 |
| 1:2 | 3 | $3,404 | $39,778 | $1,732 | 0.358 | 0.116 |
| 2:1 | 3 | $4,063 | $39,748 | $2,070 | 0.690 | 0.217 |
| P1 alone (1:0) | 1 | $1,574 | $22,853 | $1,395 | 1.000 | 0.527 |
| XM alone (0:1) | 1 | $915 | $18,631 | $994 | 0.000 | 0.473 |

**1:1 survives the wider grid.** The two mappings that beat it do so on ONE metric each while
losing the other, at **2.5× the capital**: 2:3 wins risk-share by 0.007 but its fixed-DD is 16%
worse; 3:2 wins fixed-DD by 1% but sits far off the inverse-vol share. At 1–2 contract scale,
**1:1 is the ratio.** Note 1:1 and 2:2 are the SAME ratio — the mapping question (ratio) is
settled; **how many units of that ratio to run is a separate CAPITAL decision for the owner and
must not be read off backtest dollars.**

⚠️ See `XM_CORRELATION_RULE_20260830.md`: the diversification rationale behind this mapping has
materially weakened (ρ −0.10 → +0.41; XM's P1-losing-week payoff +$1,488 → −$727). The mapping
still measures better than P1 alone, but on a weaker premise, now under a preregistered watch.

---

## ⭐ WHAT "M_11" IS — and why `WeeklyEdgeBookM11_v1` is NOT the most correct version of it

Added 2026-08-31 after the owner asked for "the most correct M_11" on finding the class had been
moved out of the compile path. **The file is restored** (`bin/Custom/Strategies/`, sha `9499F19D0C39`,
recompiled 01:06:34). But restoring it does not make it the authoritative object, and here is why.

### M_11 is a MAPPING, not a class

M_11 = **P1/PCT × 1 contract + XM_CONFLICT × 1 contract**. The **deployed book already IS M_11** —
`WeeklyEdgeP1PCT_v2` and `WeeklyEdgeXMConflict_v3` running side by side, each holding its **own
independent strategy position**.

### A single-class M_11 is STRUCTURALLY IMPOSSIBLE in NT8

An NT8 strategy holds **one position per instrument**. Two legs in one class therefore **must be
netted** — when P1 is long and XM is short, the class holds the difference, while the real book holds
two independent positions. This is not a defect in `BookM11_v1`; it is a platform constraint, and it
means **no single class can ever exactly reproduce the deployed book.**

### Measured, same engine / window / bars / cost template (NT8 basis, 2022-01-03 → 2026-08-30)

| object | closed trades | closed-trade P&L | total contracts |
|---|---:|---:|---:|
| P1/PCT (`_v2`) | 2,439 | $354,575.96 | 2,939 |
| XM_CONFLICT (`_v3`) | 378 | $182,776.92 | 378 |
| **M_11 = the two legs summed (THE DEPLOYED BOOK)** | **2,817** | **$537,352.88** | **3,317** |
| `WeeklyEdgeBookM11_v1` (netted single class) | 2,862 | $539,102.88 | 3,318 |
| difference | **+45** | **+$1,750.00** | +1 |

**The +$1,750.00 decomposes exactly**: **$1,741.28** is P1's position still open at the right edge of
the window, which the netted class closes and the two-leg sum does not; the genuine netting benefit
over 4.7 years is **$8.72**. Contract counts are identical to within 1, so netting saves essentially
no commission — the legs oppose too rarely (0.3 % of minutes).

### The rule

- ✅ **Quote the two-leg sum ($537,352.88 / 2,817) as M_11.** It is the deployed economics.
- ✅ `BookM11_v1` is a legitimate **measurement convenience** — one run, one equity curve, and it lands
  within **$8.72** of the truth in aggregate.
- ⛔ **Its TRADE LIST is not the book's** (2,862 vs 2,817, and the boundaries differ). Never quote one
  object's trade-level statistics for the other.
- ⛔ **Never deploy it.** It is not parity-certified and it drives the account with **unmanaged**
  orders to a netted target. Only `WeeklyEdgeP1PCT_v2` + `WeeklyEdgeXMConflict_v3` are deployable.

### M_11 combined performance (NT8 cost basis — commission only, ZERO modelled spread)

243 ISO weeks on session date (18:00 ET boundary):

| | |
|---|---:|
| mean / week | **$2,211.33** |
| median / week | $1,290.36 |
| positive weeks | **147 / 243 = 60.5 %** |
| best / worst week | +$32,288.96 / −$13,779.76 |
| **weekly max drawdown** | **$45,085.80** |

| year | P1 | XM | **M_11** |
|---|---:|---:|---:|
| 2022 | 44,755 | −3,023 | **41,732** |
| 2023 | 40,370 | 42,245 | **82,615** |
| 2024 | 104,889 | 75,212 | **180,102** |
| 2025 | 111,331 | 25,344 | **136,676** |
| 2026 (35 wk) | 53,230 | 42,998 | **96,228** |

2026 by month: Jan **+18,781** · Feb **+38,634** · Mar +17,087 · Apr +3,651 · May +2,164 ·
Jun +25,019 · **Jul −30,139** · Aug +21,031.

⚠️ **These are NT8 quantities, not research quantities.** NT8 charges the Lifetime template and
**zero slippage**; the research headline additionally charges a modelled spread (P1 $14.44,
XM $12.50 /ctrRT). ⚠️ And per `CURRENT_BASELINE.md`, research portfolio **B is inverse-vol weighted**
— **B's $2,012/wk at fixed DD is NOT this number.** M_11 is the integer 1:1 mapping, a different
object from B. Never substitute one for the other.