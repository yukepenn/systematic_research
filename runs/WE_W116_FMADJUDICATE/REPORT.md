# WE_W116 — FOLLOW_MORNING, adjudicated under the new regime doctrine · REPORT

Preregistered (`spec.yaml`, committed at `5bd8b22` before any code was written).
POST-W115 owner directive §§4, 5, 22, 23, 29, 33, 41, LANE 2. `W116b` corrects **this wave's own
selection bar** and was run before anything was reported.

> ## **THE VERDICT SPLITS, and that is the answer.**
> ## **STANDALONE: it survives everything.** The selection objection is now **retired** — properly constructed, the conservative best-of-15 bar is **$166** and the object earns **$179, at the 96.3rd percentile**, while sitting at the **53rd percentile of its own plateau.**
> ## **PORTFOLIO: it FAILS, and the preregistered falsifier fires.** On weeks the combined book loses, it contributes **$66 against a chance-alignment $842 — the 9.9th percentile.** Its worst-decile overlap with the book sits at the **95.8th**. The thing you would add it *for* is precisely the thing it does not do.
> ## **Classification: `CURRENT_REGIME_UNEXPLAINED` · CHALLENGER / WATCHLIST · NOT an active component.**

## 1. The causal ledger, and the nineteen-minute gap

| anchor | present on |
|---|---|
| bar 571 **OPEN** = the 09:30:00 print (true RTH open) | 99.4 % |
| bar 689 **CLOSE** = 11:29 — the *information* anchor | 99.3 % |
| bar 709 **OPEN** = the 11:48:00 print — the *fill* | 99.3 % |
| bar 944 **CLOSE** = 15:44 — the *exit* | 95.8 % |

Bars 690–708 (11:30–11:48) **exist** — 19,988 of them in window — and are **not used**. That gap was
inherited from W108's LANE C geometry, not designed. Verified with teeth:

| probe | result |
|---|---|
| corrupt bars 690–708 → does the 11:29-anchored direction change? | **NO — the gap is genuinely unused** |
| the same corruption → does an 11:48-anchored direction change? | **YES — the probe is live** |

**And the gap costs nothing.** Direction from the fresher 11:48 close gives **$183/trade at 4.89 pp**
against the primary's **$179 at 4.95 pp** — a different rule, reported as a diagnostic, **not**
substituted for the primary. There is no hidden edge in those nineteen minutes.

### Provenance (§4)

`11:48` first appears in a committed spec in `runs/WE_W108_REVRANGE/spec.yaml`, as the decision
minute for **six fade mechanisms**. FOLLOW_MORNING did not exist as an object then — it first
appears as a **control** at that inherited geometry in W111b. **No wave ever selected the minute by
comparing FOLLOW_MORNING outcomes across minutes.** From here on the object is described as
**zero-threshold and parameter-light with a broad timing plateau**, never "zero parameter".

## 2. ⚠️ I made W99's mistake again — and correcting it flips the sub-test

W116's conservative best-of-15 null drew an **independent** random sign vector for each of the
fifteen timing cells. But those cells are the **same rule at neighbouring minutes on the same
sessions**. Independent signs destroy their correlation and inflate the maximum.

> This is precisely the error W99 made, which I recorded in the discipline notes as *"the control
> permuted each rule independently, destroying cross-rule correlation and inflating the null above
> the real value."* **Recorded again rather than quietly fixed.**

**Measured:** mean pairwise correlation of the fifteen cells' per-session P&L is **+0.800**
(range +0.584 to +0.973) → **effective independent cells = 1.23**, not 15.

| null construction | p95 bar | real | |
|---|---|---|---|
| single cell (W114, W116) | $129 | $179 | **CLEARS** (98.6th) |
| best-of-15, **independent** signs — *wrong* | $215 | $179 | ~~FAILS~~ |
| **best-of-15, shared per-session sign — correct** | **$166** | **$179** | **CLEARS (96.3rd)** |

### The plateau as a distribution, not a maximum

| min | p25 | median | p75 | max |
|---|---|---|---|---|
| $82 | $150 | **$166** | $184 | $196 |

