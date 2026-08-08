# RECENT_REGIME_BMOM — the B-MOM Challenger Resolution

_2026-08-08. Owner directive §15: B-MOM reclassified RECENT_REGIME_CHALLENGER,
frozen rule, no retuning; portfolio value decides._

## Frozen rule (W8-1, unchanged)

END-stamped 3-min RTH bars; noise band = 09:30 open ± trailing-14-day same-slot mean
|close−open0930| (prior days only); RTH-anchored VWAP; LONG when close > max(band
upper, VWAP), SHORT when close < min(lower, VWAP), hold until opposite signal or 15:57
closeout; entries 09:33-15:54; 1 NQ; C1 2.872t/RT. Certified in-repo generator:
`src/analytics/sm_bmom.py` (reconciled 1,333/1,333 trades vs the committed ledger).

## Evidence stack

- Dev 2022→2026-05 (W8): PF 1.21, +47.9t/trade CI_lo>0 at C1 AND C2, Sharpe 1.253,
  positive every year, net $319k (1 NQ). FACT
- Pre-2022 (W10): PF 1.013, +0.73t/trade, Sharpe 0.066 — REGIME-LOCAL, no era passes. FACT
- **SM06 symmetry: Solar is REGIME_LOCAL on the same window too** (net −$9.0k/16yr).
  The scalping-lab ρ_full<0.3 standalone gate rejected B-MOM for "sharing Solar's
  regime fuel"; the fuel is shared BECAUSE both are current-regime engines. Under the
  owner directive, losing-day correlation is the binding complementarity criterion. FACT
- SM05 portfolio (frozen gates): **PASSES at every risk share 0.2-0.5** — ρ losing-days
  0.043 does the work; maxDD −29% at w=0.5; worst month improved at every w; H1/H2
  positive. Advanced to candidate. FACT
- Gain-side crowding: 8/20 top-gain-day overlap with Solar — combined same-day gross
  exposure is capped in the master spec. FACT

## Standing requirements on any deployment of the B-MOM leg

1. Decay monitor: rolling 2-year daily-mean of the B-MOM leg with a preregistered
   floor (pre-2022 rolling mean never sustained the 2022+ level — the leg dies if that
   statistic reverts; attach CUSUM/GLR sequential test in MONITOR-01 v2).
2. No retuning, ever, of band window / VWAP construction / clocks (killed-axis rule).
3. The leg's weight lives on the SM05 plateau (0.2-0.5 risk share); low end preferred
   for regime exposure (0.3 in the frozen 0.5/0.3/0.2 finalist).
4. Forward re-read of the parked standalone question ≥ 2027-08 stands (scalping-lab
   protocol) — portfolio adoption here does not overwrite that ledger.
