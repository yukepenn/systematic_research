# V1f — EVENT-DAY MARGIN MULTIPLIER AS A LEVERAGE CONSTRAINT

Run: `W17_C4_COMPLIANCE` · script `runs/W17_C4_COMPLIANCE/src/v1f_eventdays.py` · date 2026-08-09
Window: dev only, **2022-01-03 .. 2026-05-29** (1,139 sessions). No data ≥ 2026-08-01 was read.
**2006–2021 was not touched anywhere in this work.** Every dollar figure below is a dev-window
realized-P&L figure from a committed artifact.

---

## 0. THE FRAMING THAT GOVERNS EVERYTHING BELOW (read first)

The 4X policy is **forward-looking**. NinjaTrader Brokerage may set intraday margin to 4X
standard rates from at least 15 minutes before a key economic release, and may raise margin in
real time without notice. **No backtest in this repo ever experienced that policy.** Nothing in
this document is a correction to historical P&L, and no historical return is restated as if the
multiplier had applied. What the multiplier can constrain is **deployable leverage going
forward** — how many contracts a given account may carry on those sessions — and that is the
only thing §3 measures.

Future profitability is not established by anything here.

Object-status caveats carried forward unchanged:
* **BEST_ONE_MNQ has a confirmed defect** (KNOWN_ERRORS #7 arrangement: no voluntary exit order
  is ever submitted; 67.6% of exits are the 17:00 session-close backstop, 30.9% are managed
  auto-reversals). Every BEST_ONE_MNQ number below is **PROVISIONAL**.
* Product A (`SolarWaveSMMaster_v2`) is compliant on normal sessions.
* All three objects breach the initial-margin window on some of the 43 holiday early closes.

---

## 1. THE CALENDAR — `runs/W17_C4_COMPLIANCE/src/v1f_event_calendar.csv`

194 scheduled-release rows land inside the dev window. Every row carries an explicit provenance
tier; the tier is never averaged away, and the analysis is re-run on each subset.

| tier | meaning | rows |
|---|---|---|
| `RULE` | deterministic published rule, validated against checkpoints | 48 |
| `RECALL` | hardcoded from model recall of a published calendar; **NOT verified against a source** (no web access permitted for this task) | 33 |
| `RULE_APPROX` | rule known **not** to be exact; measured hit-rate reported below | 98 |
| `UNVERIFIED` | cannot be established — 2025-26 shutdown disruption, or forward extrapolation | **15** |

| series | RULE | RECALL | RULE_APPROX | UNVERIFIED |
|---|---|---|---|---|
| FOMC | 0 | 32 | 0 | 3 |
| NFP | 48 | 1 | 0 | 4 |
| CPI | 0 | 0 | 49 | 4 |
| PCE | 0 | 0 | 49 | 4 |

### Rules used, and their measured accuracy (DIRECT measurement, not assumed)

* **NFP / Employment Situation — `RULE`.** BLS publishes on the **third Friday after the
  conclusion of the reference week**, the reference week being the Sunday–Saturday week
  containing the 12th of the reference month; shifted to the prior business day if that Friday
  is a federal holiday. This reproduces "first Friday of the next month" in most months and
  correctly produces the second-Friday months. **Measured 12/12 exact** against recall
  checkpoints spanning 2022-01 → 2025-07 (including the 2025-07-03 Independence-Day shift).
  One documented override (`RECALL`): the rule yields 2025-01-03 for the Dec-2024 report; BLS
  scheduled 2025-01-10 (2025-01-09 was a federal closure).
* **FOMC — `RECALL`.** 8 scheduled meetings/yr, decision on day 2 at 14:00 ET. 2022–2025
  decision dates are hardcoded from recall of the published calendar. **2026 is `UNVERIFIED`**
  (pattern extrapolation); only 3 of those fall in the dev window and §2 shows the FOMC result
  is unchanged when they are dropped.
* **CPI — `RULE_APPROX`.** No exact public rule exists. Used: **8th business day of the release
  month** (federal holidays excluded). **Measured 11/12 exact, 12/12 within 3 calendar days**
  against the 2022 checkpoint set.
