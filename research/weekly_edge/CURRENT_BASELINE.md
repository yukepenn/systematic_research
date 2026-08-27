# CURRENT BASELINE — campaign #7 WEEKLY_EDGE

_Authoritative as of **2026-08-27**, through wave **W111**. Where this file and any older
weekly_edge doc disagree, **this file governs**. Every number is cited to a committed run. This is
the campaign-#7 equivalent of the root `BASELINE_MODELS.md`, which covers campaign #3's three
shipped objects and is unaffected by anything here._

> **CHANGE LOG since the W103 edition** — nothing about the base moved; one status label did.
> - **`XM_CONFLICT` → `ACTIVE COMPONENT`**, raised from the reduced-confidence position W105 left
>   it in, on the strength of **W110**. The +0.464 six-month ρ is **not** downside coupling: ρ
>   conditioned on P1's losing weeks is **−0.165 at the 5.2nd percentile** of a circular-shift
>   null, worst-decile overlap at the **7.1st**, tail beta **−0.660** against an all-week +0.073.
>   And the concentration is **mechanism-consistent** — the pre-entry state predicts the top-20
>   winners at **AUC 0.735, p = 0.000** under a fully re-fitted permutation null.
> - **W109, W110, W111 promoted nothing and closed three things.** The causal trend-day veto, the
>   volume-exhaustion family, and two of my own statistics were withdrawn. See
>   `MECHANISM_COVERAGE_20260826.md` footnotes ⁶ and ⁷.
> - **A new binding rule:** a class-conditional table requires its **matched unconditional
>   control** in the same wave. W111b showed W108's headline signature is reproduced exactly by an
>   unconditional fade.

---

## 1. THE BASE — what it is right now

### `P1/PCT`

Unchanged from `P1` in every respect except one, and that one change is a **unit correction, not a
new strategy**:

| component | status |
|---|---|
| 13-member Solar volatility-ratchet ensemble, four combiners, 32-config vote | unchanged |
| **OR-gated with the B-MOM channel** (latched ±1, `px > max(open₀₉₃₀ + mtod14, RTH VWAP)`, reset 09:31, killed 15:57) | unchanged |
| long-only | unchanged |
| range throttle q = 0.8 · delta gate | unchanged |
| causal quality sizing — size 2 when score ≥ 3 (18.3 % of trades) | unchanged |
| **session box −$1,300 / +$1,000** | ⭐ **CHANGED: now denominated PER CONTRACT, not per position** |
| flat at every session close | unchanged |

**Why the change** (`runs/WE_W98_BOXDENOM/`): a dollar stop on a variable-size position halts a
2-lot at **half** the adverse point move of a 1-lot. That is a mis-specification by construction.
Under the incumbent, loss-halts fired at **55.68 points on size-1 sessions and 37.18 on size-2**.

**What it bought** — full modern window 2022-07-01 → 2026-08-01, 1,058 sessions / 213 weeks, net of
$14.44/ctrRT candidate-specific spread plus $4.36 commission:

| | `ABS` (old) | **`PCT` (current)** |
|---|---|---|
| weekly $ | $1,154 | **$1,394** |
| **weekly $ at fixed $20,245 max DD** | $885 | **$1,231  (+39.0 %)** |
| positive weeks | 53.1 % | **56.3 %** |
| max drawdown | $26,388 | **$22,931** |
| top-5 drawdown | $18,421 | $17,835 |
| t | 3.58 | **4.16** |

**The controls, which are the actual evidence:** a *uniformly* looser dollar box is worth
**+$6/week (paired p = 0.940)**; holding the average budget fixed while making it size-conditional
keeps **+39.6 %**; both size-1 objects (BMOM, NETFUSE_1) show **exactly $0.00** across all 213
weeks; the real gap sits at the **99th percentile** of 200 size-label permutations.

**Label: `REGIME_LOCAL`.** On 2006–2021 the change **reverses (−31.4 %)** — a $1,300 box was 84 %
of a typical session's range then and is 19 % now, so it fires **5.7× more often today**. `ABS` is
retained beside `PCT` in every table and is not deleted. Paired weekly p = 0.057, and **90.8 % of
the gross difference lives in 53 of 1,058 sessions**.

---

## 2. THE BEST CANDIDATE PORTFOLIO — not the base, not promoted

### `{P1/PCT + XM_CONFLICT}`, inverse-volatility weights

