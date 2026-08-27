# WE_W96 — THE OVERNIGHT DISPLACEMENT CHANNEL, TRADED DIRECTLY · REPORT

Preregistered (`spec.yaml`). Every falsifier written before the read, including the one that says
what a *pass* on H2 would and would not mean.

> ## **H1 PASS (weakly) · H2 PASS (and it is structural, as the spec said in advance) ·
> ## H3 FAIL · H4 mixed and the rolling gate kills it.**
> ##
> ## **NIGHT is not a new stream. It fails its own specificity null at the 88th percentile
> ## against a 95th bar — the same null the incumbent B-MOM channel clears at the 100th.**
> ##
> ## Two facts worth keeping anyway: **its friction is $19.77/ctrRT, the worst in the library**,
> ## and **its SHORT leg loses $41,741.** The overnight short does not work; the RTH short does.

---

## 1. What was built

The displacement rule anchored at the **session open (18:01)**, with the slot-of-day statistic
computed over all bars so it is defined overnight, live only 18:00–09:29, latched per session,
traded directly with `sfills` — long and short, 1 contract, its own session box. **Not one
parameter chosen here**: the 14-session window, the anchor, the ±1 threshold and the box are all
inherited verbatim.

| | value |
|---|---|
| fires on | **61.46 %** of in-window bars (B-MOM: 25.69 %) |
| **bars where NIGHT and BMOM both fire** | **0 — disjoint by construction** |
| trades / net | 1,395 / **$103,433** |
| **LONG** | 702 trades, **+$145,174**, $206.8/trade, 40.5 % win |
| **SHORT** | 693 trades, **−$41,741**, **−$60.2/trade**, 34.3 % win |

## 2. `FACT` — it is the most expensive object in the library

Measured on its **own** contract-weighted fill distribution (W89's method — never assume the
champion's cost line):

> **3.953 ticks = $19.77 per contract round turn**, against BMOM's $12.99, X9a's $14.55 and P1's
> $14.52. At 6.55 ctrRT/week that is **$129/week of spread**.

It trades in the thinnest hours, and the thinnest hours cost the most. This was quoted before any
P&L, as the spec required.

## 3. `CORRECTION` to a suspicion of my own — the 18:00 concentration is NOT degeneracy

93 % of the net comes from positions entered in the **18:00 hour** (964 of 1,395 trades, i.e.
roughly one per session). I suspected the rule was degenerate there: at the session open
`|px − sessOpen|` is near zero, so the trailing-14-session mean at that slot should be near zero
too, and *any* move would cross it. **Measured, and it is false:**

| entry hour (ET) | median threshold `mtod` | median \|px − sessOpen\| | ratio |
|---|---|---|---|
| **18** | **16.39 pts** | 12.25 | **0.71** |
| 21 | 35.04 | 28.75 | 0.77 |
| 00 | 40.95 | 35.75 | 0.77 |
| 04 | 61.07 | 49.50 | 0.81 |
| 09 | 91.29 | 72.50 | 0.79 |

At the 18:01–18:05 slots the threshold is **10.75 points = 43 ticks** — the smallest of the night,
but nowhere near zero, and the displacement-to-threshold ratio at 18:00 (**0.71**) is the *lowest*
of any hour, so it is if anything **harder** to trigger there. The rule is well calibrated across
the whole session; the ratio sits in a tight 0.71–0.81 band for sixteen hours.

**The correct explanation is the latch**: the channel picks a direction early in the overnight
session and *holds* it. The entry timestamp is the first fire; the P&L is everything that follows.
**NIGHT is "take one position early in the overnight session and carry it".**

## 4. H1 `PASS`, weakly — the only chronology gate

| period | weeks | weekly $ | SE | **t** | wk + % | max DD |
|---|---|---|---|---|---|---|
| full | 213 | $356 | $346 | **1.03** | 50.2 % | $51,374 |
| **t24** | 105 | **$858** | $571 | **1.50** | 54.3 % | $32,456 |
| t12 | 53 | **$1,095** | $859 | 1.27 | **58.5 %** | $32,456 |

| | 2022 | 2023 | 2024 | 2025 | **2026** |
|---|---|---|---|---|---|
| NIGHT | **−$682** | **−$390** | $514 | $402 | **$2,099** |

It passes the gate (t24 > 0) and it is **overwhelmingly a 2026 object**. Under charter amendment
2 (b) the 2022–2023 losses are not disqualifying — but no horizon reaches t = 2, and a $51,374
full-window max drawdown against $356/week is not a tradeable shape.

## 5. H2 `PASS` — and it means exactly what the spec said it would mean

| vs | **weekly ρ** | daily ρ |
|---|---|---|
| P1 | **+0.020** | +0.103 |
| X9a | +0.193 | +0.182 |
| BMOM | **−0.163** | −0.062 |
| SHORT | +0.150 | +0.207 |
| NETFUSE_1 | +0.164 | +0.270 |

All five under 0.20 weekly. **But the honest reading was written before the read and it stands:**

> Temporal disjointness produces low ρ **by construction** — NIGHT and BMOM share **zero** firing
> bars. This is the **same mechanism on a different clock**, not a different mechanism. It counts
> for portfolio arithmetic; it is **not** evidence of independent information.

## 6. H3 ⛔ `FAIL` — it does not beat its own null

W72's session-shift null (200 shifts, preserving firing rate, latch run-lengths and intraday shape,
destroying only which session the path lands on) — the null the incumbent B-MOM channel clears at
the **100th percentile**:

