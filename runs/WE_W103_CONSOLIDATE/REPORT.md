# WE_W103 — WHAT IS THE BASE, ACTUALLY? · REPORT

Preregistered (`spec.yaml`, committed at `f68839d` before any result was read). Owner directive V4
TASK 12 + TASK 13, §12.

> ## **The best combination is the SIMPLEST one, and my preregistered primary came second.**
> ## `{P1/PCT + XM_CONFLICT}` at inverse-volatility weights: **$2,012/wk at a fixed $20,245
> ## drawdown against P1's $1,230 (+63.5 %)**, max drawdown **halved** ($22,931 → $11,489),
> ## top-5 drawdown $17,835 → **$8,735**, positive weeks 56.3 → 59.2 %, **t = 4.90**.
> ## Adding the 2:3 pair on top makes it **worse**. Two independent weighting methods agree.
> ## And the capture ledger says the base still takes **0.2 %–5.1 %** of every segment.

---

## 1. The correlation matrix, printed before any combination — because it is the honest part

| | P1_PCT | X9a_PCT | BMOM | PAIR23 | XM_CONFLICT |
|---|---|---|---|---|---|
| **P1_PCT** | 1.000 | **0.688** | 0.267 | **0.676** | **0.081** |
| **X9a_PCT** | 0.688 | 1.000 | **0.014** | 0.723 | 0.139 |
| **BMOM** | 0.267 | 0.014 | 1.000 | 0.701 | **0.446** |
| **PAIR23** | 0.676 | 0.723 | 0.701 | 1.000 | 0.407 |
| **XM_CONFLICT** | 0.081 | 0.139 | 0.446 | 0.407 | 1.000 |

> **This is not five engines.** P1 and X9a are the same object with one channel swapped (ρ 0.688);
> PAIR23 is built out of BMOM and X9a and correlates 0.68–0.72 with both. There are roughly
> **three** information sources here — the ratchet family, B-MOM, and XM_CONFLICT — and the last
> two share **ρ = 0.446**, because both are intraday-momentum-from-the-open objects on the RTH
> clock.
>
> The only genuinely low pair involving the incumbent is **ρ(P1, XM_CONFLICT) = 0.081**. That one
> number is why anything below works.

## 2. Each component alone — per unit; the fixed-DD column is scale-invariant

| component | trades | $/ctrRT | wk $ | **wk$ @ fixed DD** | wk + % | max DD | top-5 | worst wk | t |
|---|---|---|---|---|---|---|---|---|---|
| P1_PCT | 2,401 | $14.44 | $1,394 | **$1,230** | 56.3 % | $22,931 | $17,835 | −$9,221 | 4.16 |
| X9a_PCT | 2,342 | $14.46 | $1,202 | $974 | 55.9 % | $24,969 | $17,804 | −$9,517 | 3.77 |
| BMOM | 1,152 | $13.02 | $1,121 | $509 | 57.3 % | $44,584 | $27,795 | −$16,972 | 2.42 |
| **PAIR23** | 9,330 | — | $1,169 | **$1,309** | **60.6 %** | $18,088 | **$11,362** | −$8,642 | 4.36 |
| XM_CONFLICT | 348 | $12.50 | $916 | $918 | 48.8 % | $20,201 | $16,652 | −$14,577 | 3.05 |

`XM_CONFLICT` at the corrected anchor: **348 trades, $560/trade, 54.6 % hit.** Its standalone
positive-week rate is only 48.8 % — it trades ~1.6 days a week, so many weeks are flat. **It is not
a good standalone object and was never claimed to be.**

## 3. ⭐ Combinations — and the preregistered primary is not the winner

Inverse-volatility equal risk. No free parameter, which is why it was preregistered.