`XM_CONFLICT` (`runs/WE_W101_DIRECTION/`, `WE_W102_XMENGINE/`): at 09:45 ET take NQ's own opening
drive — sign(close₀₉₄₅ − open of the 09:31 bar) — **only on the ~34 % of sessions where the
ES/RTY/YM composite is moving the opposite way**. Fill at the 09:46 open, hold to 15:45, size 1,
**no stop**.

| | P1/PCT alone | **P1/PCT + XM_CONFLICT** |
|---|---|---|
| **weekly $ at fixed $20,245 DD** | $1,230 | **$2,012  (+63.5 %)** |
| positive weeks | 56.3 % | 59.2 % |
| **max drawdown** | $22,931 | **$11,489** |
| **top-5 drawdown** | $17,835 | **$8,735** |
| t | 4.16 | **4.90** |

⚠️ **Quote the range, not a point: +45 % (income-matched, W102) to +64 % (inverse-vol, W103).**
**The STRUCTURAL result — that adding XM substantially reduces drawdown overlap with P1/PCT — is
the sturdy one. The exact income number is not a forecast and is the weaker half.** Max drawdown
and top-5 drawdown roughly halve in the studied modern window; that is what is believable.

**Why it works and nothing else does:** ρ(weekly, P1) = **0.081**. Every other object in the
campaign correlates 0.27–0.72 with P1. Adding the 2:3 pair on top makes the portfolio **worse**
(−12 %), and an independent 63-cell integer grid puts its argmax at **2 P1 : 0 PAIR : 1 XM** —
zero pair. Two weighting methods converge on "drop the pair".

**Status (updated W110, directive V5 §4/§39):** EVIDENCE **STRONG (current regime) · REGIME_LOCAL**
· PORTFOLIO ROLE **ACTIVE COMPONENT** · ENGINEERING **SOURCE_READY / PARITY_PENDING**
(`WeeklyEdgeXMConflict_v1.cs` written, **not compiled, not reconciled**) · **NOT ENABLED**.
Caveats that travel with every quotation:

- **N = 348** trades, ~1.6 sessions/week.
- **The window is discovery-consumed** (2022-07 → 2026-08, mined for 103 waves).
- **ρ = +0.446 with B-MOM.** A diversifier against P1, only partly against the pair.
- **REGIME_LOCAL by DATA AVAILABILITY, not by choice** — ES/RTY/YM substrates begin 2022-01-02, so
  no 2006–2021 test exists and none can be built from anything on disk.
- **The only intra-trade risk control is the clock.** Worst adverse excursion ever: **−$10,865
  (543 points)** — **a sample maximum, not a bound**. Every ALPHA stop from 20 to 300 points makes
  it worse at fixed drawdown, but that is *not* an argument that no stop is the right live policy.
  A separate **DISASTER** layer is priced in `runs/WE_W105_XMAUDIT/`: a 300-point account-survival
  stop costs **0.7 %** of gross edge and would have triggered 13 times; 500 points costs 4.1 % and
  triggered twice. **No level is selected — the owner sets capital risk.**
- It was **selected as the best of 27 cells** (W101) and its combination as the **best of 6**
  (W103). It cleared a best-of-27 coin null, a rate-matched subsample null at the 99.6th, and a
  |drive|-**decile**-matched null at the **99.7th** — but the selections happened.
- **Last three months are weak**: the primary combination is $499/wk at fixed DD, 35.7 % positive
  weeks, **t = 0.25** over 14 weeks — inside the BURNED span.
