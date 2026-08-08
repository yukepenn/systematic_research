# W7 — RT-2 discharge wave: the named untested families (frozen before readout, 2026-08-08)

Purpose: test exactly what RT-2 named (rt2_untested_families.md) so the Amendment 6 §9
verdict can be rendered either way. Scope is BOUNDED to RT-2's list; nothing else.
Common conventions identical to W5/W6 (costs, barriers, sequential sim, CIs, seed
20260808, discovery substrate only, RTH quote-alive unless stated).

## W7-1 — C5b augmented predictability ceiling [decisive]
Re-run the C5 protocol EXACTLY (same 30s clock, 4 labels, chronological session-grouped
expanding 5 folds, logistic + HGB depth≤3, leakage guards) with the C5 27-feature matrix
PLUS the verified-missing blocks:
- VWAP/value: RTH-anchored VWAP from grid1s (cum(last·vol)/cum(vol) from 09:30);
  features vwap_dist (mid−VWAP, t), vwap_slope60 (t/min), full-session VWAP dist.
- Prior-day levels & context: PDH/PDL/prior-RTH-close distances and overnight gap,
  computed from `runs/AUDIT03_BARS/nq_3m_2022_2026.csv` in back-adjusted space and
  converted to actual contract space via a per-session offset calibrated at 09:30
  (CSV 09:30 close − sechilo mid_last at 09:30; Last-vs-mid ±~1t error documented;
  offset constant within a session — no roll inside a session). prior_day_ret sign.
- Event flags: minutes-to-next and minutes-since-last scheduled release
  (`research/04_complementary_family/c01_announcement_calendar.csv`), clipped ±120,
  else 999; RTH clock note: 08:30 releases enter via minutes-SINCE at the open.
- ES signed flow (H-D1 proper): per-second tick-rule signed volume from raw ES trade
  rows (`substrate/raw/ES/es_<tag>.parquet`, bip==0), es_sflow10/60 and z-scored
  es_zsflow60; ES-stale seconds NaN as in W6.
Same-sample rule: rows with NaN in any new block dropped from BOTH baseline and
augmented runs. Frozen readout: per (label, model) top-decile lift baseline vs
augmented, Δ with day-clustered CI. Interpretation: any augmented cell ≥ 5pp (CI>0)
→ conversion spec; else the augmented information set is ALSO insufficient.

## W7-2 — FSS-9 trade rules: dynamic/prior levels [new level class per FSS-5 retry terms]
Levels per session: RTH-VWAP (running), PDH, PDL, prior-RTH-close (offset-converted as
above). Sweep–reclaim grammar (frozen): LONG when mid_low ≤ L − 2t then mid_last ≥
L + 1t within 60s (VWAP/prior-close are two-sided levels: also SHORT symmetric at the
same level; PDH short-side / PDL long-side primary). One trade per level-sweep episode
(re-arm at |mid−L| ≥ 8t), brackets (24,8),(32,10), cap 300s, cooldown 60s. Neighbors:
pierce {1t,4t}. Pass/plateau rules as always. ALSO the acceptance mirror as frozen
diagnostic: failure-to-reclaim within 60s → enter in sweep direction (both reported).

## W7-3 — E1 event-anchored windows [sample-limited: honest handling]
(a) Tick-level: the discovery substrate contains ~3 pre-RTH release days + 1 FOMC —
DESCRIPTIVE ONLY (no kill/pass possible at n=3; report paths, spreads, excursions in
the 08:30–09:45 and 14:00–14:30 windows). (b) Minute-powered (Program-B study, dev
window 2022→2026-05 on the 3-min CSV): initial-reaction continuation — sign of
08:30→09:30 pre-open move (from the CSV's overnight bars) traded at the 09:30 open,
fixed exits {15, 30, 60} min, release days only (calendar), C1; day-clustered CI;
subperiods. This tests the event mechanism at its powered horizon; the Zone-F variant
is recorded as UNTESTABLE-IN-CURRENT-TICK-SAMPLE either way (closure text must say so).

## Deferred (not this wave, recorded): H-D3@1min retest (needs a 1-min exporter at next
NT8 restart); S2a Tier-1 confirmation read; B1 2005+ minute extension.

§9 verdict after W7: closure declared iff W7-1 augmented ceiling < 5pp everywhere AND
W7-2 fails pass/plateau AND RT-1's four text conditions are honored (regime scoping,
FSS-6 absent-not-falsified, UNRESOLVED list, ceiling library/clock-relative + E1
sample-limited). Any W7 survivor → conversion spec instead of closure.
Artifacts: `artifacts/w7_*/`. Registry S25-S27.