* **PCE (BEA Personal Income & Outlays) — `RULE_APPROX`.** Used: **last Friday of the release
  month**. **Measured 9/12 exact** against a 2023 checkpoint set that *deliberately includes
  Aug/Nov/Dec*, the months where the anchor is expected to fail. This is the weakest series.

### The UNVERIFIED class, and how much it matters

15 rows (7.7%) are UNVERIFIED: 12 BLS/BEA releases whose scheduled dates fall in the
2025-10-01 → 2026-01-31 federal-shutdown disruption window (the Sept-2025 Employment Situation
slipped its slot and at least one monthly CPI was not published on schedule; the re-scheduled
dates cannot be established without a source, so they are **marked, not guessed**), plus the 3
extrapolated 2026 FOMC dates.

**Sensitivity to the UNVERIFIED class is small and is reported directly.** Dropping the 4
shutdown-window NFP dates moves Product A's NFP-session net from +$3,613 to +$1,108 and
BEST_ONE_NQ's from −$2,078 to −$5,064 — both remain statistically null. Dropping the 3
extrapolated 2026 FOMC dates moves Product A's FOMC-session net from −$22,792 (35 sessions) to
−$23,628 (32 sessions) and the placebo p from 0.0070 to 0.0046 — the FOMC finding does **not**
depend on the unverifiable dates.

### Session mapping
A release at 08:30 or 14:00 ET on calendar date D falls inside the CME session whose `sess_date`
(= date of the 17:00 ET close) is D. Session dates come from the campaign's own bar file
(`sm01_solarsim.load_bars_3m`). Exactly 1 calendar date failed to map to a session and was
dropped: **2024-03-29**, a PCE `RULE_APPROX` date that is Good Friday — a full CME holiday with
no session. (This is also direct evidence that the last-Friday PCE anchor is wrong that month.)

Calendars used:

| name | definition | sessions |
|---|---|---|
| `CORE_FOMC_NFP` | RULE + RECALL only (= FOMC 2022-25 + NFP ex-shutdown) | **81** of 1,139 (7.11%) |
| `PLUS_APPROX_cpi_pce` | adds CPI + PCE rule dates | 176 (15.45%) |
| `ALL_incl_unverified` | adds the UNVERIFIED class | 190 (16.68%) |
| `DILATED_core_pm1` | CORE ± 1 trading session | 234 (20.54%) |

---

## 2. P&L ATTRIBUTION — DIRECT MEASUREMENT

Sources: Product A = `runs/SMV2M_MASTER_BUILD/out/parity_daily_aligned.csv` col `nt` (NT8
executable curve); Product B = the committed NT8 trade lists, session-bucketed exactly as
`build_parity_and_metrics.py` does. Reconciliation: A net $177,315.10, B-NQ $303,449.00,
B-MNQ $28,900.70 — all three match the committed headline figures exactly.

**Definitions.** "Worst-day" is reported four ways on session net P&L: worst 10, worst 25,
bottom 1% (= 12 sessions), bottom 5% (= 57 sessions). Significance is a one-sided
hypergeometric tail (P(hits ≥ observed) drawing m sessions from 1,139 of which 81 are event
sessions), plus a 10,000-draw placebo of random equal-sized session sets.

### 2a. CORE calendar (FOMC + NFP, 81 sessions = 7.11% of the window)

