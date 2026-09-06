# G3_DUREXT_20260906 — bond-index duration-extension day (G00086, family GENESIS3_EVENT)

**Verdict: CLOSED AT SCOPE (§28 block). G2 FAIL · G3 FAIL · G4 PASS — the mechanical
decision rule (`G2+G3+G4 PASS -> candidate, else closed`) closes DUREXT01.**
The closure completes the month-end/rates calendar family alongside G00077.

Evidence status of every number in this report: **DISCOVERY** (first read of this
representation; consumed by this read). Wave 5 world-scan card #11.

## The prior was adverse-leaning, and the spec said so before the read

The frozen spec recorded an ADVERSE-LEANING honest prior: G00077's banked control had
already measured the generic ES/ZB turn-of-month **spread** at ~$6/event ≈ zero over
T-2..T+1 (n=170). This object differed only in being ZB/ZN **alone**, on the **last trading
day specifically**, with a **concentration clause** (index duration extension settles at the
month-end close, so the flow should sit AT day T, not smear across the turn). The
concentration clause was declared the kill power in advance: *"a diffuse positive = generic
seasonality = FAIL."* That is exactly the clause that fired.

## Frozen object and inputs

- Events: last trading day T of each month, 2009-03..2026-07 → **209 ZB events** (spec ~210;
  ZN mirror 208 — see anomalies).
- PRIMARY: LONG ZB close(T-1)→close(T), 1-day hold, per contract. ZN mirror non-gating.
- Concentration placebos, same machinery: the **T-2 day** and the **T+1 day**, each vs the
  all-days control; PRIMARY delta must exceed BOTH.
- Inputs AS-IS from `runs/G3_AUCTCYCLE_20260906/out/` (certified causal roll, identity-gated,
  seal max 2026-07-31 asserted):
  - `zb_daily.parquet` sha256 `9446e7f19ee17754d5afd31c65790e5fe24ae76f23ebf128101c7c0bdf786c56`
  - `zn_daily.parquet` sha256 `13fc5165b8b2171bcb459e1fdb1ee47005ffa231027eb045f658de4db2fd2527`
- Costs: MODELED $4.36 RT + {1,2}-tick spread band; cons (2-tick) rung gates.
  ZB opt $35.61 / cons $66.86; ZN opt $19.98 / cons $35.61 per event.

## Numbers (program-printed; `out/gate_table.txt` is the authority)

**G1 MDE first** (printed before any event mean): ZB unconditional daily sd $951,
MDE(one-sided 5%, 80% power) at N=209 = **$164/event**. PASS.

**PRIMARY (ZB):** gross mean **+0.1681 pts = $+168.06/event**; after-cost CONS
**$+101.20** [GATING], OPT $+132.45. Event-block bootstrap (10,000, seed 20260907) 95% CI
of the cons mean: **[$-4.29, $+210.35] — includes 0**. Shared-draw circular-shift null
(2,000 shifts, one draw shared ZB/ZN, seed 20260906): null mean $+0.38, sd $66.70,
**p_1s = 0.0070** (two-sided 0.0135; normal-approx cross-check 0.0060).
In words: p_1s is the probability, under dependence-preserving circular shifts of the
month-end flag over the 4,393-session sequence, that 209 randomly placed pseudo-event days
show a mean 1-day ZB return at least as large as the observed $+168.06.
→ **G2 FAIL** (clause 2 of 3: CI includes 0; the two other clauses passed).

**G3 concentration (the declared kill power):** deltas vs the all-days control ($+3.67/day,
n=4,393), cost-invariant across cells —

| cell | n | mean $/day | delta vs control |
|---|---|---|---|
| **PRIMARY T (extension day)** | 209 | +168.06 | **+164.39** |
| placebo T-2 | 208 | +173.00 | **+169.33** |
| placebo T+1 | 208 | −121.69 | −125.37 |

delta_T > delta_T-2 is **False** (+164.39 vs +169.33). → **G3 FAIL.** The positive is
diffuse across the turn: the T-2 day carries the *same* premium as the extension day itself.
By the spec's own words, that is generic seasonality, not an extension-day flow.