- ⚠️→✅ **W105: ~20 sessions of 348 carry 85 % of the money.** Dropping the top 5 costs 28 %, top 10
  costs 49 %, top 20 costs **85 %**. Inside individual years the top-10 contribution *exceeds
  100 % of net*, i.e. the other trades lost. Any income figure must carry "carried by ~20 sessions
  in four years". **W110 answers §25's question about that concentration: it is MECHANISM-CONSISTENT,
  not accidental.** Using only features known at or before 09:45 on the trade's own session — no
  MFE, no MAE, no realized path — a cross-validated model ranks the tail winners at **AUC 0.735 /
  0.783 / 0.869** for the top 20 / 10 / 5, **p = 0.000 / 0.003 / 0.000** against 400 permutations
  that each re-run the entire fit. The separating state is a **wide overnight range** (1.62× vs
  1.14× median), a **scheduled CPI/NFP/FOMC day** (35 % vs 11.3 %), and — at the tightest cuts — a
  **small opening drive that barely disagrees with the complex** (divergence 0.26 vs 1.05). It is
  genuinely multivariate: the announcement flag **alone** ranks at AUC 0.498.
  ⚠️ **WITHDRAWN from W110's own first pass:** an AUC null that permuted labels while holding
  leave-one-out predictions fixed, reported as 0.697/0.758/0.863 at the "99.7th/99.9th/99.9th
  percentile". That null was too easy; the corrected figures above replace it and are stronger.
  ⚠️ **THE CAVEAT THAT TRAVELS WITH IT:** "tail winner" is defined by these same 348 trades.
  Cross-validation controls overfitting, it does not create a holdout. This is **descriptive**, and
  per the W110 spec **no filter was built from it.**
- ⚠️→✅ **W105 flagged the correlation as unstable; W110 measured what it actually means.** ρ(XM,
  P1) is **+0.081 full-window and +0.464 over the trailing 26 weeks** — both reproduce exactly.
  **But the 26-week series has ranged −0.537 to +0.566 with a median of +0.021 over these four
  years, 12.2 % of all 26-week windows have exceeded +0.30, and the 52-week ρ has NEVER exceeded
  +0.30.** More decisively, **the coupling is not on the downside**, against 212 circular shifts:

  | | REAL | null mean | percentile |
  |---|---|---|---|
  | ρ, all weeks | +0.081 | −0.000 | 89.2th |
  | **ρ ∣ P1 < 0** | **−0.165** | +0.000 | **5.2th** |
  | P(XM<0 ∣ P1<0) | 0.341 | 0.352 | 33.0th |
  | worst-decile overlap | 0.005 | 0.011 | 7.1th |
  | **tail beta**, P1's bottom decile | **−0.660** | +0.003 | 13.7th |
  | joint max DD | $11,489 | $13,382 | 18.9th |
  | **joint DD duration** | **7 wk** | 18.2 wk | **beyond the null** |

  **The two engines are mildly coupled when they WIN and anti-coupled when P1 LOSES.** Still watch
  the trailing 26-week ρ — and note the one statistic that did move adversely: P(XM<0 ∣ P1<0) rose
  from 0.200 to 0.500 between the first and last 26 weeks, on about eleven P1-losing weeks.
  ⚠️ **WITHDRAWN from W110's own first pass:** "zero overlap between the two ten-worst-week sets,
  0.0th percentile" — 61.3 % of circular shifts also produce zero overlap. The fact is true, the
  inference was not.
- ✅ **W105b: it is NOT an event trade.** Against the committed CPI/NFP/FOMC calendar, the
  **304 non-announcement trades earn $408/trade at a 54.9 % hit rate**. Announcement sessions are
  3.9× richer ($1,611/trade, 36 % of net from 13 % of trades) and **NFP is extreme** (n = 12,
  83.3 % hit, $3,556/trade) — recorded, **not** turned into a filter.
- ✅ **W105: it is genuinely two-sided** (longs 60.5 % hit / $701, shorts 48.0 % / $415 — both
  positive) and **not an early-sample artifact** ($540 in 2022-23 vs $569 from 2024 on).
- ⚠️ **W105 withdraws the per-year improvement story.** At the canonical anchor the profile is
  $853 / $441 / $654 / $317 / $751 — **no trend**. W101b's "$186 → $1,064 monotone" was an
  artifact of the one-minute-early anchor.
- **N = 348 is canonical** (09:31 anchor). N = 342 is the same object at the 09:30-stamped
  anchor. Both reproduce exactly; they are two anchors, not a discrepancy.

---

## 3. STRONGEST CHALLENGER, still not promoted

`PAIR23` = **2 BMOM : 3 X9a**, sleeves boxed independently, per-unit:
**$1,309/wk at fixed DD · 60.6 % positive weeks · max DD $18,088 · top-5 $11,362 · t 4.36** — the
best *single* object in the campaign, better than P1/PCT's $1,230.

It beats P1 on money, max drawdown, top-5 drawdown, positive-week rate **and** losing streak
simultaneously over the 16 unseen years 2006–2021 (`runs/WE_W97_AUDITFIX/`). It is **not promoted**
because W86's specificity null said the gain is *"two independent streams"* rather than *these two*,
and because W103 now shows it **adds nothing on top of P1 + XM_CONFLICT**.

