# CURRENT BASELINE — campaign #7 WEEKLY_EDGE

_Authoritative as of **2026-08-27**, wave **W103**. Where this file and any older weekly_edge doc
disagree, **this file governs**. Every number is cited to a committed run. This is the campaign-#7
equivalent of the root `BASELINE_MODELS.md`, which covers campaign #3's three shipped objects and
is unaffected by anything here._

---

## 1. THE BASE — what it is right now

### `P1/PCT`

Unchanged from `P1` in every respect except one, and that one change is a **unit correction, not a
new strategy**:

| component | status |
|---|---|
| 13-member Solar volatility-ratchet ensemble, four combiners, 32-config vote | unchanged |
| **OR-gated with the B-MOM channel** (latched ±1, `px > max(open₀₉₃₀ + mtod14, RTH VWAP)`, reset 09:31, killed 15:57) | unchanged |
| long-only | unchanged |
| range throttle q = 0.8 · delta gate | unchanged |
| causal quality sizing — size 2 when score ≥ 3 (18.3 % of trades) | unchanged |
| **session box −$1,300 / +$1,000** | ⭐ **CHANGED: now denominated PER CONTRACT, not per position** |
| flat at every session close | unchanged |

**Why the change** (`runs/WE_W98_BOXDENOM/`): a dollar stop on a variable-size position halts a
2-lot at **half** the adverse point move of a 1-lot. That is a mis-specification by construction.
Under the incumbent, loss-halts fired at **55.68 points on size-1 sessions and 37.18 on size-2**.

**What it bought** — full modern window 2022-07-01 → 2026-08-01, 1,058 sessions / 213 weeks, net of
$14.44/ctrRT candidate-specific spread plus $4.36 commission:

| | `ABS` (old) | **`PCT` (current)** |
|---|---|---|
| weekly $ | $1,154 | **$1,394** |
| **weekly $ at fixed $20,245 max DD** | $885 | **$1,231  (+39.0 %)** |
| positive weeks | 53.1 % | **56.3 %** |
| max drawdown | $26,388 | **$22,931** |
| top-5 drawdown | $18,421 | $17,835 |
| t | 3.58 | **4.16** |

**The controls, which are the actual evidence:** a *uniformly* looser dollar box is worth
**+$6/week (paired p = 0.940)**; holding the average budget fixed while making it size-conditional
keeps **+39.6 %**; both size-1 objects (BMOM, NETFUSE_1) show **exactly $0.00** across all 213
weeks; the real gap sits at the **99th percentile** of 200 size-label permutations.

**Label: `REGIME_LOCAL`.** On 2006–2021 the change **reverses (−31.4 %)** — a $1,300 box was 84 %
of a typical session's range then and is 19 % now, so it fires **5.7× more often today**. `ABS` is
retained beside `PCT` in every table and is not deleted. Paired weekly p = 0.057, and **90.8 % of
the gross difference lives in 53 of 1,058 sessions**.

---

## 2. THE BEST CANDIDATE PORTFOLIO — not the base, not promoted

### `{P1/PCT + XM_CONFLICT}`, inverse-volatility weights

`XM_CONFLICT` (`runs/WE_W101_DIRECTION/`, `WE_W102_XMENGINE/`): at 09:45 ET take NQ's own opening
drive — sign(close₀₉₄₅ − open of the 09:31 bar) — **only on the ~34 % of sessions where the
ES/RTY/YM composite is moving the opposite way**. Fill at the 09:46 open, hold to 15:45, size 1,
**no stop**.

| | P1/PCT alone | **P1/PCT + XM_CONFLICT** |
|---|---|---|
| **weekly $ at fixed $20,245 DD** | $1,230 | **$2,012  (+63.5 %)** |
| positive weeks | 56.3 % | 59.2 % |
| **max drawdown** | $22,931 | **$11,489** |
| **top-5 drawdown** | $17,835 | **$8,735** |
| t | 4.16 | **4.90** |

⚠️ **Quote the range, not a point: +45 % (income-matched, W102) to +64 % (inverse-vol, W103).**
The drawdown halving is the more robust half of the result.

**Why it works and nothing else does:** ρ(weekly, P1) = **0.081**. Every other object in the
campaign correlates 0.27–0.72 with P1. Adding the 2:3 pair on top makes the portfolio **worse**
(−12 %), and an independent 63-cell integer grid puts its argmax at **2 P1 : 0 PAIR : 1 XM** —
zero pair. Two weighting methods converge on "drop the pair".

