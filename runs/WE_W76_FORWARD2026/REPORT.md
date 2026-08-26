# WE_W76 — THE 44 SESSIONS NOBODY HAD EVER READ · REPORT

Protocol preregistered and committed **before** the window was opened. Frozen parameters,
nothing re-derived, nothing selected on the held-out window.

> ## THE CHAMPION FAILED. P1 lost **−$20,686 per contract** over the 46 never-seen sessions —
> ## **−22.49 pts/session against an in-sample +14.86. Retention −151 % against a +80 % bar.**

---

## 1. The defect that made this wave possible

`run_we_w17.load_deep()` hardcoded a substrate ending **2026-05-29 16:59**, while every caller in
this campaign asks for `2026-07-31` with `DEV_END = 2026-07-31` and window bound
`B = 2026-08-01`. **The campaign's stated intent has always been to evaluate through July 2026 and
it has been silently truncated at May 2026 for its entire life.**

`runs/SM1M_SUBSTRATE/out/nq_1m_2022_2026.parquet` runs to 2026-07-31 and was verified — before the
spec was written — **bit-exact on all 1,558,497 overlapping rows across every one of time, open,
high, low, close and volume**, carrying 61,547 additional bars.

Because no code in this campaign has ever been able to see those bars, **nothing was ever fitted,
screened, selected or even looked at on them.** They were the only genuinely held-out data this
campaign possessed outside the 2026-08-01 seal. They are read once, here, with the full challenger
set at frozen parameters, so the read cannot be repeated selectively later.

## 2. The read (`FACT`)

46 sessions / 9 weeks, 2026-06-01 → 2026-07-31, one contract, net $4.36/RT:

| object | in-sample pts | **held-out pts** | held-out net | stress net | week + % | weekly mean (SE) | retention |
|---|---|---|---|---|---|---|---|
| **P1 — champion** | 14.86 | **−22.49** | **−$20,686** | −$21,557 | **11.1 %** | **−$2,298 ($838)** | **−151 %** |
| w72:X3 | 9.17 | −19.73 | −$18,152 | −$19,317 | 11.1 % | −$2,017 ($937) | −215 % |
| BMOM | 13.35 | −19.51 | −$17,952 | −$18,406 | 33.3 % | −$1,995 ($3,003) | −146 % |
| w72:X2 | 13.08 | −21.98 | −$20,221 | −$21,096 | 11.1 % | −$2,247 ($838) | −168 % |
| w72:X8 | 10.10 | −12.92 | −$11,891 | −$12,911 | 22.2 % | −$1,321 ($927) | −128 % |
| w72:X5 | 9.02 | −6.98 | −$6,420 | −$7,289 | 22.2 % | −$713 ($812) | −77 % |
| **SHORT** | 6.00 | **+12.46** | **+$11,464** | +$10,467 | 44.4 % | +$1,274 ($2,160) | +208 % |
| **w72:X9a** | 10.73 | **+18.15** | **+$16,702** | +$15,856 | 33.3 % | +$1,856 ($2,891) | +169 % |
| **w72:X9b** | 12.74 | **+40.96** | **+$37,683** | +$36,883 | 55.6 % | +$4,187 ($2,684) | +322 % |

**Ten of thirteen objects lost money.** P1's weekly mean of −$2,298 with a standard error of $838
is **t = −2.74** over nine weeks — this is not a quiet stretch, it is a statistically significant
loss.

> `RECORDED`: **P1 fails its first genuine forward test.** Per the protocol written before the
> read: the campaign's headline figures are **PROVISIONAL** and are re-quoted below with the
> forward window folded in.

## 3. The check that deflates the good news (`FACT`, and it matters more than the table)

Before quoting X9b's +322 %, the concentration of every forward result:

| object | held-out net | **top-3 days** | **net WITHOUT top-3 days** | median TRADED day | positive days |
|---|---|---|---|---|---|
| **P1** | −$20,686 | $550 (−3 %) | **−$21,237** | **−$1,447** | 19.6 % |
| w72:X9b | +$37,683 | **$40,128 (106 %)** | **−$2,445** | **−$1,309** | 21.7 % |
| w72:X9a | +$16,702 | **$32,360 (194 %)** | **−$15,658** | **−$1,359** | 21.7 % |
| SHORT | +$11,464 | **$23,578 (206 %)** | **−$12,113** | **−$1,348** | 26.1 % |

> **Every object in the family has a median traded day between −$1,309 and −$1,447 in this
> window.** The differences between them are entirely *which two or three large days each one
> happened to be positioned for*. X9b's apparent triumph is **three sessions out of forty-six**;
> remove them and it is −$2,445.

This is why the protocol forbade promotion on this window, and the forbidding was right.
**No challenger is promoted. The session-anchor variants are not vindicated by this read.**

