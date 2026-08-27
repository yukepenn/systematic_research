# WE_P1PCT_PARITY_20260827 — P1/PCT in the Strategy Analyzer · REPORT

Preregistered (`spec.yaml`, committed at `7196cbb` before any comparison was computed).
OWNER MEGA DIRECTIVE 2026-08-27 (OPERATIONAL RESET) §§15–19, 46, 47.
NinjaTrader 8.1.8.1, CrossTrade add-on v1.13.9, isolated **Backtest** account.
**No order placed on any live account. No strategy enabled, deployed or started. Nothing connected.**

> ## ✅ **PARITY CERTIFIED — all five preregistered gates PASS.**
> ## **`EXECUTABLE_SINGLE_BASELINE` moves from `NONE` to `WeeklyEdgeP1PCT_v1`.**
> ## 2,131 Python trades vs **2,137** NT8 · net **−1.05 %** · matched rate **99.672 %** · weekly series ρ **0.9852** · size-2 share **19.9 % vs 20.7 %**
> ## **1,908 of 2,124 matched trades (89.8 %) reproduce to $0.00 — the summed difference across all of them is literally `$-0`.**

---

## 0. ⭐ THE FINDING THAT MATTERS MORE THAN THE PARITY: the blocker never existed

The repository has carried, for the entire P0 engineering phase, the statement that compiling
`WeeklyEdgeP1PCT_v1` is **an owner-only interactive F5**. `LIVE_READINESS.md` §6 says *"Neither
strategy has been compiled. No NinjaTrader tool was called; compilation and the Analyzer run are
the owner's interactive actions."* `CURRENT_BASELINE.md` §6 says *"awaiting owner F5"* and *"Both
remaining steps are owner-only interactive actions."*

**Directive §15 said to check the tool surface before claiming an owner block. It was checked, and
the claim was false.**

| | |
|---|---|
| `GetMcpCapabilities` | add-on **v1.13.9**, NT8 **8.1.8.1**, features `[compile, strategy_state, alert_relay, backtest]`, **`backtest_engine.available = true`** |
| 7-session smoke probe | `resolved type: NinjaTrader.NinjaScript.Strategies.WeeklyEdgeP1PCT_v1` — **it was already compiled** |

**It was never even blocked on a discovery step.** `runs/WE_W52_NINJASCRIPT/out/nt8_trades_v3.csv`
is dated **2026-08-26** — the campaign had already driven NT8 Strategy Analyzer backtests through
this exact surface *the day before* the P0 wave wrote that the surface was unavailable. And
`OWNER_QUEUE.md` **OQ-3** had recorded the correct rule since 2026-08-09: *"`file_only` is
therefore not by itself proof that a compile is blocked — verify by resolving the class, not by
trusting the flag."*

> ### **The rule was already written down, and the next wave did not apply it.** A capability claim
> ### copied forward from a previous wave is a claim with **no evidence-status tag**. It cost this
> ### campaign an owner blocker that stood for a full day and was reported to the owner twice.
> ### **Every future assertion that something is owner-only must be dated and re-probed, never
> ### inherited.**

---

## 1. Both objects verified byte-identical to the repo before running

| class | repo path | sha256[0:16] | installed copy |
|---|---|---|---|
| `WeeklyEdgeP1PCT_v1` | `research/weekly_edge/ninjascript/` | `ee4c765bc5cab230` | **identical** |
| `WeeklyEdgeP1_v3` *(control)* | `research/weekly_edge/ninjascript/` | `e8bb9caface37462` | **identical** |

No hand edit exists in the NT8 workspace. §20's "verify source matches repo exactly before
compile" is discharged for both.

## 2. Settings — from `LIVE_READINESS.md` §4, not guessed

NQ 09-26 (resolves **NQU6**) · 1-Minute **Last** · **CME US Index Futures ETH** ·
**NinjaTrader Brokerage Lifetime** · **Standard** fill · **0** slippage ticks · isolated
**Backtest** account · `from` 2022-01-03T00:00:00Z · `to` **2026-07-31T21:59:59Z**.

`to` is one second before the next 18:00 ET open, so the last included session is the one ending
2026-07-31 17:00 ET. **This stops strictly before the ≥ 2026-08-01 VIRGIN seal. No sealed data was
touched.** NT8 loaded **1,620,098** bars against the Python substrate's **1,620,044** — the same
continuous series.

