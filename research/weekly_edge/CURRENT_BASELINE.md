# CURRENT BASELINE — campaign #7 `WEEKLY_EDGE`

**Authoritative for current RESEARCH state. 2026-08-27, through wave W123, both parity runs,
the `RR_W000`–`RR_W006` action-value programme, `DATA_CAPABILITY_AUDIT_20260827`, the
`ORDERFLOW_EXPAND` / `INTERNALS_ACQUIRE` / `MULTIMARKET_INVENTORY` acquisition wave, and
`MS01` / `INT01` / `FWD_BOOTSTRAP`.**

> **Evidence depth per object lives in
> [`research/operational/ALPHA_EVIDENCE_CLASSIFICATION.md`](../operational/ALPHA_EVIDENCE_CLASSIFICATION.md).**
> **What could trade today lives in
> [`research/operational/TOMORROW_PRODUCTION_CANDIDATE.md`](../operational/TOMORROW_PRODUCTION_CANDIDATE.md).**
> **Data assets live in [`research/data/DATA_ASSET_REGISTRY.md`](../data/DATA_ASSET_REGISTRY.md).**

_This is a **state document, not a changelog.** Wave-by-wave history lives in
`runs/WE_W*/REPORT.md` and is linked, never reproduced. Execution truth lives in
[`research/operational/EXECUTION_MANIFEST.md`](../operational/EXECUTION_MANIFEST.md)._

---

## 0. THE FOUR BASELINES

> ⚠️ **Research truth and execution truth are different claims and this repo keeps them apart.**

| # | baseline | object | evidence |
|---|---|---|---|
| **A** | **RESEARCH_SINGLE** | **`P1/PCT`** | $1,394/wk raw · ⚠️ **$1,166/wk at fixed $20,245 DD — CORRECTED 2026-08-27, was $1,230** · 56.3 % positive weeks · max DD **$24,213** (was $22,931) · t 4.16 · `runs/FWD_DD_RECONCILIATION/` |
| **B** | **RESEARCH_PORTFOLIO_FRONTIER** | **`{P1/PCT + XM_CONFLICT}`** inverse-vol | ⚠️ **$2,012/wk SUSPECT — NOT audited, may carry the same cost-model defect as A. Do not quote as clean** · max DD $11,489 · 59.2 % positive weeks · t 4.90 · `runs/FWD_DD_RECONCILIATION/` |
| **C** | **EXECUTABLE_SINGLE** | **`WeeklyEdgeP1PCT_v1`** | ✅ **PARITY-CERTIFIED 2026-08-27** · `runs/WE_P1PCT_PARITY_20260827/` |
| **D** | **EXECUTABLE_COMPONENT_SET** | **`WeeklyEdgeP1PCT_v1` + `WeeklyEdgeXMConflict_v2`** | ✅ **both legs individually PARITY-CERTIFIED** · `runs/WE_XM_PARITY_20260827/`. ⚠️ a certified component set, **NOT** an executable implementation of B — see below |

**Every weekly figure above is at a fixed $20,245 max drawdown** — algebraically scale-invariant, so
it cannot be inflated by leverage. Cost model: $4.36/ctrRT commission **plus** candidate-specific
modelled spread (P1 $14.44, XM $12.50). **NT8 nets are a different quantity** — see the manifest.

> ### ⚠️ **D IS A CERTIFIED COMPONENT SET, NOT PORTFOLIO B.**
> **B is inverse-volatility weighted. The integer-contract / capital mapping that would implement it
> has NOT been selected.** Running both legs at their default quantity 1 is **not** that mapping and
> **does not reproduce B's economics** — B's $2,012/wk at fixed DD is a research figure under
> research weights and the research cost model. Selecting the mapping is an owner capital-allocation
> decision (see `research/operational/EXECUTION_MANIFEST.md`), and until it is made the
> **executable implementation of B remains PENDING.**
>
> ### 🔒 LIVE STATUS: **NOT LIVE ENABLED** — every object above, without exception.
> **EXECUTABLE ≠ ENABLED.** C and D reproduce inside NinjaTrader's Strategy Analyzer on the
> isolated Backtest account. Neither is deployed, started or connected to any account, no live
> order authorization exists, and enabling either requires an explicit recorded owner
> instruction. **EXECUTABLE · PARITY-CERTIFIED · LIVE-ENABLED are three separate statuses.**
> **Evidence status of A and B: `DISCOVERY_CONSUMED`** — the 2022-07 → 2026-08 window has been mined
> for 123 waves. Forward evidence on the sealed ≥2026-08-01 data is the only clean test remaining.

