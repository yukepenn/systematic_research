# R2V1 — formal validation/adjudication of the confirm_bars=2 candidate

**VERDICT: NOT PROMOTED.**

Per frozen `R2V1_spec.yaml`. Candidate fixed at `ConfirmBars=2`
(`SolarWaveOneContractNQ_v6_R2CONFIRM.cs`), no further tuning performed. Incumbent
(`SolarWaveOneContractNQ_v5`/`SolarWaveOneContractMNQ_v5`) unchanged throughout. This
supersedes REPORT.md's "VALIDATING" status with a completed adjudication.

## 1. Priority zero: `n_cancelled=0` resolved — INSTRUMENTATION BUG, not a behavioral fact

Built an exact entry-attempt mapping (`src/entry_mapping.py`,
`out/r2v1_entry_attempt_mapping.csv`) via fresh-restart forward simulation of the confirm=2
state machine at every one of the 1,978 incumbent entry events. Result:

| category | n | % | incumbent $ sum |
|---|---:|---:|---:|
| A_SAME_DIRECT (2-bar delay only, no cancel) | 1,838 | 92.9% | $449,399.66 |
| B_SAME_REARMED (cancelled, re-armed, same side eventually) | 69 | 3.5% | -$43,450.68 |
| D_OPPOSITE (armed, opposite side confirmed first) | 33 | 1.7% | -$71,063.48 |
| E_RESET_NO_CANCEL (hit session reset while still arming) | 23 | 1.2% | -$7,064.50 |
| C_CANCELLED_NO_REENTRY (cancelled, never re-entered that session) | 15 | 0.8% | -$11,749.88 |

**103/1,978 (5.2%) experience at least one cancel/re-arm event** — the true cancellation rate.
`construct.py`'s `n_cancelled` counter only incremented on a DIRECT flip to the opposite
nonzero side, not on reverting to neutral (the far more common cancellation mode) — **confirmed
as a cosmetic instrumentation gap, not evidence the mechanism doesn't cancel anything.** No
candidate behavior is changed by this finding (per spec, only the diagnostic counter would be
fixed; not done in this run since it does not affect any reported P&L number, only a print
statement).

## 2. True mechanism: **near-universal 2-bar delay, NOT primarily a bad-entry filter**

92.9% of entries are simply delayed 2 bars with no change in direction or outcome type. Only
7.1% are qualitatively changed (redirected, cancelled, or substantially deferred). Decomposing
the REAL candidate trajectory's dollars by category (same-span+3-bar-buffer approximation,
`out/r2v1_entry_attempt_mapping.csv` cross-referenced against `barpnl_CONFIRM2_NQ.npy`):

| category | incumbent $ | candidate $ (approx) | delta |
|---|---:|---:|---:|
| A (93% of trades — pure delay) | $449,399.66 | $367,769.58 | **-$81,630.08** |
| B+C+D+E (7% of trades — mechanism-changed) | -$133,328.54 | -$26,481.13 | **+$106,847.41** |
| **total** | $316,071.12 | $341,288.46 | **+$25,217.34** (matches the observed ~$26.1k full-history delta) |

**The mechanism is genuinely two offsetting effects of similar magnitude**: the 2-bar delay
itself is a NET COST on the 93% majority of (mostly good) trades — waiting costs the first 6
minutes of a favorable move. The net benefit comes ENTIRELY from a small (7.1%) minority of
entries where those same 2 bars correctly caught a reversal, redirect, or dead end that the
incumbent's immediate entry did not avoid. This is a real, mechanistically-understood effect,
but it is a **thin, concentrated edge**, not a broad-based one — 140 trades out of 1,978 (7.1%)
account for the entire net improvement.

## 3. Chronology — DISQUALIFYING FINDING: full-history improvement is 2026-stub-only

`src/r2v1_chronology_bootstrap.py`, `out/r2v1_year_by_year.csv`, `out/r2v1_loyo.csv`.