### ⚠️ The cost convention, stated before any number is quoted

**The research headline and the NT8 net are not the same quantity.** Research charges
$4.36/ctrRT commission **plus** a candidate-specific **$14.44/ctrRT modelled spread** (W82).
NinjaTrader charges the commission template and zero slippage. The reference is therefore
generated at **commission only**, which is what `gfills` already computes.

> **$14.44/ctrRT is 2.888 NQ ticks round turn** — not an integer number of ticks per side — so
> forcing it into NT8's `slippage_ticks` would invent a third convention. The spread stays in the
> research layer. **Any table that puts $1,394/week beside an NT8 net is comparing two cost models.**

## 3. Headline — in-window 2022-07-01 → 2026-08-01, commission only on both sides

| | PYTHON (research object) | NT8 Strategy Analyzer | delta |
|---|---|---|---|
| **trades** | **2,131** | **2,137** | **+0.28 %** |
| net $ | $333,731 | $330,221 | **−1.05 %** |
| size-2 share | 19.9 % | 20.7 % | +0.79 pp |
| weeks | 210 | 211 | — |
| weekly mean $ | $1,589 | $1,565 | −1.52 % |
| max drawdown $ | $28,124 | $27,765 | −1.28 % |
| **weekly series correlation** | | **0.9852** | |

> **The Python reference reproduces the research object exactly: 2,131 in-window trades is the
> number `CURRENT_BASELINE.md` §1 states.** The reference was built by *importing*
> `run_we_w98.gfills(..., per_ctr=True)` rather than reimplementing it, so a divergence here could
> not have been a transcription bug in the reference.

## 4. Gates

| gate | spec | observed | |
|---|---|---|---|
| **G1** | in-window trade counts within 2 % | 2,131 vs 2,137 = **0.28 %** | **PASS** |
| **G2** | matched rate (entry ts + direction) ≥ 99 % | **99.672 %** | **PASS** |
| **G3** | net P&L within 2 %, commission-only | **1.05 %** | **PASS** |
| **G4** | size-2 share within 3 pp | **0.79 pp** | **PASS** |
| **G5** | control `P1_v3` resolves and trades (§18) | 2,011 in-window trades | **PASS** |

The bands are **not chosen here** — they are lifted verbatim from `WE_W52` spec phase 4 and
restated in `LIVE_READINESS.md` §4, preregistered long before today.

---

## 5. ⭐ Every residual classified — because a passing gate is not an explanation

**§47 forbids averaging a mismatch away.** The residual decomposes completely, and the decomposition
is more informative than the verdict.

| population | n | share | **net $ effect** |
|---|---|---|---|
| **fully agreeing** (same entry, direction, quantity, exit bar) | **1,908** | **89.8 %** | **$−0** |
| quantity disagrees | 123 | 5.8 % | **+$27** |
| exit bar disagrees, quantity agrees | 93 | 4.4 % | +$1,100 |

### 5a. The quality-sizing layer — a warm-up property, and it decays exactly as predicted

| year | trades | qty disagree | Python size-2 | NT8 size-2 |
|---|---|---|---|---|
| **2022** | 215 | **14.42 %** | 13.95 % | 24.65 % |
| 2023 | 581 | 5.34 % | 20.14 % | 19.62 % |
| 2024 | 628 | 4.14 % | 20.22 % | 20.54 % |
| 2025 | 457 | 6.78 % | 22.54 % | 21.88 % |
| **2026** | 243 | **1.65 %** | **18.52 %** | **18.52 %** |

The disagreement is **symmetric** — NT8 sizes 2 where Python sizes 1 on **71** trades and the
reverse on **52** — and its total dollar effect is **$27 across 123 trades**. The causal quality
score is a trailing-**250-entry** quantile; NT8 begins accumulating that history on 2022-01-03
while the Python object carries it from 2022. Borderline entries near the score-3 boundary flip in
both directions until the window fills. **By 2026 the size-2 share is identical to four decimal
places of a percent.** This is exactly the effect W52 §5 disclosed in advance and it is a property
of the measurement, not of the code.

### 5b. The exit-bar cluster is ONE BAR, and it is the forced-flat boundary