| | real | null mean | null p95 | **percentile** |
|---|---|---|---|---|
| pts/session | 5.176 | 0.475 | **7.410** | **88.0 %** |

**Bar was ≥95th. It fails.** The channel makes money, and so does an arbitrarily reshuffled version
of itself often enough that 88 % is all it earns. **NIGHT is exposure to the overnight drive, not
a specific edge.**

## 7. H4 — passes the full-window table and fails the instrument that matters

Inverse-vol over three sleeves (BMOM 0.261 / X9a 0.399 / NIGHT 0.340), weight fixed in advance:

| | weekly $ | wk + % | max DD | top-5 DD | worst week | wk$ @ fixed DD |
|---|---|---|---|---|---|---|
| 2:3 pair (1 unit) | **$1,013** | **57.7 %** | $17,330 | $11,455 | −$8,692 | $1,183 |
| **+ NIGHT (inv-vol)** | $789 | 56.8 % | **$11,214** | **$9,411** | **−$6,209** | **$1,424** |

**2 of 3 full-window legs — and the corrected rolling gate says:**

| money | wk + % | top-5 DD | **ALL-THREE** |
|---|---|---|---|
| 20 % | 28 % | **100 %** | **12 %** |

(Oracle battery run first: all three oracles 100 %. Gate USABLE.)

> **The drawdown improvement is real and it is in 100 % of the 25 windows.** The money and the hit
> rate get *worse* in 72–80 % of them. **ALL-THREE 12 %.** This is the campaign's own standing
> meta-finding arriving on schedule: *full-sample dominance is nearly uninformative here; run the
> rolling test first.* Had I only produced §7's first table, this would have looked like a win.

## 8. Verdict

| | |
|---|---|
| H1 recency | **PASS** — t24 +$858/wk, t = 1.50. Weak, and almost entirely 2026 |
| H2 independence | **PASS** — all weekly \|ρ\| < 0.20, and **structural, not informational** |
| **H3 specificity** | **FAIL** — 88th vs a 95th bar |
| H4 portfolio | full-window 2/3, **rolling gate ALL-THREE 12 %** |

**NIGHT is not adopted and is not a candidate stream.** It goes to `PARKED_NOT_DEAD` with its
revival condition: *a version that clears the session-shift null at ≥95th, or a different
overnight mechanism that does.*

### What the clock axis actually taught us

- `FACT` **the overnight SHORT does not work**: −$41,741 on 693 trades, −$60.2 each, 34.3 % win.
  B-MOM's RTH short is +$83,691 (W90). **The short edge is an RTH phenomenon**, which is a real
  constraint on where to look next and was not known before this wave.
- `FACT` **overnight friction is $19.77/ctrRT** — 36 % above P1's. Any future overnight engine
  starts $5.25/RT in the hole against an RTH one. That is a standing tax on this whole axis.
- The clock does deliver ρ < 0.20 on demand. It does **not** deliver an edge on demand.
  **Temporal disjointness is cheap; specificity is not.**

## 9. Files
`out/night.txt` · `out/hourly.csv` · `out/per_year.csv` · `out/rho.csv` · `out/null_shift.csv` ·
`out/portfolio.csv` · `out/night_daily.csv` · code `research/weekly_edge/src/run_we_w96.py`
