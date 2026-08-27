# DATA GATE — order-flow / participation information vs the P1 decision-event target

**2026-08-27. POST-W121 owner directive §20: *"Before constructing any feature: READ DATA_CENSUS…
If historical coverage is insufficient: document exactly what is missing and STOP that
construction. Do not fake proxy precision."***

This is that determination, made **before** any feature was written. **LANE B is data-blocked for
the decision-event target.** No participation feature was constructed.

## What exists

| asset | coverage |
|---|---|
| `research/scalping_lab/substrate/grid1s/NQ/` — 1-second L1 grid with `sflow`, bid/ask/mid/spread | **48 session files**, 2025-08-11 → 2026-05-20, **non-contiguous** |
| `research/scalping_lab/substrate/raw/NQ/s*.parquet` — tick trades + BBO events | same 48 sessions, 531.6 M events |
| `research/scalping_lab/substrate/raw/ES/` | 39 sessions, manifest **ARCHIVE_ONLY** |
| quotes missing | 3 of 48 NQ sessions (`s20250811`, `s20250924`, `s20260430`) |
| DOM / Level-II / Market Replay | **PAUSED** by owner risk-control 2026-08-12 — not to be resumed autonomously |

## What that leaves against the actual target

The POST-W121 directive (§13, §22) sets the discovery unit as the **P1 entry event** and the
**XM 09:45 decision**, with the incremental question measured *after* controlling for NQ price
state, P1 state and time-of-day.

Measured against `runs/WE_W119_BOOKLOSS/out/book_loss_ledger.csv`:

| | overlapping the order-flow substrate | total in the modern window | share |
|---|---|---|---|
| **sessions** | **48** | 1,058 | **4.5 %** |
| **P1 entry events** | **71** | 2,131 | **3.3 %** |
| **XM decisions** | **16** | 348 | **4.6 %** |
| book dollars | $21,339 | $243,177 | 8.8 % |

## Why 71 events cannot answer the question

P1 entries have sd = **$1,697** per entry against an unconditional mean of **$139**.

| sample | minimum detectable effect at ~80 % power |
|---|---|
| **n = 71** (order-flow overlap) | **$564/entry — 4.0× the unconditional mean** |
| n = 2,131 (full window) | $103/entry — 0.7× the mean |
| a two-group split of 71 (36 / 35) | **~$1,128/entry difference** |

> ### To register as significant on this sample, a participation feature would need to identify entries worth **four times the average entry**. Anything real and useful — say a 30–50 % swing in entry quality — is **invisible** here.
> ### And the requirement is *incremental* information, **after** NQ/P1/time-of-day controls. Stratified matching on 71 events leaves single-digit cells.

This reproduces W82's finding on the same substrate — *"only 64 of 2,010 entries have quote
coverage, detectable |ρ| = 0.250 against W55's measured ceiling of 0.11 — UNDERPOWERED and labelled
so. 45 sessions cannot say whether microstructure data is worth buying."* **Nothing has changed
since; the substrate has not grown.**

## Determination

**LANE B (participation / order flow) is CLOSED-BY-DATA for the decision-event target, not
falsified.** The information may well exist; we cannot see it.

**Not done, deliberately:**
- No proxy built from 1-minute volume and dressed as order flow. W111 already tested 1-minute
  participation as a direction and found it **anti-predictive** (three of five below the 5th
  percentile of a volume-decile-matched null); re-deriving it under a microstructure name would be
  the rename-and-rerun §35 forbids.
- No DOM/Level-II collection resumed — owner risk-control pause, 2026-08-12, still binding.

**What would unblock it, stated concretely for the owner rather than left implicit:**

| requirement | current | needed for a usable test |
|---|---|---|
| sessions with L1/BBO coverage overlapping P1 entries | 48 | **~300+** for ~450 entries, the point at which the MDE falls near the unconditional mean |
| contiguity | non-contiguous | contiguous enough to span multiple regimes |
| ES coverage for cross-market microstructure | 39 sessions, ARCHIVE_ONLY | matched to NQ |

That is an **owner data-acquisition decision**, not a research task. It is recorded here and in
`MONITORING_CALENDAR.md`'s gated section; it is not being asked repeatedly.

**Effort therefore moves to LANE A (cross-market intraday support), which has full coverage** —
ES/RTY/YM 1-minute aligned to NQ across all 1,058 sessions, at zero acquisition cost.