## 0a. Object taxonomy

Regime vocabulary: `STRUCTURAL` · `CURRENT_REGIME_EXPLAINED` · `CURRENT_REGIME_UNEXPLAINED` ·
`TRANSITIONING/WATCH` · `DEAD/FALSIFIED`.

| category | object | regime | engineering |
|---|---|---|---|
| **BASE** | **`P1/PCT`** | `CURRENT_REGIME_UNEXPLAINED` | ✅ certified |
| **ACTIVE COMPONENT** | **`XM_CONFLICT`** | `CURRENT_REGIME_UNEXPLAINED` · **REGIME_LOCAL by data availability** | ✅ certified (`_v2`) |
| **CHALLENGER** | `PAIR23` (2 BMOM : 3 X9a) | `STRUCTURAL` — the one object beating P1 over the 16 unseen years on money, maxDD, top-5, positive weeks *and* streak. ⚠️ **It is a raw B-MOM channel + a `P1` VARIANT, not two independent sleeves** — `runs/RR_W003_X9A_CONTRACT/` | none |
| **WATCHLIST** | `MIRROR_CONT` · `FOLLOW_MORNING` | `CURRENT_REGIME_UNEXPLAINED` | none |
| **DEAD / FALSIFIED** | `NETFUSE_1` · `VWAP_RECLAIM` · trend-day state layer · volume exhaustion · AFT as a target · cross-market intraday support · turnover | — | — |
| **HISTORICAL** | campaign #3 Products A/B | closed Aug 2026 | `research/archive/campaign3_system_master/BASELINE_MODELS.md` |

---

## 1. `P1/PCT` — the base

13-member Solar volatility-ratchet ensemble, four combiners, 32-config vote, **OR-gated with the
B-MOM channel**, long-only, range throttle q = 0.8, delta gate, causal quality sizing (size 2 when
score ≥ 3, ~20 % of entries), flat at every session close, **session box −$1,300 / +$1,000
denominated PER CONTRACT**.

The per-contract box is the *only* difference from `P1`, and it is a **unit correction, not a new
strategy** (`runs/WE_W98_BOXDENOM/`): a dollar stop on a variable-size position halted a 2-lot at
**half** the adverse point move of a 1-lot (55.68 pts on size-1 sessions vs 37.18 on size-2).

| | `ABS` (old) | **`PCT` (current)** |
|---|---|---|
| weekly $ at fixed DD | $885 | **$1,231 (+39.0 %)** |
| positive weeks | 53.1 % | **56.3 %** |
| max drawdown | $26,388 | **$22,931** |
| t | 3.58 | **4.16** |

**The controls are the evidence, not the headline:** a *uniformly* looser box is worth +$6/week
(paired p = 0.940); holding the average budget fixed while making it size-conditional keeps
+39.6 %; both size-1 objects show **exactly $0.00** across all 213 weeks; the real gap sits at the
**99th percentile** of 200 size-label permutations.

⚠️ **`REGIME_LOCAL`.** On 2006–2021 the change **reverses (−31.4 %)** for a stated reason: a $1,300
box was 84 % of a typical session range then and is 19 % now, so it fires **5.7× more often today**.
Paired weekly p = 0.057, and **90.8 % of the gross difference lives in 53 of 1,058 sessions**. `ABS`
is retained beside `PCT` in every table.

> ### ⭐ **THE BOX IS WORTH FAR MORE THAN IT COSTS — measured 2026-08-27,
> ### `runs/RR_W005_BOX_LATCH_VALUE/`.**
> Ex post the latch "costs" **−$44,806** over the **247** sessions where it binds, and perfect
> *selective* un-latching would be worth **$283,856**. **Both evaporate at the fixed-DD metric.**
> Every uniform relaxation is **16–41 % WORSE** at fixed $20,245 DD and raises exposure **11–26 %**:
> no box at all **−40.7 %**, no halt **−34.3 %**, no target **−16.0 %**, box × 2 **−32.6 %**;
> `t` falls monotonically **4.17 → 3.62**. **The box is not a free lever and is not modified.**
> This also explains RR_W001's regeneration component — un-latching adds raw dollars *by adding
> exposure* — and confirms W98 rather than contradicting it.