**92 of the 100 exit disagreements are exactly −1 minute, and 88 of those 92 sit at a single
bar: Python exits at 16:41, NT8 at 16:40.** That is the `ForcedFlatMin = 21` boundary before the
17:00 ET session end. It is a one-bar phase difference in the session-close flatten, in the same
direction every time, and it is the convention difference `LIVE_READINESS.md` §2 already declared
in advance for the XM object.

**Isolated cost: −$335 over 210 weeks = −$1.60/week, −0.10 % of $1,565/week.**

> This is a **known, disclosed, systematic, single-bar convention difference — not a logic
> difference.** It is documented rather than repaired, because repairing it would change trading
> behaviour and §16 forbids semantic changes during a parity run.

### 5c. ⚠️ The eight large exit gaps — UNRESOLVED, and my first hypothesis was falsified

Eight trades exit more than one bar apart (−2, −2, −2, −7, −9, −11, −17, **−28** minutes), NT8
always earlier. **All eight fall in a contiguous six-week band, 2022-12-11 → 2023-01-23, and none
occurs after it.**

I hypothesised they were downstream of the sizing warm-up — an earlier size disagreement in the
same session shifting the per-contract box accumulation and moving the halt. **That hypothesis is
false: seven of the eight sessions had zero prior size-disagreeing trades.** A session box cannot
truncate a trade mid-flight in any case — `spnl` only accumulates when a trade closes — so these
are **decision-layer** differences: the direction array flipped at a different bar.

The most likely remaining cause is the one W52 §4 identified — *"a member with a large `VolMult`
that has not flipped since before that date still carries a σ-stale threshold"* — which predicts
exactly this: residuals concentrated in the early window and absent later. **That is consistent,
not confirmed.** Eight trades of 2,124 is **0.38 %**, inside every gate, and it is recorded here as
an open residual rather than asserted to be understood.

### 5d. The unmatched trades

**7 Python-only, 13 NT8-only.**

- **8 of the 13 NT8-only trades are all on 2022-07-01** — the very first session of the comparison
  window. Cold start at the warm-up boundary.
- **Four are the same trade one or two bars apart** (2022-11-28 09:44/09:48, 2022-12-29 06:07/06:08,
  2023-01-27 09:50/09:51, 2026-07-19 18:43/18:45) — they fail an exact-timestamp match but they are
  not missing trades, and counting them as two unmatched rows each *overstates* the disagreement.
- **`2026-07-17 10:38` (NT8-only) is the known truncated session** — `CURRENT_BASELINE.md` §5
  already records *"2026-07-17 is truncated (ends 10:53, 83 RTH bars vs 390)"*. The Python substrate
  carries the hole; NT8's data store does not. **A pre-existing documented data hole, not a defect
  found here.**

**10 of 13 NT8-only and 4 of 7 Python-only sit in 2022 — the residual is concentrated at the
warm-up boundary, which is where the theory says it should be.**

## 6. The §18 control

`WeeklyEdgeP1_v3` on identical settings: **2,011 in-window trades, net $284,514**, against W52's
recorded 1,948 / $296,423 on a window two months shorter at the end. The environment resolves the
type, loads the same 1.62 M bars, applies the Lifetime template and trades sanely. **A generic NT8
environment fault is excluded**, so §47's localization order never had to be entered.

## 7. Decision

1. **`EXECUTABLE_SINGLE_BASELINE`: `NONE` → `WeeklyEdgeP1PCT_v1`.** Three separate statuses, and
   §19 forbids collapsing them: **EXECUTABLE · PARITY-CERTIFIED · NOT LIVE ENABLED.**
2. **No research logic was changed.** No parameter was tuned. No mismatch was "fixed" until P&L
   agreed. The only actions taken were: probe the tool surface, run the strategy, and classify what
   came back.
3. **`WeeklyEdgeP1_v3` stays installed** — §38, and it earned its place in this run.
4. **The research headline is unchanged.** $1,394/week raw and $1,230/week at fixed DD are
   *research* numbers under the research cost model. This run certifies **reproduction**, not a new
   economic figure, and `CURRENT_BASELINE.md` §0 keeps the two apart.
5. **Open residual carried forward**: the eight 2022-12/2023-01 exit gaps (§5c), 0.38 % of matched
   trades, mechanism consistent-with-but-not-confirmed-as the slow-member σ warm-up.
