# GENESIS III — CHAMPION VERDICT

**2026-08-31.** `LIVE REAL MONEY = NO · $0 SPENT · NO ORDER PLACED BY THIS CAMPAIGN.`
Machine truth first; every load-bearing number below was recomputed by the orchestrator, and where
an agent and the source disagreed, **the source won and the correction is recorded.**

---

# A. TOMORROW BOOK

```
BEST DEFENSIBLE BOOK IF TRADING TOMORROW

P1:           WeeklyEdgeP1PCT_v3      x1 NQ    (dep_9c51536a7045 / 399562877)
XM:           WeeklyEdgeXMConflict_v4 x1 NQ    (dep_27ff47e7e3b7 / 399562878)
NEW SLEEVE 1: NONE
NEW SLEEVE 2: NONE

TOTAL CONTRACT/RISK MAPPING:
  1 NQ per leg. P1 sizes 1 or 2 by its causal quality score; XM is always 1.
  Peak simultaneous exposure 3 NQ contracts. Peak simultaneous exposure 3 NQ contracts.
  SUPERSEDED 2026-08-31/09-01: the MNQ variant was not merely evaluated - it was BUILT, gate-verified
  (MX01 gates G1-G6 all PASS; per-bar decision exports byte-identical, same sha256, 61,600 bars per
  leg) and DEPLOYED LIVE. MNQ COMMISSION is MEASURED: $1.30/ctr RT vs NQ $4.36 - 3.35x cheaper per
  CONTRACT but 2.98x dearer per unit of EXPOSURE ($13.00 vs $4.36). ** MNQ SPREAD IS NOT MEASURED.**
  The '~$35/week at 3 MNQ' figure is the COMMISSION penalty ALONE and contains no spread term; the
  'spread does not degrade' premise is an ASSUMPTION whose tick arithmetic is right and whose
  empirical half was never checked. Band it leaves open: -$5.6/wk to +$76.3/wk. Corrected
  2026-09-01; authority research/operational/COST_MODEL.md SS5. See
  runs/MX01_MNQ_EXECUTION_PORT_20260831/ and CURRENT_LIVE_TRUTH.md.

CAPITAL:  [1 NQ + 1 NQ CONFIGURATION ONLY - THIS IS NOT WHAT IS DEPLOYED]
  $75,000 - $90,000. WEEKLY-bucketed max drawdown $45,138 (2022-W05 -> 2022-W17) gives ~2x
  coverage - but section A2.2 of this same file rules that the TRADE-LEVEL $51,891 is "the figure
  capital planning must use". Against $51,891 the coverage is 1.4x - 1.7x, NOT ~2x.
  The retired figures $21,740 and $45,000 stay retired AS CAPITAL REQUIREMENTS.

  LIVE, AS DEPLOYED 2026-09-01: account 2047681, $10,206.86, MnqPerNq=3 = 0.30 NQ-equivalent.
  0.30 x $51,891 = $15,567 = 152.5% of the account. Coverage 0.66x. See CURRENT_LIVE_TRUTH.md.

EXPECTED AFTER-COST FORWARD RANGE:
  $900 - $1,900 / week, central region ~$1,300 - $1,600. UNCHANGED by this campaign.
  Every historical figure is in-sample and post-selection; P1's quoted research economics are
  now known to sit ~2.0% ABOVE the object that actually trades.

MAJOR FAILURE MODE:
  A 2022-style regime. In H1 2022 XM lost $24,624 in 17 traded weeks while P1 made +$9,220, and
  adding XM multiplied the book's drawdown 1.95x. In every window since, XM has multiplied it
  only 1.27x and has ADDED $491-536/wk at matched drawdown. The book is not regime-proof and
  the capital plan must carry the 2022 case, not the modern one.

CONFIDENCE / EVIDENCE CLASS:
  EXECUTABLE_COMPONENT_SET, parity-certified, paper-deployed, NOT live-enabled.
  Decisions forward from 2026-08-30 18:00 ET: FORWARD_DECISION_FIRST.
  Fills/slippage/P&L on DEMO8383477: SIMULATED_FILL_NON_EVIDENTIAL (zero information).
  All historical economics: DISCOVERY_CONSUMED / in-sample.
```

