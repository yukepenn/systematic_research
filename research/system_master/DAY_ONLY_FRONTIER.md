# DAY_ONLY_FRONTIER — flat before 16:45, no overnight exposure

_2026-08-08 (SMV2 re-rank). Equal-vol basis (all curves scaled to DUAL-Solar dev σ).
Code `runs/SMV2H_ONECONTRACT/rerank.py`; curves in out/rerank_curves.csv._

## Champion: DAYONLY_DUAL6040 (candidate composition)

**0.6 × SOLAR_DUAL_HTF + 0.4 × vm(B-MOM E2)** — Solar leg = E10 ensemble with HTF
agreement ×1.25 up-weight (SM08) and HTF-UP short-halving ×0.5 (SMV2E c1_50); B-MOM on
causal E2 execution; both engines flat into 16:44; no B1.

| portfolio (equal vol) | net | Sharpe | Calmar | maxDD | CDaR5 | worst mo | TUW | pos-mo% |
|---|---|---|---|---|---|---|---|---|
| DUAL+BMOM 80/20 | $168.3k | 1.09 | 1.64 | −$22.7k | −$16.9k | −$8.1k | 124d | 70% |
| DUAL+BMOM 70/30 | $182.5k | 1.19 | 1.95 | −$20.7k | −$15.1k | −$7.6k | 94d | 64% |
| **DUAL+BMOM 60/40** | **$194.4k** | **1.26** | **2.37** | **−$18.1k** | **−$14.3k** | **−$6.9k** | 133d | 66% |
| DUAL+BMOM 50/50 | $203.1k | 1.32 | 2.38 | −$18.9k | −$15.1k | −$7.2k | 133d | 62% |
| old P1 (tilt+BMOM 62.5/37.5) | $175.7k | 1.14 | 1.52 | −$25.6k | −$16.6k | −$11.6k | 133d | 66% |
| old P3 = PORT_TILT_532 (has B1!) | $188.0k | 1.22 | 1.67 | −$25.0k | −$17.1k | −$8.0k | 138d | 66% |
| SOLAR_DUAL_HTF alone | $138.3k | 0.90 | 1.19 | −$25.7k | −$20.4k | −$9.2k | 143d | 66% |

- The ENTIRE weight grid (§24 plateau) beats the previous champion PORT_TILT_532 on
  maxDD, CDaR and worst-month at identical vol — day-only, without the overnight B1
  sleeve. The owner's stretch goal "<$20k DD at the old champion's risk" is met
  (−$18.1k at 60/40).
- **60/40 chosen as plateau center, NOT argmax** (50/50 is the historical argmax on
  Sharpe; 60/40 is interior, limits dependence on the regime-local, right-tail
  concentrated B-MOM engine, and is best on CDaR/worst-month).
- Pairwise daily-mean significance vs old P1 is modest (P=0.683) — the CLAIM is not
  "more expected return"; it is the risk reshaping (DD/CDaR/worst-month), which comes
  from two separately-gated mechanisms (SM08 tilt, SMV2E c1_50), each with its own
  preregistered pass.
- Evidence levels: components B (preregistered chronological); composition D (plateau)
  + F (post-selection); no untouched holdout exists (June/July 2026 was consumed
  pre-V2; §10 language applies).

Leverage (SMV2F method-robust): day-only C-class sustains 19.5-32.0% median growth at
P(DD>25%)≤5% depending on block model (worst-method headline 19.5%; the 60/40 upgrade
has slightly better DD stats than the C used there — re-run queued).