**Status:** EVIDENCE **STRONG (current regime) · REGIME_LOCAL** · ENGINEERING **RESEARCH_ONLY** ·
**NOT ENABLED**. Caveats that travel with every quotation:

- **N = 348** trades, ~1.6 sessions/week.
- **The window is discovery-consumed** (2022-07 → 2026-08, mined for 103 waves).
- **ρ = +0.446 with B-MOM.** A diversifier against P1, only partly against the pair.
- **REGIME_LOCAL by DATA AVAILABILITY, not by choice** — ES/RTY/YM substrates begin 2022-01-02, so
  no 2006–2021 test exists and none can be built from anything on disk.
- **The only intra-trade risk control is the clock.** Worst adverse excursion ever: **−$10,865
  (543 points)**. Every stop distance from 20 to 300 points makes it worse at fixed drawdown.
- It was **selected as the best of 27 cells** (W101) and its combination as the **best of 6**
  (W103). It cleared a best-of-27 coin null, a rate-matched subsample null at the 99.6th, and a
  |drive|-**decile**-matched null at the **99.7th** — but the selections happened.
- **Last three months are weak**: the primary combination is $499/wk at fixed DD, 35.7 % positive
  weeks, **t = 0.25** over 14 weeks — inside the BURNED span.

---

## 3. STRONGEST CHALLENGER, still not promoted

`PAIR23` = **2 BMOM : 3 X9a**, sleeves boxed independently, per-unit:
**$1,309/wk at fixed DD · 60.6 % positive weeks · max DD $18,088 · top-5 $11,362 · t 4.36** — the
best *single* object in the campaign, better than P1/PCT's $1,230.

It beats P1 on money, max drawdown, top-5 drawdown, positive-week rate **and** losing streak
simultaneously over the 16 unseen years 2006–2021 (`runs/WE_W97_AUDITFIX/`). It is **not promoted**
because W86's specificity null said the gain is *"two independent streams"* rather than *these two*,
and because W103 now shows it **adds nothing on top of P1 + XM_CONFLICT**.

**Demoted:** `NETFUSE_1` — the only object ever to clear a specificity null, and **deep-negative**
(−$8,951 over 2006–2021) with a top-5 drawdown 32.9 % worse than P1's.

---

## 4. WHAT THE BASE DOES NOT DO

From `runs/WE_W103_CONSOLIDATE/` (capture ledger v3), against an executable ceiling of one
perfect-direction trade per segment:

| segment | executable ceiling / session | base takes | **covered** | break-even accuracy |
|---|---|---|---|---|
| MORN 09:45–11:29 | $1,744 | $78 | **4.4 %** | **0.5048** |
| ON_EU 00:00–07:59 | $1,224 | $18 | 1.5 % | 0.5078 |
| MID | $1,197 | $19 | 1.6 % | 0.5059 |
| AFT 13:30–15:44 | $1,170 | $3 | **0.3 %** | 0.5058 |
| ON_ASIA | $1,026 | $39 | 3.8 % | 0.5139 |

> **After 103 waves the base captures 0.2 %–5.1 % of what is executable in every segment**, and
> ex-post movement per session has **risen 83 %** while P1's own production went negative.
> By class: TREND-DOWN and REVERSAL have **flipped positive** for the first time (+$195, +$27
> income-matched, from −$495 and −$64) — with **$10,953 and $9,073 per session of those classes
> still open**.

---

## 5. Frozen conventions (do not change without a wave)

| | |
|---|---|
| window | 2022-07-01 → 2026-08-01, 1,058 sessions, 213 weeks |
| substrate | `load_deep(..., extend=True)` — deep file to 2026-05-29 joined to `SM1M_SUBSTRATE` |
| cost | $4.36/ctrRT commission **inside** the fill engine + candidate's own contract-weighted spread from `WE_W82_FILLAUDIT/out/spread_by_minute.csv` (P1 $14.44, BMOM $13.02, XM_CONFLICT $12.50) |
| headline metric | weekly $ at a fixed **$20,245** max drawdown — algebraically scale-invariant |
| exposure convention | **income-matched** (W97: the only one with no free parameter) |
| seal | ≥ **2026-08-01 VIRGIN**; **2026-05-31 → 07-31 BURNED** |
| known data holes | **2026-07-17 is truncated** (ends 10:53, 83 RTH bars vs 390); spread profile has 1,380 minutes, the missing 60 being the 17:00–17:59 CME break |