| combination | wk $ | **wk$ @ fixed DD** | wk + % | **max DD** | **top-5** | worst wk | CVaR5 | **t** |
|---|---|---|---|---|---|---|---|---|
| P1_PCT alone | $1,394 | $1,230 | 56.3 % | $22,931 | $17,835 | −$9,221 | −$6,092 | 4.16 |
| PAIR23 alone | $1,169 | $1,309 | 60.6 % | $18,088 | $11,362 | −$8,642 | −$5,961 | 4.36 |
| **P1 + XM** | $1,142 | **$2,012** | 59.2 % | **$11,489** | **$8,735** | −$7,611 | −$4,593 | **4.90** |
| P1 + PAIR + XM *(preregistered primary)* | $1,152 | **$1,766** | **59.6 %** | $13,205 | $8,616 | **−$6,387** | −$4,606 | **5.01** |
| all five | $1,158 | $1,641 | 59.2 % | $14,284 | $9,100 | −$6,480 | −$4,996 | 4.87 |
| BMOM + X9a + XM | $1,071 | $1,279 | 59.6 % | $16,950 | $9,767 | −$8,288 | −$5,302 | 4.51 |
| PAIR + XM | $1,050 | $1,252 | 61.5 % | $16,973 | $9,953 | −$9,155 | −$5,266 | 4.41 |
| P1 + PAIR | $1,269 | $1,554 | 59.2 % | $16,534 | $12,118 | −$7,415 | −$5,191 | 4.65 |

> **`P1 + XM` wins on the headline metric and my preregistered `P1 + PAIR + XM` comes second.**
> That is a best-of-six selection and it is disclosed as one. Two things make it more than that:
>
> 1. **`PAIR + XM` ($1,252) is *worse* than `PAIR` alone ($1,309).** Adding the pair to P1 + XM
>    costs 12 % of the headline. The matrix explains it — PAIR23 is ρ 0.676 with P1 and ρ 0.723
>    with X9a, so it contributes correlated risk without contributing information.
> 2. **The independent integer-ratio grid agrees.** Its argmax over 63 cells is
>    **2 P1 : 0 PAIR : 1 XM** — *zero* pair — at $2,241. Two different weighting methods, one
>    parameter-free and one a coarse grid, converge on "drop the pair".
>
> The grid's top-8 span $1,898 → $2,241, **18.1 % apart — a narrow plateau, not a broad one.**
> Per the rule fixed in advance, **no cell of that grid is adopted.**

⚠️ The weighting convention matters and the range should be quoted, not a point:
**W102 measured `P1 + XM` income-matched at +45.1 %; inverse-vol gives +63.5 %.** Both are
defensible; neither is "the" number. The honest statement is **+45 % to +64 % depending on how the
two are weighted**, and the drawdown improvement is the more robust half of it.

## 4. The primary combination, per year and recency

Weights: P1_PCT 0.298 · PAIR23 0.371 · XM_CONFLICT 0.331.

| window | sessions | wk $ | wk$ @ fixed DD | wk + % | day + % | max DD | top-5 | worst wk | t |
|---|---|---|---|---|---|---|---|---|---|
| FULL | 1,058 | $1,152 | $1,766 | 59.6 % | 46.6 % | $13,205 | $8,616 | −$6,387 | 5.01 |
| 2024+ | 670 | $1,417 | $2,172 | 60.7 % | 46.9 % | $13,205 | $8,616 | −$6,387 | 4.28 |
| 2025 | 259 | $1,182 | **$2,645** | 60.4 % | 45.9 % | $9,047 | $6,391 | −$6,387 | 2.22 |
| 2026 YTD ⚠️ | 152 | $1,261 | $1,933 | 51.6 % | 46.1 % | $13,205 | $6,357 | −$6,243 | 1.49 |
| t12m | 261 | $1,268 | $1,943 | 58.5 % | 47.1 % | $13,205 | $7,875 | −$6,387 | 2.16 |
| t6m ⚠️ | 131 | $1,200 | $1,840 | 46.2 % | 45.0 % | $13,205 | $6,357 | −$6,243 | 1.21 |
| **t3m** ⚠️ | 67 | **$326** | **$499** | **35.7 %** | 44.8 % | $13,205 | $10,283 | −$6,243 | **0.25** |

⚠️ 2026 YTD, t6m and t3m overlap the BURNED span 2026-05-31 → 07-31.

> **The last three months are weak — $499/wk at fixed drawdown, 35.7 % positive weeks, t = 0.25.**
> n = 14 weeks, so it is not evidence of decay; it is also not evidence against it. It is recorded
> because a combination that looks like t = 5.01 over four years and t = 0.25 over three months is
> exactly the shape that a reader deserves to see before deciding anything.

