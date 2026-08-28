# Portfolio B reconciled — the weighting worry was small, the selection worry was not

| | |
|---|---|
| **run class** | **BOUNDED DIAGNOSTIC.** No promotion, no new optimised portfolio, frozen B not rewritten |
| date | 2026-08-27 |
| code | `src/reconcile_b.py` · `out/reconcile_b.txt` · `out/adjudication.csv` |

> ### **In-sample weighting costs `$28/week` (1.4 %). Best-of-six selection costs `$246/week`
> ### (13.9 %). The selection premium is ~9× the weighting premium** — and I had been flagging
> ### both with equal weight.

---

## 1. Legacy B reproduces exactly

| | reproduced | published | diff |
|---|---:|---:|---:|
| weights (P1 / XM) | 0.473097 / 0.526903 | 0.473097 / 0.526903 | — |
| weekly mean | 1,141.678278 | 1,141.678278 | **0.000000** |
| maxDD | 11,489.404203 | 11,489.404203 | **0.000000** |
| fixed-DD $/week | 2,011.703681 | 2,011.703681 | **0.000000** |
| t | 4.903442 | 4.903442 | 0.000000 |

**Arithmetic truth confirmed.** `$2,012` is exactly what it claims to be.

## 2. Causal counterpart — one predeclared rule, no search

Expanding inverse-vol, volatility from weeks **strictly before** the allocation week, one-week lag,
**26-week warmup declared before results**. 187 of 213 weeks usable. P1 weight drifts 0.4271–0.5389
(mean 0.4839) versus the frozen 0.4731.

Compared **on the same weeks**, so this isolates the weighting rule and nothing else:

| | legacy (in-sample) | **causal (lagged)** | difference |
|---|---:|---:|---:|
| weekly mean $ | 1,174.72 | 1,170.44 | −4.28 |
| maxDD $ | 11,489.40 | 11,606.27 | +116.87 |
| **fixed-DD $/week** | **2,069.93** | **2,041.62** | **−28.30** |
| t | 4.60 | 4.55 | −0.05 |
| positive weeks % | 59.89 | **60.43** | +0.53 |

> ### **WEIGHTING OPTIMISM = $28.30/week — 1.4 %.**
> The inverse-vol weights were non-causal, and it barely mattered. Two nearly-equal-volatility
> streams give nearly-equal weights however you estimate them, so the in-sample advantage had
> almost nothing to extract. **The caution was correctly raised and is now correctly sized.**

## 3. Selection optimism — the one that actually matters

| combination | fixed-DD $/wk | |
|---|---:|---|
| **INV-VOL: P1 + XM** | **2,011.70** | **← SELECTED** |
| INV-VOL: P1 + PAIR + XM | 1,765.99 | ← **preregistered primary** |
| INV-VOL: all five | 1,640.82 | |
| INV-VOL: P1 + PAIR | 1,553.91 | |
| INV-VOL: BMOM + X9a + XM | 1,279.08 | |
| INV-VOL: PAIR + XM | 1,251.85 | |

> ### **SELECTION OPTIMISM (visible) = $245.71/week — 13.9 % above the object the spec named.**
> Spread across the six: **$1,251.85 … $2,011.70**. And this is the **observable part only** — the
> six baskets were themselves chosen from a larger space, so the true premium is *at least* this.

## 4. Incumbent adjudication — fixed windows, burned evidence

Fixed-DD $/week (each object on its own maxDD):

| object | 13w | 26w | 52w | 104w | FULL |
|---|---:|---:|---:|---:|---:|
| **PCT (P1)** | **−523** | 882 | 1,988 | 1,713 | 1,230 |
| **XM** | 648 | **1,935** | 1,414 | 1,118 | 918 |
| PCT+XM legacy | 256 | 2,104 | 2,250 | 2,563 | 2,012 |
| **PCT+XM causal** | 245 | 2,101 | 2,213 | 2,526 | **2,042** |

**Marginal value of XM** (causal weighting, same weeks, one risk denominator):

| window | P1 alone | P1+XM causal | **marginal** | ρ(P1,XM) | XM when P1 loses |
|---|---:|---:|---:|---:|---:|
| 13w | −523 | 245 | **+768** | 0.369 | **−1,243** |
| 26w | 882 | 2,101 | **+1,219** | 0.464 | −1,231 |
| 52w | 1,988 | 2,213 | **+225** | 0.258 | −321 |
| 104w | 1,713 | 2,526 | **+813** | 0.193 | −34 |
| FULL | 1,279 | 2,042 | **+763** | 0.086 | **+598** |

> ### **XM is positively marginal in EVERY window, including the last 13 weeks (+$768).**
> ### **But the REASON has inverted.**
>
> XM was admitted as a **diversifier** — it paid when P1 lost (+$598 full-sample). That property is
> **gone**: correlation has risen 0.086 → 0.369, and XM's conditional payoff in P1's losing weeks
> has flipped to **−$1,243**. What XM now contributes is **independent profitability** (13w $648,
> 26w $1,935 on its own), not a hedge.
>
> **It still earns its place. It no longer earns it the way it was admitted.** Those are different
> statements and the book should be understood on the second one.

## 5. ⚠️ What this run could NOT answer

**`P1/ABS` has no materialized weekly stream** in this artifact set — the five components are
`P1_PCT`, `X9a_PCT`, `BMOM`, `PAIR23`, `XM_CONFLICT`. **The PCT-vs-ABS question (owner question C)
is therefore NOT answerable from current artifacts** and is not guessed at. Answering it requires
rebuilding `P1/ABS` weekly P&L from the trade ledger on the same ISO-week axis and cost convention —
a real job, not a lookup, and outside the bounded scope of this diagnostic.

## 6. Verdict

| | |
|---|---|
| **what passed** | exact reproduction of legacy B to `0.000000` on all five published figures |
| **what changed** | the in-sample-weighting caution is **quantified and small (1.4 %)**; the best-of-six selection is **quantified and large (13.9 %)**. My earlier framing gave them equal weight and was wrong about the ordering |
| **what did not change** | frozen B is not rewritten; `$2,012` remains arithmetically correct and remains a **research** figure with no integer-contract mapping |
| **evidence class** | Portfolio B stays **REGIME-LOCAL, research-only**, now with a **≥13.9 % selection premium** attached to its headline |
| **honest restatement** | a selection-adjusted, causally-weighted B sits nearer **$1,750–1,800/week** than $2,012, and even that inherits XM's regime-local evidence class |
| **data burned** | none new — all four windows were already discovery-consumed |
