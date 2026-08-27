# WE_W104 — DOES `XM_CONFLICT` GENERALISE ACROSS THE SESSION? · REPORT

Preregistered (`spec.yaml`, committed at `9509155` before any result was read). Target taken from
W103's capture ledger v3. Owner directive V4 §7 TRACK G / §21.

> ## **NO. The primary fails: $41/trade across the other segments, 90.0th percentile of its own
> ## coin null (bar: $57). The mechanism is an OPENING-AUCTION phenomenon, not a general one.**
> ## $560/trade at the RTH open against $41 averaged everywhere else.

---

## 0. B1 — the overnight join is sound

A join that is sound at 10:00 is not automatically sound at 03:00, so the zero-lag known-answer
test was recomputed on **overnight bars specifically**:

| | lag −1 | **lag 0** | lag +1 | argmax |
|---|---|---|---|---|
| ES · RTH | +0.0028 | **+0.9350** | +0.0101 | 0 ✔ |
| **ES · NIGHT** | +0.0018 | **+0.9262** | +0.0006 | **0 ✔** |
| RTY · RTH | +0.0028 | +0.7349 | +0.0155 | 0 ✔ |
| **RTY · NIGHT** | +0.0089 | **+0.7868** | +0.0370 | **0 ✔** |
| YM · RTH | −0.0007 | +0.7499 | +0.0087 | 0 ✔ |
| **YM · NIGHT** | +0.0015 | **+0.7961** | +0.0110 | **0 ✔** |

All six peak at lag 0. Overnight cross-market correlation is *higher* than RTH for RTY and YM.

## 1. The cells — same construction, nothing re-fitted

| segment | decide | hold to | N | share | E\|move\| | cost | **p\*** | hit % | vs p\* | **$/trade** | AGREE $/trade |
|---|---|---|---|---|---|---|---|---|---|---|---|
| ON_EU | 01:12 | 07:59 | 149 | 14.3 % | $1,168 | $19.36 | 0.5083 | 51.01 % | +0.18 | **$33** | $80 |
| PRE | 08:15 | 09:29 | 198 | 19.0 % | $848 | $19.36 | 0.5114 | 50.51 % | −0.64 | $71 | $27 |
| **MORN** | 10:01 | 11:29 | 295 | 28.2 % | $1,517 | $16.86 | 0.5056 | 48.47 % | **−2.08** | **−$59** | $41 |
| MID | 11:48 | 13:29 | 179 | 17.7 % | $1,109 | $14.36 | 0.5065 | 53.07 % | +2.43 | $51 | −$39 |
| **AFT** | 13:50 | 15:44 | 175 | 17.3 % | $1,078 | $14.36 | 0.5067 | **54.29 %** | **+3.62** | **$146** | $36 |
| POST | 16:18 | 16:59 | 260 | 25.8 % | $311 | $16.86 | 0.5271 | 51.92 % | −0.79 | $1 | −$37 |
| *(reference, not a test)* RTH open | 09:45 | 15:45 | 348 | 34.4 % | $2,683 | $16.86 | 0.5031 | 54.60 % | +4.29 | **$560** | $41 |

## 2. ⚠️ `DEFECT` — six cells ran, not seven, and the missing one was the decisive one

`ON_ASIA` returned **0 sessions** and I found out why: **minute 1080 (18:00) has zero bars in this
substrate — sessions start at 18:01.**

| anchor minute | bars |
|---|---|
| 18:00 | **0** |
| 18:01 | 1,179 |
| 09:30 | 1,182 |
| 09:31 | 1,181 |

> **The one segment that would have tested "is this about session OPENS in general, or about the
> RTH open specifically" is exactly the one that silently didn't run.** The primary statistic is
> internally consistent — its coin null was matched to the same six cells — but it covers **six**
> segments, not the seven the spec named. Stated rather than quietly renumbered.

### The repair, run after the fact and labelled as such

| cell | N | p\* | hit % | **$/trade** | net $ |
|---|---|---|---|---|---|
| CME open 18:01 → 18:55 → 23:59 | 229 | 0.5127 | **57.21 %** | **$125** | $28,569 |
| CME open 18:01 → 19:01 → **09:29** | 223 | 0.5057 | 50.22 % | **$268** | $59,710 |
| CME open 18:01 → 18:16 → 23:59 | 258 | 0.5119 | 52.71 % | $39 | $9,995 |
| *(reference)* RTH open 09:31 → 09:45 → 15:45 | 348 | 0.5031 | 54.60 % | **$560** | $195,003 |

