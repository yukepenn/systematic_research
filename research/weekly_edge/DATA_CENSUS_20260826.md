# DATA CENSUS — 2026-08-26

What can actually be tested, before designing anything. Compiled under OWNER MEGA DIRECTIVE V4
(§2 opportunity accounting, §7 research tracks F/G, §8 mine what we own). Every row was located on
disk; the four 1-minute futures substrates were additionally re-opened and their spans asserted by
hand before this file was written.

---

## 1. ⭐ THE UNLOCK — cross-market is already on disk, aligned, and needs no purchase

| substrate | rows | span | path |
|---|---|---|---|
| **NQ** 1-min Last | 1,620,044 | 2022-01-02 18:01 → 2026-07-31 16:59 | `runs/SM1M_SUBSTRATE/out/nq_1m_2022_2026.parquet` |
| **ES** 1-min Last | 1,620,385 | identical | `runs/SM1M_ES_SUBSTRATE/out/es_1m_2022_2026.parquet` |
| **YM** 1-min Last | 1,595,378 | identical | `runs/SM1M_YM_SUBSTRATE/out/ym_1m_2022_2026.parquet` |
| **RTY** 1-min Last | 1,568,111 | identical | `runs/SM1M_RTY_SUBSTRATE/out/rty_1m_2022_2026.parquet` |

`open, high, low, close, volume`, naive exchange-session ET, all four ending on the same minute by
construction — i.e. **seal-clean**. RESEARCH TRACK G (cross-market context: does broad-index
agreement improve NQ continuation, does NQ/ES disagreement predict failed persistence, does RTY
weakness identify bad NQ longs) is testable **today**, at zero cost, on 1,058 sessions.

The row-count differences are real (RTY prints fewer minutes) and any join must be an explicit
minute-level align, not an index assumption.

## 2. NQ price history

| | span | path |
|---|---|---|
| deep 1-min Last | 2006-01-05 → 2026-05-29 (6,466,783 rows) | `research/scalping_lab/substrate/minute/NQ/nq1m_2005_202605.parquet` |
| modern 1-min Last | 2022-01-02 → 2026-07-31 | `runs/SM1M_SUBSTRATE/out/nq_1m_2022_2026.parquet` |

`run_we_w17.load_deep(..., extend=True)` joins them; that join is the ONLY way to get 2006 → 2026-07
in one series, and the deep file stops four weeks short of the modern one.

Known defects of record (`research/scalping_lab/substrate/MANIFEST_NOTES.md`): the whole week
**2014-01-27..31 is missing**, plus 2009-03-27, 2009-06-19, 2013-07-12; 46 days carry only 261–379
RTH bars.

**Volume is present and clean on the 1-min NQ bars** (0 nulls, 0 zeros on 2022–26). Volume-based
mechanisms are testable over the full history. **Signed/aggressive delta is NOT** — the bars are
Last-only.

## 3. Order flow — real, but 48 days

| | what | span |
|---|---|---|
| `research/scalping_lab/substrate/raw/NQ/s*.parquet` | tick trades **+ BBO quote events** (`bip` 0=trade/1=bid/2=ask), 2.1 GB, 531.6 M events | 48 sessions, 2025-08-11 → 2026-05-20, **not contiguous** |
| `research/scalping_lab/substrate/grid1s/NQ/` | 1-second L1 grid, already carries a signed-flow column `sflow`, plus bid/ask/mid/spread | same 48 sessions |
| `research/scalping_lab/substrate/raw/ES/` | ES ticks + BBO, 39 sessions | 2025-08-14 → 2026-05-20 (manifest: ARCHIVE_ONLY) |

Quotes are missing on 3 of the 48 NQ sessions (s20250811, s20250924, s20260430).

> TRACK F is therefore an **event-conditioned, ~45-session** question, not a universal one. Any
> order-flow claim carries n≈45 sessions and must be powered accordingly. This is also the sample
> the whole campaign's spread/cost profile rests on (W82/W89 used 45 of them).

**DOM / Level-II / Market Replay collection remains PAUSED** (owner risk-control, 2026-08-12).
Reading files that already exist is not collection. One replay day exists
(`db/replay/NQ 09-26/20260715.nrd`, 161 MB) and is not to be extended.

## 4. What we do NOT have

| | status |
|---|---|
| options / gamma / dealer positioning | **NONE.** Zero strikes, zero OI, zero Greeks. Purchase memo only: `runs/GAMMA00_DEALER_GAMMA_FEASIBILITY/DATA_PURCHASE_OPTION.md` |
| market internals (advance-decline, TICK, TRIN) | **NONE** |
| rates intraday | **NONE.** Daily only: `research/breadth_lab/BREADTH02_CARRY/data/treasury_curve.parquet` (3M/2Y/10Y/30Y, 2002 → 2026-08-19). NT8 has empty `10YR`/`2YR` minute dirs |
| signed delta before 2025-08 | **NONE** — bars are Last-only |
| SPY intraday | **NONE** (`intraday_system` carries **QQQ only**, IBKR 1-min RTH from 2020-01) |

Daily cross-asset ETFs and VIX/VIX3M do exist (`research/breadth_lab/**/data/`) but are **daily**,
so they can condition a session, not time an entry.

## 5. ⚠️ SEAL HAZARD — three on-disk assets already cross 2026-08-01

Everything dated ≥ **2026-08-01 is VIRGIN** (`research/operational/LOCKED_FORWARD.md`), and
**2026-05-31 → 2026-07-31 is BURNED** (already consumed by development).

The four futures substrates stop at 2026-07-31 16:59 by construction and are safe. These are not:

| asset | runs to |
|---|---|
| every `research/breadth_lab/**` ETF / VIX / treasury parquet | **2026-08-19** |
| `NinjaTrader 8/db/tick/NQ 09-26` | **2026-08-11** |
| `NinjaTrader 8/db/minute/NQ 09-26` | **2026-08-26** |

> **Any study touching those three must truncate at 2026-07-31 explicitly, or it silently consumes
> virgin data.** Add the truncation to the harness, not to the analyst's memory.

## 6. What this implies for the research tracks

| track | feasible now? | on what |
|---|---|---|
| A downside / bear persistence | **YES** | NQ 1-min 2006→2026, volume |
| B reversal / failed persistence | **YES** | NQ 1-min, VWAP, opening range |
| C range / value | **YES** | NQ 1-min, VWAP, volume |
| D volatility transition | **YES** | NQ 1-min |
| E open / overnight **information** | **YES** | NQ 1-min (but W97 killed the "different clock = independent alpha" rationale — needs genuinely new information) |
| F order flow | **PARTIAL — 45 sessions** | `grid1s` `sflow`, raw tick BBO |
| G **cross-market** | **YES, IMMEDIATELY** | ES/RTY/YM 1-min, same 1,058 sessions |
| H event / calendar | **YES** for dates; no macro-surprise magnitudes on disk |
