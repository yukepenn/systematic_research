# PORT01 — Product A + Product B risk-normalized portfolio synthesis

**Disposition: SYNTHESIS COMPLETE — no candidate, no alpha claim.** Given what Product A and
Product B actually are today (both unchanged after 12 independent alpha-search hypotheses
across the CONTINUOUS EVOLUTION phase), this asks the different-in-kind question directive
sec53-54/80 authorizes: what does running them together actually buy, in risk terms.

## Correctness gate: PASS

Session-level aggregation reproduces all three certified canonical nets exactly: A=$177,924.40,
B-NQ=$301,915.92, B-MNQ=$28,587.10.

## Capital footprint

Product A's exposure, expressed in NQ-equivalent contracts (MNQ is contractually 1/10 NQ
notional/margin — the same underlying index): **peak 1.10 NQ-equivalent contracts, mean 0.60
when active.** Product B (either instrument) is always exactly **1.0 NQ-equivalent contract**
when in a position. Product A's peak capital intensity is therefore very close to running a
single Product-B contract — a useful, previously-undocumented fact for thinking about relative
capital allocation between the two objects.

## Standalone battery (canonical window)

| | net | Sharpe | Sortino | Calmar | maxDD_eod | CDaR95 |
|---|---:|---:|---:|---:|---:|---:|
| A | $177,924.40 | 1.18 | 2.34 | 2.29 | $17,192.90 | $14,323.08 |
| B-NQ | $301,915.92 | 1.11 | 1.88 | 1.12 | $59,717.44 | $44,518.39 |
| B-MNQ | $28,587.10 | 1.05 | 1.78 | 1.05 | $6,050.70 | $4,507.20 |

## Combined portfolios

| | net | Sharpe | Sortino | Calmar | maxDD_eod | CDaR95 |
|---|---:|---:|---:|---:|---:|---:|
| A + B-NQ (naive dollar sum) | $479,840.32 | 1.17 | 2.10 | 1.38 | $76,910.34 | $57,172.18 |
| A + B-MNQ (naive dollar sum) | $206,511.50 | 1.18 | 2.30 | 1.97 | $23,243.60 | $18,216.79 |
| A (capital-normalized to 1.0 NQ-equiv) | $161,749.45 | 1.18 | 2.34 | 2.29 | $15,629.91 | $13,020.98 |
| A(capnorm) + B-NQ | $463,665.37 | 1.16 | 2.09 | 1.36 | $75,347.35 | $55,995.15 |
| A(capnorm) + B-MNQ | $190,336.55 | 1.18 | 2.29 | 1.94 | $21,680.61 | $16,935.77 |

## Diversification decomposition — the headline finding

Session-level correlation(A, B-NQ) = **0.8874** (matches H0's own already-documented finding).
Testing whether combined drawdown is less than the naive sum of standalone drawdowns (the
signature of genuine diversification): **maxDD(A capnorm) + maxDD(B-NQ) = $15,629.91 +
$59,717.44 = $75,347.35 — and the ACTUAL combined maxDD is $75,347.35, an exact match.**
Diversification benefit = **$0.00, 0.0% reduction.** The same exact-match pattern holds for the
A(capnorm)+B-MNQ combination ($21,680.61 naive sum = $21,680.61 actual).

**Combining Product A and Product B, at any capital normalization tested, produces zero
drawdown diversification benefit — their worst days co-occur closely enough that portfolio-level
risk is, to the dollar, the simple sum of standalone risk.** This is not a surprising result
given H0's own prior finding (0.887 correlation, 99.97% bar-level directional agreement when
both hold a position, P(A loses|B loses)=91%) — PORT01's contribution is to **quantify exactly
how much of a "free lunch" combining them offers: none, at the drawdown level.** Sharpe/Sortino
of the combined portfolios sit between the two standalone values, as expected from a
high-correlation blend, not from genuine risk reduction.

## Explicit non-alpha framing (per directive sec53's own caution)

This is a sizing/capital-allocation property of two already-existing, already-unchanged objects
that substantially share a latent signal — not a new edge, not a candidate, not a promotion
claim. The practical implication for the owner: **capital efficiency gains for this system
family will have to come from finding genuinely new, lower-correlation alpha** (the entire
CONTINUOUS EVOLUTION phase's own search, so far unsuccessful across 12 independent hypotheses),
**not from combining Product A and Product B as they currently stand** — running both together
is economically equivalent, in risk terms, to running a larger single position in whichever one
you'd otherwise prefer, not a genuine two-legged portfolio.

## Verdict

No candidate constructed. This is a synthesis/reporting result: precisely quantifies, rather than
just qualitatively describes, the limited value of combining the campaign's two current
incumbents at the portfolio level. Both Product A and Product B remain unchanged.