| | Product A | BEST_ONE_NQ | BEST_ONE_MNQ *(PROVISIONAL — buggy object)* |
|---|---|---|---|
| net, all sessions | **+$177,315.10** | **+$303,449.00** | **+$28,900.70** |
| net on event sessions | **−$22,519.90** | **−$36,766.96** | **−$8,407.90** |
| **(i) share of total net P&L on event days** | **−12.70%** | **−12.12%** | **−29.09%** |
| mean $/session, event vs non-event | −$278 vs +$189 | −$454 vs +$322 | −$104 vs +$35 |
| **(ii) share of total LOSS dollars on event days** | **11.25%** | **10.77%** | **12.59%** |
| worst-10 hits (exp 0.71) | 2 · p=0.155 | 1 · p=0.523 | **3 · p=0.029** |
| worst-25 hits (exp 1.78) | 4 · p=0.096 | 2 · p=0.542 | **6 · p=0.0064** |
| bottom-1% hits (exp 0.85) | 2 · p=0.208 | 1 · p=0.589 | **3 · p=0.048** |
| bottom-5% hits (exp 4.05) | **8 · p=0.043** | **8 · p=0.043** | **12 · p=0.00038** |
| $ of worst-10 on event days | −$9,618 of −$54,500 (17.6%) | −$11,127 of −$113,240 (9.8%) | −$4,608 of −$13,968 (33.0%) |
| $ of worst-25 on event days | −$17,279 of −$112,619 (15.3%) | −$19,440 of −$232,935 (8.3%) | −$7,305 of −$28,480 (25.7%) |
| placebo p (event net this low or lower) | 0.0202 | 0.0360 | 0.0024 |

**Reading it straight.** All three objects are net *losers* on FOMC+NFP sessions, and those
sessions carry ~11–13% of the loss dollars against a 7.1% base rate — a lift of ~1.5–1.8×, not
a tail-domination story. Extreme-day concentration is **absent for Product A and BEST_ONE_NQ**
at the worst-10/worst-25/bottom-1% definitions (all p > 0.09) and only appears at the broad
bottom-5% cut. It is materially stronger for BEST_ONE_MNQ — which is precisely the object with
the confirmed exit defect, so that is the **least** trustworthy of the three signals.

### 2b. Decomposition — the effect is FOMC, and only FOMC

| calendar | Product A net (mean $/sess) | BEST_ONE_NQ | BEST_ONE_MNQ | Product A placebo p |
|---|---|---|---|---|
| FOMC only (35) | **−$22,792 (−$651)** | −$32,600 (−$931) | −$5,277 (−$151) | 0.0070 |
| FOMC 2022-25 recall only (32) | **−$23,628 (−$738)** | −$31,703 (−$991) | −$5,182 (−$162) | 0.0046 |
| NFP only (53) | +$3,613 (+$68) | −$2,078 (−$39) | −$3,789 (−$71) | 0.395 |
| NFP ex-shutdown (49) | +$1,108 (+$23) | −$5,064 (−$103) | −$3,226 (−$66) | 0.335 |
| CPI (53, RULE_APPROX) | −$3,562 (−$67) | −$14,725 (−$278) | −$868 (−$16) | — |
| PCE (52, RULE_APPROX) | **+$14,620 (+$281)** | **+$49,539 (+$953)** | +$3,971 (+$76) | — |

Practically the entire CORE effect is the 35 FOMC sessions. NFP is null. **PCE sessions are
strongly POSITIVE for every object** — reported here with the same prominence as the negatives.
Adding CPI+PCE to the calendar shrinks the event-day P&L share from −12.7% to −7.2% (A) and
from −12.1% to −1.0% (B-NQ); adding the UNVERIFIED class shrinks it further to −1.6% (A) and
**flips B-NQ positive to +4.4%**.

Note that FOMC days are *not* the big single-day losers: **0 of the worst 10** sessions are FOMC
days for Product A or BEST_ONE_NQ. FOMC shows up as a persistent mean drag (~−$651 to −$931 per
session), not as tail risk.

### 2c. Robustness — the ±1-session dilation is the finding that should worry you

| object | CORE net | DILATED (CORE ± 1 session, 234) net | share |
|---|---|---|---|
| Product A | −$22,520 | **+$14,993** | +8.46% |
| BEST_ONE_NQ | −$36,767 | **+$6,708** | +2.21% |
| BEST_ONE_MNQ | −$8,408 | −$1,595 | −5.52% (placebo p 0.109) |

