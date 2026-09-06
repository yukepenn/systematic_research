# CL HOLDOUT FREEZE — committed 2026-09-06, BEFORE any CL signal is read

**Purpose (owner directive §6 — "preserve unused data before consuming it; if pristine data
exists, FREEZE IT before looking").** CL is the ONE genuinely untouched intraday futures market in
the repo (0 prior experiments, extraction only). Unlike ES/RTY/YM/ZB — whose pre-seal intraday is
already DISCOVERY_CONSUMED — CL can therefore support a real out-of-sample adjudication. This spec
freezes that boundary NOW, in git, before any autopsy / diagnostic / candidate touches CL, so the
holdout cannot be silently peeked. Substrate: `runs/SM1M_CL_SUBSTRATE/out/cl_1m_2022_2026.parquet`
(sha256 `e587486c…adc137`, 1,182 sessions 2022-01-03 → 2026-07-31).

## The three layers

| layer | span | use | status at freeze time |
|---|---|---|---|
| **DISCOVERY** | 2022-01-03 → **2025-06-30** (~3.5 yr, ~870 sess) | market autopsy, diagnostics, candidate construction, neighborhood, cost stress | consumable |
| 🔒 **FROZEN HOLDOUT** | **2025-07-01 → 2026-07-31** (~1 yr, ~270 sess) | ONE preregistered adjudication read of a CL candidate AFTER discovery is complete | **DO NOT LOOK** |
| **GLOBAL VIRGIN** | ≥ **2026-08-01** | true forward validation (global seal, all instruments) | **DO NOT LOOK** |

## Rules (binding)

1. All CL discovery — the Wave-1 autopsy, every Wave-2 native hypothesis, all rule/neighborhood/
   cost work — runs **only on DISCOVERY (≤ 2025-06-30)**. Loaders hard-drop sessions > 2025-06-30
   for discovery and assert it.
2. The FROZEN HOLDOUT is read **once**, under its **own** preregistered spec (committed before the
   read), only after a CL candidate has survived discovery — evaluation, not selection. No
   iterating on it, no "just a peek".
3. Reading the holdout does not consume the GLOBAL VIRGIN (≥2026-08-01), which remains the true
   forward layer.
4. This boundary is frozen by DATE and hash-anchored to the substrate sha256 above. It is not
   moved because more data later exists.

## Why the split point is 2025-06-30

Gives ~3.5 years of discovery (enough for the P1-class 250-session warmup + regime variety) and a
full ~1-year holdout that spans a complete seasonal/roll cycle for a physical-commodity market.
The point was chosen from the calendar BEFORE any CL return was computed; it is not a result.