**These three are post-hoc and are not preregistered.** Only one ($268) would clear the best-of-7
bar of $251, marginally, and it was chosen from three variants after the failure was diagnosed.
**Read as a lead, not a result:** the mechanism appears *weakly* present at the CME open and
*strongly* at the RTH open. That refinement deserves its own preregistration; it does not get to
lean on this wave's.

## 3. The primary — and it fails

| | |
|---|---|
| real, equal-weight mean of $/trade across the six cells | **$41** |
| coin null on the same statistic: mean / sd | −$14 / $44 |
| **coin null p95** | **$57** |
| **percentile** | **90.0th** |

> **VERDICT: DOES NOT GENERALISE.** Ninety per cent is not five per cent, and the primary was fixed
> before the run precisely so that a 90th-percentile result would be called what it is.

Individual cells against the **best-of-7 coin null (p95 = $251)**:

| segment | $/trade | clears its own p\* | **beats best-of-7** |
|---|---|---|---|
| AFT | $146 | **YES** | no |
| PRE | $71 | no | no |
| MID | $51 | **YES** | no |
| ON_EU | $33 | **YES** | no |
| POST | $1 | no | no |
| MORN | −$59 | no | no |

**Nothing clears the family-wise bar.** `AFT` is `WEAK` — it clears its own cost bar at 54.29 %
versus 50.67 %, and W99 flagged AFT as the segment where we capture **0.3 %** of $1,170/session, so
it is worth a preregistration of its own. It is not a finding today.

## 4. The mechanism question, answered whichever way the primary went

| segment | starts at | minutes after a session open | $/trade |
|---|---|---|---|
| MORN | 09:45 | **15** | **−$59** |
| MID | 11:30 | 120 | $51 |
| AFT | 13:30 | 240 | $146 |
| ON_EU | 00:00 | 360 | $33 |
| POST | 16:00 | 390 | $1 |
| PRE | 08:00 | 840 | $71 |

> **There is no monotone relationship with distance from an open** — MORN, the closest, is the only
> negative cell. So the finding is *not* "the effect decays with time since the open". It is
> narrower and stranger than that: **the effect lives in the specific act of measuring NQ's
> divergence from the broad index across the opening auction and then holding for the rest of the
> day.** MORN fails even though it starts 15 minutes after the RTH open — because by 10:01 the
> auction has already resolved and the divergence has already been priced.
>
> That is consistent with the W101 decomposition (`XM_AGREE` alone is *negative*; the edge is
> entirely in the disagreement) and with the CME-open cells being weakly positive: the 18:01 open
> is a real auction too, just a thinner one.

## 5. No survivor is a second copy of the same trade

| segment | wk $ | wk$ @ fixed DD | wk + % | ρ vs P1 | ρ vs RTH-open |
|---|---|---|---|---|---|
| AFT | $120 | $123 | 27.2 % | **+0.223** | +0.065 |
| PRE | $66 | $104 | 30.5 % | +0.013 | +0.068 |
| MID | $43 | $42 | 31.9 % | −0.183 | +0.035 |
| ON_EU | $23 | $24 | 25.4 % | −0.078 | −0.017 |
| POST | $2 | $5 | 41.3 % | −0.149 | +0.020 |
| MORN | −$82 | −$66 | 36.6 % | −0.099 | −0.018 |

All six are essentially uncorrelated with the RTH-open object (|ρ| ≤ 0.07), so none of them is a
duplicate — they are simply not profitable enough to matter. `AFT`'s ρ = +0.223 with P1 is the
largest and would count against it if it were ever promoted.

## 6. Decision

**Nothing promoted. The falsifier fired and is recorded.**

What the wave bought:

1. **`XM_CONFLICT` is an opening-auction object, not a general cross-market edge.** Any future
   claim that "cross-market disagreement predicts NQ persistence" must carry "**at the opening
   auction**" or it is overstated. This constrains the mechanism and stops six speculative sleeves.
2. **The overnight cross-market join is verified sound** (lag-0 argmax on all three, night and day)
   — that check is now reusable and is not owed again.
3. **`AFT` is `WEAK`** and is the only cell worth a preregistration, precisely because W99 ranks the
   segment #3 by residual and we capture 0.3 % of it.
4. **A substrate fact worth keeping: sessions start at 18:01, not 18:00.** Any segment definition
   anchored at 18:00 silently produces zero rows.
