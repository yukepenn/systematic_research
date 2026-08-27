# WE_W119 — the BOOK_LOSS_LEDGER · REPORT

Preregistered (`spec.yaml`, committed at `5677472` before any code was written).
POST-W118 owner directive §§9–13, LANE A. Artifact: `out/book_loss_ledger.csv`, **1,058 sessions ×
25 columns**, causal fields named by their availability minute (`c0931_`, `c0945_`, `c1148_`),
ex-post fields prefixed `EXPOST_`.

> ## **THE GAP IS NOT COVERAGE. `E_NO_ENGINE` = 0 sessions — there is not one session in four years where neither leg was active during a top-decile move.**
> ## **THE GAP IS TURNOVER.** On losing sessions P1 takes **3.04 trades against 1.38** on winning ones — **2.2× more** — for **18 % FEWER contract-minutes**, on sessions that move **31 % LESS** (116.5 vs 168.0 points). More entries, shorter holds, smaller moves. That is a churn signature, not a directional one.
> ## **And the TAIL is XM.** XM is active on 33 % of sessions but appears in **69.8 % of the book's worst decile** (+34.3 pp over its all-loss share). The worst 106 sessions carry **56 % of all loss**.
> ## ⚠️ **W117 is narrowed:** at session resolution the REVERSAL excess is **+1.7 pp**, not the +6.9 pp weekly aggregation showed — and **RANGE is the larger dollar class (−$114,807 vs −$91,216)**.

## 1. The book

**405 losing sessions of 1,058 (38.3 %)**, carrying **−$338,490**. Book net over the window
**+$243,177**. Weights **0.473 × P1/PCT + 0.527 × XM_CONFLICT**, inverse-vol on weekly, exactly as
W110/W117 built it.

## 2. §12 decomposition — overlapping lenses, **not** a partition

| lens | sessions | % of all | book $ there | % of total loss |
|---|---|---|---|---|
| **G_RISK_TRUNC** — P1's session box fired | 169 | 16.0 % | **−$194,735** | **57.5 %** |
| **C_XM_LOSS** — XM active and lost | 144 | 13.6 % | **−$179,668** | **53.1 %** |
| **A_P1_WRONGWAY** — P1 traded & lost, session **DOWN** | 161 | 15.2 % | −$149,059 | 44.0 % |
| **B_P1_WHIPSAW** — P1 traded & lost, session **UP** | 145 | 13.7 % | −$110,248 | 32.6 % |
| D_BOTH — both legs lost | 54 | 5.1 % | −$102,665 | 30.3 % |
| F_COST — P1 friction on losing sessions | — | — | −$26,860 | 7.9 % |
| **E_NO_ENGINE** — neither active, top-decile move | **0** | **0.0 %** | **$0** | **0.0 %** |

**Overlaps, stated rather than hidden:** A ∩ B = 0 (mutually exclusive by construction) ·
D ∩ C = 54 · G ∩ A = 81 · G ∩ B = 71. The percentages sum past 100 **by design** and must never be
read as a partition.

> ⚠️ **`G_RISK_TRUNC` is a SYMPTOM LENS, not a cause.** The box fires *because* the session went
> badly; it does not make it go badly. W98 already tested the counterfactual and a *uniformly*
> looser box is worth **+$6/week at p = 0.940** — i.e. nothing. **Do not read "57.5 % of loss
> dollars sit on box-fire sessions" as "the box costs 57.5 %."** It locates the damage; it does not
> attribute it.
>
> **`E_NO_ENGINE` = 0 is the decisive one.** The spec fixed in advance that if this were the largest
> source, *"the gap is COVERAGE and the answer is a new engine."* It is **zero sessions**. P1 is
> essentially always available. **The book does not lose because it was absent.**

## 3. The worst decile — and it belongs to XM

106 sessions at or below −$1,047 carry **−$189,670 = 56.0 % of all loss.**

| lens | in worst decile | share of decile | **vs its all-loss share** |
|---|---|---|---|
| **C_XM_LOSS** | 74 | **69.8 %** | **+34.3 pp** |
| **D_BOTH** | 43 | 40.6 % | **+27.2 pp** |
| G_RISK_TRUNC | 62 | 58.5 % | +16.8 pp |
| A_P1_WRONGWAY | 44 | 41.5 % | +1.8 pp |
| B_P1_WHIPSAW | 31 | 29.2 % | **−6.6 pp** |

> ### **XM is the book's tail.** It is active on 33 % of sessions and present in **70 %** of the worst decile. Its only intra-trade control is the clock (W102/W105: every stop from 20 to 300 points makes it worse at fixed drawdown; worst adverse excursion −$10,865).
> ### This is **not** in tension with W110. W110 measured *weekly* loss diversification — XM's bad weeks do not coincide with P1's, and that stands. W119 measures *session* tail composition — XM supplies the deepest single sessions. **Both are true and they are different statements.** The book's disaster-risk architecture is XM's, and the owner sets that level (W105 priced it: 300 points costs 0.7 % of gross, 13 triggers).

