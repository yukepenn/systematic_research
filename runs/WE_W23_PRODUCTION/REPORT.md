# WE_W23 — PRODUCTION · REPORT

Answering "why does he make $10–40k/week and we make $2,000?" with measurement.

## Q4 — the matched-tail benchmark (the only fair comparison)

| | weekly | worst week | basis |
|---|---|---|---|
| **HIS displayed** | **$8,583** | −$42,235 | **GROSS**, in-sample weekly sheets, version churned 4×, display-selected (R34) |
| **OURS at his tail** (2.0 contracts) | **$4,923** | −$43,027 | **NET**, frozen, all 205 weeks, no runtime selection |

**Efficiency per unit of tail: his 0.203 vs ours 0.117 — a 1.74× gap**, not the 5–20× the raw
weekly numbers suggest. The "$2,000 vs $10,000" comparison was 1–2 contracts against his 1
contract *at four times the tail tolerance*, and net against gross.

Exposure ladder (Sharpe is exposure-invariant; only the tail scales):

| contracts | weekly | worst week | ~annual |
|---|---|---|---|
| 1 | $2,508 | −$21,514 | $130,396 |
| **2** | **$5,015** | −$43,027 | $260,792 |
| 3 | $7,523 | −$64,541 | $391,189 |
| 5 | $12,538 | −$107,568 | $651,981 |

## Q2 — the throttle is validated a second, independent way

The bars the range throttle blocks would have produced **−$9,540 (Sharpe −0.039)** if traded.
Running with no throttle at all gives Sharpe 0.247 against the throttled 0.273. **The throttle
is not forgoing opportunity; it is declining losses.**

## Q1 — the short side: weak as built, NOT abandoned

| object | weekly | % pos | worst | Sharpe |
|---|---|---|---|---|
| SHORT vote, no halt | $184 | 47.0 % | −$15,843 | 0.038 |
| SHORT vote + halt 1300 | $265 | 45.5 % | −$8,269 | 0.067 |
| E5halt + S1 (reference) | $2,508 | 59.5 % | −$21,514 | **0.259** |
| **E5halt + S1 + SHORT vote halt1300** | **$2,769** | **63.4 %** | −$24,667 | 0.248 |

The three-sleeve version has the **highest positive-week rate in the campaign (63.4 %)** and
+10.4 % production, but costs 0.011 Sharpe and 14.7 % of tail — so it fails the preregistered
adoption rule. **The correct conclusion is not "no shorts"; it is "this short engine is not
good enough".** It was built as a mirror of the long engine, which is a design error: the
market is structurally asymmetric (up-drift, slow grinds up versus fast breaks down), so a
short sleeve should be designed for volatility expansion and breakdown, not for mirrored trend
following. W24 does that from first principles.
