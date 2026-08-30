# VERIFICATION — WeeklyEdgeBookM11_v1 vs the two certified legs

**Verdict: PASS.** The combined class reproduces both certified engines **exactly, trade for trade.**
The residual difference against the arithmetic sum is fully decomposed to the cent and is *not* an
economic divergence.

Date: 2026-08-30 · Engine: `nt8_strategy_analyzer`, NT8 8.1.8.1, addon v1.13.9,
fingerprint `sha256:b4255f1b0dd7fba1` · Account: isolated NT8 **Backtest**.
Verifier ran backtests only. No file in NT8 or in the repo was modified; no git was run.

## 1. Common run settings (identical for every row below)

NQ 09-26 · 1-minute · `2022-01-03T00:00:00Z` → `2026-08-30T21:59:59Z` ·
trading hours `CME US Index Futures ETH` · fill Standard / 0 slippage ·
commission template `NinjaTrader Brokerage Lifetime` ($2.18/side ⇒ $4.36/contract round turn).

## 2. Measurements (all runs made by this verifier in this session)

| object | closed-trade rows | Σ ProfitCurrency | TradesCount | NetProfit | TotalQuantity | Commission |
|---|---:|---:|---:|---:|---:|---:|
| `WeeklyEdgeP1PCT_v1` (certified) | 2439 | 354,575.96 | 2440 | 356,317.24 | 2941 | 12,822.76 |
| `BookM11_v1`, `EnableXM=false` | 2439 | **354,575.96** | 2440 | **356,317.24** | **2941** | 12,822.76 |
| `WeeklyEdgeXMConflict_v2` (certified) | 378 | 182,776.92 | 379 | 179,072.56 | 379 | 1,652.44 |
| `BookM11_v1`, `EnableP1=false` | 378 | **182,776.92** | 379 | **179,072.56** | **379** | 1,652.44 |
| `BookM11_v1`, both legs on | 2862 | 539,102.88 | 2863 | 535,398.52 | 3318 | 14,466.48 |

**Leg-isolation identity test (the decisive evidence).** Trade lists were compared row by row on the
ordered tuple *(entry time, exit time, quantity, entry price, exit price, P&L)*:

- P1 leg: **2439 / 2439 rows identical, 0 mismatches.**
- XM leg: **378 / 378 rows identical, 0 mismatches.**

Each leg inside the combined class is therefore not merely "within tolerance" of its certified
counterpart — it is the **same trade series**, well beyond the ≥99 % / ±2 % VALIDATED band.

**Source audit.** A normalised diff of the P1 region (223 logic lines, comments stripped, the
documented `p1_*` renames and `Times[0][0]`-style BIP-explicit accessors reversed) returns
**only** the header's declared adaptations: the `BarsInProgress != NQ` guard, the XM-only
`xmSeriesReady` gate, a `hist`→`rhist` local rename, and the order-call → `p1Target` substitution.
No threshold, formula, comparison operator or ordering differs. `SetDefaults` in the combined class
is byte-identical to both certified files on every shared parameter.

## 3. The difference, decomposed to the cent

The parent's baselines are **closed-trade-list sums** — both match Σ ProfitCurrency exactly
(354,575.96 and 182,776.92), not `NetProfit`. Compared on that same convention:

| | trades | net |
|---|---:|---:|
| Combined book | 2862 | **539,102.88** |
| Arithmetic sum of legs | 2817 | 537,352.88 |
| **Delta** | +45 | **+$1,750.00  (+0.326 %)** |

That +$1,750.00 is exactly two effects:

**(a) Netting — the real economic effect: +$8.72 (+0.0016 %).**
`TotalQuantity` is 3318 for the book versus 2941 + 379 = **3320** for the legs run separately.
The netted book crossed **exactly 2 fewer contract round turns** in 4.6 years, saving
2 × $4.36 = **$8.72**. On the all-inclusive `NetProfit` basis the book returns $535,398.52 against
$535,389.80 for the two legs — a difference of **$8.72, the entire netting effect.**
Gross P&L is unchanged, exactly as theory requires: the book's position is the *sum* of the two
legs' positions and P&L is linear in position, so netting can only ever move commission.