| year | net delta | Sharpe delta |
|---|---:|---:|
| 2022 | +$4,072.32 | +0.077 |
| 2023 | +$8,440.40 | +0.257 |
| 2024 | +$3,067.96 | +0.062 |
| 2025 | **-$20,012.04** | -0.221 |
| 2026 stub (4.5 months) | **+$30,552.96** | +0.953 |

**2022-2025 ONLY (4 full audited years): net delta = -$4,431.36 (candidate is NOT an
improvement — a wash, slightly negative).** The entire full-history headline (+$26,121.60) comes
from the 106-session 2026 stub alone. **LOYO-2026 confirms this exactly**: removing 2026 leaves
delta_net = -$4,431.36, essentially zero Sharpe delta (+0.008) — the candidate has NO
demonstrated edge on the 4 years of already-audited history. Removing any OTHER single year
(2022/2023/2024/2025) still leaves the 2026 stub's outsized contribution dominating, so LOYO for
those years stays strongly positive — an artifact of the stub's concentration, not evidence of
year-independent robustness.

**This is not specific to ConfirmBars=2.** The `ConfirmBars=1` neighbor shows the IDENTICAL
qualitative pattern: full-history delta +$10,352.20, but 2022-2025-only delta **-$1,319.60**,
2026-stub delta +$11,671.80. **The entry-confirmation mechanism at BOTH tested settings only
"works" in the 2026 stub** — this is a structural property of the mechanism-vs-regime
interaction, not noise specific to one parameter choice, and not something a different
ConfirmBars value would likely fix (no further values are tested, per the binding no-re-tuning
rule). The 2026 stub is independently already flagged elsewhere in this repo
(`research/system_master/CURRENT_TRUTH.md` Wave-19 section) as an anomalous period where the
INCUMBENT itself underperforms and does not fit its own historical regime relationships — a
mechanism that only helps during an already-flagged anomalous stretch is weak evidence of a
stable structural edge, not strong evidence of one.

Quarter-by-quarter (`out/r2v1_quarter_by_quarter.csv`) confirms this is not one blown quarter:
7 of 14 pre-2026 quarters are negative for the candidate, roughly split, consistent with "no
real edge, noise-level either way" over 2022-2025.

## 4. Block bootstrap

`out/r2v1_bootstrap.json` (block=5, seed=20260809, matching S2_SELTIME R2's own convention,
10,000 resamples on the full-history paired daily delta): P(delta net>0) = 82.2%, P(delta
Sharpe-of-delta>0) = 82.2%, median delta net +$25,916.60, 5th percentile **-$20,478.44** (a real,
non-trivial chance of material underperformance). This bootstrap pools the WHOLE 5-year sample
including the 2026 stub, so an 82% figure does not rescue the finding once the LOYO-2026 result
above is taken into account — the resampled blocks are still drawing disproportionately from the
same short, concentrated, anomalous period that drives the headline.

## 5. Exact tail/trade mapping

`out/r2v1_top20_trade_mapping.csv`, `out/r2v1_bottom20_trade_mapping.csv`. Top-20 winner
retention (exact per-trade mapping, not span-buffered): **95.0%** ($280,054.22 -> $266,134.98).
18/20 top winners are category A (pure 2-bar delay, price-neutral-ish). **One top-20 winner
($11,367.82, 2025-04-08 22:xx short) is category E_RESET_NO_CANCEL and is COMPLETELY MISSED by
the candidate** (candidate approx $0.00 over that span) — a genuine, not hypothetical, right-tail
cost, small in aggregate (1 of 20) but real. **2025-04-09's +$41,337.82 winning leg is category
A_SAME_DIRECT and is preserved (slightly improved to $41,750.64)** — the campaign's standing
stress-test day remains safe. Bottom-20 losers show the expected mixed picture: mostly category
A (delayed, similar-magnitude loss, sometimes worse/better on pure timing luck), with the one
D_OPPOSITE case ($304003, -$4,922.18 -> -$62.18) showing the mechanism's redirect benefit
concretely.