The sessions immediately adjacent to CORE event sessions are strongly *positive*, enough to flip
the sign for two of three objects. Two readings, both true: (a) the effect is confined to the
exact release sessions rather than being a diffuse "event week" phenomenon; (b) **the result is
therefore load-bearing on date precision, and the dates driving it (FOMC) are `RECALL` tier, not
verified.** If the FOMC dates were systematically off by one session the sign would flip. They
are almost certainly not — 8 meetings/yr on a widely-referenced published calendar is the
easiest of the four series to get right — but this is stated so it is not discovered later.

### 2d. Per year (CORE calendar) — full table in `out/v1f_event_attribution_by_year.csv`

| object | year | sessions | event | net (all) | net on event days | event share of net | event share of LOSS $ | worst-10 hits (exp) | worst day of year on an event day? |
|---|---|---|---|---|---|---|---|---|---|
| Product A | 2022 | 258 | 20 | +$46,852 | −$12,377 | −26.4% | 12.2% | 1 (0.78) | no |
| Product A | 2023 | 258 | 20 | +$16,962 | −$4,774 | −28.1% | 13.0% | 4 (0.78) | no |
| Product A | 2024 | 259 | 20 | +$32,603 | −$3,630 | −11.1% | 12.0% | 1 (0.77) | **yes** |
| Product A | 2025 | 258 | 17 | +$68,933 | −$15,568 | −22.6% | 13.3% | 1 (0.66) | no |
| Product A | 2026† | 106 | 4 | +$11,965 | **+$13,830** | **+115.6%** | 2.3% | 0 (0.38) | no |
| BEST_ONE_NQ | 2022 | 258 | 20 | +$115,029 | −$12,235 | −10.6% | 11.0% | 1 (0.78) | no |
| BEST_ONE_NQ | 2023 | 258 | 20 | +$26,731 | −$10,179 | −38.1% | 15.0% | 3 (0.78) | **yes** |
| BEST_ONE_NQ | 2024 | 259 | 20 | +$72,277 | −$1,871 | −2.6% | 10.8% | 1 (0.77) | no |
| BEST_ONE_NQ | 2025 | 258 | 17 | +$89,460 | −$31,120 | −34.8% | 12.7% | 2 (0.66) | no |
| BEST_ONE_NQ | 2026† | 106 | 4 | −$47 | **+$18,638** | n/m‡ | 2.1% | 0 (0.38) | no |
| BEST_ONE_MNQ | 2022 | 258 | 20 | +$9,878 | −$3,763 | −38.1% | 15.3% | 3 (0.78) | no |
| BEST_ONE_MNQ | 2023 | 258 | 20 | +$6,347 | −$1,574 | −24.8% | 17.9% | 4 (0.78) | **yes** |
| BEST_ONE_MNQ | 2024 | 259 | 20 | +$2,550 | −$34 | −1.3% | 8.4% | 1 (0.77) | no |
| BEST_ONE_MNQ | 2025 | 258 | 17 | +$13,544 | −$4,763 | −35.2% | 16.8% | 3 (0.66) | **yes** |
| BEST_ONE_MNQ | 2026† | 106 | 4 | −$3,418 | **+$1,727** | −50.5% | 2.2% | 0 (0.38) | no |

† 2026 is a **partial year** (2026-01-02 → 2026-05-29, 106 sessions) with only 4 CORE event
sessions, and **all four are NFP** (2026-02-06, 2026-03-06, 2026-04-03, 2026-05-08). The three
2026 FOMC dates are `UNVERIFIED` tier and therefore excluded from CORE by construction.
‡ share flagged `pnl_share_meaningful=False` in the CSV — the denominator (−$47) is noise.

The sign is consistent across **2022–2025 for all three objects** (negative event-day net every
year, event-day loss share 8–18% against a 6.6–7.8% base rate) and **reverses in the partial
2026 stub for all three**. The 2026 reversal is **not** a contradiction of §2b: the CORE effect is
entirely FOMC, and 2026's CORE set contains **zero FOMC sessions** — it is four NFP sessions, and
NFP is the null/positive series. The reversal is an artifact of the provenance tiering, not new
evidence against the FOMC pattern. Four consistent full years is still only a suggestive
in-sample regularity, not an established effect.

---