## 2. `XM_CONFLICT` — active component

At 09:45 ET take NQ's own opening drive — `sign(close₀₉₄₅ − open of the 09:31 bar)` — **only on the
~34 % of sessions where the ES/RTY/YM composite moves the opposite way.** Fill at the 09:46 open,
hold to 15:45, size 1, **no stop**. N = 348 canonical (09:31 anchor); 346 under the sequential
implementation the NinjaScript uses. `runs/WE_W101_DIRECTION/`, `WE_W102_XMENGINE/`.

| | P1/PCT alone | **+ XM_CONFLICT** |
|---|---|---|
| weekly $ at fixed DD | $1,230 | **$2,012 (+63.5 %)** |
| max drawdown | $22,931 | **$11,489** |
| top-5 drawdown | $17,835 | **$8,735** |
| t | 4.16 | **4.90** |

⚠️ **Quote the range, not a point: +45 % (income-matched) to +64 % (inverse-vol).** The
**structural** result — adding XM roughly halves drawdown overlap with P1/PCT — is the sturdy half.
**The exact income number is not a forecast.**

**Why it and nothing else:** ρ(weekly, P1) = **0.081**; every other object in the campaign
correlates 0.27–0.72 with P1. Two independent weighting methods both say "drop the pair".

### Standing caveats — these travel with every quotation

- **N = 348**, ~1.6 sessions/week, in a **discovery-consumed** window.
- **REGIME_LOCAL by DATA AVAILABILITY** — ES/RTY/YM substrates begin 2022-01-02, so no 2006–2021
  test exists *or can be built*. This is not a choice.
- **ρ = +0.446 with B-MOM** — a diversifier against P1, only partly against the pair.
- **The only intra-trade risk control is the clock.** Worst adverse excursion **−$10,865 (543 pts)**
  — **a sample maximum, not a bound**. Every *alpha* stop 20–300 pts makes it worse at fixed
  drawdown; a separate *disaster* layer is priced in `runs/WE_W105_XMAUDIT/` and **no level is
  selected — the owner sets capital risk.**
- **Selected as best of 27 cells**, its combination best of 6. It cleared best-of-27 coin, rate-
  matched subsample (99.6th) and |drive|-decile-matched (99.7th) nulls — **but the selections
  happened.**
- **Last three months are weak**: $499/wk at fixed DD, 35.7 % positive weeks, **t = 0.25** over 14
  weeks — inside the **BURNED** span.
- **~20 of 348 trades carry 85 % of the money.** Dropping the top 5 costs 28 %, top 20 costs 85 %.
  Inside individual years the top-10 contribution *exceeds 100 % of net*.

### Two questions the campaign answered about those caveats

**Is the concentration accidental?** No — `runs/WE_W110_XMDIVERSE/`. Using only pre-09:45 features,
a cross-validated model ranks tail winners at **AUC 0.735 / 0.783 / 0.869** (top 20/10/5),
**p = 0.000 / 0.003 / 0.000** against 400 permutations that each re-run the entire fit. The
separating state: wide overnight range, a scheduled CPI/NFP/FOMC day, and a small opening drive
barely disagreeing with the complex. Genuinely multivariate — the announcement flag alone reaches
AUC 0.498.
⚠️ **W123's rider** (`runs/WE_W123_XMTAIL/`): tail **winners** are identifiable (AUC 0.727,
p = 0.000), tail **losers are NOT** (0.513, p = 0.380), and `on_range_rel` is elevated in **both**
tails (1.620 / 1.406 vs ~1.13) — substantially a **magnitude** marker. **The clean surviving
statement: XM's pre-entry state predicts WHEN a session will be large; among large sessions it
separates winners from the field but not losers from it.** No gate was built.

**Is the +0.464 six-month ρ downside coupling?** No — the decisive result, against 212 circular
shifts:

