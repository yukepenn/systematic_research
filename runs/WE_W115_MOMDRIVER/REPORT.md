# WE_W115 — why did intraday momentum strengthen? · REPORT

Preregistered (`spec.yaml` + **AMENDMENT 1**, both committed at `8a18d71` before any result existed).
POST-W115 owner directive §§9–14, LANE 1.

> ## **NO DRIVER IDENTIFIED. Every one of the three preregistered failure conditions fired.**
> ## And the hypothesis failed at its *premise*: **late-session volume share did not rise over twenty years — it FELL, 0.1738 → 0.1464.** The market-structure story everyone assumes is, on NQ 1-minute data, **factually backwards.**
> ## ⭐ **The finding that outranks the verdict:** measured in *accuracy points above p\**, the FOLLOW_MORNING edge is **DECLINING inside the modern era** even while its dollars per trade rise. W114 saw dollars and read "strongest year is 2026". Both are true — and the accuracy read is the one that matters for regime health.

## 0. The causality check fired, and the defect was the check

The first version corrupted **every** traded session at once and asked whether each session's driver
moved. Of course it moved — session *i*'s window covers *i*−60…*i*−1, most of which were also
corrupted. It reported LEAKAGE on all three drivers. **The check was wrong, not the drivers.**

Replaced with two tests that have teeth, both of which pass on all three volume drivers:

| test | result |
|---|---|
| `driver[i]` **==** `mean(raw[i−60 : i])` — a window that strictly precedes *i* | ✅ |
| corrupt **one** session: `driver[i]` must not move | ✅ |
| the same corruption **must** move `driver[i+1]` (proves the probe is live) | ✅ |

## 1. ⚠️ The premise is false — late-session volume share FELL

No P&L in this table.

| block | sessions | **close share** | last/first hour | RTH vol (M) | NQ level |
|---|---|---|---|---|---|
| 2006–2010 | 1,418 | **0.1738** | 0.7054 | 0.261 | 5,187 |
| 2011–2015 | 1,307 | 0.1640 | 0.5861 | 0.198 | 6,695 |
| 2016–2019 | 1,035 | 0.1494 | 0.5340 | 0.264 | 9,705 |
| 2020–2021 | 519 | 0.1539 | 0.5721 | 0.380 | 15,705 |
| 2022–2023 | 517 | 0.1529 | 0.5731 | 0.476 | 16,620 |
| **2024–2026** | 670 | **0.1464** | 0.5450 | 0.421 | 23,594 |

> The passive-rebalancing / closing-auction story predicts the last hour taking a **larger** share of
> the session over twenty years. **On NQ futures it takes a smaller one** — 17.4 % → 14.6 %. Total
> RTH volume roughly doubled, but the *distribution within the session* moved the other way.
> **The hypothesis was dead before the economics were read.**

`V_CLOSE_SHARE` correlates **−0.642** with price level and **−0.601** with calendar year. It *is* a
calendar proxy — pointing the wrong way.

## 2. The primary

| | |
|---|---|
| `V_CLOSE_SHARE` pooled Q5−Q1 | **−6.06 pp** (wrong sign) |
| 2,000-permutation null | mean +0.03, sd 2.23, p95 +3.68 → **0.4th percentile** |
| null drivers' pooled spreads | PRICE_LEVEL **+8.47**, CAL_YEAR **+8.81**, TIME_IDX **+8.92** |
| volume driver larger than all three nulls | **False** |
| within-era spreads | OLD **−4.18 pp**, MODERN **+4.66 pp** → **sign flips** |

**VERDICT: NO DRIVER IDENTIFIED.** All three preregistered reasons fired at once.

## 3. ⭐ The within-era table — where the null drivers earn their keep

| driver | **OLD 2006–2022H1** Q5−Q1 | **MODERN 2022H2–2026** Q5−Q1 | same sign? |
|---|---|---|---|
| V_CLOSE_SHARE | −4.18 pp | +4.66 pp | ❌ |
| V_LASTHOUR_RATIO | −1.42 pp | +8.61 pp | ❌ |
| **SESSION_VOL_LEVEL** | **+7.87 pp** | **+7.05 pp** | ✅ |
| PRICE_LEVEL **[NULL]** | +7.93 pp | **−7.07 pp** | ❌ |
| CAL_YEAR **[NULL]** | +8.57 pp | **−2.45 pp** | ❌ |
| TIME_IDX **[NULL]** | +4.71 pp | **−5.07 pp** | ❌ |