## `M_11 UNCHANGED.`

Not by default. **By measurement:** five preregistered challenges were run today and every one was
recorded FAILED or CLOSED against a falsifier written before its results existed.

---

# A2. THE OWNER ASKED THE HARDER QUESTION: IS THIS GOOD ENOUGH FOR REAL MONEY?

"Have you found a better strategy, or is it still P1+XM in its current form?" — **still P1+XM, and
no candidate reached BUILD_READY.** But that answer is incomplete without two numbers nobody in this
repo had computed, both of which are more decision-relevant than any challenger result.

## A2.1 🔴 LIVE TRADING CANNOT TELL US IF THIS WORKS, FOR YEARS

One-sided 5% test against the null "this book earns zero", weekly SD held at its in-sample $7,195:

| if the true mean is | 1 yr power | 2 yr power | 3 yr power | **years to 80% power** |
|---|---:|---:|---:|---:|
| $900/wk | 23% | 36% | 47% | **7.8** |
| **$1,300/wk** | **37%** | **58%** | **73%** | **3.8** |
| **$1,600/wk** | **48%** | **73%** | **87%** | **2.5** |
| $1,900/wk | 60% | 85% | 95% | 1.8 |
| $2,211/wk (in-sample headline) | 72% | 93% | 99% | 1.5 |

**At the honest forward central expectation, one year of live trading is a coin flip and two years
still leaves a ~30–40% chance of failing to distinguish the book from zero.** Going live is
therefore a **2.5–4 year commitment before the evidence can answer the question you are asking of
it.** The forward paper stream cannot shorten this: fills are `SIMULATED_FILL_NON_EVIDENTIAL`, and
the *decision* stream accumulates at exactly the same 1.5 trades/week that produced this table.

## A2.2 🔴 THE $75–90k CAPITAL PLAN IS A BET, NOT A CAPITAL PLAN

🔴 **CORRECTED 2026-08-31, after an owner challenge — and the correction goes the wrong way.**
`$45,138` is the **WEEKLY-bucketed** drawdown, and **weekly aggregation smooths the within-week
path.** A trader experiences the trade-level drawdown. Full reconciliation:
`runs/G3_INCUMBENT_BASELINE_00_20260831/out/drawdown_reconciliation.txt`.

| window | object | **trade-level** | daily | weekly |
|---|---|---:|---:|---:|
| FULL 2022-01-02 → 2026-08-25 | P1 | 27,765 | 26,318 | 23,099 |
| | XM | **34,193** | 34,193 | 32,383 |
| | **M_11** | 🔴 **51,891** | 51,891 | 45,138 |
| OQ6 2022-W27 → 2026-W31 | M_11 | 37,461 | 35,417 | 28,596 |
| MODERN 2022-05 → | M_11 | 37,461 | 35,417 | 28,596 |

**Provenance of every drawdown figure this campaign has quoted — two sources of difference, only two:**