| | REAL | percentile |
|---|---|---|
| ρ, all weeks | +0.081 | 89.2th |
| **ρ ∣ P1 < 0** | **−0.165** | **5.2th** |
| worst-decile overlap | 0.005 | 7.1th |
| **tail beta**, P1's bottom decile | **−0.660** | 13.7th |
| **joint DD duration** | **7 wk** vs null 18.2 | beyond the null |

**The two engines are mildly coupled when they WIN and anti-coupled when P1 LOSES.** Still watch the
trailing 26-week ρ; P(XM<0 ∣ P1<0) rose 0.200 → 0.500 between the first and last 26 weeks on ~11
P1-losing weeks.

✅ **Not an event trade** (`WE_W105B`): the 304 non-announcement trades earn **$408/trade at 54.9 %**.
✅ **Genuinely two-sided** (longs 60.5 % / $701, shorts 48.0 % / $415) and **not an early-sample
artifact** ($540 in 2022-23 vs $569 from 2024).

---

## 3. ⭐ What the book loses on — the measurement, and how its interpretation moved

> ### ⚠️ TWO EARLIER CONCLUSIONS FROM THIS SECTION ARE **SUPERSEDED**. They are named here rather
> ### than deleted, because both were quoted for several waves and a future reader will meet them in
> ### the run reports.
> ### 1. ~~"The missing engine is a REVERSAL engine."~~ — **SUPERSEDED by W118 + W119.**
> ### 2. ~~"Coverage is not the gap. TURNOVER is."~~ — **SUPERSEDED by W121.**
> ### **Every measurement below still stands. Only the inferences drawn from them were wrong.**

### 3a. The measurement that stands — an EX-POST weekly phenotype

`runs/WE_W117_LOSESTATE/`. The candidate portfolio loses in **87 of 213 weeks (40.8 %)**. Weeks are
classified by an **ex-post** session-class mix, so this is a **phenotype of a losing week, never a
usable state** — every field is known only after the week has ended.

| market state | LOSING weeks | WINNING weeks | p |
|---|---|---|---|
| share of **TREND-UP** sessions | 0.167 | 0.238 | **0.005** |
| share of **REVERSAL** sessions | 0.299 | 0.230 | **0.011** |
| share of **TREND-DOWN** sessions | 0.147 | 0.143 | **0.880 — no difference** |

> ### **THE BOOK LOSES WHEN THE MARKET STOPS TRENDING UP — NOT WHEN IT FALLS.** ✅ **still current**
> **53 % of losing weeks are weeks NQ rose.** This **falsifies** the natural assumption that a
> long-only P1 plus an opening-auction XM must be short of *downside* exposure — an assumption W117
> wrote into its own spec in advance. Six frozen objects were screened for a fix; **zero survivors.**

### 3b. Why "a REVERSAL engine" is no longer the conclusion

- **W119** (`runs/WE_W119_BOOKLOSS/`, the `BOOK_LOSS_LEDGER`, 1,058 sessions × 25 columns)
  re-measured the same thing at **session** resolution and the REVERSAL excess collapses to
  **+1.7 pp**, against the +6.9 pp the weekly aggregation showed. **`RANGE` is the larger dollar
  class** (−$114,807 vs −$91,216). **REVERSAL is not the dominant supported explanation.**
- **W118** (`runs/WE_W118_REVERSAL/`) then built a reversal at the mechanism's **own event-driven
  geometry** instead of a fixed clock — the fairest test the family has ever had. It earns
  **−$405/trade**, while the **momentum mirror at the same trigger bars earns +$374**. On
  2006–2021 **both are ≈ zero**.

> **A weekly phenotype is not a mechanism.** "Losing weeks contain more ex-post REVERSAL sessions"
> was read as "build a reversal engine". Every reversal object actually built then lost to its own
> same-trigger continuation control. **The class label described the weather, not a tradeable edge.**

### 3c. Why "turnover is the gap" is no longer the conclusion

W119 also reported that on losing sessions P1 takes **3.04 trades**, for fewer contract-minutes, on
sessions **moving less**.

