# DATAGATE — EVENT RESPONSE is CLOSED-BY-DATA at the decision surface

| | |
|---|---|
| **run class** | **AUDIT / ENGINEERING_ONLY** — no hypothesis tested, no feature fitted, no gate read |
| date | 2026-08-27 |
| reproduction | `research/weekly_edge/src/run_rr_datagate_event.py` → `out/datagate.txt` |
| provenance | RR_W001's preregistered continuation made EVENT RESPONSE the next wave. This is the coverage check run **before** writing its spec |
| precedent | the identical instrument closed the order-flow lane in `runs/DATAGATE_ORDERFLOW_20260827/` **before a feature was written** |

> ### **VERDICT: CLOSED-BY-DATA.** Event response can reach **7.18 %** of `P1/PCT`'s decision
> ### surface on **71** effective event sessions, where the minimum detectable effect is
> ### **9.8× the lane-scaled materiality bar**. This is a **calendar** constraint. No modelling
> ### choice moves it.

---

## 1. What the calendar holds

`research/04_complementary_family/c01_announcement_calendar.csv` — committed, seal-clean, 145 rows,
**129 in-window across 128 distinct sessions**.

| event | n in window | time ET | inside a 09:45 decision's information set? |
|---|---:|---|---|
| CPI | 48 | 08:30 | **yes** — lands pre-open |
| NFP | 48 | 08:30 | **yes** — lands pre-open |
| FOMC | 33 | 14:00 | **no** — lands after `XM_CONFLICT` has already decided |

## 2. Coverage of the decision surface

A response feature exists only *after* its event. That is the whole definition (directive §27), and
it is what bounds this lane.

| | | |
|---|---:|---:|
| in-window `P1/PCT` decisions | **2,131** | |
| … on a scheduled-event session | 267 | 12.53 % |
| … **and after that session's event time** | **153** | **7.18 %** ← the reachable surface |
| **distinct event sessions carrying ≥ 1 decision** | **71** | ← **the effective N** |

**Directive §20 is binding here:** twelve `P1/PCT` opportunities after one CPI print are **one** macro
event, not twelve. **71 is the sample size that governs every inference in this lane.**

For the one-shot experts it is worse. `XM_CONFLICT` has **29 of 346** taken decisions (8.38 %) on a
pre-open event session, and **FOMC is not in its information set at all** — its decision is at 09:45
and the release is at 14:00.

## 3. Minimum detectable effect

| | |
|---|---:|
| sd(action value), all decisions | $2,123.55 |
| **sd(action value), reachable subset** | **$2,852.24** ← event sessions are *more* volatile |
| book-wide materiality bar | $13.93 / decision |
| **lane-scaled bar** — the same total dollars earned on 153 decisions rather than 2,131 | **$194.06 / decision** |

> **The lane-scaled bar is the fair target.** A filter acting on 7.18 % of the book must move those
> decisions ~14× harder to deliver the same book-level improvement. Comparing this lane's MDE against
> the book-wide $13.93 would be a units error — the same one caught in RR_W001's G3.

| unit of inference | N | MDE (top-vs-bottom half) | vs lane bar |
|---|---:|---:|---:|
| decisions, treated as independent *(invalid — clustering ignored)* | 153 | $1,292.04 | 6.7× |
| **EVENT SESSIONS — the honest unit** | **71** | **$1,896.67** | **9.8×** |
| CPI/NFP sessions only (08:30) | 96 | $1,631.12 | 8.4× |
| FOMC sessions only (14:00) | 33 | $2,782.04 | 14.3× |

The MDE is for a **top-half vs bottom-half** split — the most generous two-group contrast available.
A quintile contrast, which is what a real feature would produce, is strictly worse.

**In standard-deviation terms: only effects ≥ 0.665 sd are detectable.** The lane is not literally
blind — it could detect an enormous effect. It cannot detect a **materially-sized** one, and that is
the question that matters.

## 4. What would make it askable

Against the lane-scaled bar the MDE is short by **9.8×**. Power scales with N, so the effective N
would have to rise by **≈96×** — from **71** event sessions to roughly **6,800**. At ~2.6 scheduled
events per month that is on the order of **220 years of additional calendar.**

> That figure is a **reductio, not a plan.** It is printed to make the shape of the problem explicit:
> **the binding constraint is the calendar**, and no feature engineering, model family or estimator
> moves it.

**The only lever that does not require waiting is more event TYPES** — PPI, retail sales, initial
claims, PCE, GDP, ISM, Treasury auctions. Roughly quadrupling the event count would bring the
effective N to ~280 sessions and the MDE to ~5× the bar: **better, still short.** That is a
data-acquisition question, not a research question, and it is recorded in `OWNER_QUEUE.md`.

## 5. What this does and does not close

**CLOSES:** event response as an **incremental router feature** at `P1/PCT`'s and `XM_CONFLICT`'s
decision events, with the calendar currently held. Marked **`CLOSED-BY-DATA`**, not `NULL` —
directive §20 requires `UNDERPOWERED / INCONCLUSIVE` rather than "no information exists", and the
distinction is the whole point of running this check first.

**DOES NOT CLOSE:** event response as a **standalone expert** (directive §29). That is a different
question with a different population — **96 CPI/NFP sessions and 33 FOMC sessions**. It is not
pursued here: at n = 96 one-shot decisions it is far smaller than `XM_CONFLICT`'s 346, which this
campaign already flags as its binding small-N caveat, and a search over event types, response windows
and directions on 96 rows would be a selection machine. **If it is ever run it needs its own spec, a
frozen single hypothesis, and no window search.**

**CONTEXT that bounds how much room was ever there:** W105b measured that `XM_CONFLICT` is *not* an
event trade — its 304 non-announcement trades earn **$408/trade at 54.9 %**. W110 measured the
announcement **flag** alone at **AUC 0.498**. Neither closes the *response* question, but neither
suggests a large effect was waiting.

## 6. Consequence for the campaign

The frontier's **row 1 is closed without a wave being run**, which is the point of a data gate: it
costs one afternoon instead of a full preregistered wave that could only have returned
`UNDERPOWERED`.

With this and RR_W001 together, **every information lane reachable from data this repo currently
holds is now measured and closed.** What remains is owner-gated acquisition (order flow, options) or
bounded engineering. `RESEARCH_FRONTIER.md` is re-ranked accordingly.
