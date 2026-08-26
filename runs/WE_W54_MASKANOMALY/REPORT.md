# WE_W54 — THE MASK ANOMALY, EXPLAINED · REPORT

Diagnostic wave, preregistered, **nothing adoptable by design**. 2022-07-01 → 2026-08-01,
1,012 sessions, net $4.36/RT.

**The decomposition closes to 95 %, so the mechanism sentence below is licensed.**

---

## 1. What was unexplained

W51d's N1 null — the E4 mask rolled by a random offset inside each session — beat the object it
was a null for: 15.45 pts/session and MAR 17.66 against 14.86 / 14.86, on 92 % of the exposure.
A null that wins is not a null; it is a measurement with no mechanism.

## 2. The answer (`FACT`, ledger closes at 95 %)

At a flat 1 lot, where the parts are clean:

| component | pts/session |
|---|---|
| measured delta of the masks | **+0.792** |
| + deleted stretches (the mask removes trades entirely) | **+4.490** |
| + entry price on the stretches it merely delays | **−3.657** |
| = ledger | +0.833 |
| residual (exit paths, session-box re-timing) | −0.040 |

> **The mask does two large, opposite things. It deletes trades that were collectively costing
> +4.49 pts/session to hold, and it pays −3.66 pts/session for the delay it imposes on
> everything it does not delete. The famous +0.79 is the small difference between two big
> numbers.**

## 3. Why it deletes what it deletes — and the campaign's largest measured number

`entry_only` can only delay the start of a long stretch or delete it entirely, and it deletes a
stretch only when the mask is false for its whole length. Long stretches almost surely contain
a true bar, so the deletion is **structurally biased toward short holds**:

- deleted per draw: **537 of 1,942 trades (27.7 %)**
- their mean duration **25 min** against the kept trades' **109 min**

And the incumbent's P&L by holding duration — exact accounting, no backtest — explains
everything:

| duration | trades | mean $ | **pts/session** | win % |
|---|---|---|---|---|
| 1–3 min | 348 | −81 | −1.39 | 36.8 |
| 3–7 min | 222 | −315 | −3.45 | 18.5 |
| 7–12 min | 207 | −349 | −3.57 | 14.5 |
| 12–22 min | 184 | −406 | −3.69 | 17.9 |
| 22–37 min | 199 | −297 | −2.92 | 20.1 |
| 37–60 min | 191 | +202 | +1.90 | 42.4 |
| 60–104 min | 202 | +67 | +0.67 | 48.5 |
| 104–248 min | 193 | +603 | +5.75 | 64.8 |
| **248–1359 min** | 196 | **+2,226** | **+21.56** | **81.1** |

`FACT`: **trades held under 37 minutes cost −15.02 pts/session in aggregate, and they are
55 % of all trades. Trades held over 4 hours earn +21.56.** The win rate is monotone in
duration from 18.5 % to 81.1 %. The median hold is 22 minutes.

That −15.02 is **larger than anything else this campaign has measured** — bigger than W50's
+4.36 "do not trade the bad days", bigger than the entire quality-sizing layer's +4.10.

**The necessary caution, stated before anyone gets excited:** duration is an *outcome*, not a
decision variable. A trade is short *because* the ratchet flipped back. Filtering on duration
is filtering on the P&L symptom, which is exactly what mechanism law 3 forbids. The number is
a prize, not a strategy.

## 4. `FALSIFIED` — the delay hypothesis, with the sign reversed

The matched-flip comparison (only stretches the mask kept, entry price against the incumbent's
entry on the same stretch):

| | price change |
|---|---|
| all matched stretches | **−2.443 points** (the mask buys HIGHER) |
| on eventual **winners** | **−5.892 points** |
| on eventual losers | +0.011 points |

Delay does not buy a better price; it pays about 2.4 points a trade, and **5.9 points on
exactly the trades that were going to work.** This is the fourth independent measurement of the
same thing (R2V1's −$81,630 across 1,838 delayed entries; R2B's Spearman −0.32 of pullback
depth against outcome; W31's flip 0.0603 vs state 0.0025 pts/bar; now this). **The
entry-timing family stays closed on mechanism** — not on the 2026-stub chronology, which
Charter Amendment 1 has withdrawn as a reason.

## 5. `ELIMINATED` — H2, the sizing-pool interaction

| | pts | MAR | maxDD | mean top-5 DD | trades | size-2 % |
|---|---|---|---|---|---|---|
| incumbent, sized | 14.86 | 14.86 | $20,245 | $14,266 | 1,942 | 18.4 % |
| N1 masks, sized | 15.45 | 17.66 | $18,693 | $12,656 | 1,507 | 18.8 % |
| incumbent, flat 1 lot | 10.75 | 10.98 | $19,833 | $12,590 | 2,064 | — |
| N1 masks, flat 1 lot | 11.55 | 15.23 | $16,575 | $10,519 | 1,594 | — |

Delta +0.59 sized, **+0.79 flat**. The advantage is not smaller without the sizing layer, it is
slightly larger. H2 is eliminated as an explanation. (This does *not* contradict W51c's finding
that **E4's specific** gain needed the sizing layer — E4 is one particular mask, not the
average of 50.)

## 6. Phase 5 — is duration forecastable at entry?

Spearman on 1,942 entries, causal features only:

| feature at entry | vs realised **duration** | vs realised **P&L** |
|---|---|---|
| **runlen** | **+0.404** | −0.101 |
| **delta_mag** | **+0.367** | −0.080 |
| dist_open | +0.226 | −0.008 |
| dist_vwap | +0.160 | −0.018 |
| ratio (range throttle) | +0.134 | −0.037 |
| prev_ret | −0.055 | −0.037 |
| atr_l | −0.068 | −0.089 |

`FACT`: **duration is strongly forecastable at entry** — runlen at 0.404 and delta_mag at
0.367 are far above the 0.10 tradeability line.

`FACT`, and the tension that decides the next wave: **the same features have essentially no
positive correlation with P&L, and runlen's is negative.** Forecasting *how long* a trade lasts
is not the same as forecasting *whether it makes money*, even though realised duration and
realised P&L are almost perfectly monotone in each other. Any wave built on §3's −15.02 must
resolve that contradiction before it is allowed to spend a backtest.

## 7. What this hands to the next wave

The prize is **+4.49 pts/session available from deleting short-duration trades**, and the
masks pay **−3.66** for it because in this construction the deletion and the delay are the same
mechanism — you delete a short stretch precisely *by* waiting through it. A rule that deleted
those trades **at the flip bar**, with no delay, would keep the +4.49 and pay none of the
−3.66. Whether such a rule exists is `UNKNOWN` and is preregistered as **W55**, which must
begin by resolving §6's contradiction with exact accounting and not with a sweep.

W55 is also the sharpest available test of the unifying event-count law: it deliberately
removes ~25 % of events, and the law (4 instances) says the tail must get worse.

## 8. Files
`out/maskanomaly.txt` `out/duration.csv` `out/h3_matched.csv` `out/h2_sized.csv`
`out/h2_nosizing.csv` `out/decomp.csv` · code `research/weekly_edge/src/run_we_w54.py`