| figure | what it actually is |
|---|---|
| `$21,740` | `G2_OQ6_MAPPING` — M_11 **weekly**, window from **2022-W27**, entry-date week bucketing |
| `$28,596` | same window and object, bucketed by the ledger's own `wk` column |
| `$29,454` | GENESIS I — **P1 trade-level** (this run's comparable figure: $27,765) |
| `$45,138` | M_11 **weekly**, FULL window — the only one that **includes H1 2022** |
| **`$51,891`** | **M_11 trade-level, FULL window — the figure capital planning must use** |

1. **WINDOW.** M_11's *entire* drawdown is 2022-W05 → 2022-W17. OQ6's window starts **after** it.
2. **BUCKETING.** Trade-level is **15% deeper than weekly**.

Note also: **XM alone ($34,193) draws down more than P1 alone ($27,765)** — the same fact as "XM buys
half the return with more than all of the risk", seen from the drawdown side.

| capital | **trade-level** maxDD as % of it | annualised @ $1,300/wk | @ $1,600/wk |
|---|---:|---:|---:|
| **$10,207** (account `2047681`) — **at 1 NQ + 1 NQ (full size), NOT DEPLOYED** | 🔴 **508%** | — | — |
| **$10,207** (account `2047681`) — 🔴 **AS DEPLOYED, `MnqPerNq = 3` = 0.30 NQ-eq** | 🔴 **152.5%** (0.30 × $51,891 = $15,567) | — | — |
| **$75,000** | **69%** | 90% | 111% |
| **$90,000** | **58%** | 75% | 92% |
| $157,245 | 33% | 43% | 53% |
| **$207,564** | **25%** | 33% | 40% |

A 90–111% annual return and a 58–69% drawdown are **the same fact stated twice.** For the trade-level
drawdown to be 33% of capital requires **$157,245**; for 25%, **$207,564**.

And $51,891 is **one realised path**, not a distribution — H1 2022 demonstrates the book can produce
it, and the modern-era figure is the *lower* of the two observations, not the truth.

## A2.3 WHAT I WOULD ACTUALLY SAY TO THE OWNER

**The evidence supports P1+XM as the best book we can construct today. It does not support the
$75–90k sizing, and it does not support expecting live trading to validate the decision quickly.**

Three things that are true at once, and all three have to be held:

1. **The book is real work.** Parity-certified, an executable object now reproduced at
   100.000%/100.000%, a corrected −2.0% research offset, and five challengers killed by falsifiers
   written in advance. This is not a curve fit that nobody checked.
2. **Every historical number is in-sample and post-selection.** There is no out-of-sample regime.
   The modern window is 221 weeks of a 221-week regime.
3. **The risk is at the top of what a $75–90k account can absorb, and the feedback loop is years
   long.** Those two together are the real constraint — not the absence of a better strategy.

**If real money is the goal, the highest-value next actions are not alpha.** They are: fix the roll
procedure (~$437/wk, §H), size to the drawdown rather than to the return, and accept a multi-year
evaluation horizon before the live record can overrule the backtest.

---

# B. CHAMPION BOARD

| # | candidate | mechanism | result | why | status |
|---|---|---|---|---|---|
| 1 | **P1SZ_OPENLOC** (`G3_P1GAP01`) | opening strength (RTH open's location in the overnight range) as a P1 sizing input | **FAIL** G1/G4b/G5/G6 | **G4b 85.4th pct** — 146 of 1,000 randomly circular-shifted session series did better. G5 **3/25** rolling windows; ES95 worse in **all 25**. G6 CI90 includes 0. Gain is entirely 2024-26; 2022 and 2023 negative ⇒ direction tilt, not excursion forecast | **CLOSED** at this formulation |
| 2 | **CLOCKLAG** (`G3_CLOCKLAG01`) | cross-day periodicity at a matched clock bucket (scheduled institutional flow) | **FAIL** Stage 1 | The clock-aligned term wins **less often than a coin flip** (5/12 MODERN, 4/12 FULL). At the strongest bucket the *control* is larger (β_adj 0.1704 vs β_same 0.1006). β_nonmult is **larger in magnitude than the treatment**. Margin fell **28×** short of its multiplicity-priced bar | **CLOSED**; no P&L computed |
| 3 | **OVERNIGHT_BREAK_DIRECTION** (`G3_SESSTRUCT_00`) | forecast which overnight extreme RTH breaks first | **CLOSED** | A 14%→91% monotone table over 5,058 sessions that is **pure first-passage geometry**: null R² = **0.9965**, aggregate excess −0.004 (z −0.68) | **CLOSED**; would have been a triumphant false positive against a 50/50 null |
| 4 | **P1 sizing class** (`T2_P1SIZE01` + `G3_P1GAP01`) | any reweighting of P1's contract budget | **0 for 3** | A1_SMOOTH, A2_VOLN and P1SZ_OPENLOC all failed the same gates | class is 0/3 |
| 5 | **XM latency exploitation** (`G3_XMLAT_01`) | is XM's edge recoverable / is it execution-fragile? | **retain_rule FIRES** | 250 ms fill retains **98.1%**; break-even latency ≥ 16 s even at the most pessimistic construction = **63×** a 250 ms fill | XM RETAINED on execution grounds |
| 6 | **34 WAVE-B candidates** | eight external mining surfaces | **killed pre-compute** | rehashes of this repo's own closed experiments | **59% rehash rate** |

**Also closed today, without a candidate being born:** `open_vs_on_low`, `on_range`, `on_vol` and
`prior_rth_range` as tail markers — all four collapsed under volatility normalisation and were
volatility scaling, not information.

---

# C. BEST NEW SHORT — **NONE**

**Strongest short mechanism tested:** the short leg of `T2_ORBSHORT` (closed nine days ago at the
3.8th percentile of its own placebo; the second formulation died at n = 53).

**Strongest short mechanism *identified but not run*:** WAVE B family #2 — **implied volatility as a
signed short DIRECTION, not as a filter.** Two independent mining surfaces converged on it with the
same sign. It is the cheapest decisive short-side test available: daily VIX (certified 1990-2026)
plus two NQ prints per session; one table, no intraday computation, no new data.

**Why it was not run: a governance gate, and it needs the owner.** It reads VXN/VIX against 2022+
NQ, which **consumes `GENESIS_H1`'s deliberately preserved pristine confirmation window**.
`G2_F1_COND01` previously refused to trigger that read. **I did not consume it. See §J.**

**Honest expectation if authorised:** probably negative. `GENESIS_H1` measured neighbouring point
estimates running the *wrong* way for this thesis, and the effective-N problem is structural —
~600 raw high-VIX sessions cluster into perhaps 8–14 independent episodes, so any session-level
t-statistic is fiction.

> **Do not read "no short" as "shorts don't work."** It means: every short candidate that survived
> external mining is N-thin, power-bound, or fighting an in-repo point estimate that runs the wrong
> way — and the two that were preregistered were closed on measurement.

---

# D. P1 IMPROVEMENT VERDICT

**1. Can P1 earn more through better sizing?** **No evidence for it, and the class is now 0 for 3.**
Three arms across two preregistered runs, all using the same causal budget calibrator, all failed.

**2. Can the right tail be predicted causally?** **A scale-free marker exists and does not survive
translation into money.** Opening strength cleared a scan-priced discovery null (p = 0.0020
volatility-normalised) and then failed its money gate at the **85.4th percentile** of a
feature-shift null. Marking a tail and earning after cost are different things, and this is the
measured distance between them.

**3. Is the fixed-dollar box a real economic weakness?** **Structurally yes, economically unproven.**
`P1_BOX_INVARIANCE_00` passed Gate A (the box is highly non-invariant across eras) and the
vol-scaled successor FAILED its frozen Gate B. **No economics were ever run.** `P1_BOX_NONINVARIANT`
stands as a structural fact and is not a licence to change the box.

**4. Is any current P1 code/research divergence material?** **YES — and it is now fully resolved.**
The research chain double-lags ATR (`we_fastctx.py:46` then `:81`); the executable lags once.
Removing exactly one line reproduces the deployed object at **100.000%/100.000%, 0 of 397**.
**Every quoted P1 research figure sits ~2.0% ABOVE the object that trades** ($1,570/wk → $1,539/wk,
−$31/wk), and **87.1% of the gap is in the top decile** where P1's economics live.
**`we_fastctx.py:81` was NOT patched** — that would silently change 100+ historical runs.

**5. Is there any justified P1_vNext?** **No.**

**6. If not, why not?** Because the only two levers with any evidence behind them both failed their
own falsifiers, and the third (the box) has never had its economics computed. **The material P1
finding of this campaign is not an improvement — it is that our *description* of P1 was 2% wrong.**

---

# E. XM VERDICT

**1. Is XM's edge causal under executable timing?** **Yes.** X1-NEG: corrupting every input after
the 09:45:00 cutoff leaves all four decision series **bit-identical on 100% of sessions**
(max diff 0.000e+00). X1-POS has teeth: **17.40%** of computable sessions flip under a single
admissible ±0.5σ perturbation. The backtest fill is the **first executable print** after the
decision instant — not a fill from the future.

**2. Is the 09:45 first-minute P&L realistically capturable?** **Yes — 98.1% of it at a 250 ms
fill.** And the −$74.18/wk one-minute figure is **population-specific**: it belongs to 346 trades /
213 weeks. On the wider window it is **−$50.38/wk (t −1.91, p 0.125) — not distinguishable from
zero.** "$15,800 in one minute" and "−$74.18/wk" are **one measurement expressed twice** and may
never be cited as two findings.

**3. What is the real latency budget?** Break-even latency **16 s – 35,672 s** across three
functional forms. Even the most pessimistic construction is **63×** a 250 ms fill.

**4. Is simulated forward execution evidence useful?** **No — zero, not merely weak.** `Provider31`
is **Tradovate**; `DEMO8383477` is a **server-side** demo. A 100-lot order filled at **one price**
(`lastQty=100, lastPx=avgPx=29577.25`) against a book whose top of book never exceeded **46**
across 5,156 samples. **P(≥100) = 0.00%.** And we are using the *less realistic* of the two
simulators on this machine — NT8's local engine models queue position; the server-side one shows
none of it, and NT8's local knobs are inert here.

**5. Realistic after-cost, after-latency expectation?** **E = $918.35/wk**, stable at $709–726/wk
across three readings on the wider population. **But XM's own weekly mean carries a 95% CI of
[$199, $1,305] — a band $1,106 wide. Every latency effect ($17–74/wk) is 2–7% of that band.**

**6. Should XM remain, shrink, or be replaced?** **REMAIN, at x1, as a risk classification.**
I withdrew my own indictment: at matched drawdown M_11 looks worse than P1 alone **only on the full
record**, and **100% of that is H1 2022**. In every modern window XM is additive (+$491–536/wk at
matched maxDD), and its contribution during **P1's worst decile of weeks has been rising**:
+$281 → +$717 → +$878 → **+$1,824/wk (2024+)**. **Correlation is not the quantity that matters for
a book; worst-state contribution is, and the record conflates them.**

---

# F. NEW ALPHA VERDICT

| family examined | information used | previously tested? | result |
|---|---|---|---|
| clock-lag periodicity | NQ 1-min, cross-day same-bucket | **No — the only `GENUINELY_NEW`** | **CLOSED Stage 1** |
| opening strength → P1 tail | overnight range + RTH open | No | **CLOSED** at money gate |
| overnight-extreme break direction | overnight range + RTH open | No | **CLOSED** — first-passage geometry |
| implied vol as signed short direction | daily VIX/VXN | partially (`GENESIS_H1`) | **BLOCKED on governance** (§J) |
| implied vol as non-directional scale | daily VIX/VXN | no | **BLOCKED on governance** |
| breadth in a non-threshold role | `$TICK` 2013-2026 | mechanism-adjacent (`BREADTHPM01` info leg survived, trade died) | **queued**, not run |
| rates surface (ZB) | **ZB 1-min — a NEW raw surface** | **never read** | **queued**, not run |
| 34 further candidates | various | **yes — closed** | killed pre-compute |

**Nothing reached BUILD_READY. Nothing reached PAPER_READY. No candidate was created.**

---

# G. DATA VERDICT

Full detail: `research/data/DATA_VERDICT_20260831.md`. Authoritative artifact:
`research/data/NT8_CAPABILITY_CENSUS.csv` (51,936 rows, `research_sdk/data_census.py`, selftest 37/37).

**Binding rule: no "we do not have X" claim is admissible unless it names a census row.**

**WHAT WE OWN AND HAD NOT COUNTED** — the sixth occurrence of "we don't have X" meaning "we never
looked":

| surface | owned | extracted |
|---|---:|---:|
| NQ tick **full BBO**, pre-seal | **187 sessions** | ~93 (deduped union) |
| ES tick full BBO | 126 | ~40 |
| **NQ *minute* Bid/Ask** | **81 sessions** | **0 — recorded nowhere** |
| **ZB 1-min** | **1,113 sessions, 2023-01-02 →** | **0 — never read** |
| MNQ 1-min | 1,449 sessions | 0 |

**WHAT WE GENUINELY LACK** (each with census evidence): `^VIX` before 2022 (**zero** pre-2022
payload), `^ADD` entirely (**0 files**), VX/VXM futures intraday (**4 files** — a GENESIS I claim
corrected), L2/DOM, options, and any intraday breadth beyond `$TICK`/`$TRIN`.

**§10 residue rule, corrected from the file format:** `.ncd` is a 31-byte header plus records, so
**32 B genuinely is a zero-record minute file** — the old signature was right. What was wrong was
collapsing it to a boolean. The census emits **EMPTY / SPARSE / PAYLOAD** and reports
`sparse_max_bytes` as a parameter rather than hiding it as a constant.

---

# H. EXECUTION VERDICT — and it is the most actionable result of the campaign

Estimated dollars/week lost, against the book's $2,211/wk NT8-basis headline:

| source | $/week | basis |
|---|---:|---|
| **roll blackout** | **≈ $437** | **19.7% of net falls in the ~9-day no-new-entry window; 10.3% of trades** |
| spread + slippage | ≈ **$282** | ⚠️ **CORRECTED**: EXEC01's `$20.65/ctrRT` is **SPREAD ONLY**, not all-in — true all-in is **$25.01** ($20.65 spread + $4.36 commission). The original row subtracted commission out of $20.65 and then charged it again in the row below, double-discounting. $20.65 × 3,317 ctrRT ÷ 243 wk = **$282**, not $222. Net effect: NQ friction was understated by ≈ **$59/wk** |
| commission ⚠️ **NOT A DEDUCTION** | ($60) | $4.36/ctrRT × 3,317 ctrRT ÷ 243 weeks. 🔴 **The $2,211/wk baseline this column is measured against ALREADY NETS COMMISSION** (`IS_IT_PHACKING_20260831.md:31`, "NT8 only (commission in)"). Listed as an inventory item, never subtracted. Correct ladder: $2,211 − $282 = **$1,929** — exactly IS_IT_PHACKING's own measured row. See `COST_MODEL.md` §4 |
| latency (XM, at 250 ms) | ≈ $17 | `G3_XMLAT_01` component D |
| far-side vs print fill | ≈ $6 | measured −$11.50/ctr vs $7.50 charged |
| operational downtime | ~$0 observed | no trade was missed by any redeploy today |

> 🔴 **The roll blackout is larger than commission, spread, latency and fill convention COMBINED —
> and it is the one item that is not a market cost at all. It is a procedure.**

**XM is disproportionately exposed: 32.0% of its lifetime net** falls inside blackout windows,
versus P1's 13.4%. Persistent, not a fluke: 2023 +16.7%, 2024 +26.8%, 2025 +21.8%, 2026 +29.0%
(2022 −32.4% — the blackout *helped* in the old regime).

**This is not a reason to weaken the guard.** The guard exists so the book never holds an expiring
contract and that is correct. **What is avoidable is sitting out.** Redeploying onto the *next*
contract at or just before `blockNewEntriesFrom` resolves a *new* rollover date and no block
applies. Cost of the fix: trading the back month for ~2 days before the natural volume crossover.

⚠️ **This is an owner decision and no live action was taken.** The 2026-09 roll is the first
opportunity, and it interacts with the latching-guard red zone — see §I.

> **Execution engineering is a larger alpha source here than another predictor.** That was §H's
> hypothesis and the measurement supports it.

---

# I. REAL-MONEY READINESS PACKET

> 🔴 **SUPERSEDED 2026-09-01 — this packet describes the 1 NQ + 1 NQ book on the PAPER account.**
> **What actually went live:** `WeeklyEdgeP1PCTMnq_v1` (`399562885`) + `WeeklyEdgeXMConflictMnq_v1`
> (`399562886`) on **real-money account `2047681`**, capital **$10,206.86**, decisions on `NQ 09-26`
> and orders on **`MNQ 09-26`** at `MnqPerNq = 3` (= 0.30 NQ-equivalent). **Max simultaneous
> position is 9 MNQ, not 3 NQ.** 0.30-scaled trade-level maxDD **$15,567 = 152.5 % of the account**
> (the `capital` row's `$45,138` is the WEEKLY figure; §A2.2 of this file rules the trade-level
> **$51,891** is what capital planning must use).
> 🔴 **The `roll instructions` row below is INCOMPLETE for the live book: `MNQ 12-26` must move with
> `NQ 12-26`, and `ExpectMnq = "MNQ 12-26"` must be set, or `MxInstrumentGuard` hard-halts on the
> month mismatch.**
> ⚠️ The `expected cost` row's "$20.65/ctrRT ... all-in" label is **wrong** — $20.65 is **spread
> only**; true all-in is **$25.01**. See the §H correction.
> Authority for live state: **`research/operational/CURRENT_LIVE_TRUTH.md`**.

| item | value |

| item | value |
|---|---|
| source files | `research/weekly_edge/ninjascript/WeeklyEdgeP1PCT_v3.cs`, `WeeklyEdgeXMConflict_v4.cs` |
| sha256 | `a9ccc2331d78aea43b1eefeff24189d0277a4cdfb718f2b817f56f7ef60f6be6` / `0360f894724cfd1fe59eb2a3a14d434b6e8a082eb2f25ba483e97ff2b854bae8` — NT8 copy **identical** to repo copy |
| classes / deployments | `399562877` (`dep_9c51536a7045`), `399562878` (`dep_27ff47e7e3b7`) |
| parameters | all `SetDefaults`; `DaysToLoad=365`, `DiagDir`/`WarmupCertDir`/`ExportDir` on `C:`, `ExpectInstrument="NQ 09-26"`, XM series `ES/RTY/YM 09-26` |
| instrument / session | `NQ 09-26`, 1-min, `CME US Index Futures ETH` |
| warm-up | convergence measured at ~9 months; `DaysToLoad=365` required; certificates verdict `GO`, 7/7 gates |
| account | `DEMO8383477` (Tradovate server-side demo) — **paper only** |
| expected latency | any fill inside ~1 s is economically equivalent; break-even ≥ 16 s |
| expected cost | ⚠️ **$25.01/ctrRT all-in on NQ** = $20.65 measured **spread** (median $20.00, p90 $35.00) **+ $4.36 commission**. The earlier "$20.65 all-in" label was wrong and understated NQ friction by ≈$59/wk. **MNQ (the live execution instrument): $1.30/ctr RT commission; spread does not degrade** (same 0.25 tick, point value scales exactly 1/10) → all-in ratio ≈1.35×, ≈$35/wk at 3 MNQ |
| capital | **$75–90k**; realised maxDD $45,138 |
| max expected position | 3 NQ contracts simultaneously |
| **synthetic-stop caveat** | 🔴 **every stop in this book is synthetic and dies with the strategy.** Never restart while positioned. There is no intrabar risk control anywhere |
| roll instructions | 🔴 **red zone 2026-09-06 → 2026-09-18.** Safe re-enable **BOTH legs ≥ 2026-09-19** on `NQ 12-26` **and `MNQ 12-26`**, all series together, `ExpectInstrument="NQ 12-26"` **and `ExpectMnq="MNQ 12-26"`**. 🔴 **"P1 ≥ 09-17" WITHDRAWN 2026-09-01** — the live P1's MNQ series rolls 09-18 and the guard takes the MIN over all series. **The guard LATCHES** — a re-enable inside the window blocks entries permanently while every health check reads green. Authority: `research/operational/CURRENT_LIVE_TRUTH.md` §ROLL |
| restart rules | plan for full redeploy; rows return DISABLED regardless |
| kill conditions | `RECONCILE-BREAK`, `PARTIAL-FILL`, `instrumentMismatch`, warm-up verdict ≠ `GO`, or `ROLL-PLAN` date in the past |
| logging | `research_sdk/live_readiness_check.py` R1–R8; **R1 (roll plan must be in the FUTURE) is the only check that catches a latched-dead book** |
| **failure recovery** | if a stop-class call is refused: `DisableStrategy(strategyId=…)` uses a **different id space** and returns `strategy_not_found` on a live strategy. Use **`StopStrategy(deployment_id=…)`** |

**`REAL-MONEY ORDER PLACED: NO.`**

---

# J. THE ONE DECISION THAT REQUIRES THE OWNER

**May the campaign consume `GENESIS_H1`'s preserved pristine confirmation window?**

Three WAVE B families (the signed-short volatility direction, volatility-as-scale, and part of the
calendar family) require reading VXN/VIX against 2022+ NQ. `G2_F1_COND01` previously refused to
trigger that read, and I have not overridden it.

**What a YES buys:** the cheapest decisive short-side test available — daily VIX plus two NQ prints
per session, one table, $0. It is the highest-EVI short-side item on the board.
**What a YES costs:** the confirmation window is spent and cannot be restored.
**My recommendation:** **yes, but run discovery pre-2022 first** and reserve the modern window for a
single frozen confirmation. The honest prior is that the answer is negative.

---

# §55 — IF THIS WERE MY JOB

**What I would trade tomorrow: `P1 x1 + XM x1`, unchanged, at $75–90k.** Not from attachment — five
challengers were run today against falsifiers written in advance and all five died, and the one
change I *would* make is not a strategy change at all.

**What I would deliberately NOT trade:** any sizing overlay on P1 (0 for 3); any overnight-range
direction rule (geometry, R² 0.9965); any clock-bucket rule (loses to a coin flip); 2× P1 in place
of the book (that comparison is an H1-2022 artifact, and doubling P1 concentrates everything in a
process where 9 trades in 10 collectively lose money); and **anything sized off a Python P1 figure
without the −2.0% correction.**

**The highest-EVI frontier, in order:**

1. **The roll procedure.** Question: does redeploying onto the next contract at `blockNewEntriesFrom`
   recover the ~$437/wk without material back-month slippage? Data: already owned. Mechanism:
   procedural, no alpha claim. **Evidence that would change the decision:** measured back-month
   spread over the 2 days before the volume crossover, against the foregone net. **Largest number
   on the board and it is not a signal.**
2. **Extract the 94 unextracted NQ BBO sessions ($0).** It buys **+28 XM-decision sessions
   (33 → 59, +79%)** and is the binding input to the sub-second execution surface.
3. **Read ZB.** 1,113 sessions of 1-min on disk since 2023-01, never read — the only genuinely new
   raw information surface external mining found.
4. **The volatility short direction** — conditional on §J.
5. **Whether realtime processing differs from historical.** 100% of the parity evidence is NT8
   historical replay; the realtime tail was empty because the seal dropped every post-deployment row.

---

`CHAMPION VERDICT: M_11 = P1/PCT x1 + XM_CONFLICT x1 (EXECUTABLE_COMPONENT_SET)`

`INCUMBENT CHANGE: NONE`

`BEST NEW SHORT: NONE`

`BEST NEW ALPHA SLEEVE: NONE`

`XM LATENCY VERDICT: XM is not an execution strategy — a 250 ms fill retains 98.1% of its edge, break-even latency is at least 63x that, and the -$74.18/wk one-minute figure is a red herring for deployment.`

`TOMORROW-TRADABLE: WeeklyEdgeP1PCT_v3 x1 NQ 09-26 + WeeklyEdgeXMConflict_v4 x1 NQ 09-26, DaysToLoad=365, CME US Index Futures ETH, $75-90k capital, paper account DEMO8383477, roll red zone 2026-09-06 -> 2026-09-18.`

`REAL-MONEY ORDER PLACED: NO`