The one thing that is *not* explained away is P1's loss: it is **broad**, not tail-driven — removing
its best three days makes it *worse*. Nineteen percent positive days and a median traded day of
−$1,447 is a systematic, session-by-session bleed.

## 4. Why it happened, and it is not a broken model (`FACT`)

| | in-sample 2022-07 → 2026-05 | **held out 2026-06 → 07** |
|---|---|---|
| TREND-UP sessions | 21.2 % | 21.7 % |
| **TREND-DOWN sessions** | 13.7 % | **26.1 %** |
| RANGE sessions | 39.7 % | 19.6 % |
| **median session range** | 288 pts | **664 pts (2.3×)** |
| mean session net | **+16.4 pts** | **−71.6 pts** |
| NQ over the window | — | **−8.1 %** (30,805 → 28,306) |

W50 measured this object exactly: it earns **+88.68 pts/session on TREND-UP days** and **loses
21.89 pts/session on TREND-DOWN days**, and is in the market only 5.4 % of TREND-DOWN bars — so
the damage there is concentrated in a few bad entries, which is precisely what doubles when the
sessions themselves double in size.

> **The TREND-DOWN share nearly doubled and the sessions got 2.3× bigger, in an 8.1 % two-month
> decline.** A long-biased trend harvester losing money there is the object performing exactly to
> its measured specification. **This is not evidence of a defect. It is the first observation of
> the risk W72 had already named** — that half the object's net rests on intraday directional
> gating that only the 2022–2026 era has ever paid for, with every gate in the family sitting at
> the 85th–98th percentile of its own history.

## 5. 2026, re-quoted honestly

2026 is now **152 sessions / 31 weeks**, a **43 % larger sample** than the 106 sessions the
campaign has been reporting. At **one contract**:

| | 2026 net | pts/session | per week | week + % | worst week | **max DD** |
|---|---|---|---|---|---|---|
| **P1 — as previously reported (106 sessions)** | ~~$33,467~~ | ~~15.79~~ | ~~$1,521~~ | ~~68.2 %~~ | ~~−$6,344~~ | ~~$12,607~~ |
| **P1 — actual (152 sessions)** | **$12,781** | **4.20** | **$412** | **51.6 %** | −$6,344 | **$24,225** |

Annualised at 2026's realised rate: **$21,189 per contract against a $24,225 drawdown** — the
drawdown now **exceeds** the annual profit.

> **P1 is not shippable as it stands.** That is the plain statement and it is not softened.

## 6. What the short sleeve did, and the correction it forces

W61 and W75 both rejected the short sleeve for failing a 2026 recency gate. **That gate was
evaluated on the truncated data.** On the extended window:

| P1 + SHORT | **held-out window** | | | full window | | |
|---|---|---|---|---|---|---|
| weight | net | week + % | max DD | weekly $ | week + % | max DD |
| w = 0.00 (P1 alone) | **−$20,686** | 11.1 % | $18,341 | $1,315 | 56.3 % | $24,225 |
| w = 0.30 | **−$11,041 (−47 %)** | **33.3 %** | **$12,155** | $1,108 | **60.6 %** | **$19,435** |
| w = 0.50 | **−$4,611 (−78 %)** | **44.4 %** | $12,382 | $970 | **62.9 %** | $21,525 |

The sleeve **cushions the regime turn by half to three-quarters and does not save it.** Across the
full extended window it buys **+4.3 pp of positive weeks and a 20 % smaller maximum drawdown** for
16 % less money.

> `CORRECTION`: **W75's recency gate rejected the short sleeve on incomplete data.** Its extended
> 2026 is −$11,054 over 31 weeks, not −$22,519 over 22, and it was the best-performing long-run
> stream in the one genuine regime turn this campaign has observed. It remains unadopted — its
> forward gain is also 3 days (§3) — but the *reason* for its rejection is now weaker than
> recorded, and W38's withdrawal of the word "insurance" deserves re-examination against evidence
> rather than against the full-sample tail.

## 7. What this read costs and what it buys

**Costs**: the window is used up. From here 2026-06-01 → 2026-07-31 is in-sample like everything
else. The next virgin data is ≥ 2026-08-01 under the existing seal, whose rules this wave does not
touch.

**Buys**: the campaign now knows that its headline object loses money, broadly and significantly,
in a fast down-trending high-volatility regime — measured, not projected — and that its entire
candidate family degrades together there. Combined with W74 (76 % positive weeks needs six
independent streams) and W75 (we have two), **the strategic picture is consistent: with two
streams there was nothing to absorb a regime turn, and the turn came.**

## 8. Files
`out/forward.txt` `out/console.log` · `out/forward.csv` `out/streams_extended.csv` ·
code `research/weekly_edge/src/run_we_w76.py`, `run_we_w17.py` (`extend=` hook, opt-in, overlap
asserted bit-exact)