**G4 era (after-cost cons):** 2009-15 $+131.69 (n=82) / 2016-21 $+133.23 (n=72) /
2022-26/07 **$+13.82** (n=55) → **+/+/+ STRUCTURAL**, PASS — but the modern era is
economically thin (~$166/yr/contract at the cons rung).

**G5 cost:** ticks asserted from data (see anomalies on the half-tick grid), both rungs
printed, cons gates. PASS.

**ZN mirror (non-gating):** n=208, gross $+77.15, after-cost cons $+41.54, shared-draw
p_1s 0.0085; deltas T +74.40 / T-2 +78.10 / T+1 −31.66 → concentration **False** —
the mirror reproduces the ZB pattern exactly: real turn-of-month drift, not concentrated
at T.

## What this means (attribution, no promotion)

1. **There IS a genuine, null-clearing month-turn long-duration drift** (both ZB and ZN clear
   the shared-draw null at p<0.01 on the event day, and again at T-2), consistent across all
   three eras. It is the *generic* turn-of-month bond seasonality — the same object G00077's
   banked control saw wash out as an ES/ZB spread.
2. **The index duration-extension mechanism is falsified at this scope**: the flow does NOT
   sit at the extension day. T-2 is as large as T, and T+1 gives roughly half of it back
   (delta −$125). A duration-extension settlement story cannot produce that shape.
3. Banked descriptive facts (NOT claims, deliberately unpursued to avoid post-hoc
   sign-mining): the T+1 day is notably negative in both markets; the modern-era premium
   has decayed to ~$14/event after cost. Any future read of a "short T+1" object would be a
   NEW preregistration carrying selection debt from this observation.
4. Classification of the observed positive: **SELECTION-FREE but NOT the named mechanism**
   — generic calendar seasonality, marginal after cost (CI includes 0), thin in the modern
   era. No candidate.

## Anomalies / disclosures

- **ZB closes sit on a half-tick (1/64) grid** (91 of 4,393 closes off the full 1/32 grid;
  NT8 records half ticks). The program asserts the half-tick grid and keeps the **declared**
  1/32 tick for the cost band (conservative, matches G00073's rungs). ZN is fully on its
  1/64 grid.
- **ZN store hole inherited AS-IS**: all of 2016-09 (22 sessions) plus scattered days
  (2015-10 ×5, 2016-08 ×1, 2025 ×~3) are absent from the upstream ZN panel → 208 mirror
  events, no 2016-09 month-end. Non-gating (mirror only); ZB is complete at 209.
- **Gap-spanning days included**: the frozen spec declared no clean_daily exclusion, so
  gap-spanning returns stay in (ZB: 3 in T, 5 in T+1; ZN: 2 in T, 6 in T+1); counts printed
  by the program.
- G2 is a **marginal** fail on the CI clause (lower bound −$4.29 vs 0) while mean>0 and
  p_1s passed; recorded FAIL as frozen — no population redefinition, no clause re-weighing.
  G3's fail is not marginal in meaning: the concentration premise itself is contradicted.
- Observed gross ($168) ≈ MDE ($164): the design was powered for exactly this effect size;
  the null-clearing read is not underpowered luck.

## Outputs

- `out/gate_table.txt` — program-printed (sha256 `abc8926054c44684143fb58d54d477377438050f05b046bb915d2700150ada42`)
- `out/event_table.csv` — 209 events, ZB + ZN mirror, eras, cost rungs
- `out/placebo_days.csv` — T-2 / T+1 cells, both instruments
- `run_durext.py`, `run_stdout.txt`, `run_stderr.txt` (empty)
- REPORT.md itself was refused by the pod harness (subagent report-file policy); this
  content is returned in the pod's structured output for the parent to place.

Ledger G00086: recommend RESULT row **FAIL** (closed at scope; powered, identified as
generic turn-of-month seasonality; completes the month-end/rates calendar family with
G00077). This pod does not write the ledger.