**Demoted:** `NETFUSE_1` — the only object ever to clear a specificity null, and **deep-negative**
(−$8,951 over 2006–2021) with a top-5 drawdown 32.9 % worse than P1's.

---

## 4. WHAT THE BASE DOES NOT DO

> ⚠️ **READ `OPPORTUNITY_LANGUAGE.md` BEFORE QUOTING ANY NUMBER IN THIS SECTION.** The ceiling
> below is `EX_POST_EXECUTION_FEASIBLE_ORACLE` — **it knows the future direction of each segment.**
> It is an upper bound after turnover and friction constraints, **not causally available money**,
> and the gap to what we capture is not money we failed to collect. The four levels are
> `EX_POST_PATH_ORACLE` > `EX_POST_EXECUTION_FEASIBLE_ORACLE` > `CAUSAL_MODEL_FRONTIER` >
> `REAL_SYSTEM_CAPTURE`, and **`CAUSAL_MODEL_FRONTIER` has never been measured in this repo.**

From `runs/WE_W103_CONSOLIDATE/` (capture ledger v3):

| segment | **level-2 oracle** $/session | base takes | **ratio** | p\* *(this geometry only)* |
|---|---|---|---|---|
| MORN 09:45–11:29 | $1,744 | $78 | **4.4 %** | **0.5048** |
| ON_EU 00:00–07:59 | $1,224 | $18 | 1.5 % | 0.5078 |
| MID | $1,197 | $19 | 1.6 % | 0.5059 |
| AFT 13:30–15:44 | $1,170 | $3 | **0.3 %** | 0.5058 |
| ON_ASIA | $1,026 | $39 | 3.8 % | 0.5139 |

> **After 103 waves the base captures 0.2 %–5.1 % of the LEVEL-2 EX-POST ORACLE in every
> segment** — a ceiling that knows each segment's direction in advance — and
> ex-post movement per session has **risen 83 %** while P1's own production went negative.
> By class: TREND-DOWN and REVERSAL have **flipped positive** for the first time (+$195, +$27
> income-matched, from −$495 and −$64) — with **$10,953 and $9,073 per session of those classes
> still open**.

---

## 5. Frozen conventions (do not change without a wave)

| | |
|---|---|
| window | 2022-07-01 → 2026-08-01, 1,058 sessions, 213 weeks |
| substrate | `load_deep(..., extend=True)` — deep file to 2026-05-29 joined to `SM1M_SUBSTRATE` |
| cost | $4.36/ctrRT commission **inside** the fill engine + candidate's own contract-weighted spread from `WE_W82_FILLAUDIT/out/spread_by_minute.csv` (P1 $14.44, BMOM $13.02, XM_CONFLICT $12.50) |
| headline metric | weekly $ at a fixed **$20,245** max drawdown — algebraically scale-invariant |
| opportunity language | **`OPPORTUNITY_LANGUAGE.md` is binding.** Every ceiling figure names its level or is not quotable |
| exposure convention | **income-matched** (W97: the only one with no free parameter) |
| seal | ≥ **2026-08-01 VIRGIN**; **2026-05-31 → 07-31 BURNED** |
| known data holes | **2026-07-17 is truncated** (ends 10:53, 83 RTH bars vs 390); spread profile has 1,380 minutes, the missing 60 being the 17:00–17:59 CME break |

---

## 6. Engineering status, active challengers, and the next residual (directive V5 §31)

### Engineering — P0-B

| object | source | compiled | Analyzer parity | enabled |
|---|---|---|---|---|
| `P1/PCT` — `WeeklyEdgeP1PCT_v1.cs` | ✅ written, 14-line mechanical diff from the parity-tested `P1_v3` | ⏳ **copied into NT8 `bin/Custom/Strategies/`, awaiting owner F5** | ⏳ pending | ❌ |
| `XM_CONFLICT` — `WeeklyEdgeXMConflict_v1.cs` | ✅ written, first multi-series signal strategy in the repo | ❌ **deliberately not yet copied** — owner sequenced P1PCT first so a first-compile failure cannot take the whole `NinjaTrader.Custom.dll` down | ❌ | ❌ |
| `WeeklyEdgeX9a_v1.cs`, `WeeklyEdgeBmom_v1.cs` | ✅ written (W89 era) | ❌ never installed | ❌ | ❌ |