> ### ⚠️ **THE COMPARATOR IN THOSE FIGURES WAS WRONG — corrected 2026-08-27, `runs/RR_W000_LEDGER_AUDIT/`.**
> W119 compared losing sessions against `~(book_pnl < 0)`, which is **winning *plus* flat** (653 =
> 371 + 282). **All 282 flat sessions have `p1_trades == 0` by construction**, so they dragged the
> comparator toward zero.
>
> | | LOSING | *quoted* comparator | **WINNING** (correct) |
> |---|---:|---:|---:|
> | P1 trades / session | **3.042** | ~~1.377~~ | **2.423** |
> | P1 contract-minutes | 199.0 | ~~242.1~~ | **426.1** |
> | \|RTH move\| pts | 116.5 | ~~168.0~~ | **175.4** |
>
> **The turnover contrast is 3.04 vs 2.42, not 3.04 vs 1.38 — overstated ~1.75×.** The
> contract-minute gap is **53 %**, not 18 %, and in the direction the label implies. The
> session-move claim survives almost unchanged (31 % → **34 %** less). **Every LOSING-column number
> is unchanged; only the comparator was wrong.**
>
> ### ⚠️ **`E_NO_ENGINE` = 0 was FORCED BY CONSTRUCTION and measured nothing.**
> The lens is "neither leg held a position" — which makes `book_pnl == 0` — and it was counted
> *inside* the `book_pnl < 0` population. **It was empty before any data was read.** On its raw mask
> there are **32 sessions** where no engine was present while the session's \|RTH move\| was in its
> top decile (mean **452 pts**). Those are **absences, not losses**, and pricing them needs a
> directional oracle, so **no dollar figure is attached.**
>
> **Consequence:** *"coverage is genuinely not the gap"* was **withdrawn** as unsupported, and
> **`RR_W006` has since MEASURED it**: of the 32 raw-mask sessions, **23 (71.9 %) were moves
> DOWN** — which a **long-only** book is right to decline — and most of the rest had the signal
> **fire and get suppressed**, which is policy, not coverage. **The gap, correctly scoped, is
> 4 sessions of 1,058 = 0.38 %** (≤ 1.1 % even if all 8 unmatched sessions went the wrong way).
> **W119's conclusion was right for the wrong reason, and now has an argument instead of a
> masking artifact.** **This does not reopen turnover** — W121 killed that inference on
> independent evidence, and the corrected, *weaker* contrast is more consistent with W121, not less.

**W121** (`runs/WE_W121_TURNOVER/`) tested turnover as a *causal state*. Entry-count caps lose to
baseline at **every** K **and sit at the 0.0 / 4.0 / 1.0 / 0.0th percentile of a count-matched
random-halt placebo.**

> ### **Removing the same number of entries AT RANDOM does better than removing them by the rule.**
> That is stronger than a null: the ordinal position of an entry carries **negative** information
> about which entry to drop. The 4th entry is the *best* cell ($253 against a $139 mean).
> **A high trade count on a losing session is a SYMPTOM of a hard session — not a cause of the loss,
> and not a lever.**

### 3d. ⭐ What the gap actually is now

**W122** (`runs/WE_W122_XSUPPORT/`) then closed the nearest available information lane: cross-market
intraday support at P1's own decision events fails **all four** gates — matched Q5−Q1 **−$157**
against a **$503** dependence-preserving family bar, **−$227** prequential, and **below** an NQ-only
control. What little existed was **NQ momentum wearing a cross-market label**.

> ### **The unresolved gap is NOT "a reversal engine" and NOT "a turnover policy".**
> ### **It is genuinely NEW CAUSAL INFORMATION about action / signal quality at the decision event**
> ### — `E[PnL(action) | I_t]` from a source the book does not currently observe.
> Everything reachable from price, ex-post class labels, trade counts and currently-held
> cross-market series has now been tested and is closed. **§7 names the surfaces that remain and
> why each is blocked.**

## 4. Watchlist

**`FOLLOW_MORNING`** — buy at the 11:49 open if the 11:29 close is above the 09:31 open, sell if
below, exit 15:44, size 1. Parameter-light with a broad timing plateau (*not* "zero parameter" — the
decision minute was inherited from an earlier spec). `runs/WE_W114_INTRAMOM/`, `WE_W116_FMADJUDICATE/`.
**Standalone: CONFIRMED** — $179/trade, 55.00 %, clears the corrected best-of-15 shared-sign bar at
the **96.3rd percentile**, mid-plateau at the 53rd, two-sided, dies only at ~18× the measured spread.
**Portfolio: FAILS** — worst-decile overlap 95.8th, and it earns **+$66** on book-losing weeks where
chance gives **+$842** (9.9th percentile).

