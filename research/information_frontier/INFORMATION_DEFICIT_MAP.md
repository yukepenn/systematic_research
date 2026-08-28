# INFORMATION DEFICIT MAP — what the project does NOT observe

2026-08-28. For each: **what it would add that is not deterministically reconstructible from what
we already hold.** ⛔ A family that fails **N1** is a *transformation*, not a deficit.

---

## 1. Genuine deficits — things no owned field can reconstruct

| deficit | what it would add | N1 | N2 | N3 | N4 | N5 |
|---|---|:--:|:--:|:--:|:--:|:--:|
| **order-book DEPTH beyond best bid/offer** | displayed size at multiple levels, replenishment, cancellation dynamics. **Best-bid/offer prices cannot reconstruct size behind them** | ✅ | ✅ | ✅ `ts_recv` | ✅ | ✅ ~2,300 sessions |
| **order-LEVEL events (MBO)** | queue position and exact signed flow. **Aggregated bars cannot recover order identity** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **VIX / VX term structure** | the market's *priced* forward volatility path. **Not reconstructible from NQ price history** | ✅ | ✅ | ✅ settlement files | ✅ | ✅ 1990→ |
| **NYSE breadth (`$TICK`, `$TRIN`, `$ADD`)** | cross-sectional participation of the *underlying constituents*, which an index future does not contain | ✅ | ✅ | ⚠️ vendor-computed | ✅ | ⚠️ **35.7 % RTH ceiling on P1 — permanent** |
| **option open interest / settlement** | the *stock* of outstanding positions. **No price series contains it** | ✅ | ⚠️ **EOD, ≥1 session stale** | ⚠️ | ✅ | MED |
| **CFTC COT positioning** | who holds what, by category — the **crowding axis** | ✅ | ⚠️ weekly, lagged | ✅ public | ⚠️ resolution mismatch | MED |
| **macro release timestamps + surprise** | event identity and magnitude at a certified instant | ✅ | ✅ | ⚠️ **revision behaviour is the whole problem** | ✅ | ⛔ **N5 FATAL — see §3** |

## 2. ⛔ Failing N1 — transformations, not deficits

| claimed "new source" | actually |
|---|---|
| any vendor indicator built on OHLC / Last / BBO / volume / VWAP / MAs | **`TRANSFORMATION`**. Campaign #6's externally-sourced families all map to fields already owned. **FEATURE NAME ≠ OBSERVED FIELD** |
| **"dealer gamma" / "positioning" / "smart money" / "support walls"** | **`INFERRED LATENT`**, not an observation. Built on OI (stale, EOD) + strikes + **an assumed dealer sign that is a free parameter and flips the entire signal**. ⛔ Vendor branding does not remove model risk |
| ES↔NQ sub-minute joint quote state | **owned and failed** — corr 0.0034 |
| multi-market *daily* volume/liquidity | **owned and closed** — gross negative before costs; the mirror also loses |

## 3. ⛔ The deficit that money cannot close

> ### **MACRO SURPRISE MAGNITUDE.**
> `DATAGATE_EVENTRESPONSE` measured the binding constraint: a response feature reaches **153 of
> 2,131 P1 decisions (7.18 %)** on **71 effective event sessions**, MDE **$1,896.67 = 9.8× the
> lane-scaled bar**, requiring **~96× the effective N** — roughly **220 years of calendar**.
>
> **Buying surprise magnitudes adds ZERO SESSIONS.** It buys better features on the same 71.
> **An N-bound gate cannot be moved with money.** Even a 4× wider event calendar reaches only ~5×
> the bar. This is the clearest "do not buy" on the map, and it is clear *because it was measured*.

## 4. The deficit the project keeps re-discovering

**Three times now, a "we do not have X" has turned out to be "this REPO has not fetched X":**
order flow (`DATA_CAPABILITY_AUDIT`, 2026-08-27) · `$TICK` depth (this census) · VX term structure
(this census, **never named at all**).

> ### **The lesson is procedural, not about any one dataset: probe the connection and the disk
> ### before declaring an absence.** A registry that hard-codes `symbol="NQ"` will report MNQ as
> ### absent forever, and it did.
