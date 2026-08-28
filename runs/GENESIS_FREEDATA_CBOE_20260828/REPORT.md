# GENESIS_FREEDATA_CBOE — RESULT: **CERTIFIED (PASS; G6 FAIL recorded and disclosed)**

Executes `spec.yaml` (committed `0440f30` before results). Trial `G00009`. 300 files / 16.3 MB /
**$0** / 0 unreachable. `raw/` is quarantined (post-seal rows present, never inspected; sha256 per
file in `raw/_MANIFEST.json`); `certified/` is mechanically truncated **< 2026-08-01** with
`research_sdk.seal_guard` assertions printed (463 post-seal rows dropped blind).

## What the project now owns, certified

| source | coverage | rows |
|---|---|---:|
| VIX (OHLC) | 1990-01-02 → 2026-07-31 | 9,241 |
| **VXN** (NQ-native) | 2009-09-14 → 2026-07-31 | 4,248 |
| VIX3M · VIX9D · VVIX · SKEW · OVX · GVZ | 2009-era starts → | — |
| **VX settlements, per contract** | 2004-03-26 (launch) → 2026-07-31, **272 contracts, 0 identity mismatches** | 46,412 |
| CFE volume + OI | 2004 → | 5,624×89 |
| CFTC COT TFF (80 markets; **VIX futures 982 weekly reports** 2006-08-29→2026-07-28) | 2006 → | 19,047 |

Sanity (not alpha): corr(VIX, VXN) levels = 0.946 over 4,246 days.

## Gate outcome — program-printed

G0–G5, G7, G8 **PASS**. **G6 FAIL as coded**: preregistered "≥99% Tuesday as-of" observed
**98.81%**. Not adjusted. Diagnostic (also program-printed): all 14 non-Tuesday as-of dates in
20.1 years are CFTC holiday-week shifts — a vendor convention now documented. Ledger PASS per the
trial's preregistered criterion (core-set certification), with the G6 FAIL in the note.

## Traps recorded in `DATA_CONTRACT.md` (measured or vendor-cited)

- ⚠️ **Pre-2007-03-26 archive VX settles are 10× scale** — measured: median(front/VIX) 10.30
  before vs 1.01 after; 3,942 rows flagged `LEGACY_10X_SUSPECT`, values unaltered.
- ⚠️ **COT is knowable only Friday 15:30 ET for a Tuesday as-of** (3-day lag, cftc.gov cited);
  historical data not restated once published (vendor statement + frozen zip mtimes).
- VIX futures absent from COT 59 in-span weeks (2009/2010 concentration — reporting standards).
- Free VXN starts 2009-09-14 (not 2001); Cboe states **no revision policy** for index histories
  (restate-capable; sha256 baselines enable drift detection); pre-2003 VIX rows retro-computed.
- COT market-name trailing-space duplicate — strip before grouping.

**`LIVE ENABLED = NO` · $0 · ceiling: DATA-CAPABLE. No alpha computed, no NQ join performed.**
