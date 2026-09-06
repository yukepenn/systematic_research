# G3_AUCTCYCLE_20260906 — Treasury auction concession cycle (AUCT01) — CLOSED AT SCOPE

**Ledger:** G00073, family GENESIS3_EVENT (registered before outcomes, seq 143).
**Spec:** `spec.yaml` (committed before results). **Date executed:** 2026-09-06.
**Mechanism tested:** Lou–Yan–Zhang (RFS 2013) slow-moving dealer capital — prices concede into
scheduled 10y/30y Treasury auctions and rebound after.
**Frozen primary:** LONG the matching future (ZN for 10y, ZB for 30y) at the auction-day close,
exit at close D+5. One event = one auction day.

## Verdict

**CLOSED AT SCOPE — decision rule's negative branch fired mechanically: G2 FAIL, G3 FAIL, and
G4 = SIGN-FLIP.** The tradeable rebound leg is dead after cost (−$64.05/event at the conservative
rung, one-sided shift-null p = 0.68), *loses* to its matched non-auction control by −$123.83/event
(control days themselves earn +$59.78), and the era profile is a sign-flip: +$203.61 (2009-15) /
−$81.82 (2016-21) / −$439.21 (2022-26/07). The effect existed only in the immediate post-crisis
era — exactly the LYZ publication sample — and has since decayed through zero into its mirror.
The run was **powered**: MDE (one-sided 5%, 80% power) = $192/event at N_eff = 406, printed
before any observed mean; the observed mean is negative, so this is a genuine kill, not
underpower.

The descriptive **concession half is visible**: −$160.75/event gross drift over close(D-5)→
close(D0) (−$150.65 for the strict D-6→D-1 window) against a +$59.78 control — prices do still
walk down into auctions. But the preregistered tradeable object is the rebound, and the rebound
does not exist net of cost in any era since 2016.

ES specificity read: ES over the same event windows is **positive** (+$377.09/event after ES
cost, CI [−8.57, +746.61]) while rates are flat/negative — the same-days pattern is generic
equity drift, not a rates-supply premium; the D7 same-size rule was not tripped (rates effect
itself ≈ 0, standardized ratio −7.4, meaningless sign).

## Data and construction (all gates program-printed; see `out/gate_table.txt`)

- **Calendar:** TreasuryDirect documented securities-search endpoint
  (`https://www.treasurydirect.gov/TA_WS/securities/search?format=json&type={Note,Bond}&startDate=…&endDate=…&dateFieldName=auctionDate`),
  pulled year-by-year 2009-01-01..2026-07-31 at 2026-09-06T13:06:47Z. Raw JSON persisted in
  `out/td_raw/` (36 pulls + `urls.txt` + timestamp); parsed calendar in `out/auction_calendar.csv`
  with source URL + pull timestamp per row. 422 auctions: 213 × 10Y (70 originals, 143
  reopenings) → ZN; 209 × 30Y (70 originals, 139 reopenings) → ZB. Selection rule (declared
  before outcomes): `type` ∈ {Note, Bond} with `originalSecurityTerm` in the 10-/30-year class;
  20-Year bonds, TIPS, FRNs excluded by construction. Full term distribution printed for audit.
- **Prices:** per-contract NT8 day `.ncd` store → `research/multi_market/src/ncd_day.py` + the
  CERTIFIED causal volume-crossover roll (`roll.py`), verbatim `extract()` from
  `runs/G3_EVENT_GC_20260906/src/build_daily_inputs.py`. ZN 4,364 / ZB 4,393 / ES 4,308
  return-days, 2009-03-31 → 2026-07-31. Identity gate `ret_points == roll.economic_returns`
  max err **0.00e+00** on all three; roll causality PASS; roll.py unit tests ALL PASS.
  All math in POINTS (DELEV01-safe; $ via $1000/pt ZN/ZB, $50/pt ES).
- **Seal:** every session ≥ 2026-08-01 hard-dropped and asserted on all three series;
  calendar capped 2026-07-31.
