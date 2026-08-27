# WE_W93 — NETFUSE_1 AS A CHALLENGER · REPORT

Preregistered (`spec.yaml`). Five conditions, all falsifiers written before the read.

> ## **4 of 5. C1 PASS · C2 PASS (on three nulls, including two I built to break it) ·
> ## C3 PASS · C4 FAIL · C5 PASS.**
> ##
> ## **The one it fails is the only genuinely out-of-sample test in the set.**
> ## On 2022–2026 this is the best-evidenced object this campaign has produced — the first
> ## ever to clear a specificity null, and it clears it at the **100th percentile**.
> ## Over the sixteen unseen years it **loses money** while P1 makes $79,076.
> ##
> ## **NOTHING IS ADOPTED.** Per the spec: no outcome adopts anything in this wave.

---

## The two challengers now fail on **opposite** axes, and that is the most useful thing here

| | specificity null | deep 16 years (risk) | deep 16 years (return) |
|---|---|---|---|
| **{BMOM + X9a} 2:3** (W86/W87) | **FAIL** — 92nd vs a 95th bar | **PASS** — top-5 DD 28.2 % smaller | positive |
| **NETFUSE_1** (this wave) | **PASS** — 98.5th–100th on 3 nulls | **FAIL** — 11.4 % vs a 25 % bar | **−$5,970** |

One is *specific but not durable*; the other is *durable but generic*. Neither is a champion.

---

## C1 `PASS` — the corrected rolling gate