> ### **`XM_CONFLICT` diversifies the book's LOSSES. `FOLLOW_MORNING` diversifies its WINS.**
> That is the whole difference, and it is why one is an active component and the other is not.

**`MIRROR_CONT`** (`runs/WE_W120_MOMMARGINAL/`) — fails gate 2 only, but passes **both gates
FOLLOW_MORNING failed**, and would take book max DD **$11,489 → $8,143**. Its value is **tail, not
average** (tail beta −1.861, 0.9th percentile) on **21 weeks**. It is now the standing
**`MIRROR_CONTINUATION_CONTROL`** required of every future fade idea.

## 5. Frozen conventions (do not change without a wave)

| | |
|---|---|
| window | 2022-07-01 → 2026-08-01 · 1,058 sessions · 213 weeks |
| substrate | `load_deep(..., extend=True)` |
| cost | $4.36/ctrRT commission **inside** the fill engine + candidate-specific spread (`WE_W82_FILLAUDIT`) |
| headline metric | weekly $ at fixed **$20,245** max drawdown |
| exposure convention | **income-matched** — the only one with no free parameter |
| seal | ≥ **2026-08-01 VIRGIN** · **2026-05-31 → 07-31 BURNED** |
| known data holes | **2026-07-17 truncated** (ends 10:53); spread profile missing the 17:00–17:59 CME break |
| opportunity language | [`OPPORTUNITY_LANGUAGE.md`](OPPORTUNITY_LANGUAGE.md) is **binding** |

## 6. Closed and falsified — do not re-run these

`NETFUSE_1` (deep-negative 2006–21) · `VWAP_RECLAIM` (a trend follower wearing a reversal label) ·
**causal trend-day veto** (two independent failures, on losing fades *and* on the profitable
baseline — `WE_W109`, `WE_W113`) · **volume exhaustion** (0.0th percentile, three of five
*anti*-predictive — `WE_W111`) · **AFT as a research target** (`WE_W112` — de-prioritised with a
reason, not another null) · **cross-market intraday support** (all four gates fail; matched Q5−Q1
**−$157** against a $503 family bar — `WE_W122`) · **turnover as a causal state** (caps lose at
every K and sit at the **0.0th percentile** of a count-matched random-halt placebo — *removing the
same entries at random does better* — `WE_W121`).

### ⚠️ Standing corrections the campaign must carry

1. **Seven fade mechanisms were killed and the family recorded dead. That is too strong.** W114
   measures the **mirror** of those fades at **+$179/trade** on the same sessions and costs, while
   the matched FADE arm earns **−$208**. They were not failing because mean reversion is impossible
   on NQ — **they were on the wrong side of a live momentum effect.** The kills constrain the
   *clock*, not the class. Whether reversal sessions can be monetised is **UNKNOWN**.
2. **W111b withdrew W108's headline**: the fade class signature is definitional — an *unconditional*
   fade reproduces it exactly. **Binding rule since: a class-conditional table requires its matched
   unconditional control in the same wave.**
3. **W109's failure was at the POLICY layer, not the information layer.** Three causal states known
   at 11:48 discriminate ex-post TREND from RANGE/MIXED at **AUC 0.613–0.621**, well above 2,000-draw
   permutation nulls. A *binary* veto on information that weak removes good and bad sessions in equal
   proportion (selectivity 0.74–1.12 across all 18 cells).
4. **W112 measured the `CAUSAL_MODEL_FRONTIER` for the first time and it is a negative** — ridge OOS
   R² **−0.024**, directional accuracy **below always-long**, beaten by an unfitted control. **The
   meaningful residual is `CAUSAL_MODEL_FRONTIER − REAL_SYSTEM_CAPTURE`, not oracle − real. Do not
   headline a level-2 oracle gap as missed alpha.**
