# ALPHA THROUGHPUT SCOREBOARD (Amendment 5)

Updated: 2026-08-08 (W7 complete — **ZONE F CLOSED per §9/§34, reports/ZONE_F_FINAL_VERDICT.md**)

FINAL Zone-F tallies: 16 trade-rule families tested, 16 negative plateaus (~500 configs);
ceiling measured 3× (best +3.21pp vs 7-9.1pp needed); FSS-9 VWAP-reclaim +2.9pp =
conditional-state record; red team discharged (RT-1 four scope conditions honored,
RT-2 empty-list met after W7). UNRESOLVED carried: B1-overnight, S2a-short, H-D3@1min,
binding-recovery variant, ES spread/size, L3/L4. Holdout + confirmation pool NEVER read.
Open program: A (patient-exit test), B (momentum build spec [gate passed], B1 2005+,
event-FADE new spec, GC/CL r-screen), roles B/C on Solar.

Historical (W5 record below):

| Metric | Value |
|---|---|
| Families tested (trade-rule level) | 14 (+W5: clean-deep-entry, fast-FSS-2, FSS-3, FSS-6, FSS-7, B1-overnight) |
| Families killed | 14 |
| Candidates alive (Tier-0 positive) | 0 |
| Candidates in internal confirmation | 0 |
| StrategyV01 built | 0 |
| Best C1 net ticks/trade so far | none positive |
| **Predictability ceiling (C5)** | **INSUFFICIENT: best top-decile lift +2.42pp [+0.15,+4.63] vs 7.0–9.1pp gap; all Brier skills negative** |
| Open gates passed | B2 momentum-family correlation gate (ρ_full +0.134, ρ_losing −0.065) → build spec permitted |
| Sizing frontier (A1) | safe c=0.15 across all 6 scenarios; full-Kelly ≈ $54k/NQ; c=0.15 ⇒ ~1 MNQ/$36k |
| Sealed holdout reads consumed | 0 |
| Waves without Pareto improvement | 3 (W3, W4, W5) — stop-condition §35.9 now met for Zone F |
| Amendment 6 §9 closure checklist | families ✓ ×4 of 5 (FSS-10 ES pending), ceiling ✓, plateau ✓, no conditional state ✓, red team PENDING |

Reference constants: viability gap at C1 ≈ 7–10pp on 24–32t brackets; in-state spread
2.42t; NULL-3 curves = persistence nulls; path toll: P(−4 before +8) ≈ 0.63, median
pre-target drawdown 7.5t, clean fraction of +20t reachers ≈ 42% at MAE≤6; passive
fills at mechanical pullback levels are adversely selected (gross −1.50 vs −0.93
market, W4-A FACT).

W5 queue (highest EVI): W5-1 deep-pullback/clean-entry family (from W4-E contrast:
ret30 −15t + eff60 + flow alignment); FSS-10 ES conditional lift (pipeline confirmed,
archival running); fast FSS-2 (5–30s clocks); FSS-6/7; ML conditional quality (§23)
once any base exists.

## Program status (2026-08-08, post-W8)
- **B-MOM: the first CI_lo>0 economics in the campaign** (PF 1.21, +47.9t/trade, C1 AND
  C2, positive every year, Sharpe 1.26) — NOT PROMOTED: rho_full 0.347 vs frozen <0.3
  gate (losing-day rho 0.046 passes). Parked; any correlation-targeting successor needs
  a new spec.
- B-FADE: characterized (placebo negative; 60min CI_lo>0 NFP-driven; 2025 failed;
  concentration heavy). Confirmation = 2006-2021 minute + historical calendar (both in
  flight). Decay-amended four-way verdict governs.
- A-EXIT passive track: CLOSED by frozen rule (Arm A points +2.3/+3.5t but n=31 CI
  spans zero; Arm B negative as predicted).
- ROLE-B: weak-negative (rv60 axis in-sample; OOF AUC 0.447 null). No filter.
- W9 in flight: B1 2006+ resolution (decay-aware), H-D3@1min final. W9-3 pending
  calendar. Minute substrate: 6.47M bars 2006-01-05..2026-05-29 (hash dfd017ef).

## PHASE END (2026-08-08): Program B resolution — three parked candidates, zero frozen
| Candidate | Status | Decisive evidence |
|---|---|---|
| B-MOM | PARKED (regime-local) | 2022-26 CI_lo>0 both costs BUT rho 0.347 gate fail AND 16 unseen years show PF 1.013 (no pre-2022 structure); the 2022+ edge shares Solar's regime fuel |
| B-FADE | PARKED (possibly-recent) | OOS 2006-21 +1.68t = 1/30th of IS +47t; 2006-14 era real then decayed; resolution = forward release days (~2/month) |
| B1 overnight | PARKED (marginal) | +8.4t/night point, rho 0.015, recent-loaded trend — but bootstrap under-converged (10k-rep CI_lo<0), top-10 nights 53% |
| H-D3 | CLOSED FINAL | mechanism real (20yr t 2.92), economics unresolvable |
Forward re-reads: Solar MONITOR-01 #2 >= 2026-11-01; Program-B combined re-read
(B1/B-FADE/B-MOM on accumulated forward data) >= 2027-08-01. Blocked-on-restart:
SWScalpTickExport_v3 compile (s20251117 completeness re-export only).
