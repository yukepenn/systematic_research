# G3_EQROLLRICH_20260906 — Equity roll-cycle financing richness (EQROLLRICH01) — CLOSED AT SCOPE

**Ledger:** G00088, family GENESIS3_RV (registered before outcomes).
**Spec:** `spec.yaml` (committed before results). **Date executed:** 2026-09-06.
**Mechanism tested:** Hazelkorn–Moskowitz–Vasudevan (JF 2023) — futures-implied financing
richens into the equity quarterly roll when leverage demand is high; the richen-then-cheapen
path within the cycle is the flow signature. Differenced constructions only (dividend confound
bound — no level claims anywhere in this run).
**Frozen primary:** ES per quarterly cycle: same-date front/back calendar-spread daily CHANGES
(points) in event time; shape statistic = mean(ΔR over [FN−12,FN−6]) − mean(ΔR over [FN−5,FN−1]).
**FN anchor (documented in the program header before results, per spec):** FN := 3rd-Friday
expiry − 8 calendar days = the Thursday of the week preceding expiration week — the
CME-documented peak of the equity quarterly roll ("roll week"); asserted Thursday; mapped to
the last front-contract session ≤ FN. Equity index futures are cash-settled (no true first
notice); "FN" is this roll-date anchor.

## Verdict

**CLOSED AT SCOPE — the decision rule's negative branch fired mechanically: G2 FAIL, G4 FAIL
(G3 PASS).** The richen-then-cheapen shape is **not there — the observed shape has the wrong
sign**: −0.0350 pts/day (mean over 47 ES cycles; permutation p = 0.77, sign-flip p = 0.87,
t = −1.13). What the path actually does is the *reverse placement*: the spread is flat in
[FN−12,FN−6] (−0.003 pts/day pooled) and **richens in [FN−5,FN−1]** (+0.032 pts/day pooled) —
richening runs *into* the roll date rather than resolving before it — though that reversed
pattern is itself not significant here. Eras are unstable (−/−/+; 2016-21 = −0.055, n = 17),
so the mandated post-2016 stability fails independently.

**This is a DIRECTIONAL NULL WITH THIN POWER, not a powered kill.** MDE (one-sided 5%, 80%
power) = 0.0771 pts/day at N = 47 — roughly the size an HMV-scale effect would take — and the
observed |−0.035| is inside it. The run cannot rule out a small true richness shape; it can say
the preregistered signature is absent at this scale and granularity, with the point estimate
pointing the other way.

**The mechanism gate passed on its frozen wording but the mechanism story still fails at this
granularity.** Pooled matched daily richness changes ES↔NQ co-move (+0.153, naive 95% CI
[+0.03, +0.27], n = 249 pairs) — G3 PASS as frozen. But the annex cycle-level correlation of
the two roots' *shape statistics* is **negative** (−0.172, n = 21), and NQ's own mean shape is
**opposite-signed** (+0.323 pts/day, N = 27, 63% > 0; never rescues/vetoes, D14). The
co-moving component is day-level shared financing noise, not a common richen-then-cheapen
placement — which is what the flow signature would require.

## Key numbers (all printed by the program; `out/gate_table.txt` is authoritative)

| Quantity | Value |
|---|---|
| Candidate cycles | 70 (2009-03 .. 2026-06); spec anticipated ~68 |
| Included ES cycles | **47** (2009-06 .. 2024-09; all 12/12 valid) — back-month store availability is binding |
| Included NQ cycles | 27 (back-month bars post-2016 mostly begin only ~5–7 sessions before expiry) |
| MDE (printed first) | 0.0771 pts/day (= $3.86/day ES) at N = 47 — POWER IS THIN |
| Observed ES shape | **−0.0350 pts/day** (= −$1.75/day); median −0.071; share > 0 = 31.9% |
| Pooled window means | EARLY [FN−12,FN−6] −0.0030 · LATE [FN−5,FN−1] **+0.0319** pts/day |
| G2 permutation | p_perm = 0.7734 (20,000 per-cycle rotation draws, seed 20260906) |
| Second way (G6) | sign-flip p = 0.8704; one-sample t = −1.13 — qualitative agreement |
| G3 comovement | pooled matched ΔR corr **+0.1531** [+0.029, +0.272], n = 249; Spearman +0.200 |
| G3 annex | cycle-level shape corr **−0.172** (n = 21); all-matched-slots corr +0.153 |
| Eras (ES shape) | 2009-15: −0.041 (n=21) · 2016-21: **−0.055** (n=17) · 2022-26/07: +0.017 (n=9) → −/−/+ |
| NQ annex | mean shape +0.323 pts/day (N = 27, 63% > 0) — opposite sign to ES |
| Data hygiene | back zero-vol share 0.0%; staleness 0.7%; front-mirror corr +0.287 (no stale-back artifact) |
| Cost note (G5, diagnostic) | COMMISSION_ONLY $8.72/spread RT (2 × $4.36 Lifetime, installed); SPREAD_ONLY MODELED $5.00 (2 crossings × ES calendar tick $2.50); ALL_IN MODELED ~$13.72 — licenses a signal-lead, not a trade |

Gate table: G0a_SEAL PASS · G0b_FN_ANCHOR PASS · G0c_COVERAGE PASS · G1_MDE_first PASS ·
**G2_shape FAIL** · G3_comovement PASS · **G4_era FAIL** · G5_cost PASS · G6_P_MEANING PASS.
**Decision rule (spec, mechanical): G2=FAIL, G3=PASS, G4=FAIL → CLOSED AT SCOPE (S28 block).**

