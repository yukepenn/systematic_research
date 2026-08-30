# G2_BOOK_M11 — `WeeklyEdgeBookM11_v1` built and verified: **PASS**

Owner request 2026-08-30: one strategy that IS the M_11 book, backtestable manually in one run.
Built by merging the two certified engines; verified against them. Full evidence:
`VERIFICATION.md`. Source archived at `research/weekly_edge/ninjascript/WeeklyEdgeBookM11_v1.cs`
(925 lines, compiled 0 errors / 0 warnings).

## The verification that matters — leg isolation, not a tolerance band

| test | result |
|---|---|
| `EnableXM=false` vs certified `WeeklyEdgeP1PCT_v1` | **2439/2439 trade rows IDENTICAL**, net equal to the cent |
| `EnableP1=false` vs certified `WeeklyEdgeXMConflict_v2` | **378/378 rows IDENTICAL** |
| combined vs arithmetic leg sum | $539,102.88 vs $537,352.88 = **+0.326%** |
| position path | strictly within **[−1, +3]** — exactly M_11 |

Rows compared on entry time, exit time, qty, entry px, exit px and P&L. This is stronger than
"within band": with a leg disabled the combined class reproduces the certified trade *series*.

## The +$1,750 decomposes exactly — and my netting hypothesis was ~200× too big

- **Netting: +$8.72.** The netted book crossed **2 fewer contract round turns in 4.6 years**
  (2 × $4.36). Gross P&L is unchanged, as theory requires (position is additive, P&L is linear in
  position ⇒ netting can only move commission). The predicted "0.3% opposing minutes" effect is
  real but economically negligible.
- **Window-edge artifact: +$1,741.28.** NT8's closed-trade list omits the position open at the
  range end. Run separately, P1 leaves +$1,741.28 and XM leaves −$3,704.36 open — both dropped
  from the sum; combined, only the netted −$3,704.36 is open, so P1's +$1,741.28 falls inside the
  list. Reconciles both ways: +1741.28 − 3704.36 + 8.72 = −1954.36 = the NetProfit-basis gap.

## Two things the builder caught in its own work (recorded, not smoothed over)

1. **XM's global early-return could not stay global** — as written it would have truncated P1's
   bar processing. Converted to an XM-only gate; a normalized line-diff then revealed only half
   the gate had been carried, which would have made **XM arm one bar earlier than certified**.
   Fixed before verification.
2. Every unmatched line in the diff (11/407 P1, 17/251 XM) is individually accounted for:
   class identity, the stripped order calls, and BarsInProgress-explicit accessors.
   `SetDefaults` is byte-identical to both certified files.

## Caveats binding on any use of this class

1. ⛔ **NOT parity-certified. NOT for deployment.** The paper/shadow evidence is gathered on the
   two certified legs (`dep_306e11dfc8eb`, `dep_5a914d070687`); this class is a backtest tool.
2. **Only TOTALS are comparable.** The trade list is not the union — netting re-cuts every
   per-trade statistic (win rate, profit factor, MAE/MFE). Do not quote its win rate as the book's.
3. Capital/margin is not the two legs' sum (one netted position, peak 3 contracts).
4. **Seal note:** the verification window ran to 2026-08-30, i.e. into August. August was already
   `DIRECTLY_BURNED` for P1/PCT and XM_v2 by the owner-authorized read (G00041), and this class
   is those two engines — so **no additional object lost its seal**. Recorded explicitly because
   the verifier flagged it unprompted, which is the behaviour we want.
5. Defaults carry both engines' certified parameters plus **`DaysToLoad = 365`**; in Strategy
   Analyzer, still start the run ≥1 year before the window of interest (P1's 250-entry quality
   window).

**`LIVE ENABLED = NO` · $0.**