5. **A `P1/PCT` trade's own P&L is NOT its causal action value — but for RANKING it is 69–86 % of it**
   (`runs/RR_W001_ACTION_VALUE_LEDGER/`). Path dependence is **inert on 76.9 %** of decisions and
   flips the **sign** on **10.4 %**, and the divergence is a **box-latch phenomenon** (56.7 % in
   sessions holding a latched-out run, **3.5 %** elsewhere). **Do not pay for a counterfactual
   simulator to recover the last 15–31 % unless that margin is the object of study.** A `P1/PCT`
   counterfactual must also state whether it is **session-scoped or full-horizon**: the cross-session
   *size* channel is worth **−$101,217** and flips 226 signs.
6. **A NAME IS NOT AN OBJECT** (`runs/RR_W003_X9A_CONTRACT/`). Two economically different objects
   carried the identifier **`X9a`** for many waves: W72's **raw two-sided channel** (weekly ρ with
   `P1/PCT` **+0.07**, $61,404 over the campaign window) and the stored `w72:X9a` stream that
   `PAIR23` actually uses (**+0.613**, $233,781). **Daily ρ between them is +0.15.** The stored one is
   `long_obj(TG_for(X9a))` — **`P1`'s entire Solar ensemble with X9a substituted for B-MOM as one
   additive term in the tilt.** So `PAIR23` is **a raw channel plus a `P1` variant**, and its
   ρ(BMOM, X9a) = **+0.009 "INDEPENDENT"** is a fact about the two **wrappers**, not about two
   signals. **Nothing measured about `PAIR23` is withdrawn** — only what it *is*. ⚠️ Every
   `w72:*` column in `streams_extended.csv` is built the same way and carries the same caveat.
   **Any reference to a stream by name must resolve to a construction: signal + wrapper + cost model
   + window.**
7. **Two gate-construction errors are now on the record and must not recur.** A gate whose statistic
   is a **one-sided sum over a majority-negative distribution cannot fail** (RR_W001's G4 was VOID —
   check the sign structure before committing a spec). And a **concentration gate must be stated on
   the SUM, not on total absolute value**: RR_W001's G2 read 39.28 % on \|value\| and **104.9 %** on
   the sum, and only the sum is what a router earns.

## 7. The information gap, and what is next

Full matrix: [`INFORMATION_COVERAGE_20260827.md`](INFORMATION_COVERAGE_20260827.md). Four distinct
coverages — **PRESENCE / INFORMATION / ACTION_VALUE / REAL_CAPTURE** — and they are never collapsed
into one word.

> ### **No TESTED current information surface separates P1 action quality.**
> **`RR_W002A` (`runs/RR_W002A_ACTION_VALUE_INFORMATION/`) is now the direct test and it is a clean
> negative.** 18 causally-verified features, four model families, five arms, a dependence-preserving
> null that **refits the entire walk-forward inside every shift**: the primary lands at the
> **51.0th percentile of its own null**, and a family already proven NULL scores **higher** (77.0th)
> than any real arm. Quintiles are U-shaped, top-decile AUC is **0.4990**, and adding features and
> capacity made it *worse*. **OUTCOME A — current-data action-value information is NULL / LOW-EVI.**
> **`RR_W004` then closed the last `LIGHT` surface**: six multi-session HTF features added
> incrementally sit at the **61.5th** percentile of their refitted null, and the **known-null
> control scores higher (77.0th) than either HTF arm**. ⚠️ Two of its five gates "passed" —
> but on a comparison between two arms **both worse than chance**, so they carry no weight, and
> that reading is refused on the record.
> ### **The statement is now COMPLETE rather than partial.** What remains untested is untested
> because it is **unavailable** — order flow (3.3 % coverage), options, a wider event calendar —
> not because it failed.
> Cross-market intraday: **null**. 1-min participation: **anti-predictive**. Order flow:
> **unmeasurable** — `runs/DATAGATE_ORDERFLOW_20260827/` covers 71 of 2,131 entries (**3.3 %**) at an
> MDE of **$564/entry = 4× the mean**, so it was CLOSED-BY-DATA *before* a feature was written.
> Turnover: **worse than random**. Regime state: **real information, null policy**.

**Both surfaces that were open on 2026-08-27 are now closed by DATA, not by ideas:**

1. **BBO / trade imbalance** — blocked by data. ~300+ overlapping sessions needed. Owner decision,
   `research/operational/OWNER_QUEUE.md` OQ-5.