- **Costs (basis: MODELED, COMMISSION+SPREAD):** $4.36/ctRT + {1,2}-tick band.
  ZN $19.98/$35.61, ZB $35.61/$66.86, ES $16.86/$29.36. Gating rung = conservative (2-tick),
  declared in advance (D1). Tick sizes asserted against the data.
- **Mapping:** 414/414 mappable events matched their session date exactly; 8 early-2009
  auctions predate the usable series start (2009-03-31) and are unmapped; 8 more lack a
  complete D+1..D+5 window → **N_eff = 406** (ZN 204, ZB 202).

## Gate table (program-printed, verbatim)

```
GATE            SPEC                                                                                        OBSERVED                                                                PASS-FAIL
G0_FOUNDATIONS  calendar persisted; roll identity+causality; seal < 2026-08-01                              422 auctions; maxerr 0.0e+00 x3; seal max 2026-07-31                    PASS
G1_MDE_FIRST    MDE printed before observed; N ~ 400+ (declared floor 300)                                  MDE $192/event at N_eff=406                                             PASS
G2_EDGE         after-cost mean > 0 AND event-block CI excludes 0 AND 1-sided shift p < .05                 mean $-64.05, CI [-211.27,+80.35], p_1s 0.6822                          *** FAIL ***
G3_CONTROL      beats matched (market x weekday, +/-5-session-clean) control; delta CI ex 0                 delta $-123.83, CI [-314.11,+51.46]                                     *** FAIL ***
G4_ERA          sign per era; all+ STRUCTURAL / modern-only REGIME-LOCAL / modern<=0 SIGN-FLIP              +/-/- -> SIGN-FLIP                                                      *** FAIL ***
G5_SPECIFICITY  ES same-event read printed; same-size rule (D7) evaluated                                   ES $+377.09 CI [-8.57,+746.61]; z ratio -7.40; not same-size            PASS
G6_COST         modeled $4.36 RT + {1,2}-tick band; ticks asserted from data; cons rung gates               ZN 35.61 / ZB 66.86 cons; opt rung printed                              PASS
```

Null construction: 2000 circular shifts of the event-position mask, MIN_SHIFT 30, **one shared
uniform draw per iteration across ZN and ZB** (dependence-preserving); CIs by event-block
bootstrap (2000, fixed seed 20260906). Annex (declared non-gating): cluster-by-month bootstrap
CI [−243.82, +126.61] over 204 clusters — same conclusion, honestly wider.

## Key observed numbers

| quantity | value |
|---|---|
| Gross rebound mean | −$12.89/event (ZN −0.0279 pts, ZB +0.0022 pts) |
| After-cost (cons / opt) | **−$64.05** / −$40.65 per event |
| Event-block 95% CI (cons) | [−$211.27, +$80.35] |
| Shift null (shared draw) | mean −$28.05, sd $77.02; p 1-sided 0.6822, 2-sided 0.6367 |
| Matched control mean | +$59.78/event-equivalent (3,726 control days, 10 cells) |
| Delta vs control | −$123.83, 95% CI [−$314.11, +$51.46] |
| Eras (after-cost) | 2009-15: **+$203.61** (n=158) · 2016-21: −$81.82 (n=142) · 2022-26/07: −$439.21 (n=106) |
| ES same events | +$377.09/event after cost, CI [−$8.57, +$746.61], n=397 |
| Concession (secondary, gross) | A(D-5→D0) −$160.75 · B(D-6→D-1) −$150.65 per event |
| Combined cycle (secondary, gross) | +$148.38/event (rebound − concession A; era profile NOT gated) |
| Originals vs reopenings | +$81.58 (n=138) vs −$139.04 (n=268) after cost |
| Economics at scope | 23.5 events/yr; −$1,508/yr/contract at cons rung |

## §28 closure block