> The preregistered cell is **$179 — the 53rd percentile of its own plateau.** **8 of 15** cells
> clear the corrected conservative bar; **12 of 15** clear the single-cell bar. A cherry-picked
> artifact sits at the top of its plateau with its neighbours near zero. **This one sits in the
> middle.** The selection objection is retired.

## 3. The dashboard — every standardised window, together (§33)

| window | N | $/trade | **edge pp** | hit % | net $ | wk $ | pos wk % | max DD | CVaR5 |
|---|---|---|---|---|---|---|---|---|---|
| t3m | 62 | $661 | **+7.79** | 58.1 % | $41,010 | $2,929 | 50.0 % | $7,972 | −$6,339 |
| t6m | 125 | $564 | +5.34 | 55.2 % | $70,465 | $2,610 | 55.6 % | $14,749 | −$5,669 |
| **t12m** | 249 | $236 | **+2.87** | 53.0 % | $58,699 | $1,108 | 49.1 % | $33,114 | −$5,621 |
| YTD 2026 | 144 | $487 | +4.24 | 54.2 % | $70,177 | $2,264 | 51.6 % | $14,749 | −$5,567 |
| prior yr 2025 | 246 | $205 | +6.20 | 56.1 % | $50,377 | $951 | 50.9 % | $41,091 | −$6,459 |
| t24m | 495 | $206 | +4.52 | 54.5 % | $102,122 | $973 | 49.5 % | $43,554 | −$6,479 |
| **2022-current** | 1,009 | **$179** | **+4.95** | 55.0 % | $180,651 | $844 | 54.2 % | $43,554 | −$5,401 |
| *2006–2021 (diagnostic)* | 3,923 | −$9 | **−0.74** | 49.4 % | −$33,784 | | | | |

⚠️ **t3m and t6m sit inside the BURNED span** (2026-05-31 → 07-31) and are not independent evidence.
**t12m (+$236, +2.87 pp) is the defensible recent figure**, and it is the *weakest* recent window.

**Costs:** $189 / $179 / $169 / $159 at 0×/1×/2×/3× spread — it dies at roughly 18× the measured
spread. **Controls:** always-long $21, always-short −$50, fade −$208, matched-random −$16 (p95 $127).
**Concentration:** median +$166, 5 %-trimmed +$138, skew 2.80, worst −$16,354, top-20 110.5 %.

### ⚠️ Correcting W115's framing, from a few hours ago

W115 §5 wrote that the accuracy edge *"has been DECLINING within the modern window"*, inferred from
modern-era quintiles of the calendar null drivers. **The per-year table does not support that as
stated:**

| year | N | E∣move∣ | $/trade | **edge pp** |
|---|---|---|---|---|
| 2022 (H2) | 126 | $1,649 | $379 | **+11.47** |
| 2023 | 244 | $1,346 | $73 | +4.38 |
| 2024 | 249 | $1,492 | −$22 | **+1.33** |
| 2025 | 246 | $1,998 | $205 | +6.20 |
| 2026 | 144 | $2,321 | $487 | +4.24 |

> **The "decline" is dominated by an exceptional 2022 half-year.** From 2023 on the edge oscillates
> between +1.33 and +6.20 pp with **no trend**. W115's directional claim is **narrowed**: what is
> true is that 2022 was exceptional and that **dollars per trade have risen while the accuracy edge
> has not** — E∣move∣ went $1,649 → $2,321, so $487/trade in 2026 comes from a *smaller* edge than
> $379/trade did in 2022. That distinction stands and matters; the word "declining" does not.

## 4. ⭐ Marginal portfolio value — where it fails

| book | convention | wk $ | max DD | **wk$@fixDD** | pos wk % | CVaR5 | t |
|---|---|---|---|---|---|---|---|
| P1/PCT | — | $1,394 | $22,931 | $1,230 | 56.3 % | −$6,231 | 4.16 |
| **P1/PCT + XM** | inv-vol | $1,142 | $11,489 | **$2,012** | 59.2 % | −$4,737 | **4.90** |
| P1/PCT + XM + FOLLOW | inv-vol | $1,063 | $10,323 | **$2,085** | 62.9 % | −$4,364 | 4.58 |
| **P1/PCT + XM** | income | $1,105 | $12,533 | **$1,785** | 60.1 % | −$4,971 | 4.74 |
| P1/PCT + XM + FOLLOW | income | $999 | $13,538 | **$1,494** | 61.5 % | −$5,312 | 3.94 |