2. **EVENT RESPONSE** — **CLOSED-BY-DATA**, `runs/DATAGATE_EVENTRESPONSE_20260827/`. A response
   feature exists only *after* its event, which reaches **153 of 2,131 P1 decisions (7.18 %)** on
   **71** effective event sessions — and 12 opportunities after one CPI print are **one** event, not
   twelve. MDE there is **$1,896.67 = 9.8×** the lane-scaled bar (**0.665 sd**); closing the gap
   needs **~96× the effective N**, i.e. ~220 years of calendar. **The constraint is the calendar and
   no model moves it.** Marked **UNDERPOWERED**, not NULL. `XM_CONFLICT` is worse still — 29 of 346
   decisions, and FOMC at 14:00 is not even in its 09:45 information set.

> ### **Every information surface this campaign listed as OPEN is now closed.**
> What remains is **owner-gated acquisition** (order flow, options, more event types), **bounded
> engineering** (`X9a`'s decision contract), or the **two surfaces still marked `LIGHT` rather than
> closed** — the scheduled-event *flag* and **higher-timeframe**. Both are transformations of an NQ
> price path already labelled `DEEP`, which is the lowest-prior category in
> `research/router/THESIS_TO_REPO_ADAPTATION.md`, so neither is a discovery lane. **The next runnable
> item is engineering, not discovery**, and that is the honest state of the frontier.

### ⭐ What `RR_W001` added, and what it closed

**`runs/RR_W001_ACTION_VALUE_LEDGER/`** built the object §3d said was missing — a certified
counterfactual replay of the frozen engine, giving `E[ΔU]` at every one of `P1/PCT`'s 2,131 decision
events instead of the trade's own P&L.

> ### **59 % of `P1/PCT`'s individual decisions have NEGATIVE causal marginal value.**
> Mean **+$162.79**, sd **$2,123.55**, median **−$64.36**. The object is profitable because a
> minority of very large positives carries it. **Genuine selection, not exposure reduction** —
> activity-matched random abstention *loses* money at every fraction and the ex-post oracle beats
> **40/40** random draws, which is the inverse of the W121 failure mode.

**Conditional routing is nevertheless DE-PRIORITISED**, on its own preregistered gates: the
apparatus buys only **15–31 %** over ranking by trade P&L, **35–64 %** of its oracle is *regeneration*
(the box ceasing to latch) rather than avoidance, the top **107** events carry **104.9 %** of the
total, and the sample **cannot certify** a router below **$41–80/decision** against a **$13.93**
materiality bar. Full verdict and the two bugs an adversarial audit caught: the run's `REPORT.md`.

> ### ⚠️ **WHAT RR_W001 DID *NOT* ESTABLISH** — correction, 2026-08-27
> **It did not show that current causal information cannot predict action value. No causal model has
> been fitted to the target at all.** The comparison that made the apparatus look marginal — ranking
> by the trade's **own P&L**, which recovers 68.8–85.5 % of the causal oracle — **is not a live
> control.** Trade P&L is an **OUTCOME**, not information available at the decision. It shows only
> that *a cheaper ex-post label is highly correlated with ΔU*, which is a different claim from
> *ΔU is causally predictable*. Conflating the two was an error and is retired here.
>
> Justified by RR_W001: **FULL ECONOMIC ROUTER = DE-PRIORITISED · HMM = NOT RUN** (G3 is the one
> valid substantive FAIL; G4 was VOID, so it is *no evidence*, not evidence of stability).
> **NOT justified: calling the action-value INFORMATION frontier closed.** It is **UNTESTED.**

> ### 🎯 **The primary causal target from now on is FULL-HORIZON `delta_action_value`.**
> Session-scoped (**mean +$162.79**) remains a valid *decomposition*, but it truncates the
> trailing-250-entry size channel that propagates across sessions. The honest whole-object figure is
> **mean +$115.30, sum $245,698, with 226 events flipping sign.** **A naked +$162.79 must not be
> quoted as the complete causal action value.**

**Status:** the current task queue is
[`research/router/RESEARCH_FRONTIER.md`](../router/RESEARCH_FRONTIER.md). **EVENT RESPONSE is
CLOSED-BY-DATA and is no longer next.** The HMM / latent-state branch is **NOT RUN**.
