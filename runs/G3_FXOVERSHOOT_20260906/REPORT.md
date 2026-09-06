# G3_FXOVERSHOOT_20260906 — delayed FX overshooting after FOMC (6E) — REPORT

**Ledger:** G00089, family GENESIS3_EVENT · **Evidence status of every number:** DISCOVERY_CONSUMED
**Verdict:** **CLOSED AT SCOPE (S28)** — G2 FAIL (UNDERPOWERED_STILL), G4 FAIL (Scholl-Uhlig
one-third concentration). No FXOVERSHOOT01 candidate. **The 6E event-transition cell gets its
first entry — a closure.**

## Frozen object (as preregistered)

FOMC scheduled decision days 2009-01-01..2026-07-31 from the G00084 calendar artifact
(`runs/GENESIS_H2_CALENDAR_20260828/out/calendar_artifacts/fomc_meetings_2006_2026.csv`,
sha `57a7acfb…`), 140 events **minus the 4 data-hole dates G00084 recorded** (2014-01-29,
2015-12-16, 2018-12-19, 2024-12-18) = 136 calendar events. Surprise proxy = the rates market's
own event-day move: **sign of ZN close(D-1)→close(D0)** (roll-adjusted points, causal at D0
close). Sign convention stated in spec before results: rates DOWN = ZN UP = dovish = USD-negative
⇒ **6E position = sign(ZN D0 move)**. PRIMARY = hold 6E close(D0)→close(D+10), after-cost
(1 tick/side + $4.36/ctrRT = **$16.86 RT**, BASIS COMMISSION+SPREAD MODELED; $125,000/pt).
Data reused AS-IS with shas asserted: 6E `runs/DAILY_6E_EXTRACT_AUTOPSY_20260906/out/6e_daily.parquet`
(sha `af70be2d…` = extract_meta value; causal roll, s7 reproduction max err 0.0), ZN
`runs/G3_AUCTCYCLE_20260906/out/zn_daily.parquet` (sha `13fc5165…` = certified manifest). Seal
asserted (both max 2026-07-31 < 2026-08-01).

## Recorded amendment (before any outcome was computed)

The certified 6E store contains **46 structural roll-gap sessions with NaN ret_points** (6E
contract lives barely overlap — named in its extract_meta; the certified s7 reproduction covers
the 4,227 defined rows). Rule recorded on input inspection, before any result: NaN = NOT
COMPUTABLE → events whose D+1..D+10 window contains one are excluded and listed
(WINDOW_ROLL_GAP), never zero-filled; the same drop is re-applied inside the shift null and the
control pool; the auxiliary drift60 estimator uses nanmean (≥50 of 60 defined required).

## Event realization

136 calendar events → **126 traded**. Excluded and listed: 2 ZN_BEFORE_SERIES (2009-01-28,
2009-03-18), 2 WINDOW_ROLL_GAP (2011-12-13, 2012-03-13), 4 **6E_SESSION_MISSING** (2012-12-12,
2017-06-14, 2017-12-13, 2021-12-15 — 6E's own store holes, distinct from ZB's four),
1 SIGNAL_SESSION_MISSING (2016-09-21, the known ZN hole), 1 WINDOW_BEYOND_SEAL (2026-07-29).
Zero ZERO_SIGNAL_NO_TRADE. Min inter-event gap 23 6E sessions — 10-day windows never overlap.
Sides: 71 LONG 6E (dovish) / 55 SHORT (hawkish).

## Gate table (program-printed; full text in out/gate_table.txt)

| Gate | Result | Spec | Observed |
|---|---|---|---|
| G1_MDE_first | PASS | printed (~130 events) | N=126 traded of 136 calendar; MDE80 = 0.005115 pt ($639/ct); printed before observed |
| G2_edge | **FAIL** | after-cost mean > 0 AND event-block CI95 excludes 0 AND shift-null p < 0.05 | mean +0.000421 pt ($+53/ct), CI95 [−0.003216, +0.004133], p = 0.8410 |
| G3_control | PASS | beats matched non-FOMC same-weekday AND survives drift-residualization | (a) diff +0.000544 pt PASS; (b) resid mean +0.000779 pt PASS |
| G4_subsample_fragility | **FAIL** | era thirds printed; effect living in ONE third = FAIL | signs pos/neg/neg → one-third-concentrated |
| G5_cost | PASS | 6E tick $6.25, 10-day hold — trivial; printed | primary +0.000421, stress +0.000321 pt; no sign flip; cost 0.6% of gross sd |

Power language on the G2 FAIL: **UNDERPOWERED_STILL** (MDE80 0.005115 pt vs 3×|obs| 0.001263 —
the observed mean is ~1/12 of MDE80; this cell cannot be powered by more shifts, only by more
events). The closure does **not** hinge on power: G4 is a structural kill from the card's own
preregistered clause.

## Era thirds (out/era_thirds.csv) — the Scholl-Uhlig gate