**(b) The window-edge open trade — an accounting artifact: +$1,741.28.**
NT8's closed-trade list omits the one position still open when the range ends. Run separately, P1
leaves an open trade worth **+$1,741.28** and XM leaves one worth **−$3,704.36**; *both* are
excluded, so the arithmetic sum silently drops both. Run combined, there is only **one** netted
position at the edge (−$3,704.36), so P1's +$1,741.28 falls *inside* the closed list instead of
outside it. Nothing was earned; a trade merely moved across the reporting boundary.

Check: +1,741.28 − 3,704.36 + 8.72 = −1,954.36 = the `NetProfit`-basis gap. Both views reconcile.

**The expected cause (netting on ~0.3 % of minutes) is confirmed as real, but it is ~200× smaller
than the headline delta.** The headline is dominated by (b), which is not economics at all.

## 4. Both legs' signatures are present in the combined book

- **P1's 23-hour footprint** survives intact: the combined entry-hour histogram matches P1-only
  hour for hour across all 23 traded hours (e.g. 03h 154→154, 08h 177→177, 18h 146→147).
- **XM's RTH-only opening-auction footprint** is superimposed: hour 09 rises 388 → 767 (+379,
  i.e. XM's 378 entries plus one re-cut), and 09:45–09:50 entries rise 378 → 416.
- **XM cadence**: 378 trades over 55 months — median **7.0**/month, mean 6.87, range 2–14,
  consistent with the expected ~5–9/month.
- **Direction**: P1 is long-only, so every short is XM's. Netted position path stays strictly within
  **[−1, +3]**, exactly the stated M_11 mapping (p1Target ∈ {0,1,2} + xmTarget ∈ {−1,0,+1}).

## 5. Caveats the owner must know before using this class

1. **NOT parity-certified.** The certified objects remain `WeeklyEdgeP1PCT_v1.cs` and
   `WeeklyEdgeXMConflict_v2.cs`. This class is a convenience harness for one-run manual backtests.
2. **The trade list is not the union of the legs' trade lists** (2862 rows vs 2817). Netting re-cuts
   trade boundaries, so **every per-trade statistic is a different object**: win rate, profit factor,
   MAE/MFE, average bars in trade, max consecutive losers. Only the *total* is comparable to the
   legs. Do not quote this class's per-trade stats as the certified legs' stats, or vice versa.
3. **Capital and margin are not the sum of the legs.** The book holds ONE position in [−1, +3].
   This remains an `EXECUTABLE_COMPONENT_SET` question; running the book is still not the
   inverse-vol research portfolio, and no integer-contract/capital mapping is certified by this run.
4. ⚠️ **Data seal.** This window ends 2026-08-30 and therefore crosses the **VIRGIN** seal
   (≥ 2026-08-01, CLAUDE.md §5). The verifier used the window it was given so the comparison would
   be like-for-like, but this run **did touch sealed-forward data** and was not a scheduled read in
   `MONITORING_CALENDAR.md`. Treat every figure here as **DIRECTLY_BURNED** for the August-2026
   segment, and do not reuse this window for tuning.
5. `DaysToLoad = 365` is set in the combined class but not in the legs. In Strategy Analyzer the
   From/To range governs; the identical first trade timestamp (2022-01-02T19:53) in both the
   certified and combined runs confirms it had no effect **here**. On a chart or another harness it
   would differ.
6. `DisasterStopPoints = 0.0` — the XM disaster stop is **OFF** by default in this class, matching
   the certified default. No level has been selected.
7. `BarsRequiredToTrade = 20` now also has to be satisfied by ES/RTY/YM. It changed nothing over
   this window (the leg-isolation identity is exact), but it is a real structural difference.
8. **Status: RESEARCH_ONLY. Not enabled, not deployed. No live enablement is implied or authorised.**
