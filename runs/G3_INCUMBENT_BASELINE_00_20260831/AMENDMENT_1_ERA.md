# AMENDMENT 1 — I MUST WITHDRAW THE XM INDICTMENT AS AN UNQUALIFIED CLAIM

**`REPORT.md` §2 states: "At a common drawdown budget, M_11 earns LESS than P1 alone" and "XM adds
on one basis of three and destroys on the other two."**

**That is true of the full record and it is NOT true of the current regime. 100% of it is one
26-week episode in H1 2022 — before the structural break `ERABREAK01` (p = 0.0011) places at
2022-05.** The original text did not say so, and stated without that qualification it is misleading.

---

## THE MEASUREMENT

| window | weeks | fixDD/wk **P1 alone** | fixDD/wk **M_11** | verdict |
|---|---:|---:|---:|---|
| FULL 2021-W52 → 2026-W35 | 243 | 1,279 | **992** | M_11 **worse** |
| MODERN ≥ 2022-W22 (post-break) | 221 | 1,420 | **1,768** | **M_11 better** |
| 2023 onward | 190 | 1,468 | **1,847** | **M_11 better** |
| 2024 onward | 138 | 1,757 | **2,119** | **M_11 better** |

Increment of M_11 over a **risk-matched P1**, the test that indicted XM:

| window | matched vol | matched ES95 | matched maxDD |
|---|---:|---:|---:|
| FULL | +128 | **−182** | **−640** |
| MODERN | +240 | **+120** | **+491** |
| 2023+ | +272 | **+175** | **+536** |
| 2024+ | +176 | −37 | **+511** |

**In the modern era XM is additive on essentially every basis.** The one negative cell (2024+ matched
ES95, −$37/wk) is inside the noise of a strategy whose weekly mean carries a ±$550 confidence band.

## WHY THE FULL WINDOW SAID THE OPPOSITE

H1 2022, 26 weeks:

```
P1   net  +$9,220    /wk   +$355     worst week  -$7,529
XM   net -$24,624    /wk   -$947     worst week -$10,749
M_11 net -$15,404    /wk   -$592

maxDD within H1 2022:   P1 $23,099    XM $27,000    M_11 $45,138
```

**P1 was profitable through H1 2022. XM lost $24,624 — equal to −13.5% of its entire lifetime net —
in 17 traded weeks.** And that is the whole mechanism of the indictment:

```
adding XM multiplies the max drawdown by
    full window :  1.95x    ($23,099 -> $45,138)
    modern only :  1.27x    ($22,494 -> $28,596)
```

The drawdown-matched test scales P1 by `k = combined maxDD / P1 maxDD`. On the full window that `k`
is **1.954**, inflated by an episode in which XM alone nearly doubled the book's drawdown. On the
modern window it is **1.271**. The comparison was never really about XM's average contribution — it
was about one bear market.

## AND XM'S HEDGE VALUE HAS BEEN RISING, NOT FALLING

XM's contribution during **P1's worst decile of weeks**:

| window | XM | P1 in the same weeks |
|---|---:|---:|
| FULL | +$281/wk | −$5,598 |
| MODERN | +$717/wk | −$5,437 |
| 2023+ | +$878/wk | −$5,717 |
| **2024+** | **+$1,824/wk** | −$6,082 |

This cuts against the recorded finding that the P1/XM "hedge" degraded into a doubling-up as XM's
long share rose to 63.3% in 2026. **Both can be true**: unconditional correlation is stable and
positive (+0.159 full, +0.150 modern, +0.180 in 2024+ — it has *risen*), while the contribution
*conditional on P1 being in trouble* has also risen. Correlation is not the quantity that matters
for a book; worst-state contribution is. They are being conflated in the record, and this amendment
separates them.

## THE VERDICT THAT REPLACES THE INDICTMENT

Under standing owner doctrine (post-W115): **old-regime failure is a RISK CLASSIFICATION, not a
promotion veto.** Applied symmetrically, it is also not a *demotion* veto:

> **XM is not a strategy that fails to carry its risk. XM is a strategy that carried its risk badly
> in one old-regime bear market and has carried it well in every window since.**
>
> Neither window is "the" answer. The full record says *if a 2022-style regime returns, XM roughly
> doubles the book's drawdown.* The modern record says *in the regime we are actually in, XM adds
> $491–536/wk at matched drawdown and $717–1,824/wk exactly when P1 is worst.* Both belong in the
> capital plan; neither alone is the verdict.

**The capital consequence is unchanged and is the reason it matters:** plan for the $45,138
drawdown, not the $28,596 one. That is precisely what a risk classification is for.

## WHAT THIS DOES NOT CHANGE

- `G3_XMLAT_01`: XM's edge is not latency-fragile. Unaffected.
- Every figure remains **in-sample and post-selection**, and the modern window is 221 weeks of a
  221-week regime — there is no out-of-sample regime to check it against, by construction.
- **This is not a promotion of XM.** It withdraws an over-strong claim against XM. The champion
  board still has to decide whether the second leg should be XM or something better, and
  `G3_XMLAT_01`'s finding that XM's weekly mean is uncertain to ±$550 is the dominant fact in that
  decision — larger than every effect measured in this amendment.

## THE METHOD POINT

I ran the full-window comparison, got a clean and quotable result, and reported it. The era split
was not in the original run and I added it only because the drawdown-window analysis in §5 showed
that M_11's *entire* max drawdown was one 2022 episode. **The same fact that resolved the
$21,740-vs-$45,138 disagreement also invalidated my own headline** — and I would not have found it
if the earlier discrepancy had been left alone.
