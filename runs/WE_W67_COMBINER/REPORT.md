> **THIS IS THE MOST IMPORTANT RESULT IN THE CAMPAIGN SINCE W50, AND IT IS ABOUT WHAT THE
> OBJECT ACTUALLY IS RATHER THAN ABOUT ANY IMPROVEMENT TO IT.**

# WE_W67 — THE COMBINER, DECODED · REPORT

Preregistered, with the algebraic prediction written into the spec **before** the run so the
wave could be wrong. Phase 1 is exact enumeration with no backtest; phases 2–3 are attribution.
**Nothing adopted — and the object's description in every prior wave is now wrong.**

---

## 1. Phase 1 — six inherited constants collapse to four numbers (`FACT`)

The combiner is `T → mm → Tp → M → hysteresis`, six magic numbers inherited from the vendor
(10.0, 1.25, 0.9026, ±13, 0.7086, 2.83), never examined in 66 waves. Its domain is small enough
to enumerate exactly. The entire chain reduces to **the number of members that must be net-long
to trigger an entry**:

| tilt agrees | B-MOM | **members net-long needed to ENTER** | fraction | to HOLD |
|---|---|---|---|---|
| no | 0 | **6 of 13** | 46.2 % | 2 of 13 |
| no | **+1** | **1 of 13** | **7.7 %** | 1 of 13 |
| yes | 0 | 5 of 13 | 38.5 % | 2 of 13 |
| yes | **+1** | **1 of 13** | **7.7 %** | 1 of 13 |

- **The ±13 clamp on Tp is DEAD CODE** — Tp reaches only ±11 at either member count.
- The prediction in the spec was right: **B-MOM agreement converts a 46 % consensus requirement
  into a 7.7 % one.** The single constant `2.83` is by far the largest lever in the combiner and
  it is hidden inside a chain of decimals.

Empirically: the tilt agrees on 37.5 % of bars, B-MOM is non-zero on 25.4 %. **Of the 1,805 bars
where the target turns long, B-MOM was long at 37.3 %**, and the median entry has only **5 of 13**
members agreeing — 10th percentile **1**.

## 2. Phase 2 — whose money is it (`FACT`)

A trade is **B-MOM-enabled** if the member consensus alone would not have cleared the entry
level at its entry bar:

| entry state | trades | share | net $ | **share of net** | $/trade | win % |
|---|---|---|---|---|---|---|
| **B-MOM ENABLED** (consensus insufficient) | 401 | 20.6 % | $83,083 | **27.6 %** | $207 | 41.9 % |
| member consensus sufficed | 1,541 | 79.4 % | $217,734 | 72.4 % | $141 | 36.8 % |
| … of which the tilt agreed | 990 | 51.0 % | $170,548 | 56.7 % | $172 | 36.2 % |

**By year, the B-MOM-enabled share of net:**

| 2022 | **2023** | 2024 | 2025 | **2026** |
|---|---|---|---|---|
| 9.9 % | **82.4 %** | 17.3 % | 45.9 % | **−16.6 %** |

**B-MOM carried the worst year and is now losing money.**

## 3. Phase 3 — the headline (`FACT`)

The B-MOM weight, from 0 (Solar only) to 4.2 (B-MOM alone clears the entry level):

| w_bmom | trades | **pts/session** | day + % | week + % | median week | weekly $ | mean top-5 DD | worst week |
|---|---|---|---|---|---|---|---|---|
| **0.00 — Solar only** | 1,841 | **7.26** | 20.5 | 53.9 | $153 | $891 | $15,020 | −$10,746 |
| 1.00 | 1,961 | 10.58 | 23.7 | 55.4 | $373 | $1,119 | $12,546 | −$8,008 |
| 2.00 | 1,986 | 13.41 | 26.0 | **58.8** | $311 | $1,117 | **$10,720** | **−$5,786** |
| **2.83 — the incumbent** | 1,942 | **14.86** | 27.6 | 58.3 | $455 | $1,475 | $14,266 | −$7,418 |
| 4.20 | 2,140 | 14.62 | **32.3** | 58.3 | **$880** | $1,429 | $15,689 | −$12,435 |

> ### `FACT`: **B-MOM contributes 51 % of the object's net.**
> Solar alone earns **7.26 pts/session**; the object earns **14.86**. The daily correlation
> between Solar-only and the object is 0.648.

And per year, Solar-only against the incumbent:

| | 2022 | 2023 | 2024 | 2025 | **2026** |
|---|---|---|---|---|---|
| Solar only | 5.31 | 3.27 | 5.66 | 10.95 | **14.32** |
| incumbent | 11.59 | 3.04 | 19.59 | 23.17 | **15.79** |
| **B-MOM's contribution** | +6.28 | −0.23 | **+13.93** | +12.22 | **+1.47** |

**B-MOM's contribution is collapsing**: +13.93 pts/session in 2024, +1.47 in 2026.

## 4. What this means, stated plainly

**Every prior wave in this campaign describes the object as "a selection-free majority vote over
32 long-only Solar-ratchet configurations". That description is wrong.** The object is a Solar
ensemble **OR-gated with B-MOM**, where B-MOM can trigger an entry on a single member out of
thirteen, and where B-MOM supplies **more than half the money**.

And this repo has independently judged B-MOM twice, without ever connecting it to P1:

- the scalping lab **PARKED B-MOM as REGIME-LOCAL**: PF 1.013 over the 16 unseen years
  2006–2021, against PF 1.215 in 2022–2026;
- **W57** measured its era split directly — t = 0.27 on 4,077 sessions pre-2022 against t = 2.66
  on 1,122 sessions after, with no causal regime variable separating them and a 60-cell scan
  indistinguishable from chance;
- **W58** found its latest 24-month window at the **98th percentile of its own 234-window
  history** — an exceptional run, not a durable edge.

> **So W57's conclusion was far more serious than it read at the time.** It was written as
> *"this repo holds no engine that diversifies P1"* — a statement about a candidate we might
> add. It is actually a statement about a component **we already depend on for half the net**,
> which is in-sample, regime-local, currently at the top of its own historical range, and
> **already contributing negatively in 2026**.

This is a **risk concentration to disclose**, not a parameter to optimise. `w_bmom` is not a
dial to tune — the sensible readings are:

- at **w = 2.00** the object gives up 10 % of production for a **25 % smaller mean top-5
  drawdown, a 22 % smaller worst week and a higher positive-week rate**, and leans less on the
  fragile half. Its cost is concentrated in 2023, the year B-MOM carried.
- at **w = 0** the object is 7.26 pts/session — which is what the Solar ratchet alone is worth,
  and is the honest floor if B-MOM's edge is a 4-year artifact.

Neither is adopted here. Both are now measured, which they were not an hour ago.

## 5. What was NOT found
The other five constants are inert or near-inert once the table in §1 is read: `0.9026`,
`0.7086` and the `×10` scaling cancel out of the decision, and `±13` is unreachable. **Only two
things in the combiner decide anything: the member-consensus threshold and the B-MOM weight.**
That is the useful part of decoding before scanning — four of six constants needed no experiment
at all.

## 6. Files
`out/combiner.txt` `out/combiner2.txt` `out/map.csv` `out/thresholds.csv` `out/states.csv`
`out/trade_states.csv` `out/arms.csv` ·
code `research/weekly_edge/src/run_we_w67.py`, `run_we_w67b.py`
