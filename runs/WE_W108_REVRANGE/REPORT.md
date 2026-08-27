# WE_W108 — LANE C, REVERSAL / RANGE · REPORT

Preregistered (`spec.yaml`, committed before any result was read). Owner amendment §6 LANE C.

> ## **THE PRIMARY FAILS HARD — −$143/trade, 0.5th percentile of its coin null.**
> ## But the *shape* of the failure is the most useful thing this lane produced:
> ## **the four genuine fade mechanisms are POSITIVE on RANGE sessions and heavily NEGATIVE on
> ## TREND sessions.** They work where they claim to. The trend-day losses swamp them.
> ## And the one positive mechanism **falsified its own stated mechanism** by the preregistered rule.

## 1. Economics — decide 11:48, fill 11:49, hold to 15:44, size 1, no stop

p\* for this horizon = **0.5042**, computed not assumed.

| mechanism | rate | N | hit % | vs p\* | **$/trade** | net $ | t |
|---|---|---|---|---|---|---|---|
| VALUE_REACCEPT | 0.25 / 0.50 / 0.75 | 1,011 | 45.80 % | −4.62 | −$21 | −$21,323 | −0.32 |
| **FAILED_BREAK** | 0.25 / 0.50 / 0.75 | 299 | 43.81 % | −6.60 | **−$225** | −$67,379 | −1.51 |
| **EXHAUST_VOL** | 0.50 | 491 | **42.36 %** | **−8.05** | **−$309** | −$151,781 | **−2.45** |
| **EFFORT_NO_RES** | 0.50 | 540 | 44.44 % | −5.97 | **−$320** | −$172,634 | **−2.02** |
| **VWAP_RECLAIM** | 0.50 | 797 | **54.20 %** | **+3.79** | **+$53** | +$42,265 | 0.67 |
| VWAP_RECLAIM | 0.75 | 800 | 54.12 % | +3.71 | +$74 | +$58,892 | 0.88 |
| PATH_EFF_TRANS | 0.50 | 556 | 47.30 % | −3.12 | −$38 | −$21,319 | −0.43 |

**PRIMARY: −$143/trade · coin null mean −$15, p95 $66 · 0.5th percentile · FAILS.**
Best-of-18 bar: $419. **Nothing comes close.**

## 2. ⚠️ The one positive mechanism falsified itself, by the rule fixed in advance

The spec said: *"a mechanism positive overall but negative on REVERSAL and RANGE sessions has
FALSIFIED its own stated mechanism even if it made money."*

| mechanism, 50 % arm | TREND-UP | TREND-DOWN | **REVERSAL** | **RANGE** | MIXED |
|---|---|---|---|---|---|
| **VWAP_RECLAIM** | **+$995** | **+$1,165** | **−$87** | **−$913** | −$807 |

> `VWAP_RECLAIM` earns on **trend** sessions and loses on **exactly the two classes it was written
> for**. It is a trend-continuation mechanism wearing a reversal label. **FALSIFIED as a
> reversal/range mechanism**, whatever its P&L.

And the control makes it worse:

| | N | hit % | $/trade |
|---|---|---|---|
| **CONTROL: always LONG** 11:49 → 15:44 | 1,012 | **54.25 %** | +$19 |
| CONTROL: always SHORT | 1,012 | 45.26 % | −$48 |
| VWAP_RECLAIM @ 0.50 | 797 | **54.20 %** | +$53 |

> `VWAP_RECLAIM` takes **79 % of all sessions** and its hit rate — **54.20 %** — is
> **indistinguishable from simply being long every afternoon (54.25 %).** It is mostly a
> directional tilt, not a signal.

## 3. ⭐ The finding worth keeping — the fades work, and it does not matter

| mechanism, 50 % arm | TREND-UP | TREND-DOWN | **RANGE** | MIXED |
|---|---|---|---|---|
| VALUE_REACCEPT | −$611 | −$790 | **+$524** | **+$772** |
| FAILED_BREAK | −$781 | −$1,400 | **+$720** | **+$636** |
| EXHAUST_VOL | −$847 | −$1,174 | **+$216** | **+$251** |
| EFFORT_NO_RES | −$1,249 | −$1,374 | **+$470** | **+$342** |
| PATH_EFF_TRANS | −$258 | −$1,080 | **+$701** | **+$1,017** |

> ### **All five fade mechanisms are POSITIVE on RANGE sessions and POSITIVE on MIXED, and all
> ### five are heavily NEGATIVE on both TREND classes.** The signs are exactly what the mechanisms
> ### predict. The problem is not that fading does not work — **it is that the class is not
> ### knowable in advance, and the trend-day losses are two to three times the range-day gains.**
>
> This reframes the whole reversal/range problem. Seven prior fades were killed in this campaign
> and recorded as "fading does not work on modern NQ". That conclusion is **too strong**. The
> correct statement is: **fading works on the sessions it is designed for and there is no causal
> trend-day veto to keep it off the others.** The missing object is not a better fade. It is a
> **causal trend-day detector** — and W99 already priced how good it would need to be.

## 4. Decision

**Nothing promoted.** The primary failed at the 0.5th percentile, which is about as clear as a
negative gets.

What the wave bought:

1. **Five fade mechanisms with the correct class signature, all unprofitable in aggregate.**
   Their RANGE/MIXED profits are real and are swamped 2–3× by TREND losses.
2. **The reversal/range agenda is re-pointed.** The next object in this lane is not another fade —
   it is a causal statement about whether *today is a trend day*, which would make five already-built
   mechanisms tradeable at once. That is a different and much better-specified problem.
3. **`VWAP_RECLAIM` is closed as a reversal mechanism** and flagged as a near-duplicate of an
   unconditional long tilt (54.20 % vs 54.25 %).
4. The seven previously-killed fades stay killed, but the *reason* recorded for them is corrected:
   not "fading fails" but "fading has no trend-day veto".
