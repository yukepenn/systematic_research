# INFORMATION COVERAGE MATRIX — 2026-08-27

POST-W121 owner directive **§37**. `MECHANISM_COVERAGE_20260826.md` asks *"have we tested strategy
family X?"* This asks a different and now more useful question:

> ### **What causal information does the book actually OBSERVE, and where are the INFORMATION gaps — as distinct from the strategy-name gaps?**

Legend: **DEEP** · **SUPPORTED** · **LIGHT** · **NULL** (tested, failed) · **BLOCKED** (data) ·
**·** (untested). Every cell is marked from a committed artifact.

| information surface | depth | evidence |
|---|---|---|
| **NQ price path** | **DEEP** | the entire campaign; P1/PCT is built on it |
| **NQ volatility / range** | **DEEP** | ratchet, range throttle, W77 (verdict stands, mechanism claim withdrawn) |
| **time / clock** | **DEEP** | W104 segments, W114/W116 timing plateau, W118 event-driven entries |
| **cross-market — OPENING AUCTION** | **SUPPORTED** | `XM_CONFLICT`: the campaign's one cross-market success. W101/W102/W102c/W104/W105/W110 |
| **cross-market — INTRADAY SUPPORT** | **NULL** | **W122**: 5 primitives × 3 windows at P1's own entry events. Matched Q5−Q1 −$157, all four gates fail, best cell $262 vs a $503 family bar. Pooled signal collapses under matching ⇒ it was NQ momentum relabelled |
| **trade participation / volume (1-min)** | **NULL** | W111: −$233/trade, 0.0th pctile; three of five mechanisms **below the 5th percentile** of a volume-decile-matched null |
| **BBO / micro-price / trade imbalance** | ⚠️ **REOPENED — NOT BLOCKED** | `DATAGATE_ORDERFLOW_20260827` measured the **substrate** (48 sessions ⇒ 71 of 2,131 P1 entries, 3.3 %, MDE $564/entry). `runs/DATA_CAPABILITY_AUDIT_20260827/` measured the **disk**: the local NT8 tick store holds (**corrected to HOUR granularity** — a session spans two calendar dates of `.ncd` files, so the first date-level pass overstated by 52) **243 NQ sessions with ≥ 90 % `Last`** and **99 with ≥ 90 % quote coverage**, of which **197 / 57 have never been extracted**. **Two lanes, do not merge them:** signed flow goes **46 → 243** (**81 %** of the ~300 target, **not** meeting it — an earlier claim that it did is retracted); quote-based features go **45 → 99** (**33 %**). **Both expand hugely at zero cost; neither clears its own bar.** The bottleneck was **manual labour**, not entitlement or money |
| **DOM / Level-II** | **BLOCKED** | owner risk-control pause 2026-08-12; no history exists anyway |
| **value / acceptance (VWAP)** | **NULL** | `VWAP_RECLAIM` closed (W108); VWAP displacement is a real *class* detector (AUC 0.621, W109) but its veto fails on both fades and the baseline |
| **market state / regime (trend vs range)** | **REAL INFO, NULL POLICY** | W109: AUC 0.613–0.621, 100th pctile of permutation nulls — **genuine**. W109 + W113: the veto fails on losing fades *and* on the profitable baseline. Selectivity ratio 0.74–1.12 |
| **turnover / own decision history** | **NULL** | W121: caps sit **below** their count-matched random placebo (0.0–4.0th pctile). Marginal entry does not decay — the 4th is the *best* |
| **scheduled macro event flag** | **LIGHT** | committed CPI/NFP/FOMC calendar; W105b (XM is *not* an event trade); W110 (announcement flag alone AUC 0.498) |
| **event RESPONSE (not the flag)** | **CLOSED-BY-DATA** | `DATAGATE_EVENTRESPONSE_20260827`: a response feature reaches **153 of 2,131 P1 decisions (7.18 %)** on **71** effective event sessions; MDE **$1,896.67 = 9.8×** the lane-scaled materiality bar (0.665 sd). Closing it needs ~**96× the effective N**. The binding constraint is the **calendar**. Not `NULL` — **UNDERPOWERED**, per directive §20 |
| **overnight inventory** | **NULL** | ONRANGE01/02, W96 |
| **higher-timeframe** | **CLOSED** | **RR_W004**: six multi-session features added incrementally to RR_W002A's 18. `X+HTF` at the **61.5th** percentile of its refitted null, `HTF` alone at the **71.0th**, and the **known-null negative control at the 77.0th — higher than either real arm**. Adding HTF made fold-sign consistency *worse* (54 % → 31 %). Was `LIGHT` on `HTFMECH01`, campaign #3, a different object |
| **execution / friction** | **SUPPORTED** | W82 measured the fill cost that 82 waves had assumed |
| **market internals (TICK/ADD/TRIN)** | ⚠️ **PARTLY FALSIFIED** | `runs/DATA_CAPABILITY_AUDIT_20260827/` probed the live connection instead of the repo: **`$TICK` serves 1-minute back to 2018-07-10 (8 years)**, **`$TRIN` back to 2022-07-11**, **`$VIX` daily ~2–3 years**. **`$ADD` and `$VXN` genuinely absent** (`PROVIDER_LIMIT`, failed probes on record). The old ✗ recorded that no *file* existed, which is not the same claim |

## The honest summary — rewritten 2026-08-27 after RR_W002A / RR_W004 / the event-response gate

**No surface is both open and reachable.** The two that were listed as open here have since closed:
**event RESPONSE** is `CLOSED-BY-DATA` (7.18 % coverage, 71 effective event sessions, MDE 9.8× the
lane-scaled bar), and **higher-timeframe** is `CLOSED` on a direct incremental test.

**And the direct question was asked.** `RR_W002A` fitted 18 causally-verified features against
FULL-HORIZON action value under a null that refits the entire walk-forward: the primary landed at the
**51.0th percentile**, and a **known-null family scored higher (77.0th) than any real arm**.
`RR_W004` repeated that shape for HTF.

> ### **No tested current information surface separates P1 action quality.** That statement is now
> ### COMPLETE rather than partial — every reachable lane has been measured, not merely
> ### most of them.
>
> ⚠️ **2026-08-27, `runs/DATA_CAPABILITY_AUDIT_20260827/`: "reachable" meant "already materialized in this
> repo." That is a strictly narrower population than "servable by the owner's existing
> connections," and the second was never probed. Three lanes below are now reopened at
> ZERO COST. The measured lanes stay measured — nothing above is retracted — but the
> word COMPLETE now carries the qualifier it always needed.**

**What remains is untested because it is UNAVAILABLE, not because it failed:**

| surface | why |
|---|---|
| ~~BBO / order flow / micro-price~~ | ⚠️ **NO LONGER UNAVAILABLE** — **197** `Last`-complete and **57** quote-complete NQ sessions sit unextracted on local disk. Still **short of the ~300 bar** on both lanes. See the row above |
| **options / dealer gamma** | not owned. Owner acquisition |
| **a wider macro calendar** | ~4× the event count would take the MDE to ~5× the bar. Better, still short |
| ~~market internals~~ | ⚠️ **`$TICK` / `$TRIN` / `$VIX` are available and free.** Only `$ADD` and `$VXN` are genuinely absent |
| **DOM / Level-II** | owner risk-control pause, and no history exists anyway |

> ### The next material information jump requires **data we do not own** or a **surface nobody has
> ### named yet**. It does not require another threshold on the NQ price path — and that is now a
> ### measured claim rather than an impression.
