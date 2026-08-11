# LEVERAGE_FRONTIER — Risk-Normalized Growth of the System Objects

_2026-08-08. Zero-burn measurement on frozen ledgers (`runs/SM09_LEVERAGE_FRONTIER/out/`).
Method: daily-rebalanced fractional scaling f on a $100k base; 5,000 block-5 circular
bootstrap 252-session paths, seed 20260808; DD measured on compounded path equity.
All objects vol-matched to SOLAR's dev daily σ before scaling (CONVENTIONS §6.7).
Bar-level intraday DD is ~8-11% deeper than daily (MTM_RECONCILIATION) — thresholds
here are daily-basis; grid step 0.25 makes f* conservative-coarse._

## The frontier (dev 2022-01→2026-05)

Median annualized geometric growth by fractional exposure f:

| f | SOLAR | SOLAR_TILT50 | PORT_033 | PORT_532 | PORT_TILT_033 | PORT_TILT_532 |
|---|---|---|---|---|---|---|
| 0.5 | 11.5% | 13.2% | 18.5% | 21.3% | 19.8% | **22.5%** |
| 1.0 | 20.4% | 24.0% | 36.0% | 42.6% | 39.1% | 44.9% |
| 1.5 | 25.8% | 31.5% | 50.9% | 61.8% | 56.6% | — |
| 2.0 | 27.8% | 35.0% | 62.8% | 78.3% | 70.3% | — |

P(maxDD > 25% within 1y) at f=1: SOLAR 0.451, TILT 0.432, PORT_033 0.292,
PORT_532 0.287, PORT_TILT_033 0.275, PORT_TILT_532 0.270. FACT

## Directive answers

- **Q30 (which architecture compounds fastest at matched risk):** at P(DD>25%) ≤ 5%
  (f=0.5 on the 0.25-grid for every dev object), **PORT_TILT_532 = 22.5%/yr**
  (P(dd25) 0.007) > PORT_532 21.3% > PORT_TILT_033 19.8% > PORT_033 18.5% >
  SOLAR_TILT50 13.2% > SOLAR 11.5% (P(dd25) 0.031). FACT
- **Q31 (can the improved system be safely levered back to baseline risk): YES** —
  every portfolio at f=0.5 carries LESS tail risk than Solar at f=0.5 while growing
  ~1.6-2.0× faster; matching Solar's P(dd25)=3.1% allows portfolio f≈0.6-0.7. FACT
- **Q32 (does the levered improved system beat unmodified Solar): YES,** by roughly
  2× annualized geometric growth at matched P(DD>25%). FACT
- **Regime-death exhibit:** SOLAR on 2006-2021 daily: negative median growth at every
  f (−0.6% at f=0.5, −4.0% at f=2.0) — leverage cannot rescue a dead edge; the
  portfolio's growth premium exists only while the current-regime edges live.
  Anti-hallucination: nothing above is a forward guarantee. FACT + warning

## PORT_TILT_532 (candidate master object) at Solar-matched vol

net $205,036 (dev) | Sharpe 1.222 | logG 1.115 | maxDD −$27,209 | worst month −$8,695 |
TUW 0.898 | roll60_min −$19,882 | H1/H2 +17.4/+135.6 $/day | P(dmean≤0)=0.0173 —
vs SOLAR: net $119,009, Sharpe 0.709, maxDD −$40,208, worst month −$18,212, roll60
−$29,810. Composition of independently-promoted components (TILT50 candidate ×
SM05-passed 0.5/0.3/0.2 weights); final adjudication at the joint holdout read. FACT

## Implementability notes

f=0.5 on $100k ≈ E10 targets halved (round(5·mean member pos), max 5 MNQ) + B-MOM
0.3-risk-share ≈ 0.66 NQ-eq ≈ 7 MNQ × 0.5 → 3-4 MNQ + B1 0.2-risk share ≈ 2 MNQ
overnight. MNQ day margin $100 (flatten variants) / initial $4,343 for overnight legs:
margin never binds before the Kelly/DD wall at these sizes (research basis, drifts).
Fee sensitivity: E10 fails its audit gate if MNQ fees rise ≥$0.10/side (standing).