| third | span | n | gross pt | after-cost pt | $/ct | sign | hit |
|---|---|---|---|---|---|---|---|
| 1 | 2009-04-29..2014-12-17 | 42 | +0.004562 | +0.004427 | +$553 | pos | 0.595 |
| 2 | 2015-01-28..2020-12-16 | 42 | −0.002432 | −0.002567 | −$321 | neg | 0.500 |
| 3 | 2021-01-27..2026-06-17 | 42 | −0.000462 | −0.000597 | −$75 | neg | 0.524 |

Third 1 alone contributes +0.186 pt of pooled sum vs the pooled +0.053 pt — **more than 100% of
the pooled effect lives in 2009–2014**, and the last decade is net negative. This is precisely
the Scholl-Uhlig sample-dependence critique of delayed overshooting, reproduced in-house on
futures data; the card preregistered that finding as a FAIL condition and it fired.

## Secondary path ({D+5, D+20} reported, no gate)

D+5 after-cost +0.000325 pt ($+41/ct, n=126); D+20 +0.001263 pt ($+158/ct, n=123). The h=1..20
path is negative at h=1..4, then mildly positive, peaking near h=13-14 (+0.0019–0.0020 pt) —
*shape*-consistent with a delayed adjustment but at ~1/3 of MDE80 at best; no horizon is licensed
(post-hoc horizon-pick ban), and the thirds table says even that shape is a 2009–2014 artifact.

## Classification and reading

- **G3 PASS next to G2/G4 FAIL is a classification, not a conflict**: FOMC days beat the generic
  same-weekday ZN-sign-conditioned control (itself ≈ −0.0001 pt) and the drift residualization
  slightly *raises* the mean (+0.000779) — the tiny positive point estimate is not an artifact of
  unconditional EUR drift. There is simply not enough of it, and what there is lives in one era.
- Mechanism verdict at this scope: **delayed overshooting on FOMC monetary surprises, proxied by
  the rates market's own move, is not harvestable in 6E daily post-2009** — the pre-2015 (ZLB/QE)
  window carried the entire effect and the regime ended.
- The exclusions surfaced a new data fact: the local 6E store misses 4 FOMC decision *sessions*
  (2012-12-12, 2017-06-14, 2017-12-13, 2021-12-15) — recorded for any future 6E event work.

## S28 closure block

```
Closed:  observable = 126 FOMC decision days 2009-04..2026-06 (G00084 calendar minus its 4 recorded holes)
on certified causal-roll 6E daily; surprise proxy = sign of ZN close(D-1)->close(D0) (never a purchased series)
representation = hold 6E close(D0)->close(D+10) in the ZN-implied (dovish=long-EUR) direction
event = FOMC decision day      horizon = 10 sessions (D+5/D+20 reported)      target = delayed-overshooting
drift vs weekday-matched control + trailing-60d drift residualization      execution = MODELED 1-tick rung $16.86 RT
sample = 2009-04..2026-06, N 126, MDE80 0.005115 pt ($639/event)      reason = +$53/event after cost
(p 0.84, CI95 [-$402,+$517]) = UNDERPOWERED_STILL at ~1/12 of MDE80; Scholl-Uhlig thirds +$553/-$321/-$75 =
the effect lives ONLY in 2009-14 (>100% of pooled sum; the card's own preregistered fragility clause) --
the delayed-overshooting sample-dependence critique reproduced in-house. G3 controls PASS (beats weekday
control -0.0001 pt; drift residualization RAISES the mean to +0.000779) -- moot after the concentration kill.
{D+5, D+20} horizon variants = same object, same shape, closed with it.
```
Adjacent questions still open: EUR-USD **rate-differential carry direction** (autopsy RANK 2 —
needs one free external short-rate series, not locally computable; the stated G3 limitation);
intraday announcement-window 6E response (no local intraday FX data); 6E month-end fix flow is
its own registered card (G00091), not closed here. NOT closed: the 6E row itself — this is its
first, now-filled event-transition cell.

## Anomalies

1. 6E store NaN roll-gaps (46 sessions) required a NaN-handling amendment, recorded in the
   program header on input inspection **before any outcome was computed**; 2 events excluded
   WINDOW_ROLL_GAP. Disclosed here, mechanical everywhere (null and control pool included).
2. Four 6E-specific FOMC-session store holes (see above) — new data fact, listed, not in ZB's set.
3. Event weekday mix is nearly degenerate (115 of 126 Wednesdays), so the weekday-matched control
   is effectively a Wednesday control; spec-literal, printed as-is.
4. Shift-null shifted-family survivors run 87..123 (mean 109.9) because the frozen drop rules are
   re-applied at shifted positions — dependence-preserving, slightly conservative.
5. Bootstrap CI95 and t-CI95 agree to <0.0002 pt (second-computation cross-check consistent).
6. The p-value headline carries its stated event semantics in G1 (per the CAP01 rule) and the
   t-CI second computation.
7. REPORT.md could not be written into the run directory (harness refused the Write); full report
   content returned in structured output instead, per pod rules.

## Outputs

`out/gate_table.txt` (full program log + gate table), `out/event_table.csv` (136 rows: 126 traded
with per-h path, 10 excluded listed), `out/era_thirds.csv`. Program: `src/run_fxovershoot.py`
(seed 20260906, 999 shared-draw circular shifts along the 6E calendar, 10,000-draw event-block
bootstrap). Spec committed before results (git `cd14e0e`).