## 6. Cost stress — same 2026-stub dependency

2-tick stress (`out/tail_and_cost_stress_results.json` for the full-history figure; re-verified
here split by period): full-history candidate still beats control ($309,897.52 vs $283,150.92),
but **2022-2025-only delta under 2-tick stress is -$3,921.36** (2026-stub delta +$30,667.96) —
the same pattern holds under cost stress. Surviving cost stress on a headline number that is
itself not demonstrated outside the 2026 stub is not independent confirming evidence.

## 7. NT8 event-level semantics

The already-passing early NT8 check (`NT8_VALIDATION.md`, 149/149 exact trade-count match on
the 2024-04..2025-04 window) is retained, not rerun. Combined with the entry-attempt-mapping
taxonomy above (built from the same Python M-array logic the NinjaScript C# code mirrors
line-for-line — `armedSide`/`armedBars`/reset-on-`forceFlat`/reset-on-`entryBlocked`), the exact
trade-count agreement on a window with a mix of A/B/C/D/E-category outcomes is itself strong
evidence the two implementations agree on WHEN entries commit, without needing a separate raw
NT8 event-log dump.

## 8. Promotion-gate checklist (R2V1_spec.yaml)

| gate | result |
|---|---|
| (a) real, mechanistically-understood incremental edge, not an n_cancelled artifact | PASS (mechanism explained above) but thin (7.1% of trades) |
| (b) 2022-2025-only delta not hidden behind full-history headline | **FAIL — negative (-$4,431.36)** |
| (c) LOYO retains improvement with each year removed, esp. LOYO-2026 | **FAIL — LOYO-2026 delta ≈ $0 (-$4,431.36, essentially the full 2022-2025 wash)** |
| (d) bootstrap confidence bar | marginal-pass in isolation (82.2%), but not independent of (b)/(c) |
| (e) right-tail preserved AND left-tail genuinely improved | mostly pass (95% top-20 retention) with one genuine miss disclosed |
| (f) 2-tick cost stress | same 2026-dependency as headline, not independent confirmation |
| (g) NQ/MNQ shared-core viability | not separately broken by this finding, moot given (b)/(c) |
| (h) NT8 executable parity | PASS (retained from earlier check) |
| (i) full-history NT8 certification | NOT RUN — correctly withheld per spec, since (b)/(c) already fail |

**Gates (b) and (c) both fail decisively and independently of each other** (year-by-year AND
LOYO both isolate the same root cause). Per `R2V1_spec.yaml`'s own binding rule and the owner
directive's explicit sec14 instruction ("Do NOT promote solely from headline Sharpe/net... The
2026 concentration must be explicitly adjudicated"), this is sufficient for **NOT PROMOTED**
regardless of the headline $328k/Sharpe 1.238 numbers, which are now understood to be a
2026-stub artifact rather than a demonstrated structural edge.

## Disposition

**NOT PROMOTED.** `v5` incumbents (`SolarWaveOneContractNQ_v5`, `SolarWaveOneContractMNQ_v5`)
remain untouched and are NOT re-tuned. `SolarWaveOneContractNQ_v6_R2CONFIRM.cs` is archived as
rejected research evidence (kept in `src/ninjascript/`, NOT deployed further, NOT built into an
MNQ sibling, NOT run through full-history NT8 certification — correctly withheld per the
promotion gate's own ordering rule). No MNQ challenger is built. Campaign stop rule is NOT
triggered. Per the owner directive's sec16, continuing automatically to R3.

**What would change this verdict**: a full additional year or more of out-of-sample data showing
the 2026-stub-style edge persists outside that specific anomalous period, OR a mechanistic
explanation for WHY 2026 specifically favors a 2-bar entry delay that is independently verified
(not merely post-hoc pattern-matched) — either would require new information, not a re-run of
this same grid, per this campaign's own standing discipline against reopening closed axes
without new evidence.