## 4. ⭐ Exposure — the actionable finding

| | **losing sessions** | **winning sessions** | difference |
|---|---|---|---|
| **P1 trades** | **3.042** | **1.377** | **+1.665 (2.2×)** |
| **P1 contract-minutes** | **199.0** | **242.1** | **−43.1** |
| P1 max size | 1.123 | 0.654 | +0.470 |
| P1 box-fire rate | 0.417 | 0.322 | +0.096 |
| XM active rate | 0.402 | 0.283 | +0.119 |
| **∣RTH move∣, points** | **116.5** | **168.0** | **−51.5 (−31 %)** |
| RTH range, points | 268.2 | 281.6 | −13.4 |

> ### **On losing sessions the engine trades 2.2× as often, holds 18 % less, and the market moves 31 % less.** More entries, shorter holds, smaller moves — and the range is barely different (−5 %), so it is not that losing sessions are quiet. **They are sessions with normal range and little net displacement, and P1 keeps re-entering into them.**
> ### That is a **turnover** problem inside an engine we already own, not a missing engine and not a directional error.

## 5. EXPOST_CLASS with its matched unconditional control (W108's binding rule)

| class | losing sessions | share | **share of ALL sessions** | difference | book $ there |
|---|---|---|---|---|---|
| **RANGE** | 126 | 31.1 % | 26.8 % | **+4.3 pp** | **−$114,807** |
| REVERSAL | 111 | 27.4 % | 25.7 % | **+1.7 pp** | −$91,216 |
| TREND-DOWN | 62 | 15.3 % | 14.5 % | **+0.8 pp** | −$58,059 |
| MIXED | 56 | 13.8 % | 12.0 % | +1.8 pp | −$40,268 |
| **TREND-UP** | 50 | 12.3 % | 21.0 % | **−8.6 pp** | −$34,140 |

### ⚠️ This narrows W117

W117 measured, on 87 **weekly** observations: TREND-UP 0.167 vs 0.238 (p 0.005), **REVERSAL 0.299
vs 0.230 (p 0.011)**, TREND-DOWN 0.147 vs 0.143 (p 0.880).

At **session** resolution on 1,058 observations:

- **The TREND-UP deficit survives and is the strongest effect** (−8.6 pp). ✅
- **The TREND-DOWN null survives** (+0.8 pp) — the book still does not lose on down sessions. ✅
- **The REVERSAL excess largely does not.** +1.7 pp at session resolution against +6.9 pp weekly.
  **The weekly aggregation amplified it**, and **RANGE (+4.3 pp, −$114,807) is both the bigger
  excess and the bigger dollar class.**

> **W117's headline — "the hole is a REVERSAL engine" — is CORRECTED to: the book bleeds most on
> RANGE and REVERSAL sessions together, with RANGE the larger of the two in dollars, and the single
> strongest signal is the ABSENCE of TREND-UP.** W118 has already shown that attacking the reversal
> class directly loses to its own momentum mirror by $778/trade, so this correction moves the target
> away from a construction that is already closed.

## 6. Decision — and the one sentence the spec demanded

> ### **The largest actionable loss source is P1 TURNOVER ON LOW-DISPLACEMENT SESSIONS: 3.04 trades against 1.38, for 18 % fewer contract-minutes, on sessions moving 31 % less — and the gap is POLICY INSIDE AN ENGINE WE ALREADY OWN, not coverage (`E_NO_ENGINE` = 0) and not direction (TREND-DOWN +0.8 pp).**

**NOTHING PROMOTED.** What the next wave must target, and why the obvious objection does not apply:

1. **This is not "detect range days and stop trading."** That exact policy has been tested twice and
   failed — W109 (a trend/range veto on five fades, 85.0th percentile) and W113 (the same states
   vetoing P1's own afternoon entries: **all 8 cells worse than baseline, max DD rising in every
   one**). A *session-level regime classifier* is closed.
2. **The new quantity is INTRA-SESSION and cumulative**: how many entries the engine has already
   taken today. It is trivially causal — you know your own trade count — it is not a regime
   forecast, and it targets the largest measured loss source directly. **The coverage matrix has
   never tested turnover as a state.**
3. **XM's tail is an owner risk-policy question, not a research one.** W105 already priced the
   disaster levels and no level was selected. W119 adds the book-level framing: **XM supplies 70 %
   of the worst decile while being active on 33 % of sessions.**
4. **Cost is real but not the story**: $26,860 on losing sessions, 7.5 % of gross there.
