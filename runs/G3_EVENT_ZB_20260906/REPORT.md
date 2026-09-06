# G3_EVENT_ZB_20260906 — ZB native EVENT diagnostic (ledger G00067, family GENESIS3_EVENT)

**Stage:** DIAGNOSTIC / DISCOVERY. No strategy object tested; no gate passes into promotion.
**Evidence status:** DISCOVERY (substrate already DISCOVERY_CONSUMED for MR objects).
**Data:** `runs/SM1M_ZB_SUBSTRATE/out/zb_1m_2023_2026.parquet` — 923 sessions 2022-12-27 → 2026-07-31, POINTS basis only (additively back-adjusted, DELEV01), end-stamped bars, ET sessions 18:00→17:00. Seal asserted: max session = 2026-07-31.
**Code:** `src/run_event_zb.py` (the executable preregistration of every operationalization; all thresholds/horizons fixed before results). Artifacts: `out/event_tables.csv` (all 55 cells), `out/controls.csv`, `out/gate_table.txt`, `out/run_log.txt`.

## Verdict per event (preregistered screen)

| Event | Verdict | One-line reading |
|---|---|---|
| E1 macro-response path | **LEAD** | Down first response on NFP/CPI days continues down into settlement; release-specific; asymmetric (up responses show nothing) |
| E2 overnight displacement | DEAD | No cell near significance at either threshold; deltas $4–$107, all p>0.22 |
| E3 compression break | DESCRIPTIVE | Down-breaks' break-day remainder +$141 (p_raw 0.047, uncorrected only); aligned stats null |
| E4 multisession extreme | DESCRIPTIVE | 20-session extremes REVERSE (aligned next-1/2/3 −$153/−$244/−$260, p_raw 0.033/0.036/0.109) — sign-consistent with the "everything but NQ mean-reverts" law, but fails the corrected screen |
| E5 shock w/o follow-through | DEAD | 564 events, all six cells p>0.10, deltas ≤ $52 |
| E6 settlement transition | DEAD | All six cells p>0.21, deltas ≤ $8 |

**Catalog result: 1 LEAD / 2 DESCRIPTIVE / 3 DEAD.** A LEAD graduates only via a separate preregistered falsifier spec.

## The LEAD (E1)

**Cell `E1_0845_1500_sign-`**: NFP/CPI sessions whose realized 08:30→08:45 first response is DOWN. Forward path 08:45→15:00 (settlement): n=40, observed mean **−0.2445 pt** (−7.8 ticks), control-matched delta **−$238.3/contract** (block-bootstrap CI95 **[−$489.1, −$107.1]**), circular-shift **p_raw = 0.0030**, **p_corr = 0.0441** (K_eff = 14.70), n ≥ 30 ✓, |delta| ≥ 2× conservative ALL_IN ($133.72) ✓ — all three screen clauses pass.