## 3. THE LEVERAGE QUESTION — the answer is unambiguous and negative

### Convention (taken from the existing committed maps, unchanged)

`runs/PRODUCTB_ONECONTRACT_FINAL/out/capital_map_{nq,mnq}.csv` have columns
`stress_mult, method, thr, p95_maxdd_dollar, capital_needed`, 60 rows each = 4 stress multipliers
(1.0/1.25/1.5/2.0) × 3 bootstrap methods (L5/L20/stat60, 2,000 paths) × 5 drawdown tolerances
(thr = 0.10…0.30), with `capital_needed = p95_maxdd_dollar / thr` for **one unit** of the product.
At capital *C*, DD-based sizing supports `floor(C / capital_needed)` units.

For Product A no committed map exists, so one was built with the **identical function body,
grids and seed** (`out/v1f_capital_map_productA.csv`). Product A's unit is one copy of the
master, whose **peak physical size is 11 MNQ** (measured on `smm_v2_bars.csv`; also 11 on CORE
event sessions), so its margin per unit is 11 × the per-contract rate.

Margin per unit — NQ day $1,000 → **$4,000 at 4X**, initial $43,433.67; MNQ day $100 → **$400 at
4X**, initial $4,343.38.

### Does the multiplier even touch the book? Yes — DIRECT measurement

`out/v1f_release_exposure_productA.csv`. Product A is **not flat at the release instant**:

| window | sessions | non-flat at T | mean abs pos at T | max abs pos at T | max abs pos in [T−15m, T+60m] |
|---|---|---|---|---|---|
| FOMC 14:00 ET | 35 | **100.0%** | 3.31 MNQ | 8 | 9 |
| NFP 08:30 ET | 53 | 79.2% | 2.25 MNQ | 7 | 8 |

So the 4X policy applies to a live position essentially every FOMC. The question is only whether
the resulting margin requirement is anywhere near binding. It is not.

### The binding constraint — result: **drawdown-based sizing, in 60 of 60 rows, for all three objects**

| object | DD capital per unit, loosest row → tightest row | margin/unit 1X | margin/unit **4X** | margin/unit initial | DD ÷ 4X margin | rows where margin binds |
|---|---|---|---|---|---|---|
| BEST_ONE_NQ (1 NQ) | $273,189 → $2,183,540 | $1,000 | **$4,000** | $43,434 | **68.3× → 545.9×** | **0 / 60** |
| BEST_ONE_MNQ (1 MNQ) | $39,812 → $311,050 | $100 | **$400** | $4,343 | **99.5× → 777.6×** | **0 / 60** |
| Product A (11 MNQ) | $96,097 → $1,058,921 | $1,100 | **$4,400** | $47,777 | **21.8× → 240.7×** | **0 / 60** |

*loosest row = stat60 / thr 0.30 / stress 1.0; tightest = L5 / thr 0.10 / stress 2.0.*

**Which binds first at each capital level in the existing map: drawdown, at every single level,
by roughly two orders of magnitude.** There is no crossover to report because none exists.

Maximum contract count the map supports on event days — 4X vs 1X (`out/v1f_capital_grid.csv`):

| object | capital | units by DD sizing (min / median / max over the 60 map rows) | units at 1X margin | units at **4X margin** | binding |
|---|---|---|---|---|---|
| BEST_ONE_NQ | $1,000,000 | 0 / 1 / 3 | 1,000 | 250 | drawdown |
| BEST_ONE_NQ | $2,500,000 | 1 / 3 / 9 | 2,500 | 625 | drawdown |
| BEST_ONE_NQ | $10,000,000 | 4 / 14 / 36 | 10,000 | 2,500 | drawdown |
| BEST_ONE_MNQ | $100,000 | 0 / 1 / 2 | 1,000 | 250 | drawdown |
| BEST_ONE_MNQ | $1,000,000 | 3 / 10 / 25 | 10,000 | 2,500 | drawdown |
| Product A | $1,000,000 | 0 / 3 / 10 | 909 | 227 | drawdown |
| Product A | $5,000,000 | 4 / 17 / 51 | 4,545 | 1,136 | drawdown |

