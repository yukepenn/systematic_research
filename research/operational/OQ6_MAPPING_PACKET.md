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