> **The three null drivers reverse sign inside the modern era.** That is exactly what they were
> carried for: their large pooled spreads (+8.5 to +8.9 pp) are the **era effect itself**, nothing
> more. Amendment 1 added CAL_YEAR and TIME_IDX and they did their job.

**`SESSION_VOL_LEVEL` is the one variable with the pattern a real driver should have** — same sign,
similar magnitude in both eras (+7.87 / +7.05), and **nearly uncorrelated with the calendar**
(ρ +0.076 with CAL_YEAR, +0.102 with price level). It was preregistered as a **control**, with its
interpretation fixed in advance: *"if THIS orders the edge equally well, the story is participation
in general, not the close specifically."* It does. **So the story, if there is one, is about how
busy the session is — not about the close.**

## 4. …and the prequential arm kills it

Amendment 1 added this arm precisely because a descriptive quantile split is not a tradeable state.
Terciles from a **trailing 250-session causal quantile**, shifted one session — the only assignment
here that is fully out of sample.

| driver | LOW | MID | HIGH | **HIGH − LOW** |
|---|---|---|---|---|
| V_CLOSE_SHARE | +0.92 | +0.48 | +1.87 | +0.95 pp |
| V_LASTHOUR_RATIO | +1.17 | −1.26 | +3.10 | +1.93 pp |
| **SESSION_VOL_LEVEL** | +0.49 | +2.35 | +0.71 | **+0.23 pp** |
| PRICE_LEVEL [NULL] | +5.66 | +1.64 | +0.03 | −5.63 pp |
| CAL_YEAR [NULL] | −1.55 | +1.44 | +4.05 | +5.60 pp |

> **`SESSION_VOL_LEVEL` goes from +7.9 / +7.1 pp on descriptive quintiles to +0.23 pp on causal
> terciles.** Tercile-vs-quintile dilution would explain a drop to roughly +5.5 pp, not to zero.
> **When the state is assigned causally, the ordering disappears.** Rolling 250-session correlations
> agree: every volume driver sits at mean ρ ≈ 0.007–0.011 with 55–61 % of windows positive.

## 5. ⭐⭐ The finding that outranks the verdict

Amendment 1 corrected the primary statistic from the campaign's net-of-cost `hit` column to **raw
directional accuracy minus p\***, because p\* is *defined* as a break-even directional accuracy and
the two eras have E∣move∣ of $409 and $1,721. That correction is what makes the next line visible:

> ### Inside the modern era, the null drivers point **DOWN**: PRICE_LEVEL **+7.47 pp → +0.40 pp** from Q1 to Q5, TIME_IDX **+7.48 pp → +2.41 pp**, CAL_YEAR **+6.69 pp → +4.24 pp**.
> ### **The accuracy edge has been DECLINING within the modern window** — while W114's dollar-per-trade table showed 2026 YTD as the strongest year ($487/trade).
> ### Both are true. As NQ's level rose, E∣move∣ rose, so a *shrinking* accuracy edge still produced *more dollars per trade*. **Dollars flattered the object; accuracy did not.**

This is a **`TRANSITIONING / WATCH`** signal in the directive's §5 vocabulary, and it goes straight
into W116's classification as the single most important input. It is **not** a kill — the modern
edge is still positive in every quintile of every null driver — but "strongest year is 2026" can no
longer be quoted without the accuracy column beside it.

## 6. Decision

**NOTHING PROMOTED. NO DRIVER IDENTIFIED. The explanatory search STOPS here.**

1. Per the spec's own decision rule and directive **§39** (one clean attribution wave, then move on)
   and **§46** (a failed explanation does not falsify the object): **the momentum family is closed
   for mechanism work.** No fifth variable. No renamed variant.
2. Per **§14**, `FOLLOW_MORNING` becomes **`CURRENT_REGIME_UNEXPLAINED`** *if* W116 confirms current
   evidence is strong — and W116 must now weigh §5's `TRANSITIONING / WATCH` against it, given §5.
   **The absence of an observable driver means regime-death detection is weaker, and §34's health
   monitor has to be built from the object's own statistics instead.**
3. **New data fact for the census, recorded because it contradicts a widely-assumed story:**
   NQ's last-hour share of RTH volume **declined** from 17.4 % (2006–2010) to 14.6 % (2024–2026)
   while total RTH volume roughly doubled.
4. **Methodological, now binding:** a descriptive quantile split and a trailing-causal-quantile split
   are different instruments and can disagree completely. `SESSION_VOL_LEVEL` looked like the
   wave's one survivor at +7.9/+7.1 pp and is **+0.23 pp** the moment the state must be knowable in
   advance. **Any state variable proposed as tradeable must be assigned causally before it is
   quoted.**
