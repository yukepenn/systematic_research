# W10 — B-MOM frozen rule on unseen 2006-2021 (frozen before readout, 2026-08-08)

The W8-1 rule (14-day noise band + RTH VWAP, always-monitoring, flat 15:57, 1 NQ, C1)
is FROZEN — zero changes. Data: substrate/minute/NQ/nq1m_2005_202605.parquet,
CONFIRMATION WINDOW 2006-01→2021-12-31 ONLY (2022+ was the W8-1 characterization; do
not pool). This is a structure/decay test, not a promotion: the intraday-momentum
family has a documented decay history (Rosa 2022 on ES post-publication) — the QUESTION
is which decay shape NQ shows: (a) alive throughout; (b) alive-early→decayed→revived
(matches practitioner literature); (c) never existed pre-2022 (the W8-1 numbers are
then regime-local).

Frozen readout: net/trade + day-clustered CI by 4-year era (2006-09/2010-13/2014-17/
2018-21) and full pre-2022; PF, trades/day, yearly table; rolling 2-year daily-mean
CSV. Frozen interpretation: STRUCTURAL iff full pre-2022 daily net C1 CI_lo > 0;
REVIVED-REGIME iff 2018-21 era passes CI_lo>0 while earlier eras fail;
REGIME-LOCAL iff no era passes (the 2022-26 result then stands alone, in-sample);
CONTRADICTED iff full pre-2022 CI_hi < 0.
Verdict feeds the OWNER'S gate decision on ρ (0.347 vs 0.3) — no promotion from this
wave; no parameter changes; neighbors NOT run (frozen primary only).
Artifacts: artifacts/w10_bmom_hist/. Registry S35.