Structure around it (all printed in `out/event_tables.csv`):
- **Release-specific, not generic momentum:** a secondary null shifting only the release flag (conditioning recomputed from receiving sessions' own moves) gives p_spec = 0.0150. The all-session sign-conditioned control (in `controls.csv`) shows the generic 08:45→15:00 sign-momentum is far weaker.
- **Asymmetric:** up first responses continue by only +$99 (p_raw 0.27). The effect is direction-concentrated — the rates analogue of the direction-concentration seen on NQ (HTFMECH01).
- **Concentrated in small first responses:** `E1_0845_1500_terc1_aligned` (smallest |response| tercile, sign-aligned) is the strongest p in the catalog (+$389, p_raw 0.0010, p_corr 0.0147) but has **n=26 < 30** and is therefore NOT a LEAD per the preregistered floor — recorded as failed clause (iii), flagged as supporting structure. `E1_0845_1500_sign-_terc1` (down AND small): −$548, p_corr 0.0588, n=10.
- The 08:45→10:30 horizon shows the same signs but nothing survives correction: the continuation accrues over the full day into settlement.

**Post-hoc descriptive robustness (labeled as such; does not alter the verdict):** by-year means 2023 −0.34 / 2024 −0.12 / 2025 −0.36 / 2026 −0.03 (n=5) — sign-consistent in all full years, weak in the 2026 stub. CPI (−0.384, n=17) stronger than NFP (−0.141, n=23). Heavy-tailed: hit rate only 60%; worst three events −2.00/−1.78/−1.13 pt; dropping the worst 2 leaves −0.158 pt = −$158/ct, still above the $133.72 cost screen. Magnitude-driven, not hit-rate-driven.

**Economic size:** delta ≈ 3.6× the conservative 2-tick ALL_IN ($66.86); net ≈ $171/ct at 2-tick, ≈ $203 at 1-tick spread. But only ~11 events/yr → ~$1.9–2.3k/yr gross per contract. Economically material **per trade**, small annual footprint — a once-a-month overlay candidate, not an engine.

**Caveats (all binding):** thin margin (p_corr 0.0441 vs 0.05; p_raw 0.0030 vs corrected bar 0.0034); DISCOVERY-consumed substrate; single 3.6-yr window, no era split possible at this n; conditioning uses the 08:45 close — an executable rule must enter at/after 08:45 with realistic fill; the tercile-interaction reading (small-down strongest) is n=10-level and must not be quoted as standalone.

## Method (as executed)

- **Catalog:** the spec's 6 events, operationalized exactly as documented in the header of `src/run_event_zb.py`; 55 preregistered cells (E1 22, E2 6, E3 6, E4 9, E5 6, E6 6), ALL reported.
- **Controls:** every conditional cell's matched unconditional control in the same wave; time-matched windows for time-locked events; per-event breach/shock-minute-matched all-session windows for E3/E5; the shift-null mean is the matched center for every cell (exact for aligned statistics); descriptive unconditional stats in `out/controls.csv`.
- **Null:** circular shift of the event-label tuple (indicator + direction + tercile + window minute) along each family's chronologically ordered eligible-session calendar; **one shared draw** (2000 U(0,1) values, seed 20260906) across all cells and families; two-sided quantile p with obs included.
- **Multiplicity:** K=55; rho_bar = 0.0508 estimated from the cross-cell correlation of the SHARED null-stat vectors; **K_eff = 14.70**; corrected bar p_raw < 0.00340, attainable (min 0.00100).
- **CIs:** session-block bootstrap (moving blocks L=5, B=2000) over the chronological event contribution series.
- **Cost basis:** G00062/W2_ZB_NATIVE MODELED ALL_IN rungs $19.98/$35.61/$66.86 (comm $4.36 + 0.5/1/2-tick spread); screen at 2×$66.86 = $133.72 = 4.28 ticks.
- **E1 calendar:** the G2_F10 macro-flag set found and reused verbatim — `runs/GENESIS_H2_CALENDAR_20260828/out/calendar_artifacts/daytype_sessions_{NFP,CPI}_DAY.csv` (both 08:30 ET; FOMC is 14:00 and correctly excluded from E1). 84 in-window releases; 78 usable events (3 zero first-response dropped per prereg; 3 lacked eligible anchors).

## Bookkeeping

E1 rel-events (nonzero r1)=78 (r1==0 dropped: 3) · E2 universe=870 (on==0: 26; events 116@1.5σ / 47@2.0σ — matches Gaussian tail rates) · E3 events=122 (ties dropped: 0) · E4 events=115 · E5 shocks=830 → no-follow-through events=564 (dropped +60 missing: 1; followed-through: 265) · E6 universe=889 (s1==0: 241; dnet==0: 15).

## What would graduate the LEAD

A separate preregistered falsifier spec, e.g.: frozen rule "on NFP/CPI sessions, if close(08:45)−close(08:30) < 0, short 1 ZB at the 08:46 bar and exit at the 15:00 settlement anchor"; ALL_IN cost at the {1,2}-tick rungs; era/half split; matched same-weekday non-release control days; circular-shift null; N ≈ 40 in-sample events plus any forward accrual. Decide the MDE honestly: at σ≈0.55 pt per event and n=40, only effects ≥ ~0.25 pt are detectable — the falsifier is near its own power edge and should say so up front.
