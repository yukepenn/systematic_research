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