Margin utilisation at median DD sizing, **even at the 4X rate**, is 0.3%–1.5% of capital.

### How far from binding? Three ways of saying the same thing

1. **Breakeven margin multiplier** — the multiple of the *standard* day rate at which margin
   would first bind: **273× (NQ)**, **398× (MNQ)**, **87× (Product A)**. The stated policy is 4×.
2. **Breakeven drawdown tolerance** — the `thr` at which DD-based capital would fall to the 4X
   margin requirement: **20.5 (NQ)**, **29.9 (MNQ)**, **6.55 (Product A)** — i.e. a policy of
   tolerating a drawdown of 2,049% / 2,986% / 655% of capital. The map's loosest row is 0.30.
3. **Notional leverage.** At the median dev session close (20,119.25) an NQ contract is $402,385
   notional and an MNQ $40,238. DD-based sizing tops out at **1.47× (B-NQ)**, **1.01× (B-MNQ)**,
   **4.61× (Product A)** notional-to-capital. 4X day margin permits **100.6×**. DD sizing runs at
   1.0%–4.6% of what the multiplier allows.

**Even INITIAL (overnight) margin does not bind** — DD capital ÷ initial margin ranges from
6.29× (NQ) and 9.17× (MNQ) down to **2.01× (Product A at its loosest row)**. Product A is the
closest any object gets to a margin wall, and it is still 2× clear of the *initial* rate and 22×
clear of the 4X *day* rate.

**INFERENCE (not measured):** a portfolio running all three objects simultaneously would sum
margin but partially diversify drawdowns. Since every object individually clears 4X day margin by
21×–778×, no plausible combination flips the answer.

### Worst-case stack: event day AND initial-margin-window breach

Three dev sessions are **both** a genuine holiday early close (the V1e initial-margin breach) and
a CORE event session: **2023-04-07** and **2026-04-03** (Good Friday, 09:15 ET close, NFP at
08:30) and **2025-07-03** (13:15 ET close, NFP pulled forward off Independence Day). On these the
object is inside the initial-margin window on a day the broker may also have raised intraday
margin. This is the single worst margin configuration in the dev window and it *still* does not
bind (initial-margin ratio ≥ 2.01×). It belongs in the C4 compliance narrative as an exposure
case, not as a leverage constraint.

---

## 4. DOES THIS PROMOTE BACKLOG ITEM B6?

**On the margin channel: NO. Plainly no.** B6 (scheduled-event selectivity recalibration) is
**not** promoted from an optional idea to a feasibility constraint by the 4X policy. The
constraint is not close to binding — it is 21× to 778× away from binding across every row of
every capital map, and would require a 87×–398× margin multiplier rather than the stated 4×.
A strategy sized to survive its own drawdown distribution is sized far below anything the margin
schedule cares about. **The 4X event-day multiplier is not a leverage constraint for these
objects at any capital level in the existing maps.** That is the answer to the question asked,
and it is a null result.

**On the P&L channel: not established either, and the case is weaker than it first looks.**
The event-day P&L evidence (§2) is real but modest and heavily qualified:
* it is **entirely FOMC** — 35 sessions, mean −$651/−$931/−$151 per session — with NFP null and
  PCE **positive**;
* it is a **mean drag, not tail risk**: 0 of the worst-10 sessions are FOMC days for Product A or
  BEST_ONE_NQ, and worst-10/worst-25/bottom-1% concentration is insignificant for both;
* it **flips sign for two of three objects** under a ±1-session dilation, so it is load-bearing on
  `RECALL`-tier dates;
* the strongest version of it is on **BEST_ONE_MNQ, the object with the confirmed exit defect**;
* the three objects share one signal, so these are ~one test, not three;
* it is **in-sample on the dev window**, and acting on it would introduce a new tuned parameter
  (which events, what window, flat-or-reduce) into a program whose own findings say ensembles
  beat parameter selection.

