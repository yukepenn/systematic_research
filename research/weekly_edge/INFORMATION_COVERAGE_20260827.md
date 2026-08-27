# INFORMATION COVERAGE MATRIX — 2026-08-27

POST-W121 owner directive **§37**. `MECHANISM_COVERAGE_20260826.md` asks *"have we tested strategy
family X?"* This asks a different and now more useful question:

> ### **What causal information does the book actually OBSERVE, and where are the INFORMATION gaps — as distinct from the strategy-name gaps?**

Legend: **DEEP** · **SUPPORTED** · **LIGHT** · **NULL** (tested, failed) · **BLOCKED** (data) ·
**·** (untested). Every cell is marked from a committed artifact.

| information surface | depth | evidence |
|---|---|---|
| **NQ price path** | **DEEP** | the entire campaign; P1/PCT is built on it |
| **NQ volatility / range** | **DEEP** | ratchet, range throttle, W77 (verdict stands, mechanism claim withdrawn) |
| **time / clock** | **DEEP** | W104 segments, W114/W116 timing plateau, W118 event-driven entries |
| **cross-market — OPENING AUCTION** | **SUPPORTED** | `XM_CONFLICT`: the campaign's one cross-market success. W101/W102/W102c/W104/W105/W110 |
| **cross-market — INTRADAY SUPPORT** | **NULL** | **W122**: 5 primitives × 3 windows at P1's own entry events. Matched Q5−Q1 −$157, all four gates fail, best cell $262 vs a $503 family bar. Pooled signal collapses under matching ⇒ it was NQ momentum relabelled |
| **trade participation / volume (1-min)** | **NULL** | W111: −$233/trade, 0.0th pctile; three of five mechanisms **below the 5th percentile** of a volume-decile-matched null |
| **BBO / micro-price / trade imbalance** | **BLOCKED** | `DATAGATE_ORDERFLOW_20260827`: 48 sessions ⇒ **71 of 2,131 P1 entries (3.3 %)**; MDE $564/entry = **4× the mean**. Owner acquisition decision |
| **DOM / Level-II** | **BLOCKED** | owner risk-control pause 2026-08-12; no history exists anyway |
| **value / acceptance (VWAP)** | **NULL** | `VWAP_RECLAIM` closed (W108); VWAP displacement is a real *class* detector (AUC 0.621, W109) but its veto fails on both fades and the baseline |
| **market state / regime (trend vs range)** | **REAL INFO, NULL POLICY** | W109: AUC 0.613–0.621, 100th pctile of permutation nulls — **genuine**. W109 + W113: the veto fails on losing fades *and* on the profitable baseline. Selectivity ratio 0.74–1.12 |
| **turnover / own decision history** | **NULL** | W121: caps sit **below** their count-matched random placebo (0.0–4.0th pctile). Marginal entry does not decay — the 4th is the *best* |
| **scheduled macro event flag** | **LIGHT** | committed CPI/NFP/FOMC calendar; W105b (XM is *not* an event trade); W110 (announcement flag alone AUC 0.498) |
| **event RESPONSE (not the flag)** | **·** | untested |
| **overnight inventory** | **NULL** | ONRANGE01/02, W96 |
| **higher-timeframe** | **LIGHT** | HTFMECH01 (campaign #3) |
| **execution / friction** | **SUPPORTED** | W82 measured the fill cost that 82 waves had assumed |
| **market internals (TICK/ADD/TRIN)** | **✗ no data** | `DATA_CENSUS` §"market internals: NONE" |

## The honest summary

**Two surfaces are genuinely open and both are gated by data, not by ideas:**

1. **BBO / trade imbalance / micro-price** — blocked at 3.3 % event coverage. An owner acquisition
   decision (~300+ overlapping sessions would bring the MDE near the unconditional mean).
2. **Event RESPONSE** as distinct from the event flag — untested, and the calendar exists.

**Everything cheap has been measured.** The campaign has now tested cross-market intraday support,
1-minute participation, turnover, regime state and value/acceptance against P1's own decision
quality. All are null or policy-null.

> ### The next material information jump requires either **data we do not own** or a **surface nobody has named yet**. It does not require another threshold on the NQ price path.