## §28 closure block

```
Closed:  observable = ES+NQ per-contract NT8 day-store dailies (certified ncd_day.py reader,
  seal-filtered < 2026-08-01): same-date front/back quarterly calendar-spread daily CHANGES,
  points (dividend LEVEL differenced out -- no level claims)
representation = event-time path on the front-contract session grid anchored at FN = CME equity
  roll date (3rd-Friday expiry - 8cd Thursday, documented pre-results); shape = mean(dR over
  [FN-12,FN-6]) - mean(dR over [FN-5,FN-1]); per-cycle rotation permutation null (D7)
event = quarterly equity roll cycle (ES primary, NQ mechanism mirror)   horizon = 12 pre-FN sessions
target = richen-then-cheapen shape > 0 with perm p < .05, ES/NQ comovement > 0, post-2016 stability
execution = none licensed (signal-lead scope); cost note MODELED ~$13.72 ALL_IN per ES spread RT
sample = 47 ES cycles 2009-06..2024-09 + 27 NQ cycles of 70 candidates (back-month daily bars
  post-2016 mostly begin ~5-7 sessions pre-expiry -- availability, recorded not patched);
  DISCOVERY_CONSUMED on this representation
reason = shape has the WRONG SIGN: -0.035 pts/day, perm p .77 / sign-flip .87 / t -1.13, vs MDE
  0.077 -- a DIRECTIONAL NULL WITH THIN POWER, not a powered kill; the spread actually RICHENS
  into the roll date ([FN-5,FN-1] +0.032/day vs flat earlier), the reverse placement, itself not
  significant; eras -/-/+ fail mandated post-2016 stability (2016-21 -0.055, n=17); daily ES/NQ
  richness changes do co-move (+0.15, CI [+.03,+.27]) but cycle-level SHAPE corr is NEGATIVE
  (-0.17) and NQ's own shape is opposite-signed (+0.32) -- the co-moving part is day-level
  financing noise, not a common richen-then-cheapen placement, so the flow-signature story
  fails at this daily-settle granularity
```

**Still open (adjacent, NOT closed by this run):** (1) the HMV object proper — implied financing
measured from *quote-level* calendar-spread markets with OI-weighted roll windows; the NT8 day
store structurally cannot carry it (back-month daily bars begin near the roll after 2016), so
this is an owner-gated data question (Databento GLBX has the calendar-spread book), not a free
re-run; (2) the observed *late richening into FN* (+0.032/day) as its own preregistered object —
descriptive here, untested, and would need its own falsifier, null and era read before anyone
quotes it; (3) level-based financing richness (needs a dividend model — excluded by the spec's
dividend confound bound, still excluded). **Closed with this run:** any re-windowing or
re-anchoring of the daily-settle event-time shape on ES/NQ (window variants [FN−k] on this
representation are the same object; the wrong-signed point estimate and era instability kill
the family, not one window choice).

## Anomalies / declarations (none improvised around)

1. **Sample is 47/70 ES and 27/70 NQ, not the spec's ~68.** The day store's back-month daily
   bars in later years begin only ~5–7 sessions before expiry (at/after FN), so the early
   window is unobservable for those cycles. Availability rule D5 was declared in the program
   header before results; exclusions with reasons are in `out/exclusions.csv`. Recorded, not
   patched. ES's included span ends 2024-09; the 2022-26/07 era carries n = 9.
2. **G3 passed on its frozen wording while the mechanism annex points the other way.** The spec
   froze "within-cycle richness changes co-move (corr > 0)" — the pooled daily-change corr
   (+0.153) satisfies it. The cycle-level shape-statistic corr is −0.172 and NQ's mean shape is
   opposite-signed. Had the spec frozen shape-level comovement, G3 would have FAILED. Gate
   recorded PASS as frozen; the tension is disclosed here and in the closure reason, and the
   run closes anyway on G2+G4.
3. **G6_P_MEANING added beyond the spec's five gates** (campaign doctrine: a headline
   probability needs its event stated in words plus a second computation). Decision rule
   unchanged (G2+G3+G4). Both computations agree (0.77 vs 0.87).
4. **No trimming (D6):** two December-cycle outliers reach |ΔR| = 8.0 pts (2020-12) and 6.75
   pts (2016-12), retained; top-5 printed. Staleness diagnostics show no stale-back artifact
   (0.7% flat-back-moving-front; front-mirror corr +0.287, not negative).
5. **Grid quirk:** the front session grid is the store's own session set; it contains a
   2009-05-25 (Memorial Day) bar for ES 06-09. The grid convention (D3: the store's
   front-contract sessions) was declared before results; no session was hand-edited.
6. **NQ 2026-06 cycle is included** (recent back-month coverage is richer), so NQ's span runs
   to 2026-06 while ES's ends 2024-09; the G3 co-included set (both roots) is 21 cycles, all
   2009-06..2015-09 — the comovement gate is effectively measured pre-2016.
7. **REPORT.md could not be written into the run directory** (harness refused report-file
   writes for this pod); this document is returned through the structured output instead, per
   standing instruction. All program outputs live in `runs/G3_EQROLLRICH_20260906/out/`.

**Evidence status:** DISCOVERY → this representation is now **DISCOVERY_CONSUMED**.
**Outputs:** `out/gate_table.txt` (program-printed gates), `out/cycle_paths.csv` (1,781
slot-level rows, both roots), `out/cycle_stats.csv`, `out/exclusions.csv`, `out/verdicts.json`,
`out/run_log.txt`, `src/eqrollrich.py` (frozen conventions D1–D14 in header).