**Recommended disposition:** B6 stays an *optional research idea*, not a feasibility constraint,
and if it is ever run it should be run as a **FOMC-only, pre-registered, zero-free-parameter
flat-through-14:00 test** with the ±1-session dilation and the PCE-positive result as
pre-declared falsifiers — not as a general "scheduled-event selectivity" search. Any such test
costs alpha budget; the margin argument does not buy it a free pass.

---

## 5. INCIDENTAL FINDINGS (reported, not hidden)

1. **CONFIRMS spec.yaml V1e's holiday count.** Independently: 44 dev sessions have a last bar
   before 17:00 ET — 2 @ 09:15, 1 @ 09:30, 31 @ 13:00, 9 @ 13:15, and 1 @ 14:03. The 14:03 one
   is **2023-04-05**, a data-gap pseudo-session, not a scheduled early close. Excluding it gives
   exactly **43 = 31 + 9 + 2 + 1**, matching the spec's V1e figure.
2. **`parity_daily_aligned.csv` col `nt` carries a session-bucketing artifact at
   2023-04-05/06**: +$129,340.30 / −$126,974.10 (pair sum +$2,366.20) against twin values of
   +$600.70 / +$1,358.20. These are the only two dev sessions where |nt − tw| exceeds $1,562.
   `runs/SMV2Q_DIAGNOSTICS/smv2q.py` already established the house convention ("merge the
   2023-04-05/06 data-gap boundary pair"); this script follows it and **exactly reproduces
   `nt8_dev_battery.csv`** (net 177,315.09999995603 / daily_vol 2,109.4522724752574 / Sharpe
   1.1715277061807747 / maxDD_eod 18,894.300000003248) — confirming the committed Product A
   battery was itself computed on the merged series. **Caution for future work:** on the *raw*
   column maxDD_eod is **$129,916.90** and Sharpe **0.428**; any bootstrap capital map built on
   the raw column is badly contaminated (it inflated Product A's minimum DD capital per unit from
   $96,097 to $464,507 in an intermediate run of this script). Both variants are carried through
   the whole analysis as separate objects so the effect is visible.
3. One BEST_ONE_MNQ trade (exit 2023-04-05 17:00) needs the calendar-date fallback — the same
   single unmapped exit already recorded in the committed `parity_mnq.json`
   (`n_nt_trades_sessdate_unmapped: 1`). Handled identically to the committed script.

---

## 6. FILES WRITTEN

| path | contents |
|---|---|
| `runs/W17_C4_COMPLIANCE/src/v1f_eventdays.py` | the script (deterministic, seed 20260809) |
| `runs/W17_C4_COMPLIANCE/src/v1f_event_calendar.csv` | **the auditable calendar** — 194 rows, `date,series,tier,ref_period,basis` |
| `runs/W17_C4_COMPLIANCE/V1F_EVENTDAY.md` | this report |
| `runs/W17_C4_COMPLIANCE/out/v1f_event_attribution.csv` | full attribution × 4 objects × 8 calendars |
| `runs/W17_C4_COMPLIANCE/out/v1f_event_attribution_by_year.csv` | per-year table |
| `runs/W17_C4_COMPLIANCE/out/v1f_event_attribution_by_series.csv` | FOMC / NFP / CPI / PCE split |
| `runs/W17_C4_COMPLIANCE/out/v1f_release_exposure_productA.csv` | position size at the release instant |
| `runs/W17_C4_COMPLIANCE/out/v1f_capital_map_productA.csv` | Product A map, same convention as the committed B maps |
| `runs/W17_C4_COMPLIANCE/out/v1f_leverage_binding.csv` | 180 rows: DD capital vs 1X / 4X / initial margin per map row |
| `runs/W17_C4_COMPLIANCE/out/v1f_capital_grid.csv` | contract counts by capital level, 1X vs 4X vs DD |
| `runs/W17_C4_COMPLIANCE/out/v1f_leverage_summary.csv` | the binding-constraint summary |
| `runs/W17_C4_COMPLIANCE/out/v1f_summary.json` | machine-readable digest |

Nothing was deleted, overwritten, or rewritten. No NT8/CrossTrade tool was used. No commit was
made.