## 5. ⭐ CAPTURE LEDGER v3 (TASK 13) — what is STILL unmonetized

| segment | executable ceiling | p\* | P1 alone | **BASE** | **residual** | **covered** |
|---|---|---|---|---|---|---|
| MORN 09:45–11:29 | $1,744 | 0.5048 | $34 | **$78** | $1,667 | **4.4 %** |
| ON_EU 00:00–07:59 | $1,224 | 0.5078 | $39 | $18 | $1,206 | 1.5 % |
| MID 11:30–13:29 | $1,197 | 0.5059 | $48 | $19 | $1,178 | 1.6 % |
| AFT 13:30–15:44 | $1,170 | 0.5058 | $9 | $3 | $1,166 | **0.3 %** |
| ON_ASIA 18:00–23:59 | $1,026 | 0.5139 | $60 | $39 | $987 | 3.8 % |
| OPEN 09:30–09:44 | $887 | 0.5106 | $34 | $45 | $841 | 5.1 % |
| PRE 08:00–09:29 | $886 | 0.5107 | $51 | $28 | $858 | 3.1 % |
| POST | $545 | 0.5144 | $3 | $1 | $544 | 0.2 % |
| CLOSE | $515 | 0.5130 | $3 | $1 | $514 | 0.2 % |

⚠️ **Scale caveat, stated because the table would otherwise mislead:** the BASE column is the
inverse-vol *weighted* combination, whose total income is 0.826× P1's. Divide by 0.826 to compare
capture like-for-like. Doing that:

| class | ceiling | p\* | P1 alone | **BASE, income-matched** | direction |
|---|---|---|---|---|---|
| TREND-UP | $8,610 | 0.5092 | **+$1,991** | +$1,605 | ↓ worse |
| **TREND-DOWN** | $11,115 | 0.5072 | **−$495** | **+$195** | ⭐ **sign flipped** |
| **REVERSAL** | $9,096 | 0.5088 | **−$64** | **+$27** | ⭐ **sign flipped** |
| RANGE | $8,765 | 0.5091 | −$215 | −$317 | ↓ worse |
| MIXED | $9,063 | 0.5087 | +$71 | −$51 | ↓ worse |

> **The base trades TREND-UP capture for TREND-DOWN and REVERSAL capture.** That is a genuine
> diversification trade, not a free lunch, and it is the first time in this campaign that either of
> those two classes has been positive. TREND-DOWN was W99's #1 ranked block; it is now **+$195**
> instead of **−$495** — and **$10,953 of it per session of that class is still on the table.**

### And the number that should govern the next hundred waves

> ### **After 103 waves, the base captures between 0.2 % and 5.1 % of what is executable in every
> ### segment of the session.** The largest single hole is unchanged: **MORN, $1,667/session,
> ### at a break-even direction accuracy of 50.48 %.**
>
> This is not a failure — a 50.48 % bar means the ceiling is enormous relative to what anyone
> captures, and the ceiling assumes a perfect direction call nine times a day. But it does mean the
> honest description of the state of this campaign is **"we monetize a few percent of a very large
> and rising opportunity"**, and the agenda is nowhere near exhausted.

## 6. Decision

**Nothing promoted, nothing enabled.**

| | |
|---|---|
| **Research base** | `P1/PCT` — the incumbent with W98's per-contract box. Unchanged by this wave. |
| **Best candidate portfolio** | `{P1/PCT + XM_CONFLICT}`, inverse-vol. EVIDENCE **STRONG (current regime) · REGIME_LOCAL**; ENGINEERING **RESEARCH_ONLY**. |
| **Strongest ratchet-family object** | `PAIR23` at $1,309 — and it adds nothing on top of P1 + XM. |
| **Demoted** | `NETFUSE_1` (deep-negative). `PAIR23` as a *portfolio addition* — it is the best single ratchet object and the worst third wheel. |

Next: the NinjaScript for `XM_CONFLICT`, and the two rows the ledger still points at — MORN at
p\* = 0.5048, and the volume forms W100 did not test.