> **Incremental fixed-DD from adding FOLLOW: +$74/wk (inverse-vol) and −$291/wk (income-matched).
> The RANGE straddles zero.** Two reasonable conventions disagree *in sign*, which is exactly the
> situation the campaign's own rule says must be quoted as a range and never at the better one.

### Downside behaviour vs the combined book — 1,000-shift circular null

| statistic | REAL | null mean | null p95 | percentile |
|---|---|---|---|---|
| ρ, all weeks | +0.253 | −0.001 | +0.120 | **100.0th** |
| ρ ∣ book losing | −0.090 | +0.001 | +0.153 | 16.5th ✅ |
| P(FM<0 ∣ book<0) | 0.506 | 0.460 | 0.529 | 83.5th |
| **worst-decile overlap** | **0.023** | 0.011 | **0.019** | **95.8th** ❌ |
| **$ FM earns on book-losing weeks** | **+$66** | **+$842** | +$1,792 | **9.9th** ❌ |
| tail beta in book's worst decile | −1.853 | +0.009 | +1.535 | 2.4th ✅ |

> ### **The preregistered falsifier fires.** The spec said the object does not enter the active book if *"its downside overlap with the combined book is worse than the 95th percentile of the circular-shift null."* Worst-decile overlap is at the **95.8th**.
> ### And the economically decisive line is the one below it: **on weeks the combined book loses, FOLLOW contributes $66 — against $842 from a random re-alignment of its own returns.** It is not there when it would be needed.
>
> Contrast `XM_CONFLICT`, which is in the book precisely because it *does* pass this test: ρ∣P1<0 at
> the **5.2nd** percentile, worst-decile overlap at the **7.1st** (W110). **XM diversifies losses.
> FOLLOW diversifies wins** — ρ +0.253 overall at the 100th percentile, and nothing when it counts.

## 5. Decision — classification and book status

| axis | verdict |
|---|---|
| **REGIME** | **`CURRENT_REGIME_UNEXPLAINED`** — strong current evidence; 2006–2021 fails on *behaviour* not cost (W114); **W115 found no causal driver**, so per §14 regime-death detection is weaker and monitoring must come from the object's own statistics |
| **STANDALONE ALPHA** | **CONFIRMED.** Clears the single-cell null (98.6th) *and* the correctly-constructed conservative best-of-15 bar (96.3rd); mid-plateau; two-sided; beats every simple control; dies only at ~18× spread |
| **PORTFOLIO ROLE** | **NOT AN ACTIVE COMPONENT.** Falsifier fired on downside overlap; contribution on book-losing weeks at the 9.9th percentile; incremental fixed-DD range **−$291 to +$74** straddles zero |
| **BOOK STATUS** | **CHALLENGER / WATCHLIST** |

**W114's `REGIME_LOCAL` verdict is `SUPERSEDED BY DOCTRINE`, not withdrawn on evidence.** The
measurement was correct; the owner has replaced the rule that converted it into a demotion. Under
the new doctrine the object is *not* demoted for failing 2006–2021 — **it is held out of the book
for a completely different and current reason: it does not diversify the book's losses.**

**What would change the verdict**, recorded now so it cannot be invented later:

1. **Forward evidence** on sealed ≥2026-08-01 data — the rule is parameter-light and needs no refit.
   Already in `MONITORING_CALENDAR.md`.
2. **A different pairing.** It fails against *this* book. Its ρ with P1 is +0.279 because P1 is a
   trend engine; against a genuinely mean-reverting or short-biased engine the answer could differ.
   That is a portfolio question, not an alpha question.
3. **It does NOT get another timing wave, another anchor, or a conditional variant.** §23 and §39
   are explicit, and W115 already spent the family's one attribution wave.