```
Closed:  observable = ZN+ZB certified causal-roll daily continuous 2009-03-31..2026-07-31 +
  TreasuryDirect 10y/30y auction calendar (422 auctions incl. reopenings, $0 public, raw pull persisted)
representation = LONG matching future at auction-day close -> close D+5 (the LYZ rebound leg);
  matched market x weekday non-auction control (+/-5-session clean); shared-draw circular-shift null
event = 10y note / 30y bond auction day (originals + reopenings)      horizon = 5 trading days
target = after-cost rebound mean > 0, beats matched control, era-classified
execution = MODELED $4.36 RT + 2-tick conservative spread (ZN $35.61, ZB $66.86/ctRT)
sample = 406 effective events 2009-04..2026-07 (DISCOVERY_CONSUMED on this representation)
reason = rebound leg DEAD and era-FLIPPED: after-cost -$64/event with MDE $192 (powered kill,
  not underpower), 1-sided shift p .68; non-auction control days at +$60 BEAT auction windows
  (delta -$124, CI [-314,+51]); eras +$204 / -$82 / -$439 = SIGN-FLIP -- alive only in the
  2009-15 post-crisis window that IS the LYZ publication sample, decayed through zero since;
  ES same-days +$377 shows the residual same-window pattern is generic drift, not rates-supply
```

**Still open (adjacent, NOT closed by this run):** (1) the CONCESSION half — prices still walk
down ~$160 gross into auctions vs a +$60 control (≈ −$220 excess); a SHORT D-5→D0 pre-auction
object is a *different frozen object* and would need its own preregistration, its own cost proof
(same ~$36-67 rung), and an era read before anyone quotes it; (2) auction-day intraday response
paths around the 13:00 ET result release (no local intraday rates data — owner-gated data
question); (3) when-issued vs futures basis (no data). **Closed with the rebound:** any
re-parameterization of the post-auction long window on this daily representation (D+1..D+5
variants are the same object; the era sign-flip kills the family, not one horizon).

## Anomalies / declarations (none improvised around)

1. **8 early-2009 auctions unmapped**: the certified day-store series' usable start is
   2009-03-31 (data-availability fact from the store, same start as every multi_market build);
   spec asked for calendar from 2009-01-01 — calendar rows are present, price coverage is not.
   Recorded, not patched.
2. **Spec ambiguities were resolved by declarations D1–D10 in the program header, written
   before any outcome was computed** (gating cost rung = conservative; one-sided null p for the
   preregistered LONG direction with two-sided printed; ±5 *trading-session* control exclusion;
   era sign rule; two concession window definitions both reported; cluster-CI annex).
3. **By-event bootstrap understates 10y/30y same-week dependence** in the pooled family (the
   two auctions are typically 1 day apart on ~0.9-correlated markets). The preregistered gate
   is the by-event CI (spec: "block bootstrap by event"); the declared non-gating
   cluster-by-month CI is printed beside it and does not change any verdict.
4. **Transport note:** the calendar was pulled with plain HTTPS GET (curl) against the exact
   documented public endpoint named in the tasking, with every raw response, URL, and the pull
   timestamp persisted under `out/td_raw/` — chosen over a summarizing fetch tool so the
   persisted pull is byte-raw. Public $0 data; no other external data touched.
5. **REPORT.md write refused by the harness** (subagent policy); the report content is returned
   in this structured output instead, per standing instruction. All other spec outputs exist:
   `out/auction_calendar.csv`, `out/gate_table.txt`, `out/event_study.csv`, `out/era_table.csv`.

**Evidence status:** all figures DISCOVERY (first read of this representation);
the 2009..2026-07 sample is DISCOVERY_CONSUMED for the auction-rebound family.
Cost basis: MODELED COMMISSION+SPREAD (never "all-in").

## Artifacts (all under `runs/G3_AUCTCYCLE_20260906/`)

- `out/auction_calendar.csv` — 422 auctions with source URL + pull timestamp
- `out/td_raw/` — 36 raw JSON pulls, `urls.txt`, `pull_timestamp_utc.txt`
- `out/zn_daily.parquet`, `out/zb_daily.parquet`, `out/es_daily.parquet` — certified causal-roll
  daily series (+ `out/inputs_manifest.json`, `out/build_inputs_log.txt`)
- `out/event_study.csv` — 414 mapped events (outcomes, concessions, flags)
- `out/era_table.csv` — the G4 table
- `out/gate_table.txt` — full program-printed run log incl. the gate table
- `out/verdicts.json` — machine-readable verdicts
- `src/build_calendar.py`, `src/build_daily_inputs.py`, `src/auction_event_study.py`