**Both remaining steps are owner-only interactive actions.** Parity protocol is binding from WE_W52:
compare the **decision series** first — ≥99 % agreement plus trade counts within 2 % = VALIDATED;
90–99 % = classify every mismatch; <90 % = the C# is not the object.

### Active challengers

| object | status |
|---|---|
| `PAIR23` (2 BMOM : 3 X9a) | best *single* object ($1,309/wk at fixed DD) but **adds nothing on top of P1/PCT + XM** (W103, two independent weighting methods) — **not promoted** |
| `D1_DIR_EFF` @ 0.50 as a fade veto | **CLOSED by W113.** The same state layer that failed to route five losing fades also fails to route P1/PCT — all 8 cells below baseline, best at the 58.0th percentile of a random-veto null, and max DD *rises* in every cell |
| ⭐ **`FOLLOW_MORNING`** — buy at 11:49 if the 11:29 close is above the 09:31 open, sell if below, exit 15:44, size 1, **no parameters at all** | **`REGIME_LOCAL` · WATCH.** W114: **$179/trade, 55.00 %, 98.9th percentile** on 2022-07 → 2026-08, genuinely two-sided (long leg $198, short leg $158, always-long only $21), 14 of 15 decision-time cells between $146 and $196, positive in 4 of 5 calendar years, **t12m $236**. ⚠️ **FAILS its 16-year out-of-window half** (2006–2021: −$9/trade, 49.40 % vs p\* 51.76 %) and the failure is **behavioural, not cost** — implied directional edge **0.70 % then vs 5.62 % now** at zero spread. ρ **+0.279** with P1/PCT, so it is *not* an orthogonal source; adds +3.6 % at fixed DD to the candidate portfolio while lowering t from 4.90 to 4.58. **Decided by the sealed forward data and nothing else.** |

### Demoted / closed since W103

`NETFUSE_1` (deep-negative 2006–21) · `VWAP_RECLAIM` (trend follower wearing a reversal label) ·
**`CAUSAL TREND-DAY VETO`** (W109 fades 85.0th percentile, **and W113 on the baseline 58.0th — two
independent failures on opposite kinds of engine, family CLOSED**) · **`VOL-EXHAUST / ABSORB`**
(W111, 0.0th percentile, three of five *anti*-predictive against a volume-matched null) ·
**`AFT as a research target`** (W112 — de-prioritised with a *reason* rather than another null).

### ⚠️ A standing correction the campaign has to carry

**Seven fade mechanisms were killed here and the family was recorded as dead.** W114 measures the
**mirror** of those fades — follow the morning direction instead of fading it — at **+$179/trade on
the same sessions, with the same costs and the same geometry**, while the matched FADE arm earns
**−$208**. The fades were not failing because mean reversion is impossible on NQ. **They were on the
wrong side of a live momentum effect**, and W111b separately showed that the class table which had
been read as evidence for them is definitional. Both corrections point the same way.

### The next residual, and what is actually pointed at

The capture ledger in §4 is unchanged — **MORN remains the largest single-segment gap** at $1,744
per session of level-2 oracle against $78 taken, at p\* = 0.5048. Three lanes have now attacked the
afternoon and the late morning and all three failed.

⚠️ **W112 and W113 have since narrowed this considerably.** W112 measured the level-3 causal
frontier for AFT directly and found **no fitted model beat a one-line momentum control** (ridge
out-of-sample R² −0.024, directional accuracy *below* always-long) — the first direct evidence that
most of the AFT gap is the oracle's foreknowledge rather than money we are failing to collect, so
**AFT moves DOWN the queue, not up.** W113 then closed the routing hypothesis on the profitable
engine as well as the losing ones.

**W109's finding was that the failure was at the POLICY layer, not the information layer:** three causal states known at 11:48 discriminate ex-post TREND from
RANGE/MIXED at **AUC 0.613–0.621**, decisively above 2,000-draw permutation nulls, and that is not
definitional because the detectors see only the morning while the label sees the whole session. A
**binary** veto on information that weak removes good and bad sessions in equal proportion
(selectivity ratio 0.74–1.12 across all 18 cells). The successor object — **untested, and it may
well fail too** — is directive §22's continuous action value: estimate `E[PnL(action) | I_t]` and
weight exposure by it rather than thresholding a weak state into a binary cut.