Oracle battery first (W85's rule): all four strictly-dominant synthetic objects score
**ALL-THREE 100 %**. Gate USABLE.

NETFUSE_1 vs P1, 25 rolling 24-month windows, exposure-matched in contract-minutes
(scale 0.7001 — NETFUSE carries 314,308 contract-minutes against P1's 220,039), at W89's
candidate-specific costs:

| money | wk + % | raw top-5 DD | **ALL-THREE** |
|---|---|---|---|
| 76 % | **100 %** | 60 % | **60 %** |

Bar was > 50 %. **PASS.** Note `wk+% 100 %` — it beats P1 on positive-week rate in **every one of
the 25 windows**, which is the owner's first-ranked metric.

## C2 `PASS` — and the preregistered null turned out to be contaminated

The preregistered null (session-wise circular shift of the short book, re-netted) scored the
object at the **100th / 99.5th / 100th** percentile. That is the first specificity null this
campaign has ever cleared, so I audited it before believing it (`out/null_audit.txt`):

> ⚠️ **`CORRECTION` — the preregistered C2 null was contaminated.** In the real object the long
> and short votes **never both fire** (0 of 1,620,044 bars — they are the two signs of one
> ratchet state). A session-shifted short book has no such relationship, so it fires on top of
> long bars and the tie rule forces FLAT. Measured over 200 shifts: **46,820 collision bars on
> average, silently deleting 18.5 % of the short book.** The null was partly testing *"did I
> break the object"*, not *"is the alignment specific"*.

So two harder nulls were built and run:

**Null 2 — collision-free.** Shift the short book, then restrict it to bars where the long book
is silent, so mutual exclusivity is preserved and the tie rule can never fire:

| leg | real | null mean | null p95 | **percentile** |
|---|---|---|---|---|
| positive-week % | 58.69 | 51.88 | 55.87 | **99.0 %** |
| raw mean top-5 DD | $15,611 | $24,735 | $17,750 | **98.5 %** |
| weekly $ at fixed DD | $1,068 | $284 | $609 | **99.5 %** |

*(Residual handicap, stated: the collision-free nulls still carry a lower short firing rate —
12.49 % vs the real 15.59 % — because mutual exclusivity is exactly what the real construction
supplies and a shifted book cannot get it for free.)*

**Null 3 — the strongest available: hold the POSITION SCHEDULE completely fixed and randomise
DIRECTION.** 7,326 latched runs (3,368 long, 3,958 short) are identified in the real target
array and the multiset of run signs is **permuted across runs**. Same bars in a position, same
run lengths, same long/short counts — only *which run gets which sign* changes. This cannot
damage the structure at all:

| leg | real | null mean | null p95 | **percentile** |
|---|---|---|---|---|
| positive-week % | **58.69** | 46.15 | 53.05 | **100.0 %** |
| raw mean top-5 DD | **$15,611** | **$68,019** | $23,904 | **100.0 %** |
| weekly $ at fixed DD | **$1,068** | **−$47** | $47 | **100.0 %** |

> ## `FACT` — **with the schedule held fixed and only the directions shuffled, the object earns
> ## −$47/week at fixed drawdown against its real $1,068, and its top-5 drawdown quadruples
> ## from $15,611 to $68,019. The direction information is unambiguously real.**
>
> This is the cleanest answer this campaign has to the owner's question *"why can't we earn from
> short"*: **the short side carries genuine directional information**, and it is worth roughly
> the entire object.

## C3 `PASS` — walk-forward, with a flag

W29's protocol: refit `(halt, target)` quarterly on a trailing year over a 5 × 5 grid, trade only
the next quarter. 12 refits over 732 traded sessions:

| | wk$ @ fixed DD | weekly $ | wk + % |
|---|---|---|---|
| walk-forward | $1,174 | $1,707 | **61.5 %** |
| fixed quote | $1,282 | $1,480 | 59.5 % |

**Retention 92 %** (bar 80 %). **PASS.**

> ⚠️ **But choice churn is 64 % and the incumbent `(1300, 1000)` is chosen in 0 of 12 refits.**
> That is the same flag W78 raised (`w = 0.30` chosen 0/12). It does not fail the condition —
> retention is what the bar measures, and the alternatives chosen do about as well — but it means
> **the inherited constants are not special for this object**, and a trader refitting honestly
> would never have landed on them.

## C4 ⛔ `FAIL` — the sixteen unseen years

2006–2021, 4,279 sessions, frozen parameters, commission only (W82's $14.65 does **not**
transport to NQ 1,600–16,000):

| | trades | weeks | net $ | pts/session | wk + % | max DD | top-5 DD | worst week | streak |
|---|---|---|---|---|---|---|---|---|---|
| **NETFUSE_1** | **20,147** | 834 | **−$5,970** | **0.61** | 42.4 % | $33,322 | $16,773 | −$5,717 | 8 |
| P1 | 9,557 | 834 | **+$79,076** | 1.51 | 44.5 % | $39,555 | $18,925 | −$7,019 | 7 |

Top-5 drawdown **11.4 %** smaller (bar was ≥ 25 %). **FAIL.**

Per year, deep:

| | 2008 | 2013 | 2015 | 2016 | **2018** | **2019** | 2020 | **2021** |
|---|---|---|---|---|---|---|---|---|
| NETFUSE_1 | **+$2,303** | $179 | $1,881 | $1,234 | **−$4,315** | $1,693 | $23,787 | **−$5,375** |
| P1 | −$10,386 | $6,553 | $12,554 | $7,037 | **+$19,064** | **+$24,487** | $28,996 | **+$21,917** |

**Read honestly, two separate things fail here and they need separating:**

1. **The RETURN is deep-negative.** Under charter amendment 2 (b) — *old-era weakness is not
   disqualifying; requiring uniformity across the measurement window is itself a fit to the
   measurement window* — **this alone does not disqualify the object.** And it is mechanistically
   expected: W73 measured the short book fighting a **−$23,078 drift headwind**, and 2009–2021
   was a sustained bull market. A netted long+short object *should* underperform a long-only one
   there. It trades 2.1× as often for it.
2. **The DRAWDOWN GEOMETRY does not replicate, and that IS the condition.** C4 was written as a
   *risk* test precisely because return is regime-dependent and risk geometry should not be.
   W87 put the same bar on `{BMOM + X9a}` and it delivered **28.2 %**. NETFUSE_1 delivers 11.4 %.
   **The pair's drawdown advantage survives sixteen unseen years; NETFUSE_1's does not.**

## C5 `PASS` — top-k-day concentration

| drop best | full weekly $ | full wk + % | t24 weekly $ | t24 wk + % |
|---|---|---|---|---|
| 0 | $1,233 | 58.7 % | $1,583 | 58.1 % |
| 1 | $1,158 | 58.2 % | $1,430 | 57.1 % |
| 3 | $1,013 | 57.7 % | $1,137 | 56.2 % |
| **5** | **$883** | **57.7 %** | **$872** | **56.2 %** |
| 10 | $658 | 56.3 % | $689 | 55.2 % |

Positive on both horizons with its best five sessions removed, and the positive-week rate barely
moves. **PASS** — this is not a three-day object, which is what W76 caught in three others.

## Verdict and status

| condition | result |
|---|---|
| C1 corrected rolling gate | **PASS** (60 %, wk+% 100 %) |
| C2 specificity null | **PASS** (98.5th–100th on two harder nulls; the preregistered one was contaminated and is superseded) |
| C3 walk-forward | **PASS** (92 % retention; churn 64 %, incumbent constants chosen 0/12) |
| **C4 deep risk geometry** | **FAIL** (11.4 % vs a 25 % bar; deep return −$5,970) |
| C5 concentration | **PASS** |

**NETFUSE_1 remains a CHALLENGER and nothing is adopted**, per the spec's decision rule, which
binds under every outcome. What must travel with it:

- **it is not an independent stream** — weekly ρ +0.556 with P1, +0.719 with SHORT. It may never
  be counted in a census;
- **its trailing-12-month positive-week rate is 52.8 %** against its full-window 59.2 % — its
  best statistic is decaying like everything else in this campaign;
- **everything modern is in-sample.** SHORT, B-MOM, the delta gate and the five quality features
  were all specified on 2022–2026, and this campaign has no unspent forward window;
- **the deep result is the only unseen evidence and it is negative.**

## Files
`out/netfuse_challenge.txt` · `out/null_audit.txt` · `out/null_shift.csv` (superseded) ·
`out/null_shift_clean.csv` · `out/null_signperm.csv` · `out/null_damage.csv` ·
`out/walkforward.csv` · `out/concentration.csv` · `out/deep.csv` · `out/deep_per_year.csv` ·
`out/verdict.csv` · `out/series.csv` · code `run_we_w93.py`, `run_we_w93b.py`
