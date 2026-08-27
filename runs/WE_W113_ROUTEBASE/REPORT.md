# WE_W113 — routing the actual baseline with the proven state layer · REPORT

Preregistered (`spec.yaml`, committed at `f678744` before any code was written).
Directive V5 §§30, 37, 26, 45. B1 harness check **PASSED**: the blocked engine with nothing blocked
is byte-identical to `gfills` on all 2,401 trades.

> ## **FAILS, decisively, and in a way that is worth more than a pass would have been.**
> ## **All eight cells are WORSE than the untouched baseline** — $443 to $1,062 per week at fixed drawdown against **$1,230**. The best of eight sits at the **58.0th percentile** of a rate-matched random-veto null. And **max drawdown gets worse in every single cell**, from $22,931 up to as much as $36,705.
> ## The state layer that failed to route five losing fades (W109) also fails to route the one engine that makes money. **§37's question — can one state layer route more than one engine — now has an answer on both sides of the ledger, and it is no.**

## 1. How much was even at risk — reported first, as the spec requires

| P1/PCT entries | trades | net |
|---|---|---|
| **before 11:49** | 1,475 | $166,837 |
| **at/after 11:49** | 656 | **$129,994 — 43.8 % of P1/PCT's net** |

> This is the opposite of the "it could not have mattered" outcome the spec braced for. **Nearly
> half the baseline's money comes from afternoon entries**, so the intervention had full scope to
> help or hurt. It hurt.

## 2. The 3 × 3 grid, with its unconditional control

Veto polarity **LOW = range-like**, inverted from W109 and fixed by mechanism in the spec before any
P&L was read, because P1 is a long-only trend-following engine whose breakouts fail on range days.

| cell | veto % | trades | net $ | wk $ | **wk$@fixDD** | pos wk % | **maxDD** | CVaR5 | t |
|---|---|---|---|---|---|---|---|---|---|
| **BASELINE — no veto** | 0.0 % | 2,131 | **$296,831** | $1,394 | **$1,230** | **56.3 %** | **$22,931** | −$2,754 | **4.16** |
| D1_DIR_EFF @ 0.25 | 24.4 % | 2,035 | $257,802 | $1,210 | $865 | 56.8 % | $28,322 | −$2,736 | 3.63 |
| D1_DIR_EFF @ 0.50 | 49.5 % | 1,925 | $170,987 | $803 | $443 | 51.6 % | $36,705 | −$2,697 | 2.73 |
| D1_DIR_EFF @ 0.75 | 74.9 % | 1,797 | $168,169 | $790 | $534 | 52.1 % | $29,956 | −$2,570 | 2.79 |
| **D4_VWAP_DISP @ 0.25** *(best)* | 24.9 % | 2,041 | $259,037 | $1,216 | **$1,062** | 54.9 % | $23,184 | −$2,735 | 3.68 |
| D4_VWAP_DISP @ 0.50 | 48.8 % | 1,917 | $244,421 | $1,148 | $879 | 54.5 % | $26,442 | −$2,735 | 3.47 |
| D4_VWAP_DISP @ 0.75 | 74.2 % | 1,800 | $194,052 | $911 | $606 | 54.0 % | $30,430 | −$2,610 | 3.21 |
| D5_MR_FAIL @ 0.25 | 45.9 % | — | *UNCALIBRATED, excluded (W107b rule)* | | | | | | |
| D5_MR_FAIL @ 0.50 | 54.1 % | 1,930 | $201,659 | $947 | $579 | 54.0 % | $33,085 | −$2,640 | 3.23 |
| D5_MR_FAIL @ 0.75 | 76.5 % | 1,830 | $193,753 | $910 | $650 | 53.5 % | $28,345 | −$2,573 | 3.14 |
| *CONTROL — block on EVERY session* | 100 % | 1,736 | $184,928 | $868 | $622 | 52.6 % | $28,272 | −$2,587 | 3.09 |

**Primary:** best of 8 = D4_VWAP_DISP @ 0.25, **$1,062/wk at fixed DD**.
Rate-matched random-veto null (200 draws, same 263 sessions blocked at random): mean $1,018,
sd $194, **p95 $1,325 → 58.0th percentile**. Baseline **$1,230**. **VERDICT: FAILS on both gates.**

## 3. ⭐ The two things this measured that are worth keeping

### (a) P1/PCT's afternoon entries reduce drawdown, they do not add it

**Every cell raises max drawdown**, from the baseline's $22,931 to between $23,184 and $36,705 —
and the worst drawdown belongs to the *middle* veto rate, not the most aggressive one. Blocking
half the afternoon entries costs **$168,000 of net and $13,800 of extra drawdown at once.**

> The intuition a veto trades on — "stop trading into chop and you will lose less" — is **false for
> this engine**. Its afternoon entries are diversifying its own equity path. The random-veto null
> agrees: its mean is $1,018, comfortably **below** the baseline's $1,230, so *any* reduction of
> afternoon exposure is costly on average and the detectors merely do about as well as chance.

### (b) Two thirds of every veto lands where P1 was already flat

P1/PCT takes a post-11:49 entry on **367 of 1,058** in-window sessions — it is already flat after
11:49 on the other 65 %.

| cell | sessions vetoed | of which P1 had no entry anyway | **sessions actually changed** |
|---|---|---|---|
| D1_DIR_EFF @ 0.25 | 258 | 172 | **86** |
| D4_VWAP_DISP @ 0.25 | 263 | 181 | **82** |
| D4_VWAP_DISP @ 0.75 | 785 | 508 | 277 |
| D5_MR_FAIL @ 0.75 | 809 | 528 | 281 |

> The detectors and P1's own gates **agree about two thirds of the time** — which is itself an
> answer to the spec's redundancy question. The state layer is substantially re-expressing what the
> engine's range throttle and delta gate already do, and the third of the time it disagrees, it is
> wrong.

## 4. Decision

**NOTHING PROMOTED. NOTHING CHANGED ABOUT THE BASELINE.** `P1/PCT` stands exactly as
`CURRENT_BASELINE.md` records it.

1. **§37's question is answered on both sides.** The same three causal states — genuinely
   informative about trend vs range at AUC 0.613–0.621 — fail to route five losing fade engines
   (W109) *and* fail to route the one profitable engine (W113). **A trend/range state layer, at the
   discrimination we can actually achieve, is not a router.** Two independent failures on opposite
   kinds of engine is much stronger evidence than either alone.
2. **A plausible-sounding "improvement" to the baseline has been killed before it could be
   believed.** "Don't let the trend engine enter into afternoon chop" is exactly the kind of change
   that reads as obviously sensible and would have cost $168k of net and $13.8k of drawdown.
3. **The state-layer family is now closed** (§13, §32, §38). It has had one clean primary on fades,
   one justified decomposition, and one clean primary on the baseline. **Do not rescue it further.**
4. **Retained as a fact about the base:** 43.8 % of P1/PCT's net comes from entries at or after
   11:49, and those entries *lower* its maximum drawdown. Any future proposal that trims the
   baseline's afternoon must clear this wave first.
